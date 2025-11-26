![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey.svg)
![Jamf Pro](https://img.shields.io/badge/Jamf%20Pro-REST%20API-green.svg)
![Language](https://img.shields.io/badge/Language-Python%203-orange.svg)

# Jamf Pro Wake-Up Call Script

**A Python utility to remotely wake up and redeploy the Jamf Management Framework on macOS computers in your Jamf Pro environment.**

## Overview

This script provides an easy-to-use interface to send wake-up commands (MDM redeploy commands) to macOS computers managed by Jamf Pro. It supports three operational modes:

1. **Group Mode** - Wake up all computers in a dynamic group
2. **Single Mode** - Wake up a specific computer by serial number
3. **File Mode** - Wake up multiple computers from a serial number list

## Why Use This Script?

When Jamf Pro devices enter sleep state or go offline, management commands may queue indefinitely. This script:
- Sends immediate redeploy commands to wake up the Jamf Management Framework
- Processes multiple computers efficiently
- Supports automation with batch files
- Includes safety features (dry-run, confirmation prompts)
- Provides detailed logging for troubleshooting

## Features

✅ **Multiple Target Modes**
- Wake up entire dynamic groups
- Target individual computers by serial number
- Batch operations using a serial number file

✅ **Safety Features**
- Interactive confirmation prompts
- Dry-run mode to preview actions
- Detailed logging of all operations
- Error handling with informative messages

✅ **Flexible Authentication**
- Token-based authentication (recommended)
- Username/password authentication
- Automatic token refresh

✅ **User-Friendly**
- Clear console output with formatted results
- Support for comments in batch files
- Skip confirmation for automation
- Detailed operation reports

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/CaputoDavide93/Jamf_WakeUp_Call.git
cd Jamf_WakeUp_Call
```

### 2. Install Dependencies

```bash
pip install requests python-dotenv
```

### 3. Configure Credentials

Create a `.env` file in the project directory:

```bash
cp .env.example .env
```

Edit `.env` with your Jamf Pro credentials:

```env
JAMF_PRO_URL=https://your-jamf-instance.jamfcloud.com
JAMF_PRO_USERNAME=your_username
JAMF_PRO_PASSWORD=your_password
JAMF_DYNAMIC_GROUP_ID=144

# Optional
LOG_LEVEL=INFO
LOG_FILE=jamf_wakeup.log
API_TIMEOUT=30
```

> **⚠️ Important:** Never commit `.env` files with real credentials. The `.gitignore` is already configured to prevent this.

## Usage

### Mode 1: Wake Up Entire Dynamic Group

Wake up all computers in your configured dynamic group (with confirmation):

```bash
python3 main.py
```

Preview without sending commands:

```bash
python3 main.py --dry-run
```

Skip confirmation (for automation):

```bash
python3 main.py --skip-confirmation
```

Target a different group:

```bash
python3 main.py --group-id 42
```

### Mode 2: Wake Up Single Computer

Wake up a specific computer by serial number:

```bash
python3 main.py H644YVR9VT
```

Dry-run preview:

```bash
python3 main.py H644YVR9VT --dry-run
```

### Mode 3: Wake Up Multiple Computers from File

Create a file with serial numbers (one per line):

```bash
cat > computers.txt << EOF
# Production Servers
H644YVR9VT
C02C94GVLVDL

# Development Machines
C02C71SGLVDL
MYGK7MXR4V
EOF
```

Wake up all computers in the file:

```bash
python3 main.py --file computers.txt
```

Preview first:

```bash
python3 main.py --file computers.txt --dry-run
```

## File Format (for --file mode)

- One serial number per line
- Lines starting with `#` are treated as comments
- Empty lines are ignored

```
# Team A Computers
H644YVR9VT
C02C94GVLVDL

# Team B Computers
C02C71SGLVDL
MYGK7MXR4V
```

## Command-Line Options

```
usage: main.py [-h] [--file FILE] [--group-id GROUP_ID] [--dry-run] 
               [--skip-confirmation] [serial]

Send wake-up calls to computers in Jamf Pro

positional arguments:
  serial                Computer serial number (e.g., C02C94GVLVDL)

optional arguments:
  -h, --help            show help message
  --file FILE, -f FILE  File with serial numbers (one per line)
  --group-id ID         Dynamic group ID (overrides config)
  --dry-run             Show what would be done (no commands sent)
  --skip-confirmation   Skip confirmation prompt
```

## Output Examples

### Successful Wake-Up

```
====================================================================================================
WAKE-UP COMMAND SENT
====================================================================================================
✓ Computer 819 (H644YVR9VT)
  Device ID: 819
  Command UUID: 7695d8a1-71b9-4594-b60a-54f43ca09f59
====================================================================================================
```

### Batch Results

```
====================================================================================================
WAKE-UP CAMPAIGN RESULTS
====================================================================================================
Total computers: 3
Successful: 2
Failed: 1
====================================================================================================

✓ Successfully sent wake-up commands to:
  ✓ Computer 819 (UUID: cad91f3c-85c6-4456-95dc-424f499deb76)
  ✓ Computer 33 (UUID: 9babffb5-f0ec-4024-9f68-bdadd1a7d37a)

⚠️  Some computers failed:
  ✗ Computer 25: 500 Server Error
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `JAMF_PRO_URL` | Yes | Base URL of your Jamf Pro instance |
| `JAMF_PRO_USERNAME` | Yes* | Username for authentication |
| `JAMF_PRO_PASSWORD` | Yes* | Password for authentication |
| `JAMF_PRO_API_TOKEN` | Yes* | API Bearer token (alternative to username/password) |
| `JAMF_DYNAMIC_GROUP_ID` | No | Default group ID for group mode |
| `LOG_LEVEL` | No | Logging level (INFO, DEBUG, WARNING, ERROR) |
| `LOG_FILE` | No | Log file path |
| `API_TIMEOUT` | No | API request timeout in seconds |

*Either username/password OR API token is required.

## Troubleshooting

### 401 Unauthorized Error

**Problem:** The script returns a 401 Unauthorized error.

**Solution:**
- Verify your credentials in `.env` are correct
- Ensure your Jamf Pro user has API access permissions
- Check that the account is not locked or disabled

### Computer Not Found

**Problem:** Serial number doesn't match any computer in Jamf Pro.

**Solution:**
- Verify the serial number is correct
- Check that the computer is enrolled in Jamf Pro
- Use `--dry-run` to preview before executing

### Connection Refused

**Problem:** Cannot connect to Jamf Pro server.

**Solution:**
- Verify `JAMF_PRO_URL` is correct and reachable
- Check internet connectivity
- Ensure there are no firewall rules blocking the connection

## Logging

All operations are logged to the file specified in `LOG_FILE` (default: `jamf_wakeup.log`):

```bash
tail -f jamf_wakeup.log
```

Set `LOG_LEVEL=DEBUG` in `.env` for detailed troubleshooting information.

## Security

🔒 **Best Practices:**

1. **Never commit `.env` files** - Already prevented by `.gitignore`
2. **Use strong passwords** - Store securely
3. **Limit API permissions** - Give Jamf Pro user minimal required permissions
4. **Review logs regularly** - Monitor what commands are being executed
5. **Use `--dry-run` first** - Always preview before execution
6. **Implement confirmation prompts** - Default behavior includes confirmation

## Project Structure

```
Jamf_WakeUp_Call/
├── main.py              # Main script with CLI and orchestration
├── jamf_client.py       # Jamf Pro API client
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── .env.example         # Configuration template
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── LICENSE              # MIT License
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

## Disclaimer

This script is provided as-is. Test thoroughly in a non-production environment before using in production. Always use `--dry-run` to preview changes before execution.

---

**Made with ❤️ for Jamf Pro administrators**
