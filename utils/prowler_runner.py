import os
import subprocess
import logging
import json
import datetime
from pathlib import Path

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
        # Prowler command with expanded options
        prowler_command = [
            "prowler", 
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
