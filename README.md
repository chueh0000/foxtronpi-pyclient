# Foxtronpi-pyclient

This is an example python project to control the FoxtronEV's car model FoxtronPi(D31x) under project FoxtronPI with python-doipclient and python-udsoncan.

## 📁 Project Contents

| File Name | Description |
|----------------|------------------------------|
| `FoxPi_read.py`  | Function Library to Read Vehicle Signal Status(e.g. vehicle speed, lights, battary, motor, etc.) |
| `FoxPi_write.py` | Function Library to Control Vehicle Signals（e.g. acceleration, target speed, lights, gear shifting）    |
| `FoxPi_DTC.py`     | Function Library to Read and clear DTCs |
| `FoxPi_TP.py`     | Function Library to send the TesterPresent service request and keep the connection alive. |
| `client_config.cpython-310-x86_64-linux-gnu.so`     | Connection configuration (.so) file |
| `common.cpython-310-x86_64-linux-gnu.so`     | Diagnostic configuration (.so) file |
| `README.md`     | Project Documentation |
| `requirement.txt` | Package Requirements |
| `read.py` | Sample code: Read vehicle signal status |
| `write.py` | Sample code: Write vehicle control parameter |

---

## <img src="https://img.icons8.com/color/48/windows-10.png" width="24"/> <img src="https://img.icons8.com/color/48/linux.png" width="24"/> Recommendation — Insatll WSL before development 
When working in a Windows environment, we recommend installing WSL first, as it will make subsequent Python development more convenient.

### 1. Install WSL+ubuntu-22.04
Open the windows CMD and type in the command
```bash
wsl --install -d Ubuntu-22.04
```
The system will automatically download and install some Linux kernel components.

Next, you’ll see an installation progress bar.

Once it finishes, a prompt will appear asking you to enter a username and password.

Note: When entering your password, nothing will appear in the terminal as you type — this is normal behavior.
So, don’t worry if it looks like nothing is being entered, and avoid pressing keys repeatedly!

`Once the username and password are entered, the setup is complete.`

### 2. Update Ubuntu
```bash
sudo apt update
sudo apt upgrade
```

### 3. How to launch WSL after exiting the installer or restarting your computer
Open the CMD and type in the `wsl` command.
```bash
wsl
```

## <img src="https://img.icons8.com/color/30/python.png" width="28"/> Create the Python Virtual Environment 
### Why do we need to create a Python Virtual Environment? 
A Python Virtual Environment helps isolate dependencies and prevents the global development environment from becoming messy when working on multiple projects.

1. Install Python3 and Venv(If not already installed)
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

##  <img src="https://img.icons8.com/fluency/28/maintenance.png" width="24"/> Installation and setup the system requirements packages
### 1. Clone the repository
First, Open the CMD and type in `wsl`.

Then, enter the following command after WSL starts:
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
     sudo apt install direnv
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

### Read the status of vehicle signals
```bash
python3 read.py
```

### Write the vehicle Control parameter
```bash
python3 write.py
```

## <img src="https://img.icons8.com/fluent/24/visual-studio-code-2019.png" width="24"/> Visual Studio Code development environment 
Open VS code to develop Python code if you want, but make sure you are inside the `foxtronpi-pyclient` folder.
```bash
code .
```