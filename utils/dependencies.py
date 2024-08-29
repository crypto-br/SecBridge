import subprocess
import sys
import os
import platform

def check_deps():
    # Determine the package manager based on the operating system
    os_type = detect_os()
    package_manager = "apt-get" if os_type == "Debian" else "yum"

    # AWS CLI
    if not command_exists("aws"):
        print("AWS CLI is not installed.")
        if ask_user(f"Do you want to install it? [1] yes / [2] no \n") == 1:
            subprocess.run(["sudo", package_manager, "update", "-y"])
            subprocess.run(["sudo", package_manager, "install", "-y", "awscli"])
            print("AWS CLI installed successfully.")
        else:
            print("Exiting the script.")
            sys.exit(1)
    else:
        print("AWS CLI is already installed. [OK]")
    
    # Python3
    if not command_exists("python3"):
        print("Python3 is not installed.")
        if ask_user(f"Do you want to install it? [1] yes / [2] no \n") == 1:
            subprocess.run(["sudo", package_manager, "update", "-y"])
            subprocess.run(["sudo", package_manager, "install", "-y", "python3"])
            print("Python3 installed successfully.")
        else:
            print("Installation is necessary. Exiting.")
            sys.exit(1)
    else:
        print("Python3 is already installed. [OK]")
    
    # Prowler
    if not command_exists("prowler"):
        print("Prowler is not installed.")
        if ask_user(f"Do you want to install it? [1] yes / [2] no \n") == 1:
            subprocess.run(["sudo", package_manager, "update", "-y"])
            subprocess.run(["sudo", package_manager, "install", "-y", "prowler"])
            print("Prowler installed successfully.")
        else:
            print("Installation is necessary. Exiting.")
            sys.exit(1)
    else:
        print("Prowler is already installed. [OK]")

    # PACU Framework
    if not command_exists("pacu"):
        print("PACU Framework is not installed.")
        if ask_user(f"Do you want to install it? [1] yes / [2] no \n") == 1:
            print("Installing PACU Framework...")
            #os.system("git clone https://github.com/RhinoSecurityLabs/pacu.git")
            os.system("python3 -m pip install -U pacu")
            print("PACU Framework installed successfully.")
        else:
            print("PACU Framework installation is necessary. Exiting.")
            sys.exit(1)
    else:
        print("PACU Framework is already installed. [OK]")

def command_exists(command):
    return subprocess.call(f"type {command}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

def ask_user(prompt):
    return int(input(prompt))

def detect_os():
    os_info = platform.system()
    if os_info == "Linux":
        try:
            # Use subprocess to call lsb_release for better compatibility
            distro_info = subprocess.check_output(["lsb_release", "-is"], text=True).strip().lower()
        except subprocess.CalledProcessError:
            print("Unable to determine Linux distribution using lsb_release.")
            sys.exit(1)

        if distro_info in ["debian", "ubuntu"]:
            return "Debian"
        elif distro_info in ["centos", "redhat", "fedora", "amazon"]:
            return "RedHat"
        else:
            print(f"Unsupported Linux distribution: {distro_info}")
            sys.exit(1)
    elif os_info == "Darwin":
        return "macOS"
    else:
        print("Unsupported operating system.")
        sys.exit(1)

if __name__ == "__main__":
    check_deps()
