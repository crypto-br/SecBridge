import subprocess
import sys
import os

def verificar_deps():
    # AWS CLI
    if not command_exists("aws"):
        print("AWS CLI não está instalado.")
        if ask_user("Deseja instalar? [1] sim / [2] não \n") == 1:
            subprocess.run(["sudo", "apt-get", "update"])
            subprocess.run(["sudo", "apt-get", "install", "-y", "awscli"])
            print("AWS CLI instalado com sucesso.")
        else:
            print("Saindo do script.")
            sys.exit(1)
    else:
        print("AWS CLI já está instalado. [OK]")
    
    # Python3
    if not command_exists("python3"):
        print("Python3 não está instalado.")
        if ask_user("Deseja instalar? [1] sim / [2] não \n") == 1:
            subprocess.run(["sudo", "apt-get", "update"])
            subprocess.run(["sudo", "apt-get", "install", "-y", "python3"])
            print("Python3 instalado com sucesso.")
        else:
            print("Instalação é necessária. Saindo.")
            sys.exit(1)
    else:
        print("Python3 já está instalado. [OK]")
    
    # Prowler
    if not command_exists("prowler"):
        print("Prowler não está instalado.")
        if ask_user("Deseja instalar? [1] sim / [2] não \n") == 1:
            subprocess.run(["sudo", "apt-get", "update"])
            subprocess.run(["sudo", "apt-get", "install", "-y", "prowler"])
            print("Prowler instalado com sucesso.")
        else:
            print("Instalação é necessária. Saindo.")
            sys.exit(1)
    else:
        print("Prowler já está instalado. [OK]")

    # PACU Framework
    if not command_exists("pacu"):
        print("PACU Framework não está instalado.")
        if ask_user("Deseja instalar? [1] sim / [2] não \n") == 1:
            print("Instalando o PACU Framework...")
            os.system("git clone https://github.com/RhinoSecurityLabs/pacu.git")
            os.system("cd pacu && ./install.sh")
            print("PACU Framework instalado com sucesso.")
        else:
            print("Instalação do PACU Framework é necessária. Saindo.")
            sys.exit(1)
    else:
        print("PACU Framework já está instalado. [OK]")

def command_exists(command):
    return subprocess.call(f"type {command}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

def ask_user(prompt):
    return int(input(prompt))
