import time
import sys
from pynput import keyboard # Required for asynchronous arrow key detection

from doipclient import DoIPClient
from doipclient.connectors import DoIPClientUDSConnector
from common import get_uds_client
from client_config import DOIP_SERVER_IP, DoIP_LOGICAL_ADDRESS
from udsoncan.client import Client

# Import both your Write and Read classes
from FoxPi_write import FoxPiWriteDID 
from FoxPi_read import FoxPiReadDID 

# Globals for control state
current_speed = 0
speed_changed = False
stop_triggered = False
SPEED_LIMIT = 7

PARK_SHIFT_VALUE = 2
DRIVE_SHIFT_VALUE = 5

def on_press(key):
    """Listens for keypresses in a background thread."""
    global current_speed, speed_changed, stop_triggered
    
    if stop_triggered:
        return # Ignore inputs once shutdown sequence has started

    try:
        if key == keyboard.Key.up:
            if current_speed < SPEED_LIMIT:
                current_speed += 1
                speed_changed = True
        elif key == keyboard.Key.down:
            if current_speed > 0:
                current_speed -= 1
                speed_changed = True
        elif key == keyboard.Key.enter:
            stop_triggered = True
            return False # Stop the listener thread
    except AttributeError:
        pass

def read_vehicle_data(FoxPi_Read):
    """Helper function to keep the continuous reading logic clean."""
    try:
        driving_ctrl_status = FoxPi_Read.FoxPi_Driving_Ctrl()
        time.sleep(0.5)
        motion_status = FoxPi_Read.FoxPi_Motion_Status()
        time.sleep(0.5)
        motor_status = FoxPi_Read.FoxPi_Motor_Status()
        
        # Displaying APSSpeedCMD instead of TargetSpd for this specific mode
        print(f"\033[96m[Vehicle Status]\033[0m APS TargetSpd: {driving_ctrl_status.get('APSSpeedCMD', current_speed)} kph | "
              f"VehicleSpeed: {motion_status.get('VehicleSpeed', 'N/A')} | "
              f"TqSource: {motor_status.get('TqSource', 'N/A')}")
    except Exception as e:
        print(f"\033[91mError reading data: {e}\033[0m")

def main():
    global current_speed, speed_changed, stop_triggered

    print("Connecting to DoIP server...")
    doip_client = DoIPClient(DOIP_SERVER_IP, DoIP_LOGICAL_ADDRESS, protocol_version=3)
    uds_connection = DoIPClientUDSConnector(doip_client)
    
    assert uds_connection.is_open, "Failed to open UDS connection!"
    
    with Client(uds_connection, request_timeout=4, config=get_uds_client()) as client:
        FoxPi_Write = FoxPiWriteDID(client)
        FoxPi_Read = FoxPiReadDID(client)
        
        # 1. Execute the Reset Sequence First
        print("\n--- Step 1: Executing Reset Sequence ---")
        FoxPi_Write.FoxPi_Reset_Sequence()
        time.sleep(1)
        
        # 2. Put Vehicle in Drive via APS
        print("\n--- Step 2: Putting Vehicle in Drive via APS ---")
        # Base APS values layout:
        # Index 10: APSVMCReqA_flg    (1 = Enable APS)
        # Index 11: APSStaSystem      (2 = System Active)
        # Index 12: APSShiftPosnReq   (5 = Drive)
        # Index 13: APSSpeedCMD       (0 = Initial Speed)
        aps_values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, DRIVE_SHIFT_VALUE, 0]
        
        FoxPi_Write.FoxPi_Driving_Ctrl(aps_values)
        time.sleep(1)
        FoxPi_Write.FoxPi_Reset_Sequence()
        time.sleep(1)
        
        # 3. Setup Controls and Keyboard Listener
        print("\n--- Step 3: Starting APS Speed Control ---")
        print("\033[93m*** CONTROLS ***\033[0m")
        print("\033[93m[UP ARROW]   : Increase speed (Max 7 km/h)\033[0m")
        print("\033[93m[DOWN ARROW] : Decrease speed\033[0m")
        print("\033[93m[ENTER]      : Slowly stop, Park, and Exit\033[0m\n")

        # Start listening for arrow keys
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        
        # Write initial state once
        FoxPi_Write.FoxPi_Driving_Ctrl(aps_values)
        
        # 4. Main Control Loop
        while not stop_triggered:
            # --- WRITE ONLY ON CHANGE ---
            if speed_changed:
                aps_values[13] = current_speed
                FoxPi_Write.FoxPi_Driving_Ctrl(aps_values)
                print(f"\033[92m>>> SPEED UPDATED: {current_speed} km/h <<<\033[0m")
                speed_changed = False
            
            # --- READ CONTINUOUSLY ---
            read_vehicle_data(FoxPi_Read)
            
            # Delay before next read cycle
            time.sleep(0.1) 
            
        # 5. Stop Sequence
        print("\n--- Step 4: Stop Triggered. Decelerating... ---")
        while current_speed > 0:
            current_speed -= 1
            aps_values[13] = current_speed
            FoxPi_Write.FoxPi_Driving_Ctrl(aps_values)
            print(f"\033[93mDecelerating... Target Speed: {current_speed} km/h\033[0m")
            
            # Continue updating reads while decelerating
            for _ in range(5): # Simulates a 0.5s pause between speed drops
                read_vehicle_data(FoxPi_Read)
                time.sleep(0.1)
                
        print("\n--- Step 5: Putting Vehicle in Park ---")
        aps_values[12] = PARK_SHIFT_VALUE 
        FoxPi_Write.FoxPi_Driving_Ctrl(aps_values)
        
        # Brief read loop while the park command engages
        for _ in range(10): 
            read_vehicle_data(FoxPi_Read)
            time.sleep(0.1)
            
        print("\n--- Step 6: Disabling Control ---")
        disable_APS_values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
        FoxPi_Write.FoxPi_Driving_Ctrl(disable_APS_values)
        time.sleep(0.1)
        FoxPi_Write.FoxPi_Ctrl_Enable_Switch([0])
        print("\033[92mControl safely disabled. Exiting program.\033[0m")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\033[91mProgram interrupted manually. Exiting...\033[0m")