#!/usr/bin/env python3
"""
SecBridge v1.1.1
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
    Configura o sistema de logging com formatação colorida e rotação de arquivos.
    """
    # Criar diretório para logs se não existir
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Nome do arquivo de log com timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    log_file = log_dir / f"secbridge_{timestamp}.log"
    
    # Handler para arquivo
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Handler para console com cores
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
    
    # Configurar o logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Remover handlers existentes
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Adicionar os novos handlers
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
|_____|_____|____||_____||__|  |__|  |_____||___ |_____| v1.1.1
      |_____|
Luiz Machado (@cryptobr)
######################################################################
"""
    print(header)

def run_command(command, description=""):
    """
    Execute a system command using subprocess.run with error handling.
    
    Args:
        command (list): Lista de strings representando o comando e seus argumentos.
        description (str, optional): Descrição do comando para logging.
        
    Returns:
        dict: Um dicionário contendo o status da execução e uma mensagem descritiva.
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
        prompt (str): A mensagem a ser exibida ao usuário.
        cast_type (type, optional): O tipo para converter a entrada. Defaults to str.
        valid_options (list, optional): Lista de opções válidas. Defaults to None.
        
    Returns:
        O valor convertido para o tipo especificado.
    """
    while True:
        try:
            value = cast_type(input(prompt))
            if valid_options and value not in valid_options:
                print("Opção inválida. Tente novamente.")
                continue
            return value
        except ValueError:
            print("Entrada inválida. Por favor, tente novamente.")

@click.group()
def cli():
    """SecBridge: Integrates Prowler and Pacu for AWS security assessments."""
    print_header()
    pass

@cli.command()
def deps():
    """Verifica as dependências necessárias (AWS CLI, Python3, Prowler e PACU)."""
    logging.info("Verificando dependências...")
    result = check_deps()
    if result["success"]:
        logging.info(result["message"])
    else:
        logging.error(result["message"])

@cli.command()
def prowler():
    """Inicia o Prowler para avaliação de segurança."""
    logging.info("Iniciando o Prowler...")
    profile = input("Digite o perfil do AWS-CLI que deseja utilizar: ").strip()
    result = run_prowler(profile)
    if result["success"]:
        logging.info(result["message"])
    else:
        logging.error(result["message"])

@cli.command()
def prowler_dash():
    """Inicia o dashboard do Prowler."""
    logging.info("Iniciando o Dashboard do Prowler...")
    result = run_command(["prowler", "dashboard"], "iniciando Dashboard do Prowler")
    if result["success"]:
        logging.info(result["message"])
    else:
        logging.error(result["message"])

@cli.command()
def pacu_enum():
    """Inicia o PACU Framework no modo enumeração e gera um relatório."""
    logging.info("Limpando dados de sessão do PACU...")
    run_command(["rm", "-rf", os.path.expanduser("~/.local/share/pacu/*")],
                "limpeza de sessão do PACU")
    
    logging.info("Iniciando o PACU em modo enumeração...")
    profile = input("Digite o perfil do AWS-CLI que deseja utilizar: ").strip()
    session_name = input("Digite o nome da sessão para iniciar o PACU: ").strip()
    category = "category_enum"
    
    result = run_pacu(profile, session_name, category)
    if result["success"]:
        logging.info("PACU executado com sucesso. Gerando relatório...")
        report_result = generate_report(result["data"])
        if report_result["success"]:
            logging.info(f"Relatório gerado com sucesso: {report_result['data']['html_report']}")
        else:
            logging.error(f"Erro ao gerar relatório: {report_result['message']}")
    else:
        logging.error(f"Erro ao executar PACU: {result['message']}")

@cli.command()
def pacu():
    """Inicia o PACU Framework com categoria informada."""
    logging.info("Limpando dados de sessão do PACU...")
    run_command(["rm", "-rf", os.path.expanduser("~/.local/share/pacu/*")],
                "limpeza de sessão do PACU")
    
    profile = input("Digite o perfil do AWS-CLI que deseja utilizar: ").strip()
    session_name = input("Digite o nome da sessão para iniciar o PACU: ").strip()
    
    logging.info("Categorias disponíveis:\n"
                 "category_enum, category_exploit, category_escalate, category_recon_unauth,\n"
                 "category_exfil, category_lateral_move, category_evade, category_persist")
    category = input("Digite a categoria desejada para iniciar o PACU: ").strip()
    
    result = run_pacu(profile, session_name, category)
    if result["success"]:
        logging.info(result["message"])
    else:
        logging.error(result["message"])

@cli.command()
def prune_pacu():
    """Exclui os dados de sessão do PACU Framework."""
    logging.info("Excluindo dados de sessão do PACU...")
    result = run_command(["rm", "-rf", os.path.expanduser("~/.local/share/pacu/*")],
                "exclusão de sessão do PACU")
    if result["success"]:
        logging.info("Dados de sessão do PACU excluídos com sucesso.")
    else:
        logging.error(f"Erro ao excluir dados de sessão do PACU: {result['message']}")

@cli.command()
@click.option('--port', default=8000, help='Porta para o servidor HTTP')
def pacu_dash(port):
    """Inicia o dashboard do PACU (servidor HTTP na pasta 'reports/')."""
    reports_dir = Path("reports")
    if not reports_dir.exists():
        reports_dir.mkdir(parents=True)
    
    logging.info(f"Iniciando o Dashboard do PACU na porta {port}...")
    result = run_command(["python3", "-m", "http.server", str(port), "-d", "reports/"],
                "iniciando Dashboard do PACU")
    if result["success"]:
        logging.info(f"Dashboard do PACU disponível em http://localhost:{port}/")
    else:
        logging.error(result["message"])

@cli.command()
def full():
    """Executa Prowler e PACU, gerando relatório."""
    logging.info("Limpando dados de sessão do PACU...")
    run_command(["rm", "-rf", os.path.expanduser("~/.local/share/pacu/*")],
                "limpeza de sessão do PACU")
    
    profile = input("Digite o perfil do AWS-CLI que deseja utilizar: ").strip()
    session_name = input("Digite o nome da sessão: ").strip()
    
    logging.info("Executando o Prowler...")
    prowler_result = run_prowler(profile)
    
    if prowler_result["success"]:
        logging.info("Prowler executado com sucesso.")
        json_file_path = prowler_result["data"]
        
        # Se necessário, carregar e processar o relatório JSON gerado pelo Prowler
        if os.path.exists(json_file_path):
            try:
                with open(json_file_path) as pr:
                    risks = json.load(pr)
                logging.info("Dados de risco do Prowler carregados.")
            except Exception as e:
                logging.warning(f"Erro ao carregar relatório JSON do Prowler: {e}")
        else:
            logging.warning("Relatório JSON do Prowler não encontrado.")
        
        # Inicia o PACU em modo enumeração após o Prowler
        logging.info("Iniciando o PACU em modo enumeração...")
        category = "category_enum"
        pacu_result = run_pacu(profile, session_name, category)
        
        if pacu_result["success"]:
            logging.info("PACU executado com sucesso. Gerando relatório...")
            report_result = generate_report(pacu_result["data"])
            if report_result["success"]:
                logging.info(f"Relatório gerado com sucesso: {report_result['data']['html_report']}")
            else:
                logging.error(f"Erro ao gerar relatório: {report_result['message']}")
        else:
            logging.error(f"Erro ao executar PACU: {pacu_result['message']}")
    else:
        logging.error(f"Erro ao executar Prowler: {prowler_result['message']}")

@cli.command()
def np():
    """Configura um novo perfil no AWS CLI."""
    logging.info("Configurando um novo perfil para o AWS CLI...")
    result = configure_profile()
    if result:
        logging.info("Perfil configurado com sucesso.")
    else:
        logging.error("Erro ao configurar o perfil.")

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
