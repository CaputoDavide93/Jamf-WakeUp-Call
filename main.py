"""
Main script to wake up computers in Jamf Pro dynamic group
"""
import logging
import json
import sys
from typing import Optional, List, Dict
from jamf_client import JamfProClient
import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def validate_config() -> bool:
    """Validate that required configuration is present"""
    if not config.JAMF_PRO_URL:
        logger.error("JAMF_PRO_URL is not configured")
        return False
    
    # Check for at least one authentication method
    has_token = config.JAMF_PRO_API_TOKEN
    has_basic_auth = config.JAMF_PRO_USERNAME and config.JAMF_PRO_PASSWORD
    
    if not (has_token or has_basic_auth):
        logger.error("No authentication method configured. Provide either:")
        logger.error("  1. JAMF_PRO_API_TOKEN (Bearer token)")
        logger.error("  2. JAMF_PRO_USERNAME and JAMF_PRO_PASSWORD (Basic auth)")
        return False
    
    # Dynamic group ID is now optional - can target individual computers instead
    return True


def format_computer_display(computer_data: Dict, client: JamfProClient) -> str:
    """
    Format computer data for display in dry-run
    
    Args:
        computer_data: Computer dictionary from API
        client: JamfProClient instance for extracting user info
        
    Returns:
        Formatted string for display
    """
    comp_id = computer_data.get('id', 'N/A')
    comp_name = computer_data.get('name', 'Unknown')
    
    # Extract user information
    user_info = client.extract_user_info(computer_data)
    user_display = user_info['full_name'] or user_info['username'] or 'No user assigned'
    
    # Extract position if available
    position = user_info.get('position') or ''
    position_display = f" - {position}" if position else ""
    
    return f"[{comp_id:>4}] {comp_name:<30} | User: {user_display}{position_display}"


def prompt_confirmation(computers: List[Dict], client: JamfProClient) -> bool:
    """
    Show user confirmation prompt with computer details
    
    Args:
        computers: List of computers to process
        client: JamfProClient instance
        
    Returns:
        True if user confirms, False otherwise
    """
    print("\n" + "="*100)
    print("CONFIRMATION REQUIRED - The following computers will receive a wake-up call:")
    print("="*100)
    
    for i, comp in enumerate(computers, 1):
        display = format_computer_display(comp, client)
        print(f"  {i:2}. {display}")
    
    print("="*100)
    print(f"\nTotal computers to wake up: {len(computers)}")
    
    while True:
        user_input = input("\nDo you want to proceed? (yes/no): ").strip().lower()
        if user_input in ['yes', 'y']:
            return True
        elif user_input in ['no', 'n']:
            print("Operation cancelled.")
            return False
        else:
            print("Please enter 'yes' or 'no'")


def wake_up_single_computer(
    serial_number: str,
    dry_run: bool = False,
    skip_confirmation: bool = False
) -> int:
    """
    Send a wake-up call to a single computer by serial number
    
    Args:
        serial_number: Computer serial number (e.g., C02C94GVLVDL)
        dry_run: If True, only show what would be done without sending commands
        skip_confirmation: Skip user confirmation prompt
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Validate configuration
        if not validate_config():
            logger.error("Configuration validation failed")
            return 1
        
        # Create API client
        logger.info(f"Connecting to Jamf Pro: {config.JAMF_PRO_URL}")
        client = JamfProClient(
            base_url=config.JAMF_PRO_URL,
            timeout=config.API_TIMEOUT,
            api_token=config.JAMF_PRO_API_TOKEN,
            username=config.JAMF_PRO_USERNAME,
            password=config.JAMF_PRO_PASSWORD
        )
        
        try:
            # Fetch computer by serial number
            logger.info(f"Looking up computer by serial: {serial_number}")
            computer = client.get_computer_by_serial(serial_number)
            
            computers = [computer]  # Wrap in list for consistency
            
            logger.info(f"Found computer to process")
            
            # Show summary with confirmation
            if not skip_confirmation:
                if not prompt_confirmation(computers, client):
                    return 0
            
            # In dry-run mode, don't send commands
            if dry_run:
                logger.info("DRY RUN MODE - Showing what would be done (no commands sent)")
                display = format_computer_display(computer, client)
                logger.info(f"  [1/1] Would send wake-up to: {display}")
                return 0
            
            # Extract computer ID and send command
            computer_id = str(computer.get('general', {}).get('id'))
            
            try:
                result = client.redeploy_management_framework(computer_id)
                
                print("\n" + "="*100)
                print("WAKE-UP COMMAND SENT")
                print("="*100)
                print(f"✓ Computer {computer_id} ({computer.get('name')})")
                print(f"  Device ID: {result.get('deviceId')}")
                print(f"  Command UUID: {result.get('commandUuid')}")
                print("="*100 + "\n")
                
                return 0
            except Exception as e:
                print("\n" + "="*100)
                print("FAILED TO SEND WAKE-UP COMMAND")
                print("="*100)
                print(f"✗ Computer {computer_id}: {str(e)}")
                print("="*100 + "\n")
                return 1
            
        finally:
            client.close()
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n✗ Error: {e}\n")
        return 1


def wake_up_from_file(
    file_path: str,
    dry_run: bool = False,
    skip_confirmation: bool = False
) -> int:
    """
    Send wake-up calls to multiple computers from a file with serial numbers
    
    Args:
        file_path: Path to file containing serial numbers (one per line)
        dry_run: If True, only show what would be done without sending commands
        skip_confirmation: Skip user confirmation prompt
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Validate configuration
        if not validate_config():
            logger.error("Configuration validation failed")
            return 1
        
        # Read serial numbers from file
        logger.info(f"Reading serial numbers from: {file_path}")
        try:
            with open(file_path, 'r') as f:
                serials = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            print(f"✗ Error: File not found: {file_path}\n")
            return 1
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            print(f"✗ Error reading file: {e}\n")
            return 1
        
        if not serials:
            logger.warning("No serial numbers found in file")
            print("⚠️  No serial numbers found in file\n")
            return 0
        
        logger.info(f"Found {len(serials)} serial numbers to process")
        
        # Create API client
        logger.info(f"Connecting to Jamf Pro: {config.JAMF_PRO_URL}")
        client = JamfProClient(
            base_url=config.JAMF_PRO_URL,
            timeout=config.API_TIMEOUT,
            api_token=config.JAMF_PRO_API_TOKEN,
            username=config.JAMF_PRO_USERNAME,
            password=config.JAMF_PRO_PASSWORD
        )
        
        try:
            # Fetch computer details for all serial numbers
            logger.info("Fetching computer details...")
            computers = []
            failed_serials = []
            
            for serial in serials:
                try:
                    computer = client.get_computer_by_serial(serial)
                    computers.append(computer)
                    logger.debug(f"✓ Found: {serial}")
                except Exception as e:
                    logger.warning(f"Could not find computer {serial}: {e}")
                    failed_serials.append(serial)
            
            if not computers:
                logger.error("No computers found for any of the serial numbers")
                print("✗ No computers found for any serial numbers\n")
                return 1
            
            if failed_serials:
                print(f"⚠️  Warning: {len(failed_serials)} serial numbers not found:")
                for serial in failed_serials:
                    print(f"   - {serial}")
                print()
            
            logger.info(f"Successfully found {len(computers)}/{len(serials)} computers")
            
            # Show summary with confirmation
            if not skip_confirmation:
                if not prompt_confirmation(computers, client):
                    return 0
            
            # In dry-run mode, don't send commands
            if dry_run:
                logger.info("DRY RUN MODE - Showing what would be done (no commands sent)")
                for i, comp in enumerate(computers, 1):
                    display = format_computer_display(comp, client)
                    logger.info(f"  [{i}/{len(computers)}] Would send wake-up to: {display}")
                return 0
            
            # Extract computer IDs for sending
            computer_ids = [str(comp.get('general', {}).get('id')) for comp in computers]
            
            # Send redeploy commands
            results = client.redeploy_batch(computer_ids)
            
            # Log results
            print("\n" + "="*100)
            print("WAKE-UP CAMPAIGN RESULTS")
            print("="*100)
            print(f"Total computers: {results['total']}")
            print(f"Successful: {results['successful']}")
            print(f"Failed: {results['failed']}")
            print("="*100 + "\n")
            
            if results['failed'] > 0:
                print("⚠️  Some computers failed to receive wake-up call:")
                for detail in results['details']:
                    if detail['status'] == 'failed':
                        print(f"  ✗ Computer {detail['computer_id']}: {detail['error']}")
            
            # Log successful deployments
            if results['successful'] > 0:
                print("✓ Successfully sent wake-up commands to:")
                for detail in results['details']:
                    if detail['status'] == 'success':
                        print(
                            f"  ✓ Computer {detail['computer_id']} "
                            f"(UUID: {detail['command_uuid']})"
                        )
            
            return 0 if results['failed'] == 0 else 1
            
        finally:
            client.close()
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n✗ Error: {e}\n")
        return 1


def wake_up_dynamic_group(
    group_id: Optional[str] = None,
    dry_run: bool = False,
    stop_on_error: bool = False,
    skip_confirmation: bool = False
) -> int:
    """
    Send wake-up calls to all computers in a dynamic group
    
    Args:
        group_id: Dynamic group ID (uses config if not provided)
        dry_run: If True, only show what would be done without sending commands
        stop_on_error: Stop processing if an error occurs
        skip_confirmation: Skip user confirmation prompt
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Validate configuration
        if not validate_config():
            logger.error("Configuration validation failed")
            return 1
        
        group_id = group_id or config.JAMF_DYNAMIC_GROUP_ID
        
        if not group_id:
            logger.error("No group ID provided. Use --group-id or set JAMF_DYNAMIC_GROUP_ID in .env")
            return 1
        
        # Create API client
        logger.info(f"Connecting to Jamf Pro: {config.JAMF_PRO_URL}")
        client = JamfProClient(
            base_url=config.JAMF_PRO_URL,
            timeout=config.API_TIMEOUT,
            api_token=config.JAMF_PRO_API_TOKEN,
            username=config.JAMF_PRO_USERNAME,
            password=config.JAMF_PRO_PASSWORD
        )
        
        try:
            # Fetch computers from dynamic group
            logger.info(f"Fetching computers from dynamic group: {group_id}")
            computers = client.get_dynamic_group_computers(group_id)
            
            if not computers:
                logger.warning("No computers found in dynamic group")
                return 0
            
            logger.info(f"Found {len(computers)} computers to process")
            
            # Show dry-run with confirmation
            if not skip_confirmation:
                if not prompt_confirmation(computers, client):
                    return 0
            
            # In dry-run mode, don't send commands
            if dry_run:
                logger.info("DRY RUN MODE - Showing what would be done (no commands sent)")
                for i, comp in enumerate(computers, 1):
                    display = format_computer_display(comp, client)
                    logger.info(f"  [{i}/{len(computers)}] Would send wake-up to: {display}")
                return 0
            
            # Extract computer IDs for sending
            computer_ids = [str(comp.get('general', {}).get('id')) for comp in computers]
            
            # Send redeploy commands
            results = client.redeploy_batch(computer_ids, stop_on_error)
            
            # Log results
            print("\n" + "="*100)
            print("WAKE-UP CAMPAIGN RESULTS")
            print("="*100)
            print(f"Total computers: {results['total']}")
            print(f"Successful: {results['successful']}")
            print(f"Failed: {results['failed']}")
            print("="*100 + "\n")
            
            if results['failed'] > 0:
                print("⚠️  Some computers failed to receive wake-up call:")
                for detail in results['details']:
                    if detail['status'] == 'failed':
                        print(f"  ✗ Computer {detail['computer_id']}: {detail['error']}")
            
            # Log successful deployments
            if results['successful'] > 0:
                print("✓ Successfully sent wake-up commands to:")
                for detail in results['details']:
                    if detail['status'] == 'success':
                        print(
                            f"  ✓ Computer {detail['computer_id']} "
                            f"(UUID: {detail['command_uuid']})"
                        )
            
            return 0 if results['failed'] == 0 else 1
            
        finally:
            client.close()
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Send wake-up calls to computers in Jamf Pro',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Wake up entire dynamic group (with confirmation)
  python main.py
  
  # Wake up entire dynamic group (dry-run - no commands sent)
  python main.py --dry-run
  
  # Wake up specific computer by serial number
  python main.py C02C94GVLVDL
  
  # Wake up specific computer (dry-run)
  python main.py C02C94GVLVDL --dry-run
  
  # Wake up multiple computers from a file
  python main.py --file serials.txt
  
  # Wake up multiple computers from a file (dry-run)
  python main.py --file serials.txt --dry-run
  
  # Target specific group
  python main.py --group-id 42
  
  # Skip confirmation (use with caution)
  python main.py --skip-confirmation
        """
    )
    
    # Positional argument for serial number (optional)
    parser.add_argument(
        'serial',
        nargs='?',
        help='Computer serial number to target (e.g., C02C94GVLVDL). If omitted, uses dynamic group from config.'
    )
    
    parser.add_argument(
        '--file',
        '-f',
        help='File containing serial numbers (one per line). Lines starting with # are ignored.'
    )
    parser.add_argument(
        '--group-id',
        help='Dynamic group ID (overrides config). Ignored if serial is provided.'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without sending commands'
    )
    parser.add_argument(
        '--stop-on-error',
        action='store_true',
        help='Stop processing if an error occurs (group mode only)'
    )
    parser.add_argument(
        '--skip-confirmation',
        action='store_true',
        help='Skip user confirmation prompt (use with caution)'
    )
    
    args = parser.parse_args()
    
    # Determine which mode to run
    if args.file:
        # File mode - read serial numbers from file
        exit_code = wake_up_from_file(
            file_path=args.file,
            dry_run=args.dry_run,
            skip_confirmation=args.skip_confirmation
        )
    elif args.serial:
        # Single computer mode
        exit_code = wake_up_single_computer(
            serial_number=args.serial,
            dry_run=args.dry_run,
            skip_confirmation=args.skip_confirmation
        )
    else:
        # Group mode - use dynamic group
        exit_code = wake_up_dynamic_group(
            group_id=args.group_id,
            dry_run=args.dry_run,
            stop_on_error=args.stop_on_error,
            skip_confirmation=args.skip_confirmation
        )
    
    exit(exit_code)


if __name__ == '__main__':
    main()
