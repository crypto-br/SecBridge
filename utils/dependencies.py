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
    Verifica as dependências necessárias e instala as que estiverem ausentes.
    
    Returns:
        dict: Um dicionário contendo o status da verificação e uma mensagem descritiva.
    """
    # Configurar logging
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
    
    logging.info("Verificando dependências do SecBridge...")
    
    # Detectar o sistema operacional
    os_type = detect_os()
    if os_type in ["Debian", "RedHat"]:
        package_manager = "apt-get" if os_type == "Debian" else "yum"
    elif os_type == "macOS":
        package_manager = "brew"
    else:
        logging.error("Sistema operacional não suportado.")
        return {"success": False, "message": "Sistema operacional não suportado."}
    
    # Lista de dependências para verificar
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
    
    # Verificar cada dependência
    missing_deps = []
    for dep in dependencies:
        if not command_exists(dep["command"]):
            logging.info(f"{dep['name']} não está instalado.")
            missing_deps.append(dep)
        else:
            logging.info(f"{dep['name']} já está instalado. [OK]")
    
    # Se houver dependências ausentes, perguntar ao usuário se deseja instalá-las
    if missing_deps:
        logging.info(f"Encontradas {len(missing_deps)} dependências ausentes.")
        
        for dep in missing_deps:
            if dep["required"]:
                if ask_user(f"Deseja instalar {dep['name']}? [1] sim / [2] não: ") == 1:
                    try:
                        # Converter a lista de comandos em uma string para execução
                        install_cmd = " ".join(dep["install_commands"][package_manager])
                        logging.info(f"Instalando {dep['name']}...")
                        
                        # Executar o comando de instalação
                        result = subprocess.run(install_cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        
                        # Verificar se a instalação foi bem-sucedida
                        if command_exists(dep["command"]):
                            logging.info(f"{dep['name']} instalado com sucesso.")
                        else:
                            logging.error(f"Falha ao instalar {dep['name']}. Por favor, instale manualmente.")
                            return {"success": False, "message": f"Falha ao instalar {dep['name']}. Por favor, instale manualmente."}
                    except subprocess.CalledProcessError as e:
                        logging.error(f"Erro durante a instalação de {dep['name']}: {e}")
                        logging.error(f"Saída de erro: {e.stderr}")
                        return {"success": False, "message": f"Erro durante a instalação de {dep['name']}: {e}"}
                else:
                    logging.error(f"A instalação de {dep['name']} é obrigatória. Encerrando.")
                    return {"success": False, "message": f"A instalação de {dep['name']} é obrigatória."}
    
    # Verificar se todas as dependências estão instaladas agora
    all_deps_installed = all(command_exists(dep["command"]) for dep in dependencies)
    
    if all_deps_installed:
        logging.info("Todas as dependências estão instaladas corretamente.")
        return {"success": True, "message": "Todas as dependências estão instaladas corretamente."}
    else:
        logging.error("Algumas dependências ainda estão faltando. Por favor, instale-as manualmente.")
        return {"success": False, "message": "Algumas dependências ainda estão faltando. Por favor, instale-as manualmente."}

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
    Solicita uma entrada ao usuário e retorna um inteiro (1 ou 2).
    
    Args:
        prompt (str): A mensagem a ser exibida ao usuário.
        
    Returns:
        int: 1 para sim, 2 para não.
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
    
    Returns:
        str: "Debian", "RedHat", "macOS" ou None se não for suportado.
    """
    os_info = platform.system()
    if os_info == "Linux":
        try:
            distro = subprocess.check_output(["lsb_release", "-is"], text=True).strip().lower()
            if distro in ["debian", "ubuntu", "linuxmint", "pop"]:
                return "Debian"
            elif distro in ["centos", "redhat", "fedora", "amazon", "rhel"]:
                return "RedHat"
            else:
                logging.error(f"Distribuição Linux não suportada: {distro}")
                return None
        except subprocess.CalledProcessError:
            # Tentar método alternativo para detectar a distribuição
            try:
                if os.path.exists("/etc/debian_version"):
                    return "Debian"
                elif os.path.exists("/etc/redhat-release"):
                    return "RedHat"
                else:
                    logging.error("Não foi possível determinar a distribuição Linux.")
                    return None
            except Exception as e:
                logging.error(f"Erro ao detectar a distribuição Linux: {e}")
                return None
    elif os_info == "Darwin":
        return "macOS"
    else:
        logging.error(f"Sistema operacional não suportado: {os_info}")
        return None

def run_command(command, description=""):
    """
    Executa um comando no sistema utilizando subprocess.run com verificação de erros.
    
    Args:
        command (list): Lista de strings representando o comando e seus argumentos.
        description (str, optional): Descrição do comando para logging.
        
    Returns:
        subprocess.CompletedProcess: O resultado da execução do comando.
        
    Raises:
        subprocess.CalledProcessError: Se o comando falhar.
    """
    try:
        logging.info(f"Executando comando: {' '.join(command)}")
        return subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Erro durante {description}: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    check_deps()

