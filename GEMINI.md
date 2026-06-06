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
  - **Library Layer**: Modular Python files (`FoxPi_*.py`) that abstract UDS DIDs and data conversion logic.
  - **GUI Layer**: A modern dashboard (`dashboard/`) with real-time gauges, interactive controls, and dynamic plots.
  - **CLI Layer**: Interactive scripts (`read.py`, `write.py`) for manual testing and demonstration.
  - **Config/Common**: Shared connection settings and UDS client configurations.

## Key Components

| File/Folder | Description |
|------|-------------|
| `dashboard/` | Source code for the real-time PyQt6/QML dashboard application. |
| `FoxPi_read.py` | Library for reading vehicle Data Identifiers (DIDs) like speed, battery, etc. |
| `FoxPi_write.py` | Library for writing vehicle DIDs to control signals like acceleration and lamps. |
| `FoxPi_DTC.py` | Library for reading and clearing Diagnostic Trouble Codes. |
| `FoxPi_TP.py` | Helper for sending TesterPresent requests to keep the diagnostic session alive. |
| `read.py` | Interactive CLI for reading vehicle signals. |
| `write.py` | Interactive CLI for writing vehicle control parameters. |

## Building and Running

### Prerequisites
- **Architecture**: x86-64 (AMD64) for real vehicle connection; ARM support is provided for GUI development via mock data.
- **OS**: Linux (Ubuntu 22.04 recommended) or WSL2.
- **Python**: 3.10.

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
     python3 -m venv Pi
     source Pi/bin/activate
     ```
2. **Install Dependencies**:
     ```bash
     pip install -r requirements.txt
     ```

### Execution
- **Launch Real-time Dashboard**:
  ```bash
  python3 dashboard/main.py
  ```
- **Read Vehicle Data (CLI)**:
  ```bash
  python3 read.py
  ```
- **Write Control Data (CLI)**:
  ```bash
  python3 write.py
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
- **IP/Logical Addressing**: Connection parameters are managed in `client_config.so`. Ensure `DOIP_SERVER_IP` and `DoIP_LOGICAL_ADDRESS` match the vehicle's gateway configuration.

## TODOs
- [ ] Implement automated testing suite for library functions using a DoIP/UDS simulator.
- [ ] Enhance Dashboard with more detailed visualizations.
