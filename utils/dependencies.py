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
    if os_type in ["Debian", "RedHat"]:
        package_manager = "apt-get" if os_type == "Debian" else "yum"
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
        str: "Debian", "RedHat", "macOS" or None if not supported.
    """
    os_info = platform.system()
    if os_info == "Linux":
        try:
            # First try using lsb_release command
            try:
                distro = subprocess.check_output(["lsb_release", "-is"], text=True).strip().lower()
                if distro in ["debian", "ubuntu", "linuxmint", "pop"]:
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

