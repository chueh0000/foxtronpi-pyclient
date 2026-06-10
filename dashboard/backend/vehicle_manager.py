import sys
import threading
import time
import math
from PySide6.QtCore import QObject, Property, Signal, Slot, QTimer, QThread

from collections import deque

class VehicleManager(QObject):
    # Signals for UI updates
    dataUpdated = Signal()
    connectionStatusChanged = Signal(bool)
    connectionError = Signal(str)

    def __init__(self):
        super().__init__()
        self._connected = False
        self._data = {}
        self.client = None
        self.reader = None
        self.writer = None
        self.tp = None
        
        # Buffers for plotting (last 100 points)
        self.speed_buffer = deque([0.0]*100, maxlen=100)
        self.sas_buffer = deque([0.0]*100, maxlen=100)
        
        # Initialize with empty/default values for all DIDs
        self._init_data_store()

        # Timer for polling
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.poll_vehicle_data)

        # Mock data timer for UI testing when disconnected
        self.mock_timer = QTimer()
        self.mock_timer.timeout.connect(self._generate_mock_data)
        self.mock_timer.start(100)
        self._mock_time = 0.0

    @Slot()
    def connectVehicle(self):
        if not self._connected:
            threading.Thread(target=self._async_connect, daemon=True).start()

    @Slot()
    def disconnectVehicle(self):
        self._connected = False
        self.poll_timer.stop()
        self.mock_timer.start(100)
        self.connectionStatusChanged.emit(False)

    def _init_data_store(self):
        # All readable values from FoxPi_read.py
        self._data = {
            # Motion
            "speed": 0.0, "long_acc": 0.0, "lat_acc": 0.0, "yaw_rate": 0.0,
            # Battery
            "lv_batt_12v": 0.0, "hv_batt_soc": 0.0, "hv_batt_temp": 0.0,
            "hv_batt_contactor": 0, "hv_batt_err": 0,
            # Pedal
            "accel_pedal": 0.0, "brake_pedal": 0.0,
            # Motor
            "tm_torque_req": 0, "real_tm_torque": 0, "tm_speed": 0,
            # Lamps
            "pos_lamp": 0, "low_beam": 0, "high_beam": 0, "left_turn": 0, "right_turn": 0,
            # Steering
            "sas_angle": 0.0,
            # More as needed...
        }

    def _async_connect(self):
        try:
            # Dynamic imports to prevent crash on ARM where common/client_config may be missing
            from foxtronpi_client import FoxPiReadDID, FoxPiWriteDID, FoxPiTP
            from foxtronpi_client.common import get_uds_client
            from foxtronpi_client.client_config import DOIP_SERVER_IP, DoIP_LOGICAL_ADDRESS

            self.client = get_uds_client(DOIP_SERVER_IP, DoIP_LOGICAL_ADDRESS)
            self.reader = FoxPiReadDID(self.client)
            self.writer = FoxPiWriteDID(self.client)
            self.tp = FoxPiTP(self.client)
            
            # Start TesterPresent
            self.tp.start_tp()
            
            self._connected = True
            self.connectionStatusChanged.emit(True)
            self.mock_timer.stop() # Stop mock data when connected
            self.poll_timer.start(100) # Poll every 100ms
        except ImportError as e:
            err_msg = f"Import Error (Missing x86_64 modules?): {e}"
            print(err_msg)
            self.connectionError.emit(err_msg)
            self._connected = False
            self.connectionStatusChanged.emit(False)
        except Exception as e:
            err_msg = f"Connection failed: {e}"
            print(err_msg)
            self.connectionError.emit(err_msg)
            self._connected = False
            self.connectionStatusChanged.emit(False)

    def _generate_mock_data(self):
        # Generate some sine wave data to make the UI look alive during development
        self._mock_time += 0.1
        self._data["speed"] = 50 + 20 * math.sin(self._mock_time)
        self._data["sas_angle"] = 30 * math.sin(self._mock_time * 0.5)
        self._data["hv_batt_soc"] = 85.0
        self._data["hv_batt_temp"] = 35.0
        self._data["accel_pedal"] = abs(50 * math.sin(self._mock_time))
        
        self.speed_buffer.append(self._data["speed"])
        self.sas_buffer.append(self._data["sas_angle"])
        self.dataUpdated.emit()

    @Slot()
    def poll_vehicle_data(self):
        if not self._connected or not self.reader:
            return

        try:
            # For efficiency, we should probably only read what's currently being viewed.
            # But the requirement is "all data displayed", so let's read the main ones.
            motion = self.reader.FoxPi_Motion_Status()
            battery = self.reader.FoxPi_Battery_Status()
            pedal = self.reader.FoxPi_Pedal_position()
            motor = self.reader.FoxPi_Motor_Status()
            lamps = self.reader.FoxPi_Lamp_Status()
            eps = self.reader.FoxPi_EPS_Status()
            brake = self.reader.FoxPi_Brake_Status()
            wheel = self.reader.FoxPi_WheelSpeed()
            buttons = self.reader.FoxPi_Button_Status()
            switches = self.reader.FoxPi_Switch_Status()

            # Update local store
            # ... existing ...
            self._data["mc_pressure"] = float(brake.get("MCPressure", 0.0))
            self._data["abs_act"] = brake.get("ABS_Act", 0)
            
            self._data["whl_speed_rr"] = float(wheel.get("RR_WhlSpeed", 0.0))
            self._data["whl_speed_lr"] = float(wheel.get("LR_WhlSpeed", 0.0))
            self._data["whl_speed_rf"] = float(wheel.get("RF_WhlSpeed", 0.0))
            self._data["whl_speed_lf"] = float(wheel.get("LF_WhlSpeed", 0.0))

            self._data["door_driver"] = switches.get("Driver_Door_Switch_Status", 0)
            self._data["door_passenger"] = switches.get("Passenger_Door_Switch_Status", 0)
            self._data["hood"] = switches.get("Hood_Switch_Status", 0)
            self._data["tailgate"] = switches.get("Tailgate_Switch_Status", 0)
            self._data["speed"] = motion.get("VehicleSpeed", 0.0)
            self._data["long_acc"] = motion.get("LongAcc", 0.0)
            self._data["lat_acc"] = motion.get("LatAcc", 0.0)
            self._data["yaw_rate"] = motion.get("YawRate", 0.0)
            
            self._data["lv_batt_12v"] = battery.get("LVBatt12V", 0.0)
            self._data["hv_batt_soc"] = battery.get("HVBattSOC", 0.0)
            self._data["hv_batt_temp"] = battery.get("HVBattTemp", 0.0)
            self._data["hv_batt_contactor"] = battery.get("HVBattContactorSta", 0)
            self._data["hv_batt_err"] = battery.get("HVBattErr", 0)

            self._data["accel_pedal"] = float(pedal.get("AccelPedalPos", 0.0))
            self._data["brake_pedal"] = float(pedal.get("BrakePedalPos", 0.0))

            self._data["tm_torque_req"] = motor.get("TMTqReq ", 0)
            self._data["real_tm_torque"] = motor.get("RealTMTq", 0)
            self._data["tm_speed"] = motor.get("TMSpd", 0)

            self._data["pos_lamp"] = lamps.get("Position_Lamp_Status", 0)
            self._data["low_beam"] = lamps.get("Low_Beam_Status", 0)
            self._data["high_beam"] = lamps.get("High_Beam_Status", 0)
            self._data["left_turn"] = lamps.get("Left_Turn_Lamp_Status", 0)
            self._data["right_turn"] = lamps.get("Right_Turn_Lamp_Status", 0)
            
            self._data["sas_angle"] = float(eps.get("SAS_Angle", 0.0))

            # Update buffers
            self.speed_buffer.append(self._data["speed"])
            self.sas_buffer.append(self._data["sas_angle"])

            self.dataUpdated.emit()
        except Exception as e:
            print(f"Polling error: {e}")

    # Properties exposed to QML
    @Property(float, notify=dataUpdated)
    def speed(self): return self._data.get("speed", 0.0)

    @Property(float, notify=dataUpdated)
    def hvBattSOC(self): return self._data.get("hv_batt_soc", 0.0)

    @Property(float, notify=dataUpdated)
    def hvBattTemp(self): return self._data.get("hv_batt_temp", 0.0)
    
    @Property(float, notify=dataUpdated)
    def accelPedal(self): return self._data.get("accel_pedal", 0.0)

    @Property(float, notify=dataUpdated)
    def brakePedal(self): return self._data.get("brake_pedal", 0.0)

    @Property(float, notify=dataUpdated)
    def sasAngle(self): return self._data.get("sas_angle", 0.0)

    @Property(list, notify=dataUpdated)
    def speedBuffer(self): return list(self.speed_buffer)

    @Property(list, notify=dataUpdated)
    def sasBuffer(self): return list(self.sas_buffer)

    @Property(bool, notify=connectionStatusChanged)
    def connected(self): return self._connected

    # Control Methods
    @Slot(list)
    def setLamps(self, values):
        if self._connected and self.writer:
            self.writer.FoxPi_Lamp_Ctrl(values)

    @Slot(list)
    def setDrivingCtrl(self, values):
        if self._connected and self.writer:
            self.writer.FoxPi_Driving_Ctrl(values)
    
    @Slot(list)
    def setCtrlEnableSwitch(self, values):
        if self._connected and self.writer:
            self.writer.FoxPi_Ctrl_Enable_Switch(values)

    @Slot()
    def resetSequence(self):
        if self._connected and self.writer:
            self.writer.FoxPi_Reset_Sequence()
