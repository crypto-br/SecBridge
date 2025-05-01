import os
import sys
import boto3
import configparser
import logging
from botocore.exceptions import ClientError

def configure_profile():
    """
    Configures a new profile in AWS CLI with credential validation.
    
    This function prompts the user for the necessary information to configure
    a new AWS profile, validates the credentials before saving them, and stores
    them securely in the AWS credentials file.
    
    Returns:
        bool: True if the profile was configured successfully, False otherwise.
    """
    print("Configuring new profile in AWS CLI...")
    profile_name = input("What is the profile name? ")
    access_key = input("Enter the Access Key: ")
    secret_key = input("Enter the Secret Key: ")
    region = input("What is the region? ")
    
    # Validate credentials before saving
    try:
        logging.info(f"Validating credentials for profile {profile_name}...")
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        sts = session.client('sts')
        identity = sts.get_caller_identity()  # Verify if credentials are valid
        account_id = identity['Account']
        logging.info(f"Credentials validated successfully for account {account_id}")
        
        # Save credentials securely
        config = configparser.ConfigParser()
        aws_credentials_path = os.path.expanduser("~/.aws/credentials")
        
        # Ensure ~/.aws directory exists
        os.makedirs(os.path.dirname(aws_credentials_path), exist_ok=True)
        
        # Read existing configuration, if any
        if os.path.exists(aws_credentials_path):
            config.read(aws_credentials_path)
        
        if profile_name not in config:
            config[profile_name] = {}
        
        config[profile_name]['aws_access_key_id'] = access_key
        config[profile_name]['aws_secret_access_key'] = secret_key
        
        # Configure region in config file
        aws_config_path = os.path.expanduser("~/.aws/config")
        config_parser = configparser.ConfigParser()
        
        if os.path.exists(aws_config_path):
            config_parser.read(aws_config_path)
        
        profile_section = f"profile {profile_name}" if profile_name != "default" else "default"
        if profile_section not in config_parser:
            config_parser[profile_section] = {}
        
        config_parser[profile_section]['region'] = region
        
        # Save configurations
        with open(aws_credentials_path, 'w') as credfile:
            config.write(credfile)
            
        with open(aws_config_path, 'w') as conffile:
            config_parser.write(conffile)
            
        print(f"Profile {profile_name} configured successfully for account {account_id}.")
        return True
        
    except ClientError as e:
        logging.error(f"Error validating AWS credentials: {e}")
        print(f"Error: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during profile configuration: {e}")
        print(f"Unexpected error: {e}")
        return False
