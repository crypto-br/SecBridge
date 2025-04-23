import os
import subprocess
import json
import logging
from pathlib import Path

def load_module_categories():
    """
    Carrega as categorias de módulos do Pacu de um arquivo de configuração.
    
    Returns:
        dict: Um dicionário contendo as categorias de módulos do Pacu.
    """
    config_path = Path("config/pacu_modules.json")
    try:
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            logging.warning(f"Configuration file {config_path} not found. Using default categories.")
            # Retornar um dicionário vazio que será preenchido com as categorias padrão
            return {}
    except Exception as e:
        logging.error(f"Error loading module categories: {e}")
        return {}

def execute_pacu_module(session_name, module_name, profile, args=None):
    """
    Executa um módulo específico do Pacu.
    
    Args:
        session_name (str): Nome da sessão do Pacu.
        module_name (str): Nome do módulo a ser executado.
        profile (str): Nome do perfil AWS CLI a ser usado.
        args (str, optional): Argumentos adicionais para o módulo.
        
    Returns:
        dict: Um dicionário contendo o nome do módulo, a saída padrão e a saída de erro.
    """
    cmd = ['pacu', '--session', session_name, '--exec', '--module-name', module_name, '--import-keys', profile]
    if args:
        cmd.extend(['--module-args', args])
    
    logging.info(f"Executing Pacu module: {module_name}")
    logging.debug(f"Command: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            stdin=subprocess.PIPE, 
            text=True
        )
        stdout, stderr = process.communicate(input="y\n")  # Responde "Y" para qualquer prompt de confirmação
        
        if "AccessDeniedException" in stderr:
            stderr = "Module cannot be executed due to lack of permission"
            
        return {
            "module": module_name,
            "stdout": stdout,
            "stderr": stderr,
            "status": "success" if process.returncode == 0 else "error",
            "return_code": process.returncode
        }
    except Exception as e:
        logging.error(f"Error executing Pacu module {module_name}: {e}")
        return {
            "module": module_name,
            "stdout": "",
            "stderr": str(e),
            "status": "error",
            "return_code": -1
        }

def run_pacu(profile_for_pacu, session_name, category):
    """
    Executa o Pacu Framework com base na categoria especificada.
    
    Args:
        profile_for_pacu (str): Nome do perfil AWS CLI a ser usado.
        session_name (str): Nome da sessão do Pacu.
        category (str): Categoria de módulos a ser executada.
        
    Returns:
        dict: Um dicionário contendo o status da execução, os resultados e uma mensagem descritiva.
    """
    print(f"Running PACU Framework with profile {profile_for_pacu}, session {session_name}, category {category}")
    logging.info(f"Running PACU Framework with profile {profile_for_pacu}, session {session_name}, category {category}")
    
    # Configurar o perfil AWS
    os.environ['AWS_PROFILE'] = profile_for_pacu
    
    # Carregar categorias de módulos
    categories = load_module_categories()
    
    # Se o arquivo de configuração não existir ou estiver vazio, usar as categorias padrão
    if not categories:
        logging.warning("Using default module categories")
        # Definir categorias padrão aqui se necessário
    
    # Lista para armazenar resultados
    results = []
    
    # Verificar se a sessão já existe e está ativa, ou criar uma nova sessão
    try:
        logging.info(f"Activating Pacu session: {session_name}")
        activate_session_command = ['pacu', '--session', session_name]
        subprocess.run(activate_session_command, check=True, capture_output=True)
        logging.info(f"Session {session_name} activated")
    except subprocess.CalledProcessError:
        logging.info(f"Creating new Pacu session: {session_name}")
        create_session_command = ['pacu', '--new-session', session_name]
        subprocess.run(create_session_command, check=True, capture_output=True)
        logging.info(f"Session {session_name} created")
    
    # Criar diretório para relatórios se não existir
    reports_dir = Path("reports/data")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Executar módulos com base na categoria
    if category == "category_enum":
        modules_to_run = categories.get("category_enum", [])
        special_modules = categories.get("special_modules", {})
        
        for module_name in modules_to_run:
            if module_name in special_modules:
                # Módulos especiais que não precisam de argumentos de região
                result = execute_pacu_module(session_name, module_name, profile_for_pacu)
            elif module_name == "iam__enum_action_query":
                logging.info("Skipping iam__enum_action_query as it requires a query case")
                continue
            elif module_name == "systemsmanager__download_parameters":
                # Configuração especial para systemsmanager__download_parameters
                downloads_dir = os.path.expanduser("~/.local/share/pacu/data/downloads/ssm_parameters/")
                os.makedirs(downloads_dir, exist_ok=True)
                ssm_region = "us-east-2"
                with open(os.path.join(downloads_dir, '{}.txt'.format(ssm_region)), 'w+') as f:
                    pass
                result = execute_pacu_module(session_name, module_name, profile_for_pacu, "--regions us-east-2")
            else:
                # Módulos padrão com argumento de região
                result = execute_pacu_module(session_name, module_name, profile_for_pacu, "--regions us-east-2")
            
            results.append(result)
            print(f"Executed module: {module_name} - Status: {result['status']}")
    else:
        # Para outras categorias, verificar se a categoria existe no arquivo de configuração
        if category in categories:
            modules_to_run = categories[category]
            for module_name in modules_to_run:
                result = execute_pacu_module(session_name, module_name, profile_for_pacu)
                results.append(result)
                print(f"Executed module: {module_name} - Status: {result['status']}")
        else:
            # Se a categoria não for reconhecida, tratar como um nome de módulo individual
            logging.warning(f"Category {category} not recognized, treating as individual module")
            result = execute_pacu_module(session_name, category, profile_for_pacu)
            results.append(result)
            print(f"Executed module: {category} - Status: {result['status']}")
    
    # Salvar os resultados em um arquivo JSON
    output_file = reports_dir / "pacu_report.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
    
    logging.info(f"Results saved in {output_file}")
    print(f"Results saved in {output_file}")
    
    return {
        "success": True,
        "data": str(output_file),
        "message": f"Pacu execution completed. Report saved to: {output_file}",
        "results": results
    }