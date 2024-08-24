import sqlite3
import re
import json
import os

# Função para extrair dados das tabelas e identificar recursos AWS
def gerar_relatorio():
    # Conectar ao banco de dados SQLite
    home_dir = os.path.expanduser('~')
    sql_dir = f"{home_dir}/.local/share/pacu/sqlite.db"
    conn = sqlite3.connect(sql_dir)  # Usando o caminho 'sqlite.db'
    cursor = conn.cursor()

    print("Construindo relatório do PACU Framework....")
    # Verificar as colunas disponíveis em cada tabela
    cursor.execute("PRAGMA table_info(pacu_session);")
    pacu_session_columns = cursor.fetchall()
    print("Colunas na tabela pacu_session:", pacu_session_columns)

    cursor.execute("PRAGMA table_info(aws_key);")
    aws_key_columns = cursor.fetchall()
    print("Colunas na tabela aws_key:", aws_key_columns)

    # Extrair dados relevantes da tabela pacu_session
    cursor.execute("SELECT * FROM pacu_session;")
    pacu_session_data = cursor.fetchall()

    # Extrair dados relevantes da tabela aws_key
    cursor.execute("SELECT * FROM aws_key;")
    aws_key_data = cursor.fetchall()

    # Processar e exibir os dados extraídos
    print("\nDados da tabela pacu_session:")
    for row in pacu_session_data:
        print(row)

    print("\nDados da tabela aws_key:")
    for row in aws_key_data:
        print(row)

    # Combinar os dados extraídos em uma string para aplicar as regexes
    output_content = ' '.join(str(row) for row in pacu_session_data)

    # Padrões para identificar diferentes tipos de recursos AWS
    patterns = {
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
    }

    # Dicionário para armazenar os recursos encontrados
    aws_resources = {key: set() for key in patterns.keys()}  # Usando set para evitar duplicatas

    # Extração dos recursos
    for resource_type, pattern in patterns.items():
        matches = re.findall(pattern, output_content)
        aws_resources[resource_type].update(matches)  # Adiciona itens ao set, evitando duplicatas

    # Converter sets para listas para serialização em JSON
    aws_resources = {key: list(values) for key, values in aws_resources.items()}

    # Gerar o arquivo JSON
    with open('reports/data/aws_resources.json', 'w') as json_file:
        json.dump(aws_resources, json_file, indent=4)

    print("Arquivo JSON 'aws_resources.json' criado com sucesso.")

    # Fechar a conexão com o banco de dados
    conn.close()
