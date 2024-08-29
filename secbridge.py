from utils.dependencies import check_deps
from utils.aws_config import configure_profile
from utils.prowler_runner import run_prowler
from utils.pacu_runner import run_pacu
from utils.pacu_report import generate_report
import sys
import time
import json
import os

def print_header():
    print("""
######################################################################
                   __          __     __              
.-----.-----.----.|  |--.----.|__|.--|  |.-----.-----.
|__ --|  -__|  __||  _  |   _||  ||  _  ||  _  |  -__|
|_____|_____|____||_____|__|  |__||_____||___  |_____| v1.0
                                         |_____|      
Luiz Machado (@cryptobr)
######################################################################
""")

print_header()

def main():
    # Conditional parameters
    if "--deps" in sys.argv or "-deps" in sys.argv:
        print("#################################")
        print("Checking Dependencies...")
        print("#################################")
        time.sleep(1)
        check_deps()
        sys.exit(1)

    if "--prowler" in sys.argv or "-prowler" in sys.argv:
        print("#################################")
        print("Starting Prowler...")
        time.sleep(1)
        print("#################################")
        profile_for_prowler = input("Enter the AWS-CLI profile you want to use: \n")
        print("#################################")
        run_prowler(profile_for_prowler)
        sys.exit(1)

    if "--prowler-dash" in sys.argv or "-prowler-dash" in sys.argv:
        print("#################################")
        print("Starting Prowler Dashboard...")
        time.sleep(1)
        print("#################################")
        os.system("prowler dashboard")
        print("#################################")
        sys.exit(1)

    if "--pacu-enum" in sys.argv or "-pacu-enum" in sys.argv:
        print("#################################")
        print("Cleaning session data...")
        time.sleep(1)
        os.system("rm -rf ~/.local/share/pacu/*")
        print("#################################")
        print("Starting PACU framework in enumeration mode...")
        time.sleep(1)
        print("#################################")
        profile_for_pacu = input("Enter the AWS-CLI profile you want to use: \n")
        session_name = input("Enter the session name to start PACU: \n")
        category = "category_enum"
        run_pacu(profile_for_pacu, session_name, category)
        print("#################################")
        print("Generating report...")
        generate_report()
        time.sleep(1)
        print("Report available in --pacu-dash")
        print("#################################")
        
        sys.exit(1)

    if "--pacu" in sys.argv or "-pacu" in sys.argv:
        print("#################################")
        print("Cleaning session data...")
        time.sleep(1)
        print("#################################")
        os.system("rm -rf ~/.local/share/pacu/*")
        time.sleep(1)
        profile_for_pacu = input("Enter the AWS-CLI profile you want to use: \n")
        print("#################################")
        session_name = input("Enter the session name to start PACU: \n")
        time.sleep(1)
        print("#################################")
        print("List of categories: \n")
        print("""
category_enum
category_exploit
category_escalate
category_recon_unauth
category_exfil
category_lateral_move
category_evade
category_persist
        """)
        print("#################################")
        category = input("Enter the category you want to start in PACU: \n")
        print("#################################")
        run_pacu(profile_for_pacu, session_name, category)
        sys.exit(1)
    
    if "--prune-pacu" in sys.argv or "-prune-pacu" in sys.argv:
        print("#################################")
        print("Deleting session data from PACU framework")
        os.system("rm -rf ~/.local/share/pacu/*")
        print("#################################")

    if "--pacu-dash" in sys.argv or "-pacu-dash" in sys.argv:
        print("#################################")
        os.system("python3 -m http.server -d reports/")

    if "--full" in sys.argv or "-full" in sys.argv:
        print("Cleaning session data...\n")
        time.sleep(1)
        os.system("rm -rf ~/.local/share/pacu/*")
        print("#################################")
        profile_for_secbridge = input("Enter the AWS-CLI profile you want to use: \n")
        print("#################################")
        session_name = input("Enter the session name: \n")
        print("#################################")
        json_file_path = run_prowler(profile_for_secbridge)
        with open(f'{json_file_path}') as pr:
            risks = json.load(pr)
        # Starting enumeration with PACU
        category = "category_enum"
        run_pacu(profile_for_pacu, session_name, category)
        
    if "--np" in sys.argv or "-np" in sys.argv:
        print("#################################")
        print("Configuring a new profile for AWS-CLI...")
        time.sleep(1)
        print("#################################")
        configure_profile()
        sys.exit(1)

    if "--help" in sys.argv or "-help" in sys.argv:
        print("""
Usage: python secbridge.py [option]

Available options:
    --deps, -deps                   Check necessary dependencies (AWS-CLI, Python3, Prowler, and PACU)
    --prowler, -prowler             Start Prowler
    --prowler-dash, -prowler-dash   Start Prowler Dashboard
    --pacu, -pacu                   Start PACU Framework, specifying the category is required using --category
    --pacu-enum, -pacu-enum         Start PACU Framework in enumeration mode and generate a report
    --full, -full                   Start both Prowler and PACU framework, generating a report
    --prune-pacu, -prune-pacu       Remove PACU Framework session files
    --pacu-dash, -pacu-dash         Start the web server on port 8000
    --np, -np                       Configure a new profile in AWS CLI
""")
        sys.exit(1)
    
    print("No arguments provided, use --help to see the options")

if __name__ == "__main__":
    main()
