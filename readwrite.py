import time
import threading
import sys
from doipclient import DoIPClient
from doipclient.connectors import DoIPClientUDSConnector
from common import get_uds_client
from client_config import DOIP_SERVER_IP, DoIP_LOGICAL_ADDRESS
from udsoncan.client import Client

# Import both your Write and Read classes
from FoxPi_write import FoxPiWriteDID 
from FoxPi_read import FoxPiReadDID 

# Global flag to control the continuous loop
keep_driving = True

def listen_for_enter():
    """Runs in a separate thread to listen for the Enter key without blocking the main loop."""
    global keep_driving
    input("\n\033[93m*** PRESS ENTER AT ANY TIME TO STOP DRIVING CONTROL ***\033[0m\n")
    keep_driving = False

def main():
    # 1. Establish DoIP/UDS Connection
    print("Connecting to DoIP server...")
    doip_client = DoIPClient(DOIP_SERVER_IP, DoIP_LOGICAL_ADDRESS, protocol_version=3)
    uds_connection = DoIPClientUDSConnector(doip_client)
    
    assert uds_connection.is_open, "Failed to open UDS connection!"
    
    with Client(uds_connection, request_timeout=4, config=get_uds_client()) as client:
        
        # Initialize both classes
        FoxPi_Write = FoxPiWriteDID(client)
        FoxPi_Read = FoxPiReadDID(client)
        
        # 2. Execute the Reset Sequence First
        print("\n--- Step 1: Executing Reset Sequence ---")
        FoxPi_Write.FoxPi_Reset_Sequence()
        time.sleep(1)
        
        # 3. Put Vehicle in Drive
        print("\n--- Step 2: Putting Vehicle in Drive then Run Reset Sequence again ---")
        put_in_Drive_values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 5, 0]
        FoxPi_Write.FoxPi_Driving_Ctrl(put_in_Drive_values)
        time.sleep(1)
        FoxPi_Write.FoxPi_Reset_Sequence()
        time.sleep(1)
        
        # 4. Setup the Continuous Driving Loop
        print("\n--- Step 3: Starting Continuous Driving Control ---")
        listener_thread = threading.Thread(target=listen_for_enter, daemon=True)
        listener_thread.start()
        
        # Default driving parameters
        # ["AccReq","AccReq_A",
        # "TargetSpd","TargetSpd_A",
        # "Angle_V","Angle_Req","Angle",
        # "Torque_V","Torque_Req","Torque",
        # "APSVMCReqA_flg","APSStaSystem","APSShiftPosnReq","APSSpeedCMD"]
        default_driving_values = [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        while keep_driving:
            # --- WRITE ---
            FoxPi_Write.FoxPi_Driving_Ctrl(default_driving_values)
            
            # Add a tiny delay to give the ECU time to process the write before we read
            time.sleep(0.1) 
            
            # --- READ ---
            try:
                # Fetch the dictionary of parsed physical values
                current_status = FoxPi_Read.FoxPi_Driving_Ctrl()
                time.sleep(0.1)
                current_status = FoxPi_Read.FoxPi_WheelSpeed()
                
                # Print a clean, formatted summary of the key driving parameters
                print(f"\033[96m[Vehicle Status]\033[0m TargetSpd: {current_status['Spd']} kph | "
                      f"TargetSpd_A: {current_status['Spd_A']} | "
                      f"RR_WhlSpeed: {current_status['RR_WhlSpeed']} | "
                      f"RR_WhlSpeed_V: {current_status['RR_WhlSpeed_V']}")
            except Exception as e:
                print(f"\033[91mError reading data: {e}\033[0m")
            
            # Delay before the next cycle
            time.sleep(0.1) 
            
        # 5. Turn off control enable switch after the loop breaks
        print("\n--- Step 4: Stop Triggered. Disabling Control ---")
        FoxPi_Write.FoxPi_Ctrl_Enable_Switch([0])
        print("\033[92mControl safely disabled. Exiting program.\033[0m")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\033[91mProgram interrupted manually. Exiting...\033[0m")