import os
import subprocess
import json
import logging
from pathlib import Path

def load_module_categories():
    """
    Loads Pacu module categories from a configuration file.
    
    Returns:
        dict: A dictionary containing Pacu module categories.
    """
    config_path = Path("config/pacu_modules.json")
    try:
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            logging.warning(f"Configuration file {config_path} not found. Using default categories.")
            # Return an empty dictionary that will be filled with default categories
            return {}
    except Exception as e:
        logging.error(f"Error loading module categories: {e}")
        return {}

def execute_pacu_module(session_name, module_name, profile, args=None):
    """
    Executes a specific Pacu module.
    
    Args:
        session_name (str): Name of the Pacu session.
        module_name (str): Name of the module to execute.
        profile (str): Name of the AWS CLI profile to use.
        args (str, optional): Additional arguments for the module.
        
    Returns:
        dict: A dictionary containing the module name, standard output, and error output.
    """
    cmd = ['pacu', '--session', session_name, '--exec', '--module-name', module_name, '--import-keys', profile]
    if args:
        cmd.extend(['--module-args', args])
    
    logging.info(f"Executing Pacu module: {module_name}")
    logging.debug(f"Command: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            stdin=subprocess.PIPE, 
            text=True
        )
        stdout, stderr = process.communicate(input="y\n")  # Respond "Y" to any confirmation prompt
        
        if "AccessDeniedException" in stderr:
            stderr = "Module cannot be executed due to lack of permission"
            
        return {
            "module": module_name,
            "stdout": stdout,
            "stderr": stderr,
            "status": "success" if process.returncode == 0 else "error",
            "return_code": process.returncode
        }
    except Exception as e:
        logging.error(f"Error executing Pacu module {module_name}: {e}")
        return {
            "module": module_name,
            "stdout": "",
            "stderr": str(e),
            "status": "error",
            "return_code": -1
        }

def run_pacu(profile_for_pacu, session_name, category):
    """
    Runs the Pacu Framework based on the specified category.
    
    Args:
        profile_for_pacu (str): Name of the AWS CLI profile to use.
        session_name (str): Name of the Pacu session.
        category (str): Category of modules to execute.
        
    Returns:
        dict: A dictionary containing the execution status, results, and a descriptive message.
    """
    print(f"Running PACU Framework with profile {profile_for_pacu}, session {session_name}, category {category}")
    logging.info(f"Running PACU Framework with profile {profile_for_pacu}, session {session_name}, category {category}")
    
    # Configure AWS profile
    os.environ['AWS_PROFILE'] = profile_for_pacu
    
    # Load module categories
    categories = load_module_categories()
    
    # If the configuration file doesn't exist or is empty, use default categories
    if not categories:
        logging.warning("Using default module categories")
        # Define default categories here if needed
    
    # List to store results
    results = []
    
    # Check if the session already exists and is active, or create a new session
    try:
        logging.info(f"Activating Pacu session: {session_name}")
        activate_session_command = ['pacu', '--session', session_name]
        subprocess.run(activate_session_command, check=True, capture_output=True)
        logging.info(f"Session {session_name} activated")
    except subprocess.CalledProcessError:
        logging.info(f"Creating new Pacu session: {session_name}")
        create_session_command = ['pacu', '--new-session', session_name]
        subprocess.run(create_session_command, check=True, capture_output=True)
        logging.info(f"Session {session_name} created")
    
    # Create directory for reports if it doesn't exist
    reports_dir = Path("reports/data")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Execute modules based on category
    if category == "category_enum":
        modules_to_run = categories.get("category_enum", [])
        special_modules = categories.get("special_modules", {})
        
        for module_name in modules_to_run:
            if module_name in special_modules:
                # Special modules that don't need region arguments
                result = execute_pacu_module(session_name, module_name, profile_for_pacu)
            elif module_name == "iam__enum_action_query":
                logging.info("Skipping iam__enum_action_query as it requires a query case")
                continue
            elif module_name == "systemsmanager__download_parameters":
                # Special configuration for systemsmanager__download_parameters
                downloads_dir = os.path.expanduser("~/.local/share/pacu/data/downloads/ssm_parameters/")
                os.makedirs(downloads_dir, exist_ok=True)
                ssm_region = "us-east-2"
                with open(os.path.join(downloads_dir, '{}.txt'.format(ssm_region)), 'w+') as f:
                    pass
                result = execute_pacu_module(session_name, module_name, profile_for_pacu, "--regions us-east-2")
            else:
                # Standard modules with region argument
                result = execute_pacu_module(session_name, module_name, profile_for_pacu, "--regions us-east-2")
            
            results.append(result)
            print(f"Executed module: {module_name} - Status: {result['status']}")
    else:
        # For other categories, check if the category exists in the configuration file
        if category in categories:
            modules_to_run = categories[category]
            for module_name in modules_to_run:
                result = execute_pacu_module(session_name, module_name, profile_for_pacu)
                results.append(result)
                print(f"Executed module: {module_name} - Status: {result['status']}")
        else:
            # If the category is not recognized, treat it as an individual module name
            logging.warning(f"Category {category} not recognized, treating as individual module")
            result = execute_pacu_module(session_name, category, profile_for_pacu)
            results.append(result)
            print(f"Executed module: {category} - Status: {result['status']}")
    
    # Save results to a JSON file
    output_file = reports_dir / "pacu_report.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
    
    logging.info(f"Results saved in {output_file}")
    print(f"Results saved in {output_file}")
    
    return {
        "success": True,
        "data": str(output_file),
        "message": f"Pacu execution completed. Report saved to: {output_file}",
        "results": results
    }