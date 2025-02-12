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

def check_deps():
    """
    Verifica as dependências necessárias e instala as que estiverem ausentes.
    """
    os_type = detect_os()
    if os_type in ["Debian", "RedHat"]:
        package_manager = "apt-get" if os_type == "Debian" else "yum"
    elif os_type == "macOS":
        package_manager = "brew"
    else:
        logging.error("Sistema operacional não suportado.")
        sys.exit(1)
    
    # Verificação do AWS CLI
    if not command_exists("aws"):
        logging.info("AWS CLI não está instalado.")
        if ask_user("Deseja instalar o AWS CLI? [1] sim / [2] não: ") == 1:
            if package_manager in ["apt-get", "yum"]:
                run_command(["sudo", package_manager, "update", "-y"], "atualizando a lista de pacotes")
                run_command(["sudo", package_manager, "install", "-y", "awscli"], "instalando o AWS CLI")
            elif package_manager == "brew":
                run_command(["brew", "install", "awscli"], "instalando o AWS CLI")
            logging.info("AWS CLI instalado com sucesso.")
        else:
            logging.error("A instalação do AWS CLI é obrigatória. Encerrando.")
            sys.exit(1)
    else:
        logging.info("AWS CLI já está instalado. [OK]")

    # Verificação do Python3
    if not command_exists("python3"):
        logging.info("Python3 não está instalado.")
        if ask_user("Deseja instalar o Python3? [1] sim / [2] não: ") == 1:
            if package_manager in ["apt-get", "yum"]:
                run_command(["sudo", package_manager, "update", "-y"], "atualizando a lista de pacotes")
                run_command(["sudo", package_manager, "install", "-y", "python3"], "instalando o Python3")
            elif package_manager == "brew":
                run_command(["brew", "install", "python3"], "instalando o Python3")
            logging.info("Python3 instalado com sucesso.")
        else:
            logging.error("A instalação do Python3 é necessária. Encerrando.")
            sys.exit(1)
    else:
        logging.info("Python3 já está instalado. [OK]")

    # Verificação do Prowler
    if not command_exists("prowler"):
        logging.info("Prowler não está instalado.")
        if ask_user("Deseja instalar o Prowler? [1] sim / [2] não: ") == 1:
            if package_manager in ["apt-get", "yum"]:
                run_command(["sudo", package_manager, "update", "-y"], "atualizando a lista de pacotes")
                run_command(["sudo", package_manager, "install", "-y", "pipx"], "instalando o pipx")
                run_command(["sudo", "pipx", "ensurepath"], "configurando pipx")
                run_command(["sudo", "pipx", "install", "prowler"], "instalando o Prowler")
            elif package_manager == "brew":
                run_command(["brew", "install", "pipx"], "instalando o pipx")
                run_command(["pipx", "ensurepath"], "configurando pipx")
                run_command(["pipx", "install", "prowler"], "instalando o Prowler")
            logging.info("Prowler instalado com sucesso.")
        else:
            logging.error("A instalação do Prowler é obrigatória. Encerrando.")
            sys.exit(1)
    else:
        logging.info("Prowler já está instalado. [OK]")

    # Verificação do PACU Framework
    if not command_exists("pacu"):
        logging.info("PACU Framework não está instalado.")
        if ask_user("Deseja instalar o PACU Framework? [1] sim / [2] não: ") == 1:
            logging.info("Instalando o PACU Framework...")
            run_command(["python3", "-m", "pip", "install", "-U", "pacu"], "instalando o PACU Framework")
            logging.info("PACU Framework instalado com sucesso.")
        else:
            logging.error("A instalação do PACU Framework é obrigatória. Encerrando.")
            sys.exit(1)
    else:
        logging.info("PACU Framework já está instalado. [OK]")

def command_exists(command):
    """
    Verifica se um comando existe no sistema.
    """
    result = subprocess.run(["which", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

def ask_user(prompt):
    """
    Solicita uma entrada ao usuário e retorna um inteiro (1 ou 2).
    """
    while True:
        try:
            choice = int(input(prompt))
            if choice in [1, 2]:
                return choice
            else:
                print("Por favor, escolha [1] ou [2].")
        except ValueError:
            print("Entrada inválida. Por favor, insira 1 ou 2.")

def detect_os():
    """
    Detecta o sistema operacional e retorna um identificador.
    """
    os_info = platform.system()
    if os_info == "Linux":
        try:
            distro = subprocess.check_output(["lsb_release", "-is"], text=True).strip().lower()
            if distro in ["debian", "ubuntu"]:
                return "Debian"
            elif distro in ["centos", "redhat", "fedora", "amazon"]:
                return "RedHat"
            else:
                logging.error("Distribuição Linux não suportada: %s", distro)
                sys.exit(1)
        except subprocess.CalledProcessError:
            logging.error("Não foi possível determinar a distribuição Linux usando lsb_release.")
            sys.exit(1)
    elif os_info == "Darwin":
        return "macOS"
    else:
        logging.error("Sistema operacional não suportado: %s", os_info)
        sys.exit(1)

def run_command(command, description=""):
    """
    Executa um comando no sistema utilizando subprocess.run com verificação de erros.
    """
    try:
        logging.info("Executando comando: %s", ' '.join(command))
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        logging.error("Erro durante %s: %s", description, e)
        sys.exit(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    check_deps()

