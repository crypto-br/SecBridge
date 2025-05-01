#!/usr/bin/env python3
"""
SecBridge v1.2
Integrates Prowler and Pacu for AWS security assessments.
Author: Luiz Machado (@cryptobr)
"""

import argparse
import logging
import sys
import time
import json
import os
import subprocess
import click
from pathlib import Path
import datetime
import colorlog

from utils.dependencies import check_deps
from utils.aws_config import configure_profile
from utils.prowler_runner import run_prowler
from utils.pacu_runner import run_pacu
from utils.pacu_report import generate_report

# Configuração do logging
def setup_logging():
    """
    Configure the logging system with colored formatting and file rotation.
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Log filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    log_file = log_dir / f"secbridge_{timestamp}.log"
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Console handler with colors
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)s: %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add new handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return log_file

def print_header():
    """
    Exibe o cabeçalho do SecBridge.
    """
    header = """
######################################################################
 __   __   __ 
.-----.-----.----.| |--.----.|__|.--| |.-----.-----.
|__ --| -__| __||  _  |   _||  |  |  |  -__|
|_____|_____|____||_____||__|  |__|  |_____||___ |_____| v1.2
      |_____|
Luiz Machado (@cryptobr)
######################################################################
"""
    print(header)

def run_command(command, description=""):
    """
    Execute a system command using subprocess.run with error handling.
    
    Args:
        command (list): List of strings representing the command and its arguments.
        description (str, optional): Description of the command for logging.
        
    Returns:
        dict: A dictionary containing the execution status and a descriptive message.
    """
    try:
        logging.info(f"Executing command: {' '.join(command)}")
        subprocess.run(command, check=True)
        return {"success": True, "message": f"{description} completed successfully."}
    except subprocess.CalledProcessError as e:
        error_msg = f"Error during {description}: {e}"
        logging.error(error_msg)
        return {"success": False, "message": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error during {description}: {e}"
        logging.error(error_msg)
        return {"success": False, "message": error_msg}

def prompt_input(prompt, cast_type=str, valid_options=None):
    """
    Prompt user input with validation.
    
    Args:
        prompt (str): The message to display to the user.
        cast_type (type, optional): The type to convert the input to. Defaults to str.
        valid_options (list, optional): List of valid options. Defaults to None.
        
    Returns:
        The value converted to the specified type.
    """
    while True:
        try:
            value = cast_type(input(prompt))
            if valid_options and value not in valid_options:
                print("Invalid option. Please try again.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please try again.")

@click.group()
def cli():
    """SecBridge: Integrates Prowler and Pacu for AWS security assessments."""
    print_header()
    pass

@cli.command()
def deps():
    """Checks required dependencies (AWS CLI, Python3, Prowler and PACU)."""
    logging.info("Checking dependencies...")
    result = check_deps()
    if result["success"]:
        logging.info(result["message"])
    else:
        logging.error(result["message"])

@cli.command()
def prowler():
    """Starts Prowler for security assessment."""
    logging.info("Starting Prowler...")
    profile = input("Enter the AWS-CLI profile you want to use: ").strip()
    result = run_prowler(profile)
    if result["success"]:
        logging.info(result["message"])
    else:
        logging.error(result["message"])

@cli.command()
def prowler_dash():
    """Starts the Prowler dashboard."""
    logging.info("Starting Prowler Dashboard...")
    result = run_command(["prowler", "dashboard"], "starting Prowler Dashboard")
    if result["success"]:
        logging.info(result["message"])
    else:
        logging.error(result["message"])

@cli.command()
def pacu_enum():
    """Starts PACU Framework in enumeration mode and generates a report."""
    logging.info("Cleaning PACU session data...")
    run_command(["rm", "-rf", os.path.expanduser("~/.local/share/pacu/*")],
                "cleaning PACU session")
    
    logging.info("Starting PACU in enumeration mode...")
    profile = input("Enter the AWS-CLI profile you want to use: ").strip()
    session_name = input("Enter the session name to start PACU: ").strip()
    category = "category_enum"
    
    result = run_pacu(profile, session_name, category)
    if result["success"]:
        logging.info("PACU executed successfully. Generating report...")
        report_result = generate_report(result["data"])
        if report_result["success"]:
            logging.info(f"Report generated successfully: {report_result['data']['html_report']}")
        else:
            logging.error(f"Error generating report: {report_result['message']}")
    else:
        logging.error(f"Error executing PACU: {result['message']}")

@cli.command()
def pacu():
    """Starts PACU Framework with specified category."""
    logging.info("Cleaning PACU session data...")
    run_command(["rm", "-rf", os.path.expanduser("~/.local/share/pacu/*")],
                "cleaning PACU session")
    
    profile = input("Enter the AWS-CLI profile you want to use: ").strip()
    session_name = input("Enter the session name to start PACU: ").strip()
    
    logging.info("Available categories:\n"
                 "category_enum, category_exploit, category_escalate, category_recon_unauth,\n"
                 "category_exfil, category_lateral_move, category_evade, category_persist")
    category = input("Enter the desired category to start PACU: ").strip()
    
    result = run_pacu(profile, session_name, category)
    if result["success"]:
        logging.info(result["message"])
    else:
        logging.error(result["message"])

@cli.command()
def prune_pacu():
    """Deletes PACU Framework session data."""
    logging.info("Deleting PACU session data...")
    result = run_command(["rm", "-rf", os.path.expanduser("~/.local/share/pacu/*")],
                "deleting PACU session")
    if result["success"]:
        logging.info("PACU session data deleted successfully.")
    else:
        logging.error(f"Error deleting PACU session data: {result['message']}")

@cli.command()
@click.option('--port', default=8000, help='Port for the HTTP server')
def pacu_dash(port):
    """Starts the PACU dashboard (HTTP server in the 'reports/' folder)."""
    reports_dir = Path("reports")
    if not reports_dir.exists():
        reports_dir.mkdir(parents=True)
    
    logging.info(f"Starting PACU Dashboard on port {port}...")
    result = run_command(["python3", "-m", "http.server", str(port), "-d", "reports/"],
                "starting PACU Dashboard")
    if result["success"]:
        logging.info(f"PACU Dashboard available at http://localhost:{port}/")
    else:
        logging.error(result["message"])

@cli.command()
def full():
    """Runs Prowler and PACU, generating a report."""
    logging.info("Cleaning PACU session data...")
    run_command(["rm", "-rf", os.path.expanduser("~/.local/share/pacu/*")],
                "cleaning PACU session")
    
    profile = input("Enter the AWS-CLI profile you want to use: ").strip()
    session_name = input("Enter the session name: ").strip()
    
    logging.info("Running Prowler...")
    prowler_result = run_prowler(profile)
    
    if prowler_result["success"]:
        logging.info("Prowler executed successfully.")
        json_file_path = prowler_result["data"]
        
        # If needed, load and process the JSON report generated by Prowler
        if os.path.exists(json_file_path):
            try:
                with open(json_file_path) as pr:
                    risks = json.load(pr)
                logging.info("Prowler risk data loaded.")
            except Exception as e:
                logging.warning(f"Error loading Prowler JSON report: {e}")
        else:
            logging.warning("Prowler JSON report not found.")
        
        # Start PACU in enumeration mode after Prowler
        logging.info("Starting PACU in enumeration mode...")
        category = "category_enum"
        pacu_result = run_pacu(profile, session_name, category)
        
        if pacu_result["success"]:
            logging.info("PACU executed successfully. Generating report...")
            report_result = generate_report(pacu_result["data"])
            if report_result["success"]:
                logging.info(f"Report generated successfully: {report_result['data']['html_report']}")
            else:
                logging.error(f"Error generating report: {report_result['message']}")
        else:
            logging.error(f"Error executing PACU: {pacu_result['message']}")
    else:
        logging.error(f"Error executing Prowler: {prowler_result['message']}")

@cli.command()
def np():
    """Configures a new profile in AWS CLI."""
    logging.info("Configuring a new profile for AWS CLI...")
    result = configure_profile()
    if result:
        logging.info("Profile configured successfully.")
    else:
        logging.error("Error configuring profile.")

def main():
    # Configurar logging
    log_file = setup_logging()
    logging.info(f"Log file: {log_file}")
    
    try:
        cli()
    except Exception as e:
        logging.error(f"Erro não tratado: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
