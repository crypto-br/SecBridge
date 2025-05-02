#!/usr/bin/env python3
"""
Módulo de verificação e instalação de dependências.
Verifica se AWS CLI, Python3, Prowler e PACU Framework estão instalados,
solicitando ao usuário instalar as ausentes.
"""

import subprocess
import sys
import os
import platform
import logging
from pathlib import Path

def check_deps():
    """
    Checks required dependencies and installs missing ones.
    
    Returns:
        dict: A dictionary containing the check status and a descriptive message.
    """
    # Configure logging
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "dependencies.log"
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logging.info("Checking SecBridge dependencies...")
    
    # Detect operating system
    os_type = detect_os()
    if os_type in ["Debian", "RedHat", "Kali", "ParrotOS"]:
        package_manager = "apt-get" if os_type in ["Debian", "Kali", "ParrotOS"] else "yum"
        
        # Automatically install security distro specific dependencies
        if os_type in ["Kali", "ParrotOS"]:
            logging.info(f"Detected {os_type} security distribution. Installing specific dependencies...")
            result = install_security_distro_deps(os_type)
            if not result["success"]:
                logging.error(f"Failed to install {os_type} specific dependencies: {result['message']}")
                return result
            logging.info(f"{os_type} specific dependencies installed successfully.")
    elif os_type == "macOS":
        package_manager = "brew"
    else:
        logging.error("Unsupported operating system.")
        return {"success": False, "message": "Unsupported operating system."}
    
    # List of dependencies to check
    dependencies = [
        {
            "name": "AWS CLI",
            "command": "aws",
            "install_commands": {
                "apt-get": ["sudo", "apt-get", "update", "-y", "&&", "sudo", "apt-get", "install", "-y", "awscli"],
                "yum": ["sudo", "yum", "update", "-y", "&&", "sudo", "yum", "install", "-y", "awscli"],
                "brew": ["brew", "install", "awscli"]
            },
            "required": True
        },
        {
            "name": "Python3",
            "command": "python3",
            "install_commands": {
                "apt-get": ["sudo", "apt-get", "update", "-y", "&&", "sudo", "apt-get", "install", "-y", "python3", "python3-pip"],
                "yum": ["sudo", "yum", "update", "-y", "&&", "sudo", "yum", "install", "-y", "python3", "python3-pip"],
                "brew": ["brew", "install", "python3"]
            },
            "required": True
        },
        {
            "name": "Prowler",
            "command": "prowler",
            "install_commands": {
                "apt-get": ["sudo", "apt-get", "update", "-y", "&&", "sudo", "apt-get", "install", "-y", "pipx", "&&", "sudo", "pipx", "ensurepath", "&&", "sudo", "pipx", "install", "prowler"],
                "yum": ["sudo", "yum", "update", "-y", "&&", "sudo", "yum", "install", "-y", "pipx", "&&", "sudo", "pipx", "ensurepath", "&&", "sudo", "pipx", "install", "prowler"],
                "brew": ["brew", "install", "pipx", "&&", "pipx", "ensurepath", "&&", "pipx", "install", "prowler"]
            },
            "required": True
        },
        {
            "name": "PACU Framework",
            "command": "pacu",
            "install_commands": {
                "apt-get": ["python3", "-m", "pip", "install", "-U", "pacu"],
                "yum": ["python3", "-m", "pip", "install", "-U", "pacu"],
                "brew": ["python3", "-m", "pip", "install", "-U", "pacu"]
            },
            "required": True
        }
    ]
    
    # Check each dependency
    missing_deps = []
    for dep in dependencies:
        if not command_exists(dep["command"]):
            logging.info(f"{dep['name']} is not installed.")
            missing_deps.append(dep)
        else:
            logging.info(f"{dep['name']} is already installed. [OK]")
    
    # If there are missing dependencies, ask the user if they want to install them
    if missing_deps:
        logging.info(f"Found {len(missing_deps)} missing dependencies.")
        
        for dep in missing_deps:
            if dep["required"]:
                if ask_user(f"Do you want to install {dep['name']}? [1] yes / [2] no: ") == 1:
                    try:
                        # Convert the command list to a string for execution
                        install_cmd = " ".join(dep["install_commands"][package_manager])
                        logging.info(f"Installing {dep['name']}...")
                        
                        # Execute the installation command
                        result = subprocess.run(install_cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        
                        # Check if the installation was successful
                        if command_exists(dep["command"]):
                            logging.info(f"{dep['name']} installed successfully.")
                        else:
                            logging.error(f"Failed to install {dep['name']}. Please install it manually.")
                            return {"success": False, "message": f"Failed to install {dep['name']}. Please install it manually."}
                    except subprocess.CalledProcessError as e:
                        logging.error(f"Error during installation of {dep['name']}: {e}")
                        logging.error(f"Error output: {e.stderr}")
                        return {"success": False, "message": f"Error during installation of {dep['name']}: {e}"}
                else:
                    logging.error(f"Installation of {dep['name']} is required. Exiting.")
                    return {"success": False, "message": f"Installation of {dep['name']} is required."}
    
    # Check if all dependencies are installed now
    all_deps_installed = all(command_exists(dep["command"]) for dep in dependencies)
    
    if all_deps_installed:
        logging.info("All dependencies are correctly installed.")
        return {"success": True, "message": "All dependencies are correctly installed."}
    else:
        logging.error("Some dependencies are still missing. Please install them manually.")
        return {"success": False, "message": "Some dependencies are still missing. Please install them manually."}

def command_exists(command):
    """
    Verifica se um comando existe no sistema.
    
    Args:
        command (str): O comando a ser verificado.
        
    Returns:
        bool: True se o comando existir, False caso contrário.
    """
    result = subprocess.run(["which", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

def ask_user(prompt):
    """
    Prompts the user for input and returns an integer (1 or 2).
    
    Args:
        prompt (str): The message to display to the user.
        
    Returns:
        int: 1 for yes, 2 for no.
    """
    while True:
        try:
            choice = int(input(prompt))
            if choice in [1, 2]:
                return choice
            else:
                print("Please choose [1] or [2].")
        except ValueError:
            print("Invalid input. Please enter 1 or 2.")

def detect_os():
    """
    Detects the operating system and returns an identifier.
    
    Returns:
        str: "Debian", "RedHat", "macOS", "Kali", "ParrotOS" or None if not supported.
    """
    os_info = platform.system()
    if os_info == "Linux":
        try:
            # First try using lsb_release command
            try:
                distro = subprocess.check_output(["lsb_release", "-is"], text=True).strip().lower()
                if distro == "kali":
                    logging.info("Detected Kali Linux distribution")
                    return "Kali"
                elif distro == "parrot":
                    logging.info("Detected ParrotOS distribution")
                    return "ParrotOS"
                elif distro in ["debian", "ubuntu", "linuxmint", "pop"]:
                    return "Debian"
                elif distro in ["centos", "redhat", "fedora", "amazon", "rhel"]:
                    return "RedHat"
                else:
                    logging.warning(f"Unsupported Linux distribution: {distro}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                # lsb_release command not found, try alternative method
                logging.warning("lsb_release command not found, trying alternative detection method")
                pass
                
            # Alternative method to detect distribution
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release") as f:
                    os_release = f.read().lower()
                    if "kali" in os_release:
                        logging.info("Detected Kali Linux distribution via /etc/os-release")
                        return "Kali"
                    elif "parrot" in os_release:
                        logging.info("Detected ParrotOS distribution via /etc/os-release")
                        return "ParrotOS"
            
            if os.path.exists("/etc/debian_version"):
                logging.info("Detected Debian-based distribution via /etc/debian_version")
                return "Debian"
            elif os.path.exists("/etc/redhat-release"):
                logging.info("Detected RedHat-based distribution via /etc/redhat-release")
                return "RedHat"
            else:
                logging.error("Could not determine Linux distribution.")
                return None
        except Exception as e:
            logging.error(f"Error detecting Linux distribution: {e}")
            return None
    elif os_info == "Darwin":
        return "macOS"
    else:
        logging.error(f"Unsupported operating system: {os_info}")
        return None

def install_security_distro_deps(distro_type):
    """
    Automatically installs dependencies specific to security distributions like Kali Linux and ParrotOS.
    
    Args:
        distro_type (str): The type of security distribution ("Kali" or "ParrotOS").
        
    Returns:
        dict: A dictionary containing the installation status and a descriptive message.
    """
    try:
        logging.info(f"Installing {distro_type} specific dependencies...")
        
        # Update package lists
        logging.info("Updating package lists...")
        subprocess.run(["sudo", "apt", "update", "-y"], check=True)
        
        # Install basic dependencies
        logging.info("Installing basic dependencies...")
        subprocess.run(["sudo", "apt", "install", "-y", "python3", "python3-pip", "python3-venv", "git", "awscli"], check=True)
        
        # Install Python packages
        logging.info("Installing Python packages...")
        subprocess.run(["pip3", "install", "boto3", "botocore"], check=True)
        
        # Install Prowler if not already installed
        if not command_exists("prowler"):
            logging.info("Installing Prowler...")
            prowler_dir = Path.home() / "prowler"
            if not prowler_dir.exists():
                subprocess.run(["git", "clone", "https://github.com/prowler-cloud/prowler.git", str(prowler_dir)], check=True)
                subprocess.run(["pip3", "install", "-r", str(prowler_dir / "requirements.txt")], check=True)
                
                # Add Prowler to PATH
                prowler_bin = prowler_dir / "prowler"
                if prowler_bin.exists():
                    # Create symlink in /usr/local/bin
                    try:
                        subprocess.run(["sudo", "ln", "-sf", str(prowler_bin), "/usr/local/bin/prowler"], check=True)
                        logging.info("Prowler symlink created in /usr/local/bin")
                    except subprocess.CalledProcessError:
                        logging.warning("Failed to create Prowler symlink. You may need to add it to your PATH manually.")
        
        # Install Pacu if not already installed
        if not command_exists("pacu"):
            logging.info("Installing Pacu...")
            pacu_dir = Path.home() / "pacu"
            if not pacu_dir.exists():
                subprocess.run(["git", "clone", "https://github.com/RhinoSecurityLabs/pacu.git", str(pacu_dir)], check=True)
                subprocess.run(["pip3", "install", "-r", str(pacu_dir / "requirements.txt")], check=True)
                
                # Add Pacu to PATH
                pacu_bin = pacu_dir / "pacu.py"
                if pacu_bin.exists():
                    # Create symlink in /usr/local/bin
                    try:
                        # Create executable wrapper script
                        wrapper_content = f"""#!/bin/bash
cd {str(pacu_dir)}
python3 pacu.py "$@"
"""
                        wrapper_path = "/usr/local/bin/pacu"
                        with open("/tmp/pacu_wrapper", "w") as f:
                            f.write(wrapper_content)
                        
                        subprocess.run(["sudo", "mv", "/tmp/pacu_wrapper", wrapper_path], check=True)
                        subprocess.run(["sudo", "chmod", "+x", wrapper_path], check=True)
                        logging.info("Pacu wrapper script created in /usr/local/bin")
                    except (subprocess.CalledProcessError, IOError) as e:
                        logging.warning(f"Failed to create Pacu wrapper script: {e}. You may need to add it to your PATH manually.")
        
        # Adjust permissions for reports and logs directories
        logging.info("Adjusting permissions for reports and logs directories...")
        reports_dir = Path("reports")
        logs_dir = Path("logs")
        
        if reports_dir.exists():
            subprocess.run(["chmod", "-R", "755", str(reports_dir)], check=True)
        
        if logs_dir.exists():
            subprocess.run(["chmod", "-R", "755", str(logs_dir)], check=True)
        
        return {"success": True, "message": f"{distro_type} specific dependencies installed successfully."}
    
    except subprocess.CalledProcessError as e:
        error_msg = f"Error installing {distro_type} dependencies: {e}"
        logging.error(error_msg)
        return {"success": False, "message": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error during {distro_type} dependency installation: {e}"
        logging.error(error_msg)
        return {"success": False, "message": error_msg}

def run_command(command, description=""):
    """
    Executes a system command using subprocess.run with error checking.
    
    Args:
        command (list): List of strings representing the command and its arguments.
        description (str, optional): Description of the command for logging.
        
    Returns:
        subprocess.CompletedProcess: The result of the command execution.
        
    Raises:
        subprocess.CalledProcessError: If the command fails.
    """
    try:
        logging.info(f"Executing command: {' '.join(command)}")
        return subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during {description}: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    check_deps()

