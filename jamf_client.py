"""
Jamf Pro API client for managing computers and sending wake-up calls
"""
import logging
import requests
import time
from typing import List, Dict, Optional
from urllib.parse import urljoin
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


class JamfProClient:
    """Client for interacting with Jamf Pro API"""
    
    def __init__(self, base_url: str, timeout: int = 30, api_token: Optional[str] = None, 
                 username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize Jamf Pro API client
        
        Args:
            base_url: Base URL of Jamf Pro instance
            timeout: Request timeout in seconds
            api_token: API Bearer token for authentication (preferred)
            username: Username for basic authentication (alternative)
            password: Password for basic authentication (alternative)
            
        Raises:
            ValueError: If no authentication method provided
        """
        if not api_token and not (username and password):
            raise ValueError("Either api_token OR (username AND password) must be provided")
        
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.timeout = timeout
        self._token = None
        self._token_exp = 0
        
        # If api_token provided, use it directly; otherwise will obtain token via username/password
        if api_token:
            self._token = api_token
            self._token_exp = float('inf')  # Assume static token doesn't expire
        
        self.session = self._create_session()
    
    def _get_token(self) -> str:
        """
        Get or refresh auth token using username/password.
        Tries multiple token endpoints like the working script does.
        """
        now = time.time()
        
        # Return existing token if still valid
        if self._token and now < self._token_exp - 30:
            return self._token
        
        # Try multiple token endpoints (same as working script)
        for path in ["/api/v1/auth/token", "/api/auth/tokens", "/uapi/auth/tokens"]:
            url = f"{self.base_url}{path}"
            try:
                logger.debug(f"Attempting token auth at {path}")
                auth = (self.username, self.password) if self.username and self.password else None
                response = requests.post(url, auth=auth, timeout=self.timeout)
                
                if response.status_code in (200, 201):
                    data = response.json()
                    token = data.get("token") or data.get("access_token")
                    exp_seconds = data.get("expires_in", 1800)
                    
                    if token:
                        self._token = token
                        self._token_exp = now + int(exp_seconds) - 30
                        logger.debug(f"Successfully obtained token from {path}")
                        return token
            except Exception as e:
                logger.debug(f"Token endpoint {path} failed: {e}")
        
        raise RuntimeError(f"Failed to obtain Jamf API token for user {self.username}. Check credentials and ensure account has API access.")
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with proper headers and authentication"""
        session = requests.Session()
        
        # Set common headers
        session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        return session
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers with current token"""
        token = self._get_token()
        return {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make an API request to Jamf Pro
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response object
            
        Raises:
            requests.RequestException: If request fails
        """
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        kwargs.setdefault('timeout', self.timeout)
        
        # Add auth headers to any provided headers
        headers = kwargs.get('headers', {})
        headers.update(self._get_auth_headers())
        kwargs['headers'] = headers
        
        logger.debug(f"Making {method} request to {url}")
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def get_dynamic_group_computers(self, group_id: str) -> List[Dict]:
        """
        Get all computers in a dynamic group with detailed information
        
        Args:
            group_id: Dynamic group ID
            
        Returns:
            List of computer dictionaries with extended user information
        """
        logger.info(f"Fetching computers from dynamic group: {group_id}")
        
        try:
            # Use JSS Resource API endpoint (works with token auth)
            response = self._make_request('GET', f'/JSSResource/computergroups/id/{group_id}')
            data = response.json()
            
            # Extract computers from the group
            computers = data.get('computer_group', {}).get('computers', [])
            logger.info(f"Found {len(computers)} computers in dynamic group")
            
            # Fetch detailed information for each computer to get user data
            detailed_computers = []
            for comp in computers:
                try:
                    detailed_info = self.get_computer_details(str(comp.get('id')))
                    detailed_computers.append(detailed_info)
                except Exception as e:
                    logger.warning(f"Could not fetch details for computer {comp.get('id')}: {e}")
                    # Still include the computer with limited info
                    detailed_computers.append(comp)
            
            return detailed_computers
        except Exception as e:
            logger.error(f"Failed to fetch dynamic group computers: {e}")
            raise
    
    def get_computer_details(self, computer_id: str) -> Dict:
        """
        Get detailed information about a computer including user data
        
        Args:
            computer_id: Jamf Pro Computer ID
            
        Returns:
            Computer dictionary with extended details
        """
        try:
            # Use JSS Resource API to get full computer details
            response = self._make_request('GET', f'/JSSResource/computers/id/{computer_id}')
            data = response.json()
            # Extract the computer object from the response
            return data.get('computer', {})
        except Exception as e:
            logger.debug(f"Could not fetch extended details for computer {computer_id}: {e}")
            raise
    
    def get_computer_by_serial(self, serial_number: str) -> Dict:
        """
        Get computer information by serial number using JSS Resource API
        
        Args:
            serial_number: Computer serial number (e.g., C02XXXXXXXXX)
            
        Returns:
            Computer dictionary with extended details
            
        Raises:
            Exception: If computer not found
        """
        logger.info(f"Searching for computer by serial: {serial_number}")
        
        try:
            # Try JSS Resource API search endpoint
            response = self._make_request(
                'GET',
                f'/JSSResource/computers/serialnumber/{serial_number}'
            )
            
            data = response.json()
            computer = data.get('computer', {})
            
            if not computer or not computer.get('general', {}).get('id'):
                raise Exception(f"Computer with serial {serial_number} not found")
            
            computer_id = computer.get('general', {}).get('id')
            comp_name = computer.get('general', {}).get('name', 'Unknown')
            logger.info(f"Found computer: {comp_name} (ID: {computer_id}, Serial: {serial_number})")
            
            return computer
        except Exception as e:
            logger.error(f"Failed to fetch computer by serial {serial_number}: {e}")
            raise
    
    def search_computers_by_criteria(self, criteria: Dict) -> List[Dict]:
        """
        Search for computers by specific criteria
        
        Args:
            criteria: Search criteria (e.g., checked in last 15 days)
            
        Returns:
            List of matching computers
        """
        logger.info(f"Searching computers with criteria: {criteria}")
        
        try:
            # Build query parameters
            params = criteria
            response = self._make_request('GET', '/api/v2/computers', params=params)
            data = response.json()
            
            computers = data.get('results', [])
            logger.info(f"Found {len(computers)} computers matching criteria")
            
            return computers
        except Exception as e:
            logger.error(f"Failed to search computers: {e}")
            raise
    
    def redeploy_management_framework(self, computer_id: str) -> Dict:
        """
        Send a wake-up call to redeploy Jamf Management Framework
        
        Args:
            computer_id: Jamf Pro Computer ID
            
        Returns:
            Response data with deviceId and commandUuid
            
        Raises:
            requests.RequestException: If the API call fails
        """
        logger.info(f"Sending redeploy command to computer ID: {computer_id}")
        
        try:
            response = self._make_request(
                'POST',
                f'/api/v1/jamf-management-framework/redeploy/{computer_id}'
            )
            
            result = response.json()
            logger.info(f"Redeploy command queued successfully. UUID: {result.get('commandUuid')}")
            
            return result
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.error(f"Computer with ID {computer_id} not found")
            else:
                logger.error(f"Failed to redeploy management framework: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during redeploy: {e}")
            raise
    
    def redeploy_batch(self, computer_ids: List[str], stop_on_error: bool = False) -> Dict:
        """
        Redeploy management framework for multiple computers
        
        Args:
            computer_ids: List of Jamf Pro Computer IDs
            stop_on_error: Stop processing if an error occurs
            
        Returns:
            Dictionary with success/failure counts and details
        """
        results = {
            'total': len(computer_ids),
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for computer_id in computer_ids:
            try:
                result = self.redeploy_management_framework(computer_id)
                results['successful'] += 1
                results['details'].append({
                    'computer_id': computer_id,
                    'status': 'success',
                    'command_uuid': result.get('commandUuid'),
                    'device_id': result.get('deviceId')
                })
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'computer_id': computer_id,
                    'status': 'failed',
                    'error': str(e)
                })
                
                if stop_on_error:
                    logger.error("Stopping batch processing due to error")
                    break
        
        logger.info(
            f"Batch redeploy complete: {results['successful']} successful, "
            f"{results['failed']} failed"
        )
        
        return results
    
    def close(self):
        """Close the session"""
        self.session.close()
    
    def extract_user_info(self, computer_data: Dict) -> Dict:
        """
        Extract user and location information from computer data
        
        Args:
            computer_data: Computer dictionary from API response
            
        Returns:
            Dictionary with user information
        """
        user_info = {
            'username': None,
            'full_name': None,
            'email': None,
            'position': None
        }
        
        # Try different API response formats
        # Format from v2 API
        if 'userAndLocation' in computer_data:
            loc = computer_data['userAndLocation']
            user_info['username'] = loc.get('username')
            user_info['full_name'] = loc.get('realName')
            user_info['email'] = loc.get('email')
            user_info['position'] = loc.get('position')
        
        # Try JSS/v1 API format (uses different field names)
        elif 'location' in computer_data:
            loc = computer_data['location']
            user_info['username'] = loc.get('username')
            # Try both realName (v2) and realname (v1)
            user_info['full_name'] = loc.get('real_name') or loc.get('realName') or loc.get('realname')
            user_info['email'] = loc.get('email_address') or loc.get('email')
            user_info['position'] = loc.get('position')
        
        return user_info
