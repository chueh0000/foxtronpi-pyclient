# FoxtronPi Python Client (foxtronpi-pyclient)

This is a Python-based diagnostic and control client for FoxtronEV vehicles (specifically the FoxtronPi D31x model). It enables interaction with vehicle ECUs using Diagnostics over IP (DoIP) and Unified Diagnostic Services (UDS).

See [FoxtronPi-Manual](https://chueh0000.github.io/FoxtronPi-Manual/) for detailed instructions on FoxtronPi.

> [!IMPORTANT]
> **Python 3.10 is strictly required** for direct vehicle connection because the precompiled diagnostic configuration and client configuration library files (`*.so`) are built specifically for CPython 3.10 on x86-64 Linux.

## 📁 Project Contents

| File Name | Description |
|----------------|------------------------------|
| `FoxPi_read.py`  | Function Library to Read Vehicle Signal Status (e.g., vehicle speed, lights, battery, motor, etc.) |
| `FoxPi_write.py` | Function Library to Control Vehicle Signals (e.g., acceleration, target speed, lights, gear shifting) |
| `FoxPi_DTC.py`     | Function Library to Read and clear Diagnostic Trouble Codes (DTCs) |
| `FoxPi_TP.py`     | Function Library to send the TesterPresent service request and keep the connection alive |
| `client_config.cpython-310-x86_64-linux-gnu.so`     | Precompiled connection configuration binary |
| `common.cpython-310-x86_64-linux-gnu.so`     | Precompiled diagnostic configuration binary |
| `read.py` | Sample CLI script: Read vehicle signal status |
| `write.py` | Sample CLI script: Write vehicle control parameters |
| `readwrite.py` | Sample CLI script: Combined read and write continuous driving loop (Experimental purpose only) |
| `aps_control.py` | Interactive CLI tool: Controls driving speed using keyboard arrow keys |
| `dashboard/` | Source code for the real-time PyQt6/QML dashboard application (Under Development / WIP) |
| `requirements.txt` | Package dependencies |
| `README.md`     | Project Documentation |

---

## <img src="https://img.icons8.com/color/48/windows-10.png" width="24"/> <img src="https://img.icons8.com/color/48/linux.png" width="24"/> Recommendation — Install WSL before development

When working in a Windows environment, we recommend installing WSL (Windows Subsystem for Linux) first, as it will make subsequent Python development more convenient.

### 1. Install WSL + Ubuntu-22.04
Open the Windows Command Prompt and run:
```bash
wsl --install -d Ubuntu-22.04
```
The system will automatically download and install the required Linux kernel components.

Once it finishes, a prompt will appear asking you to enter a username and password.

> [!NOTE]
> When entering your password, nothing will appear in the terminal as you type — this is normal behavior. Do not worry if it looks like nothing is being entered, and avoid pressing keys repeatedly!

Once the username and password are set, the setup is complete.

### 2. Update Ubuntu
```bash
sudo apt update && sudo apt upgrade -y
```

### 3. Launching WSL
After exiting the installer or restarting your computer, open your command prompt and run:
```bash
wsl
```

## <img src="https://img.icons8.com/color/30/python.png" width="28"/> Create the Python Virtual Environment

A Python Virtual Environment helps isolate dependencies and prevents the global development environment from conflicts when working on multiple projects.

### 1. Install Python3 and Venv (If not already installed)
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip -y
```

##  <img src="https://img.icons8.com/fluency/28/maintenance.png" width="24"/> Installation and Setup of System Dependencies

### 1. Clone the repository
Open WSL and run the following command to clone the repository:
```bash
git clone --branch main https://github.com/chueh0000/foxtronpi-pyclient
```

### 2. Enter the project folder
```bash
cd foxtronpi-pyclient
```

### 3. Set up and Activate the Python Virtual Environment
We support two methods to manage the Python environment:

#### Method A: Using `direnv` (Recommended - Automated)
Using `direnv` automatically activates and manages your Python environment when you enter the project directory.

1. **Install `direnv`**:
   - Linux / WSL (Ubuntu):
     ```bash
     sudo apt update
     sudo apt install direnv -y
     ```
2. **Hook `direnv` to your shell**:
   Follow the [direnv installation instructions](https://direnv.net/docs/hook.html) to add it to your shell configuration (e.g., `~/.bashrc`):
   ```bash
   # Add this line to your shell configuration file
   eval "$(direnv hook bash)"
   ```
3. **Allow `direnv` in the project folder**:
   ```bash
   direnv allow
   ```
   This will automatically detect the `.envrc` configuration and set up a virtual environment.

#### Method B: Manual Virtual Environment (Fallback)
If you prefer not to use `direnv`, you can configure and activate it manually:

1. **Create the virtual environment folder `Pi`**:
   ```bash
   python3 -m venv Pi
   ```
2. **Activate the virtual environment**:
   ```bash
   source Pi/bin/activate
   ```

### 4. Install the package requirements
Once your environment is active (either via `direnv` or manually), run:
```bash
pip install -r requirements.txt
```

## <img src="https://img.icons8.com/fluency/28/console.png" width="22"/> Execution Method

### 1. Launch the Real-Time Dashboard (GUI - Under Development)
The project includes a PySide6/QML dashboard with interactive gauges, control controls, and real-time plotting.
```bash
python3 dashboard/main.py
```
> [!NOTE]
> The dashboard feature is currently **under development (WIP)**. If you are not connected to a physical vehicle, the dashboard will automatically start in **Mock Mode**, generating simulated vehicle telemetry. This allows testing the user interface on any architecture (including ARM-based systems like macOS).

### 2. Read Vehicle Status (CLI)
```bash
python3 read.py
```

### 3. Write Vehicle Control Parameters (CLI)
```bash
python3 write.py
```

### 4. Interactive Keyboard Drive Control (CLI)
Allows driving controls using arrow keys on your keyboard:
```bash
python3 aps_control.py
```

### 5. Combined Read & Write Loop (CLI - Experimental Only)
Runs a continuous read/write control loop with a vehicle reset sequence. Note that `readwrite.py` is for **experimental purposes only**.
```bash
python3 readwrite.py
```

> [!IMPORTANT]
> **Vehicle Connection Standard**:
> All components connecting to the vehicle must strictly follow the connection method established in `aps_control.py`, `read.py`, and `write.py`. This uses the `udsoncan` standard `Client` context manager:
> ```python
> doip_client = DoIPClient(DOIP_SERVER_IP, DoIP_LOGICAL_ADDRESS, protocol_version=3)
> uds_connection = DoIPClientUDSConnector(doip_client)
> with Client(uds_connection, request_timeout=4, config=get_uds_client()) as client:
>     # Perform UDS read/write diagnostics here...
> ```

## <img src="https://img.icons8.com/fluent/24/visual-studio-code-2019.png" width="24"/> Visual Studio Code Development Environment
Open VS Code to develop Python code. Make sure your shell is working in the `foxtronpi-pyclient` directory and the virtual environment is activated before running:
```bash
code .
```