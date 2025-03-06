# File Patrole

File Patrole is a lightweight, command-line interface, File Integrity Monitor (FIM) tool. Built entirely in Python, this solution uses baseline snapshots to track changes in specified directories and detect modifications, additions, or deletions.

## Features
- **Baseline Comparison**: Establishes baselines for monitoring file integrity over time.
- **Flexible Monitoring**: Specify individual paths or provide a file containing a list of directories to monitor.
- **Verbose Output**: Enable detailed logging for insights into the monitoring process.
- **Notifications**: Send SMS or WhatsApp notifications for specific events such as modifications or deletions.

---

## Requirements

- Python 3.8 or higher
- `pip` for dependency installation

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fim.git
   cd fim
   ```
   
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

## Usage

First, create an environment file, .env, at the root of the directory with Twilio credentials and admin phone number
```bash
TWILIO_ACCOUNT_SID="..."
TWILIO_AUTH_TOKEN="..."
TWILIO_VIRTUAL_PHONE="..." # i.e. "+1112223333
TWILIO_WHATSAPP_NUMBER="..." # i.e. "+1112223333
ADMIN_PHONE="..." # i.e. "+1112223333
```

Run the fim command with the appropriate arguments:

## Basic Syntax

```bash
python fim.py [OPTIONS]
```

## Options

| **Argument**     | **Description**                                                                     |
| :--------------- | :---------------------------------------------------------------------------------- |
| PATH             | Specify one or more directories to monitor (separated by spaces).                   |
| -p, --path-file  | Path to a text file containing a list of directories to monitor (one path per line).|
| -v, --verbose    | Enable verbose mode for detailed output.                                            |
<!--| --notify         | Enable notifications for events (SMS or WhatsApp).                                  |-->

## Examples
1. Monitor a single directory: 
  ```bash
  python fim.py /path/to/directory 
  ```

2. Monitor multiple directories: 
```bash 
python fim.py /path/to/dir1 /path/to/dir2 
```
3. Monitor directories listed in a file: 
```bash 
python fim.py -p directories.txt
```
4. Verbose monitoring: 
```bash 
python fim.py -v /path/to/directory
```
5. Enable notifications: 
```bash 
python fim.py --notify -p directories.txt
```
---
## How It Works
1. Baseline Creation: The tool generates a baseline snapshot of files in the monitored paths, storing critical metadata like file size, modification time, and checksum. 
2. Integrity Checking: During subsequent scans, FIM compares the current state of files to the baseline, flagging any discrepancies. 
3. Notifications: When enabled, FIM can send notifications via SMS or WhatsApp for specified events, such as unauthorized file changes. 
4. Verbose Logging: When enabled, the tool provides detailed logs of operations, including files scanned and integrity checks performed.
