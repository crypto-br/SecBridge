#!/usr/bin/env python3
"""
SecBridge v1.1
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

from utils.dependencies import check_deps
from utils.aws_config import configure_profile
from utils.prowler_runner import run_prowler
from utils.pacu_runner import run_pacu
from utils.pacu_report import generate_report

def print_header():
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
    """
    try:
        logging.info("Executing command: %s", ' '.join(command))
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        logging.error("Error during %s: %s", description, e)
        sys.exit(1)

def prompt_input(prompt, cast_type=str, valid_options=None):
    """
    Prompt user input with validation.
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

def main():
    # Configuração do logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    parser = argparse.ArgumentParser(
        description="SecBridge: Integrates Prowler and Pacu for AWS security assessments."
    )
    parser.add_argument('--deps', action='store_true',
                        help="Verifica as dependências necessárias (AWS CLI, Python3, Prowler e PACU).")
    parser.add_argument('--prowler', action='store_true',
                        help="Inicia o Prowler para avaliação de segurança.")
    parser.add_argument('--prowler-dash', action='store_true',
                        help="Inicia o dashboard do Prowler.")
    parser.add_argument('--pacu-enum', action='store_true',
                        help="Inicia o PACU Framework no modo enumeração e gera um relatório.")
    parser.add_argument('--pacu', action='store_true',
                        help="Inicia o PACU Framework com categoria informada.")
    parser.add_argument('--full', action='store_true',
                        help="Executa Prowler e PACU, gerando relatório.")
    parser.add_argument('--prune-pacu', action='store_true',
                        help="Exclui os dados de sessão do PACU Framework.")
    parser.add_argument('--pacu-dash', action='store_true',
                        help="Inicia o dashboard do PACU (servidor HTTP na pasta 'reports/').")
    parser.add_argument('--np', action='store_true',
                        help="Configura um novo perfil no AWS CLI.")
    
    args = parser.parse_args()

    print_header()
    
    if args.deps:
        logging.info("Verificando dependências...")
        check_deps()
        sys.exit(0)

    if args.prowler:
        logging.info("Iniciando o Prowler...")
        profile = input("Digite o perfil do AWS-CLI que deseja utilizar: ").strip()
        run_prowler(profile)
        sys.exit(0)

    if args.prowler_dash:
        logging.info("Iniciando o Dashboard do Prowler...")
        run_command(["prowler", "dashboard"], description="iniciando Dashboard do Prowler")
        sys.exit(0)

    if args.pacu_enum:
        logging.info("Limpando dados de sessão do PACU...")
        run_command(["rm", "-rf", os.path.expanduser("~/.local/share/pacu/*")],
                    description="limpeza de sessão do PACU")
        logging.info("Iniciando o PACU em modo enumeração...")
        profile = input("Digite o perfil do AWS-CLI que deseja utilizar: ").strip()
        session_name = input("Digite o nome da sessão para iniciar o PACU: ").strip()
        category = "category_enum"
        run_pacu(profile, session_name, category)
        logging.info("Gerando relatório...")
        generate_report()
        logging.info("Relatório disponível no dashboard do PACU.")
        sys.exit(0)

    if args.pacu:
        logging.info("Limpando dados de sessão do PACU...")
        run_command(["rm", "-rf", os.path.expanduser("~/.local/share/pacu/*")],
                    description="limpeza de sessão do PACU")
        profile = input("Digite o perfil do AWS-CLI que deseja utilizar: ").strip()
        session_name = input("Digite o nome da sessão para iniciar o PACU: ").strip()
        logging.info("Categorias disponíveis:\n"
                     "category_enum, category_exploit, category_escalate, category_recon_unauth,\n"
                     "category_exfil, category_lateral_move, category_evade, category_persist")
        category = input("Digite a categoria desejada para iniciar o PACU: ").strip()
        run_pacu(profile, session_name, category)
        sys.exit(0)

    if args.prune_pacu:
        logging.info("Excluindo dados de sessão do PACU...")
        run_command(["rm", "-rf", os.path.expanduser("~/.local/share/pacu/*")],
                    description="exclusão de sessão do PACU")
        sys.exit(0)

    if args.pacu_dash:
        logging.info("Iniciando o Dashboard do PACU na porta 8000...")
        run_command(["python3", "-m", "http.server", "8000", "-d", "reports/"],
                    description="iniciando Dashboard do PACU")
        sys.exit(0)

    if args.full:
        logging.info("Limpando dados de sessão do PACU...")
        run_command(["rm", "-rf", os.path.expanduser("~/.local/share/pacu/*")],
                    description="limpeza de sessão do PACU")
        profile = input("Digite o perfil do AWS-CLI que deseja utilizar: ").strip()
        session_name = input("Digite o nome da sessão: ").strip()
        logging.info("Executando o Prowler...")
        json_file_path = run_prowler(profile)
        # Se necessário, carregar e processar o relatório JSON gerado pelo Prowler
        if os.path.exists(json_file_path):
            with open(json_file_path) as pr:
                risks = json.load(pr)
            logging.info("Dados de risco do Prowler carregados.")
        else:
            logging.warning("Relatório JSON do Prowler não encontrado.")
        # Inicia o PACU em modo enumeração após o Prowler
        category = "category_enum"
        run_pacu(profile, session_name, category)
        sys.exit(0)

    if args.np:
        logging.info("Configurando um novo perfil para o AWS CLI...")
        configure_profile()
        sys.exit(0)

    parser.print_help()

if __name__ == "__main__":
    main()
