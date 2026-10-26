# Day 15: Python Installation and Environment Setup Log

## 1. Objective

To configure Python, create a project-specific virtual environment, install the required Python packages, and prepare the software environment for the Karnaphuli Underwater Road Tunnel Real-Time Maintenance Monitoring (SHM) project.

## 2. Environment Information

- **Project Name:** Karnaphuli Underwater Road Tunnel Real-Time Maintenance Monitoring
- **Project Directory:** `D:\karnaphuli-shm-month2`
- **Operating System:** Windows
- **Python Version:** 3.13.5
- **Virtual Environment:** `venv`
- **Package Manager:** pip

## 3. Tasks Completed

- [x] Verified the installed Python version.
- [x] Created a virtual environment using `python -m venv venv`.
- [x] Activated the virtual environment using `venv\Scripts\activate.bat`.
- [x] Installed the required Python packages.
- [x] Verified package imports successfully.
- [x] Generated `requirements.txt` using `python -m pip freeze > requirements.txt`.
- [x] Saved this setup log.

## 4. Installed Python Packages

The following packages were installed in the project's virtual environment:

| Package | Installed Version | Purpose |
|---|---|---|
| paho-mqtt | 2.1.0 | MQTT communication |
| influxdb-client | 1.50.0 | InfluxDB integration |
| pandas | 3.1.0 | Sensor data processing and analysis |
| numpy | 2.5.4 | Numerical computation |

Additional dependencies were recorded automatically in `requirements.txt`.

## 5. Verification Results

### Python Version

Command:

```bash
python --version
```

Output:

```text
Python 3.13.5
```

### Virtual Environment

Command:

```bat
venv\Scripts\activate.bat
```

Result: The virtual environment was activated successfully. The terminal prompt displayed `(venv)`.

### Package Import Test

Command:

```bash
python -c "import paho.mqtt.client, influxdb_client, pandas, numpy; print('All packages imported successfully')"
```

Output:

```text
All packages imported successfully
```

**Result:** All four required packages imported successfully.

### Requirements File

Command:

```bash
python -m pip freeze > requirements.txt
```

Result: The `requirements.txt` file was generated successfully with the installed package versions and dependencies.

## 6. Application in the SHM Project

The Python environment will support future development and integration tasks, including:

- Processing ESP32 sensor data.
- Reading and analyzing CSV and JSONL datasets.
- Communicating with MQTT brokers.
- Integrating sensor data with InfluxDB.
- Performing numerical calculations and preliminary sensor-data analysis.

These are planned uses of the environment; successful installation does not by itself confirm that MQTT or InfluxDB connectivity has been configured or tested.

## 7. Output Files

The expected output files are:

```text
karnaphuli-shm-month2/
├── venv/
├── requirements.txt
└── documentation/
    └── python_setup_log.md
```

The existing `firmware/`, `hardware/`, and `data/` directories remain part of the project.

## 8. Issues and Observations

- Python 3.13.5 was already installed on the system.
- The virtual environment was created successfully.
- The PowerShell activation command was initially attempted in Command Prompt. The correct CMD command, `venv\Scripts\activate.bat`, was used instead.
- All required package imports passed the verification test.
- No package import errors were reported during verification.

## 9. Conclusion

Day 15 was completed successfully. Python 3.13.5 was verified, the project-specific virtual environment was created and activated, the required packages were installed and tested, and `requirements.txt` was generated.

The Python environment is ready for subsequent SHM software development tasks. MQTT broker connectivity, InfluxDB connectivity, and actual sensor-data ingestion will require separate configuration and testing.

**Status: Completed**
