"""
Configuration file for Jamf Pro Wake-Up Script
"""
import os
import sys

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Jamf Pro API Configuration (required — no default)
JAMF_PRO_URL = os.getenv('JAMF_PRO_URL', '').strip()
if not JAMF_PRO_URL:
    sys.exit(
        "ERROR: JAMF_PRO_URL is not set.\n"
        "Set it in your environment or .env file, e.g.:\n"
        "  JAMF_PRO_URL=https://your-jamf-instance.jamfcloud.com"
    )

# Authentication methods (supports both Token and Basic Auth)
# Only set if actually provided (not empty placeholders)
_token = os.getenv('JAMF_PRO_API_TOKEN', '').strip()
_username = os.getenv('JAMF_PRO_USERNAME', '').strip()
_password = os.getenv('JAMF_PRO_PASSWORD', '').strip()

JAMF_PRO_API_TOKEN = _token if _token and not _token.startswith('your_') else None
JAMF_PRO_USERNAME = _username if _username and not _username.startswith('dev_') else None
JAMF_PRO_PASSWORD = _password if _password and not _password.startswith('dev_') else None

# Dynamic Group Configuration
JAMF_DYNAMIC_GROUP_ID = os.getenv('JAMF_DYNAMIC_GROUP_ID', '')  # Optional - can target individual computers

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'jamf_wakeup.log')

# Timeout settings (in seconds)
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))
