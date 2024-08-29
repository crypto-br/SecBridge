import os
import sys

def configure_profile():
    print("Configuring new profile in AWS CLI...")
    profile_name = input("What is the profile name? ")
    access_key = input("Enter the Access Key: ")
    secret_key = input("Enter the Secret Key: ")
    region = input("What is the region? ")
    
    os.system(f"aws configure set aws_access_key_id {access_key} --profile {profile_name}")
    os.system(f"aws configure set aws_secret_access_key {secret_key} --profile {profile_name}")
    os.system(f"aws configure set region {region} --profile {profile_name}")
    sys.exit(1)
