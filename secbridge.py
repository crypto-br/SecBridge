from utils.dependencies import verificar_deps
from utils.aws_config import configurar_perfil
from utils.prowler_runner import run_prowler
from utils.pacu_runner import run_pacu
from utils.pacu_report import gerar_relatorio
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
    # Condicionais dos parametros
    if "--deps" in sys.argv or "-deps" in sys.argv:
        print("#################################")
        print("Verificando Dependências...")
        print("#################################")
        time.sleep(1)
        verificar_deps()
        sys.exit(1)

    if "--prowler" in sys.argv or "-prowler" in sys.argv:
        print("#################################")
        print("Iniciando o Prowler...")
        time.sleep(1)
        print("#################################")
        profile_for_prowler = input("Informe o profile do AWS-CLI que deseja utilizar: \n")
        print("#################################")
        run_prowler(profile_for_prowler)
        sys.exit(1)

    if "--prowler-dash" in sys.argv or "-prowler-dash" in sys.argv:
        print("#################################")
        print("Iniciando o Prowler Dashboad...")
        time.sleep(1)
        print("#################################")
        os.system("prowler dashboard")
        print("#################################")
        sys.exit(1)

    if "--pacu-enum" in sys.argv or "-pacu-enum" in sys.argv:
        print("#################################")
        print("Limpados dados de sessoes....")
        time.sleep(1)
        os.system("rm -rf ~/.local/share/pacu/*")
        print("#################################")
        print("Iniciando o Pacu framework em modo de enumreração...")
        time.sleep(1)
        print("#################################")
        profile_for_pacu = input("Informe o profile do AWS-CLI que deseja utilizar: \n")
        session_name = input("Informe o nome da sessao para iniciar o PACU: \n")
        category = "category_enum"
        run_pacu(profile_for_pacu, session_name, category)
        print("#################################")
        print("Gerando relatorio...")
        gerar_relatorio()
        time.sleep(1)
        print("Relatorio disponivel em --pacu-dash")
        print("#################################")
        
        sys.exit(1)

    if "--pacu" in sys.argv or "-pacu" in sys.argv:
        print("#################################")
        print("Limpados dados de sessoes....")
        time.sleep(1)
        print("#################################")
        os.system("rm -rf ~/.local/share/pacu/*")
        time.sleep(1)
        profile_for_pacu = input("Informe o profile do AWS-CLI que deseja utilizar: \n")
        print("#################################")
        session_name = input("Informe o nome da sessao para iniciar o PACU: \n")
        time.sleep(1)
        print("#################################")
        print("Lista de categorias: \n")
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
        category = input("Informe a categoria que deseja iniciar no PACU: \n")
        print("#################################")
        run_pacu(profile_for_pacu, session_name, category)
        sys.exit(1)
    
    if "--prune-pacu" in sys.argv or "-prune-pacu" in sys.argv:
        print("#################################")
        print("Deletando dados das sessões do pacu framework")
        os.system("rm -rf ~/.local/share/pacu/*")
        print("#################################")

    if "--pacu-dash" in sys.argv or "-pacu-dash" in sys.argv:
        print("#################################")
        os.system("python3 -m http.server -d reports/")

    if "--full" in sys.argv or "-full" in sys.argv:
        print("Limpados dados de sessoes....\n")
        time.sleep(1)
        os.system("rm -rf ~/.local/share/pacu/*")
        print("#################################")
        profile_for_secbridge = input("Informe o profile do AWS-CLI que deseja utilizar: \n")
        print("#################################")
        session_name = input("Informe o nome da sessao: \n")
        print("#################################")
        json_file_path = run_prowler(profile_for_secbridge)
        with open(f'{json_file_path}') as pr:
            risks = json.load(pr)
        # Iniciando enumeração com PACU
        category = "category_enum"
        run_pacu(profile_for_pacu, session_name, category)
        
    if "--np" in sys.argv or "-np" in sys.argv:
        print("#################################")
        print("Configurando um novo profile para o AWS-CLI...")
        time.sleep(1)
        print("#################################")
        configurar_perfil()
        sys.exit(1)

    if "--help" in sys.argv or "-help" in sys.argv:
        print("""
Utilização: python secbridge.py [opção]

Opções disponiveis:
    --deps, -deps                   Verifica dependências necessárias (AWS-CLI, Python3, Prowler e PACU)
    --prowler, -prowler             Inicia o Prowler
    --prowler-dash, -prowler-dash   Inicia o Prowler Dashboard
    --pacu, -pacu                   Inicia o PACU Framework informando a categoria  é necessário infromar --category
    --pacu-enum, -pacu-enum         Inicia o PACU Framework em modo de enumeração e gera um relatrorio
    --full, -full                   Inicia o prowler e o pacu framework gerando relatorio
    --prune-pacu, -prune-pacu       Remove arquivos de sessão do PACU Framework
    --pacu-dash, -pacu-dash         Inicia o servidor web na porta 8000
    --np, -np                       Configura um novo perfil no AWS CLI
""")
        sys.exit(1)
    
    print("sem argumentos, utilize o --help para ver as opções")

if __name__ == "__main__":
    main()
