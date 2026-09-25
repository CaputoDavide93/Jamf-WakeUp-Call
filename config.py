"""
Configuration file for Jamf Pro Wake-Up Script
"""
import os
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Values copied unedited from .env.example are treated as unset
_PLACEHOLDER_PREFIXES = ('your_', 'your-', 'dev_', 'https://your-')


def _real_value(name: str) -> Optional[str]:
    """Return the env var, or None if it is empty or still an example placeholder"""
    value = os.getenv(name, '').strip()
    if not value or value.lower().startswith(_PLACEHOLDER_PREFIXES):
        return None
    return value


# Jamf Pro API Configuration (required, no default tenant)
JAMF_PRO_URL = _real_value('JAMF_PRO_URL')

# Authentication methods (supports both Token and Basic Auth)
# Only set if actually provided (not empty placeholders)
JAMF_PRO_API_TOKEN = _real_value('JAMF_PRO_API_TOKEN')
JAMF_PRO_USERNAME = _real_value('JAMF_PRO_USERNAME')
JAMF_PRO_PASSWORD = _real_value('JAMF_PRO_PASSWORD')

# Dynamic Group Configuration
JAMF_DYNAMIC_GROUP_ID = os.getenv('JAMF_DYNAMIC_GROUP_ID', '')  # Optional - can target individual computers

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'jamf_wakeup.log')

# Timeout settings (in seconds)
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))
