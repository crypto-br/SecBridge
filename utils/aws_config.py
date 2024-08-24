import os
import sys

def configurar_perfil():
    print("Configurando novo perfil no AWS CLI...")
    profile_name = input("Qual o nome do profile? ")
    access_key = input("Informe a Access Key: ")
    secret_key = input("Informe a Secret Key: ")
    region = input("Qual a região? ")
    
    os.system(f"aws configure set aws_access_key_id {access_key} --profile {profile_name}")
    os.system(f"aws configure set aws_secret_access_key {secret_key} --profile {profile_name}")
    os.system(f"aws configure set region {region} --profile {profile_name}")
    sys.exit(1)
