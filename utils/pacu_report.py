import sqlite3
import re
import json
import os
import logging
from pathlib import Path
import datetime
from tabulate import tabulate

def extract_resources_from_db():
    """
    Extrai dados das tabelas do Pacu e identifica recursos AWS.
    
    Returns:
        tuple: Uma tupla contendo os dados da sessão do Pacu e os dados das chaves AWS.
    """
    # Conectar ao banco de dados SQLite
    home_dir = os.path.expanduser('~')
    sql_dir = f"{home_dir}/.local/share/pacu/sqlite.db"
    
    try:
        conn = sqlite3.connect(sql_dir)
        cursor = conn.cursor()
        
        logging.info("Connected to Pacu SQLite database")
        
        # Verificar as colunas disponíveis em cada tabela
        cursor.execute("PRAGMA table_info(pacu_session);")
        pacu_session_columns = cursor.fetchall()
        logging.debug(f"Columns in the pacu_session table: {pacu_session_columns}")
        
        cursor.execute("PRAGMA table_info(aws_key);")
        aws_key_columns = cursor.fetchall()
        logging.debug(f"Columns in the aws_key table: {aws_key_columns}")
        
        # Extrair dados relevantes da tabela pacu_session
        cursor.execute("SELECT * FROM pacu_session;")
        pacu_session_data = cursor.fetchall()
        
        # Extrair dados relevantes da tabela aws_key
        cursor.execute("SELECT * FROM aws_key;")
        aws_key_data = cursor.fetchall()
        
        # Fechar a conexão com o banco de dados
        conn.close()
        
        return pacu_session_data, aws_key_data
        
    except sqlite3.Error as e:
        logging.error(f"SQLite error: {e}")
        return [], []
    except Exception as e:
        logging.error(f"Unexpected error accessing Pacu database: {e}")
        return [], []

def extract_resources_with_regex(combined_data):
    """
    Aplica expressões regulares para identificar diferentes tipos de recursos AWS.
    
    Args:
        combined_data (str): String combinada de dados para aplicar regex.
        
    Returns:
        dict: Um dicionário contendo os recursos AWS identificados.
    """
    # Padrões para identificar diferentes tipos de recursos AWS
    patterns = {
        # pacu_session_data
        "AccountId": r'account_id": "([^"]+)',
        "InstanceId": r'InstanceId": "([^"]+)',
        "VolumeId": r'VolumeId": "([^"]+)',
        "SecurityGroupId": r'GroupId": "([^"]+)',
        "VPCId": r'VpcId": "([^"]+)',
        "SubnetId": r'SubnetId": "([^"]+)',
        "LambdaFunctionName": r'FunctionName": "([^"]+)',
        "BucketName": r's3://([^/"]+)',
        "RDSInstanceId": r'DBInstanceIdentifier": "([^"]+)',
        "IAMRole": r'Role": "arn:aws:iam::[^:]+:role/([^"]+)',
        "IAMUser": r'UserName": "([^"]+)',
        "DynamoDBTable": r'TableName": "([^"]+)',
        "KMSKeyId": r'KeyId": "([^"]+)',
        "EIPId": r'AllocationId": "([^"]+)',
        "NatGatewayId": r'NatGatewayId": "([^"]+)',
        "ElasticLoadBalancer": r'LoadBalancerName": "([^"]+)',
        "AutoScalingGroup": r'AutoScalingGroupName": "([^"]+)',
        "CloudFormationStack": r'StackName": "([^"]+)',
        "SQSQueue": r'QueueName": "([^"]+)',
        "SNSArn": r'TopicArn": "([^"]+)',
        "CloudWatchAlarm": r'AlarmName": "([^"]+)',
        "ElasticBeanstalkEnv": r'EnvironmentName": "([^"]+)',
        "EFSFileSystemId": r'FileSystemId": "([^"]+)',
        "TransitGatewayId": r'TransitGatewayId": "([^"]+)',
        "RouteTableId": r'RouteTableId": "([^"]+)',
        "VpcPeeringConnectionId": r'VpcPeeringConnectionId": "([^"]+)',
        "GlueJobName": r'JobName": "([^"]+)',
        "CodeBuildProject": r'ProjectName": "([^"]+)',
        "CodePipelineName": r'PipelineName": "([^"]+)',
        "SecretsManagerSecret": r'SecretName": "([^"]+)',
        "WAFRuleId": r'RuleId": "([^"]+)',
        "WAFWebACL": r'WebACLName": "([^"]+)',
        "IAMPolicy": r'PolicyName": "([^"]+)',
        "IAMGroup": r'GroupName": "([^"]+)',
        # aws_key_data
        "IAMRoleARN": r'arn:aws:iam::(?:aws|\d{12}):role/([^"]+)',
        "IAMPolicyARN": r'arn:aws:iam::(?:aws|\d{12}):policy/([^"]+)'
    }
    
    # Dicionário para armazenar os recursos encontrados
    aws_resources = {key: set() for key in patterns.keys()}  # Usando set para evitar duplicatas
    
    # Extrair os recursos
    for resource_type, pattern in patterns.items():
        matches = re.findall(pattern, combined_data)
        aws_resources[resource_type].update(matches)  # Adicionar itens ao set, evitando duplicatas
    
    # Converter sets para listas para serialização JSON
    aws_resources = {key: list(values) for key, values in aws_resources.items()}
    
    return aws_resources

def generate_html_report(aws_resources, pacu_results, output_path):
    """
    Gera um relatório HTML com os recursos AWS identificados e os resultados do Pacu.
    
    Args:
        aws_resources (dict): Dicionário contendo os recursos AWS identificados.
        pacu_results (list): Lista de resultados da execução do Pacu.
        output_path (str): Caminho para salvar o relatório HTML.
    """
    # Carregar os resultados do Pacu se fornecido como caminho
    if isinstance(pacu_results, str) and os.path.exists(pacu_results):
        try:
            with open(pacu_results, 'r') as f:
                pacu_results = json.load(f)
        except Exception as e:
            logging.error(f"Error loading Pacu results: {e}")
            pacu_results = []
    
    # Criar o conteúdo HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SecBridge - Pacu Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                color: #333;
            }}
            h1, h2, h3 {{
                color: #0066cc;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            .header {{
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 5px;
                margin-bottom: 20px;
                border-left: 5px solid #0066cc;
            }}
            .section {{
                margin-bottom: 30px;
                padding: 20px;
                background-color: #fff;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            th, td {{
                padding: 12px 15px;
                border-bottom: 1px solid #ddd;
                text-align: left;
            }}
            th {{
                background-color: #f8f9fa;
                font-weight: bold;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .resource-count {{
                font-weight: bold;
                color: #0066cc;
            }}
            .module-success {{
                color: green;
            }}
            .module-error {{
                color: red;
            }}
            .timestamp {{
                color: #666;
                font-style: italic;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>SecBridge - Pacu Security Assessment Report</h1>
                <p class="timestamp">Generated on: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            
            <div class="section">
                <h2>AWS Resources Summary</h2>
                <table>
                    <tr>
                        <th>Resource Type</th>
                        <th>Count</th>
                    </tr>
    """
    
    # Adicionar contagem de recursos
    for resource_type, resources in aws_resources.items():
        if resources:  # Só mostrar recursos que foram encontrados
            html_content += f"""
                    <tr>
                        <td>{resource_type}</td>
                        <td class="resource-count">{len(resources)}</td>
                    </tr>
            """
    
    html_content += """
                </table>
            </div>
            
            <div class="section">
                <h2>Detailed AWS Resources</h2>
    """
    
    # Adicionar detalhes de cada tipo de recurso
    for resource_type, resources in aws_resources.items():
        if resources:  # Só mostrar recursos que foram encontrados
            html_content += f"""
                <h3>{resource_type}</h3>
                <table>
                    <tr>
                        <th>#</th>
                        <th>Resource Identifier</th>
                    </tr>
            """
            
            for i, resource in enumerate(resources, 1):
                html_content += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{resource}</td>
                    </tr>
                """
            
            html_content += """
                </table>
            """
    
    # Adicionar resultados do Pacu
    if pacu_results:
        html_content += """
            <div class="section">
                <h2>Pacu Module Execution Results</h2>
                <table>
                    <tr>
                        <th>Module</th>
                        <th>Status</th>
                        <th>Details</th>
                    </tr>
        """
        
        for result in pacu_results:
            module_name = result.get("module", "Unknown")
            status = result.get("status", "Unknown")
            stderr = result.get("stderr", "")
            
            status_class = "module-success" if status == "success" else "module-error"
            
            html_content += f"""
                    <tr>
                        <td>{module_name}</td>
                        <td class="{status_class}">{status}</td>
                        <td>{stderr if stderr else "No errors"}</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
        """
    
    # Fechar o HTML
    html_content += """
        </div>
    </body>
    </html>
    """
    
    # Salvar o arquivo HTML
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    logging.info(f"HTML report generated at: {output_path}")

def generate_report(pacu_results_path=None):
    """
    Gera um relatório completo com base nos dados do Pacu.
    
    Args:
        pacu_results_path (str, optional): Caminho para o arquivo JSON com os resultados do Pacu.
        
    Returns:
        dict: Um dicionário contendo o status da geração do relatório e os caminhos dos arquivos gerados.
    """
    print("Building PACU Framework report....")
    logging.info("Building PACU Framework report")
    
    try:
        # Criar diretório para relatórios se não existir
        reports_dir = Path("reports/data")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Extrair dados do banco de dados do Pacu
        pacu_session_data, aws_key_data = extract_resources_from_db()
        
        # Combinar os dados extraídos em uma string para aplicar regexes
        combined_data = ' '.join(str(row) for row in pacu_session_data + aws_key_data)
        
        # Extrair recursos AWS usando regex
        aws_resources = extract_resources_with_regex(combined_data)
        
        # Gerar arquivo JSON
        json_output_path = reports_dir / "aws_resources.json"
        with open(json_output_path, 'w') as json_file:
            json.dump(aws_resources, json_file, indent=4)
        
        logging.info(f"JSON file generated at: {json_output_path}")
        
        # Carregar resultados do Pacu se o caminho for fornecido
        pacu_results = []
        if pacu_results_path and os.path.exists(pacu_results_path):
            try:
                with open(pacu_results_path, 'r') as f:
                    pacu_results = json.load(f)
            except Exception as e:
                logging.error(f"Error loading Pacu results: {e}")
        
        # Gerar relatório HTML
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        html_output_path = reports_dir / f"pacu_report_{timestamp}.html"
        generate_html_report(aws_resources, pacu_results, html_output_path)
        
        # Exibir um resumo no console
        print("\nAWS Resources Summary:")
        resource_summary = []
        for resource_type, resources in aws_resources.items():
            if resources:  # Só mostrar recursos que foram encontrados
                resource_summary.append([resource_type, len(resources)])
        
        print(tabulate(resource_summary, headers=["Resource Type", "Count"], tablefmt="grid"))
        print(f"\nDetailed reports saved to:")
        print(f"  - JSON: {json_output_path}")
        print(f"  - HTML: {html_output_path}")
        
        return {
            "success": True,
            "data": {
                "json_report": str(json_output_path),
                "html_report": str(html_output_path)
            },
            "message": "Report generation completed successfully."
        }
        
    except Exception as e:
        error_msg = f"Error generating report: {e}"
        logging.error(error_msg)
        return {
            "success": False,
            "data": None,
            "message": error_msg
        }