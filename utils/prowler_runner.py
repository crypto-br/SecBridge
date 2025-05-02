import os
import subprocess
import logging
import json
import datetime
import platform
from pathlib import Path

def get_prowler_command():
    """
    Returns the appropriate Prowler command based on the operating system.
    
    Returns:
        str: The command to run Prowler.
    """
    # Check if we're on Kali or ParrotOS
    if platform.system().lower() == "linux":
        try:
            with open("/etc/os-release") as f:
                os_release = f.read().lower()
                if "kali" in os_release or "parrot" in os_release:
                    # Check if prowler.py exists in the home directory
                    prowler_path = os.path.expanduser("~/prowler/prowler.py")
                    if os.path.exists(prowler_path):
                        return "python3 " + prowler_path
        except FileNotFoundError:
            pass
    
    # Default command for other systems
    return "prowler"

def run_prowler(profile_for_prowler):
    """
    Runs Prowler to perform a security assessment on the specified AWS account.
    
    Args:
        profile_for_prowler (str): Name of the AWS CLI profile to use.
        
    Returns:
        dict: A dictionary containing the execution status, the path of the generated JSON file (if successful)
              and a descriptive message.
    """
    logging.info(f"Running Prowler with profile: {profile_for_prowler}")
    print(f"Running Prowler with profile: {profile_for_prowler}...")
    
    # Create directory for reports if it doesn't exist
    reports_dir = Path("reports/prowler")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = reports_dir / f"prowler_report_{timestamp}.json"
    
    try:
        # Get the appropriate prowler command
        prowler_base = get_prowler_command()
        
        # Prowler command with expanded options
        if " " in prowler_base:  # If it's a command with arguments (like python3 path/to/prowler.py)
            prowler_command = prowler_base.split() + [
                "aws", 
                "--severity", "critical", 
                "--profile", profile_for_prowler,
                "-M", "json-asff",
                "-o", str(reports_dir)
            ]
        else:
            prowler_command = [
                prowler_base, 
                "aws", 
                "--severity", "critical", 
                "--profile", profile_for_prowler,
                "-M", "json-asff",
                "-o", str(reports_dir)
            ]
        
        logging.info(f"Executing command: {' '.join(prowler_command)}")
        
        # Execute Prowler command
        process = subprocess.run(
            prowler_command, 
            capture_output=True, 
            text=True,
            check=True  # Raises exception if command fails
        )
        
        # Process output to find the generated JSON file
        output_text = process.stdout.strip()
        json_path = None
        
        for line in output_text.splitlines():
            if "ASFF" in line and line.endswith(".json"):
                json_path = line.split()[-1]
                if os.path.exists(json_path):
                    logging.info(f"JSON-ASFF file generated at: {json_path}")
                    
                    # Copy the file to our reports directory with standardized name
                    with open(json_path, 'r') as src_file:
                        json_content = json.load(src_file)
                    
                    with open(output_file, 'w') as dest_file:
                        json.dump(json_content, dest_file, indent=2)
                    
                    logging.info(f"Report copied to: {output_file}")
                    break
        
        if json_path:
            return {
                "success": True, 
                "data": str(output_file), 
                "message": f"Prowler assessment completed. Report saved to: {output_file}"
            }
        else:
            return {
                "success": False, 
                "data": None, 
                "message": "Prowler completed but no JSON report was found."
            }
            
    except subprocess.CalledProcessError as e:
        error_msg = f"Error executing Prowler command: {e}"
        logging.error(error_msg)
        return {"success": False, "data": None, "message": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error while executing Prowler: {e}"
        logging.error(error_msg)
        return {"success": False, "data": None, "message": error_msg}
