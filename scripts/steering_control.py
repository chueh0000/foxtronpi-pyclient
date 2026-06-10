import time
import os
import sys
import threading
import tty
import termios

# Add the parent directory to the Python path to access package modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from doipclient import DoIPClient
from doipclient.connectors import DoIPClientUDSConnector
from udsoncan.client import Client
from foxtronpi_client.common import get_uds_client
from foxtronpi_client.client_config import DOIP_SERVER_IP, DoIP_LOGICAL_ADDRESS
from foxtronpi_client import FoxPiWriteDID, FoxPiReadDID

# Globals for steering control state
target_angle = 0.0
stop_triggered = False
angle_changed = False

def get_key():
    """Reads a single keypress from standard input (Unix/Linux/Mac)."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        # If the first character is an escape sequence (\x1b)
        if ch == '\x1b': 
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            if ch2 == '[':
                if ch3 == 'A':
                    return 'UP'
                elif ch3 == 'B':
                    return 'DOWN'
                elif ch3 == 'C':
                    return 'RIGHT'
                elif ch3 == 'D':
                    return 'LEFT'
        # Enter key might be \r or \n depending on terminal
        elif ch == '\r' or ch == '\n':
            return 'ENTER'
        # Ctrl+C
        elif ch == '\x03':
            return 'CTRL_C'
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def keyboard_listener():
    """Runs in a background thread to listen for LEFT/RIGHT arrow keys."""
    global target_angle, stop_triggered, angle_changed
    
    while not stop_triggered:
        key = get_key()
        
        if key == 'LEFT':
            # Turn Left (negative)
            target_angle = max(-360.0, target_angle - 45.0)
            angle_changed = True
        elif key == 'RIGHT':
            # Turn Right (positive)
            target_angle = min(360.0, target_angle + 45.0)
            angle_changed = True
        elif key == 'ENTER' or key == 'CTRL_C':
            stop_triggered = True
            break

def main():
    global target_angle, stop_triggered, angle_changed

    print(f"Connecting to DoIP server at {DOIP_SERVER_IP}...")
    try:
        doip_client = DoIPClient(DOIP_SERVER_IP, DoIP_LOGICAL_ADDRESS, protocol_version=3)
        uds_connection = DoIPClientUDSConnector(doip_client)
    except Exception as e:
        print(f"\033[91mFailed to establish DoIP/UDS connection: {e}\033[0m")
        return
    
    assert uds_connection.is_open, "Failed to open UDS connection!"
    
    with Client(uds_connection, request_timeout=4, config=get_uds_client()) as client:
        FoxPi_Write = FoxPiWriteDID(client)
        FoxPi_Read = FoxPiReadDID(client)
        
        print("\n--- Step 1: Executing Reset Sequence ---")
        FoxPi_Write.FoxPi_Reset_Sequence()
        time.sleep(1)
        
        print("\n--- Step 2: Starting Keyboard Steering Angle Control ---")
        print("\033[93m*** CONTROLS ***\033[0m")
        print("\033[93m[LEFT ARROW]  : Turn steering wheel LEFT by 45° (Max -360°)\033[0m")
        print("\033[93m[RIGHT ARROW] : Turn steering wheel RIGHT by 45° (Max +360°)\033[0m")
        print("\033[93m[ENTER]       : Center wheel, disable control, and Exit\033[0m\n")

        # Start the raw terminal keyboard listener in a separate thread
        listener_thread = threading.Thread(target=keyboard_listener, daemon=True)
        listener_thread.start()
        
        # State Machine definitions
        # 0: DISENGAGED_RESET, 1: INIT_STEP_1, 2: INIT_STEP_2, 3: CONTROL_ACTIVE
        state_names = {
            0: "DISENGAGED_RESET",
            1: "INIT_STEP_1",
            2: "INIT_STEP_2",
            3: "CONTROL_ACTIVE"
        }
        
        control_state = 1  # Start with INIT_STEP_1
        state_timer = time.time()
        
        # Steering safety constraints
        max_angle_diff = 80.0  # Max diff between commanded and real angle (ECU limit: 100)
        max_rate_deg_per_sec = 300.0  # Max angular velocity of command (ECU limit: 500)
        
        commanded_angle = 0.0
        disengage_count = 0
        
        last_time = time.time()
        
        # Main loop at ~20Hz
        while not stop_triggered:
            loop_start = time.time()
            dt = loop_start - last_time
            last_time = loop_start
            if dt <= 0:
                dt = 0.001
                
            # Read vehicle EPS status (DID 0x1005)
            try:
                eps = FoxPi_Read.FoxPi_EPS_Status()
                current_real_angle = float(eps.get("SAS_Angle", 0.0))
                eps_aoi = eps.get("EPS_AOI_Ctrl", 0)
                eps_flt = eps.get("EPS_Flt", 0)
                sas_v = eps.get("SAS_V", 0)
                sas_cal = eps.get("SAS_CAL", 0)
            except Exception as e:
                # Output read error but keep loop running
                sys.stdout.write(f"\r\033[91m[Read Error] {e}\033[0m" + " " * 20)
                sys.stdout.flush()
                time.sleep(0.05)
                continue
                
            # Log keypress updates
            if angle_changed:
                print(f"\n\033[92m>>> Target Steering Angle Updated: {target_angle}° <<<\033[0m")
                angle_changed = False
                
            # State transitions and outputs
            angle_v = 0
            angle_req = 0
            cmd_angle = 0.0
            
            if control_state == 0:  # DISENGAGED_RESET
                angle_v = 0
                angle_req = 0
                cmd_angle = 0.0
                if time.time() - state_timer >= 0.2:
                    control_state = 1
                    state_timer = time.time()
                    print("\n\033[93m>>> State Transition: INIT_STEP_1 (Angle_V=1, Angle_Req=0, Angle=0) <<<\033[0m")
                    
            elif control_state == 1:  # INIT_STEP_1
                angle_v = 1
                angle_req = 0
                cmd_angle = 0.0
                if time.time() - state_timer >= 0.2:
                    control_state = 2
                    state_timer = time.time()
                    print("\n\033[93m>>> State Transition: INIT_STEP_2 (Angle_V=1, Angle_Req=1, Angle=0) <<<\033[0m")
                    
            elif control_state == 2:  # INIT_STEP_2
                angle_v = 1
                angle_req = 1
                cmd_angle = 0.0
                if time.time() - state_timer >= 0.2:
                    control_state = 3
                    state_timer = time.time()
                    disengage_count = 0
                    commanded_angle = current_real_angle  # Start ramping from the current real angle to prevent jumps
                    print("\n\033[92m>>> State Transition: CONTROL_ACTIVE (Angle Control engaged) <<<\033[0m")
                    
            elif control_state == 3:  # CONTROL_ACTIVE
                angle_v = 1
                angle_req = 1
                
                # Ramping and Clamping Safety Logic
                max_change = max_rate_deg_per_sec * dt
                raw_change = target_angle - commanded_angle
                clamped_change = max(-max_change, min(max_change, raw_change))
                temp_commanded = commanded_angle + clamped_change
                
                # Clamp commanded angle relative to actual real angle to satisfy < 100° difference limit
                commanded_angle = max(current_real_angle - max_angle_diff, min(current_real_angle + max_angle_diff, temp_commanded))
                
                # Absolute boundary clamping
                commanded_angle = max(-360.0, min(360.0, commanded_angle))
                cmd_angle = commanded_angle
                
                # Monitor for driver intervention or other disengagement events
                # (EPS_AOI_Ctrl values: 0=Inhibit, 1=Available, 2=Controlled, 3=Permanent Fail)
                if eps_aoi != 2:
                    disengage_count += 1
                    if disengage_count >= 5:  # ~250ms of disengaged state
                        print(f"\n\033[91m>>> EPS disengaged/driver override detected! (EPS_AOI_Ctrl={eps_aoi}). Resetting control state... <<<\033[0m")
                        control_state = 0
                        state_timer = time.time()
                else:
                    disengage_count = 0
            
            # Write Driving Ctrl DID 0x1001
            # Note: Speed, Torque and APS values are all zeroed as requested.
            try:
                aps_values = [0, 0, 0, 0, angle_v, angle_req, cmd_angle, 0, 0, 0, 0, 0, 0, 0]
                FoxPi_Write.FoxPi_Driving_Ctrl(aps_values)
            except Exception as e:
                sys.stdout.write(f"\r\033[91m[Write Error] {e}\033[0m" + " " * 20)
                sys.stdout.flush()
                
            # Decode control state name and EPS AOI name
            aoi_names = {0: "Inhibit", 1: "Available", 2: "Controlled", 3: "PermFail"}
            eps_aoi_name = aoi_names.get(eps_aoi, f"Unknown({eps_aoi})")
            
            # Print continuous status block
            sys.stdout.write(
                f"\r\033[96m[EPS Status]\033[0m State: {state_names[control_state]} | "
                f"Target: {target_angle:.1f}° | Cmd: {cmd_angle:.1f}° | Real: {current_real_angle:.1f}° | "
                f"AOI: {eps_aoi_name} | Flt: {eps_flt} | SAS_V: {sas_v} | SAS_Cal: {sas_cal}    "
            )
            sys.stdout.flush()
            
            # Control rate limit (~20Hz)
            elapsed = time.time() - loop_start
            sleep_time = max(0.001, 0.05 - elapsed)
            time.sleep(sleep_time)
            
        print("\n\n--- Step 3: Stop Triggered. Centering Steering Wheel... ---")
        target_angle = 0.0
        cleanup_start = time.time()
        last_time = time.time()
        
        # Centering loop (runs for max 3 seconds or until steering is centered < 2.0 degrees)
        while time.time() - cleanup_start < 3.0:
            loop_start = time.time()
            dt = loop_start - last_time
            last_time = loop_start
            if dt <= 0:
                dt = 0.001
                
            try:
                eps = FoxPi_Read.FoxPi_EPS_Status()
                current_real_angle = float(eps.get("SAS_Angle", 0.0))
                eps_aoi = eps.get("EPS_AOI_Ctrl", 0)
            except Exception:
                current_real_angle = 999.0
                eps_aoi = 0
                
            if abs(current_real_angle) < 2.0:
                print("\033[92mSteering wheel centered successfully.\033[0m")
                break
                
            # Safety Ramping logic to center
            max_change = max_rate_deg_per_sec * dt
            raw_change = 0.0 - commanded_angle
            clamped_change = max(-max_change, min(max_change, raw_change))
            commanded_angle = commanded_angle + clamped_change
            commanded_angle = max(current_real_angle - max_angle_diff, min(current_real_angle + max_angle_diff, commanded_angle))
            commanded_angle = max(-360.0, min(360.0, commanded_angle))
            
            # Write to center
            try:
                # Keep control active while centering
                aps_values = [0, 0, 0, 0, 1, 1, commanded_angle, 0, 0, 0, 0, 0, 0, 0]
                FoxPi_Write.FoxPi_Driving_Ctrl(aps_values)
            except Exception:
                pass
                
            sys.stdout.write(f"\rCentering... Cmd: {commanded_angle:.1f}° | Real: {current_real_angle:.1f}°   ")
            sys.stdout.flush()
            
            elapsed = time.time() - loop_start
            time.sleep(max(0.001, 0.05 - elapsed))
            
        print("\n\n--- Step 4: Disabling Steering Angle Control ---")
        # Write Angle_V=0, Angle_Req=0, Angle=0 to release EPS
        try:
            disable_values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            FoxPi_Write.FoxPi_Driving_Ctrl(disable_values)
            time.sleep(0.5)
            # Disable control enable switch
            FoxPi_Write.FoxPi_Ctrl_Enable_Switch([0])
            print("\033[92mControl safely disabled. Exiting program.\033[0m")
        except Exception as e:
            print(f"\033[91mError during disable sequence: {e}\033[0m")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\033[91mProgram interrupted manually. Exiting...\033[0m")
