# FoxtronPi Python Client (foxtronpi-pyclient)

A Python-based diagnostic and control client for FoxtronEV vehicles (specifically the FoxtronPi D31x model). It enables interaction with vehicle ECUs using Diagnostics over IP (DoIP) and Unified Diagnostic Services (UDS).

## Project Overview

- **Purpose**: To provide a library, CLI tools, and a real-time GUI for reading vehicle status, controlling vehicle signals, and managing Diagnostic Trouble Codes (DTCs).
- **Core Technologies**:
  - **Python 3**: Main development language.
  - **PySide6 (Qt for Python)**: For the real-time GUI dashboard and control center.
  - **QML**: For modern, responsive UI design.
  - **PyQtGraph**: For real-time plotting of vehicle metrics.
  - **python-doipclient**: For DoIP protocol implementation.
  - **python-udsoncan**: For UDS service implementation.
- **Architecture**:
  - **Library Layer**: Python package `foxtronpi_client/` containing modules for read/write DIDs, DTCs, TesterPresent, and precompiled configurations.
  - **GUI Layer**: A modern PySide6/QML dashboard (`dashboard/`) importing from the core package.
  - **CLI Layer**: Interactive test scripts (`scripts/read.py`, `scripts/write.py`, etc.) for driving control simulations.

## Key Components

| File/Folder | Description |
|------|-------------|
| `foxtronpi_client/` | Core package containing UDS/DoIP wrappers (`FoxPi_read.py`, `FoxPi_write.py`, `FoxPi_DTC.py`, `FoxPi_TP.py`) and precompiled extension binaries (`client_config...so`, `common...so`). |
| `dashboard/` | Source code for the real-time PyQt6/QML dashboard application (Under Development / WIP). |
| `scripts/` | Interactive CLI scripts for manual testing and demonstration. |
| `scripts/read.py` | Interactive CLI for reading vehicle signals. |
| `scripts/write.py` | Interactive CLI for writing vehicle control parameters. |
| `scripts/aps_control.py` | Interactive keyboard-driving control console. |
| `scripts/readwrite.py` | Combined continuous driving control simulation (Experimental). |

## Building and Running

### Prerequisites
- **Architecture**: x86-64 (AMD64) for real vehicle connection; ARM support is provided for GUI development via mock data.
- **OS**: Linux (Ubuntu 22.04 recommended) or WSL2.
- **Python**: 3.10 (strictly required due to precompiled `.so` binary dependencies).

### System GUI Dependencies (Linux / WSL2)
Since PySide6/Qt relies on system graphics and windowing packages, run the following command if you encounter GUI startup/rendering issues:
```bash
sudo apt update
sudo apt install libegl1 libgl1-mesa-glx libxkbcommon-x11-0 libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-xfixes0 -y
```

### Setup
1. **Activate Virtual Environment**:
   - **Using `direnv` (Recommended)**:
     If you have `direnv` installed and hooked to your shell, simply run:
     ```bash
     direnv allow
     ```
     This automatically creates and activates a Python 3.10 virtual environment in the `.direnv/` folder when you enter the directory.
   - **Manually**:
     ```bash
     # For Ubuntu 22.04:
     python3 -m venv Pi
     # For other versions (explicit Python 3.10):
     python3.10 -m venv Pi

     source Pi/bin/activate
     ```
2. **Install Dependencies**:
     ```bash
     pip install -r requirements.txt
     ```

### Execution
- **Launch Real-time Dashboard (Under Development)**:
  ```bash
  python3 dashboard/main.py
  ```
- **Read Vehicle Data (CLI)**:
  ```bash
  python3 scripts/read.py
  ```
- **Write Control Data (CLI)**:
  ```bash
  python3 scripts/write.py
  ```
- **Run Keyboard driving controls (CLI)**:
  ```bash
  python3 scripts/aps_control.py
  ```

## Real-time Dashboard Features
- **Interactive Gauges**: Real-time Speed, Battery SOC/Temp, and Steering Angle indicators.
- **Control Center**: Interactive UI for modifying Driving Controls (DID 0x1001) and Lamp Controls (DID 0x100C).
- **Dynamic Plots**: Real-time line graphs for Speed and Steering Angle history.
- **Mock Mode**: Automatically generates simulated data when not connected to a vehicle, allowing for UI development and testing on any platform.
- **Lazy Loading**: x86-64 specific binary dependencies are only loaded during an active connection attempt, preventing crashes on ARM devices.

## Development Conventions

- **Diagnostic Sessions**: Writing to vehicle DIDs typically requires switching to the `extendedDiagnosticSession` and performing a security unlock (`unlock_security_access(1)`).
- **TesterPresent**: Use `FoxPiTP` to maintain the session if performing multiple operations that require an active diagnostic session.
- **IP/Logical Addressing**: Connection parameters are managed in `foxtronpi_client/client_config.cpython-310-x86_64-linux-gnu.so`. Ensure `DOIP_SERVER_IP` and `DoIP_LOGICAL_ADDRESS` match the vehicle's gateway configuration.
- **Vehicle Connection Standard**:
  Any connection wrapper or client connection sequence must strictly follow the standard initialization established in `scripts/aps_control.py`, `scripts/read.py`, and `scripts/write.py` using `udsoncan` standard `Client` context managers:
  ```python
  from foxtronpi_client.common import get_uds_client
  from foxtronpi_client.client_config import DOIP_SERVER_IP, DoIP_LOGICAL_ADDRESS

  doip_client = DoIPClient(DOIP_SERVER_IP, DoIP_LOGICAL_ADDRESS, protocol_version=3)
  uds_connection = DoIPClientUDSConnector(doip_client)
  with Client(uds_connection, request_timeout=4, config=get_uds_client()) as client:
      # Perform diagnostic functions
  ```
- **Dashboard Status**: Note that the real-time QML Dashboard feature is currently a work-in-progress (under development) and is not yet production-ready.
- **Experimental Code**: The `readwrite.py` script is strictly for temporary experimental usage only. Do not rely on it for official driving or configuration routines.

## TODOs
- [ ] Implement automated testing suite for library functions using a DoIP/UDS simulator.
- [ ] Enhance Dashboard with more detailed visualizations.
- [ ] Support custom target IP configuration directly via Dashboard UI.

