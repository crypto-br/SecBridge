#!/usr/bin/env python3
"""
Testes unitários para o módulo pacu_report.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import json
import sqlite3

# Adicionar o diretório pai ao path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.pacu_report import extract_resources_from_db, extract_resources_with_regex, generate_html_report, generate_report

class TestPacuReport(unittest.TestCase):
    """Testes para o módulo pacu_report."""

    @patch('sqlite3.connect')
    def test_extract_resources_from_db_success(self, mock_connect):
        """Testa se extract_resources_from_db extrai corretamente os dados do banco de dados."""
        # Configurar mocks
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [('column1', 'column2')],  # Colunas da tabela pacu_session
            [('column1', 'column2')],  # Colunas da tabela aws_key
            [('session1', 'data1')],   # Dados da tabela pacu_session
            [('key1', 'data1')]        # Dados da tabela aws_key
        ]
        
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        # Executar a função
        pacu_session_data, aws_key_data = extract_resources_from_db()
        
        # Verificar resultado
        self.assertEqual(pacu_session_data, [('session1', 'data1')])
        self.assertEqual(aws_key_data, [('key1', 'data1')])
        
        # Verificar se os mocks foram chamados corretamente
        mock_connect.assert_called_once()
        self.assertEqual(mock_cursor.execute.call_count, 4)
        self.assertEqual(mock_cursor.fetchall.call_count, 4)
        mock_connection.close.assert_called_once()

    @patch('sqlite3.connect')
    def test_extract_resources_from_db_error(self, mock_connect):
        """Testa se extract_resources_from_db lida corretamente com erros de banco de dados."""
        # Configurar mock para lançar exceção
        mock_connect.side_effect = sqlite3.Error("Database error")
        
        # Executar a função
        pacu_session_data, aws_key_data = extract_resources_from_db()
        
        # Verificar resultado
        self.assertEqual(pacu_session_data, [])
        self.assertEqual(aws_key_data, [])
        
        # Verificar se o mock foi chamado corretamente
        mock_connect.assert_called_once()

    def test_extract_resources_with_regex(self):
        """Testa se extract_resources_with_regex extrai corretamente os recursos usando regex."""
        # Dados de teste
        test_data = '''
        {"account_id": "123456789012", "InstanceId": "i-1234567890abcdef0", "VolumeId": "vol-1234567890abcdef0",
        "GroupId": "sg-1234567890abcdef0", "VpcId": "vpc-1234567890abcdef0", "SubnetId": "subnet-1234567890abcdef0",
        "FunctionName": "test-lambda", "s3://test-bucket", "DBInstanceIdentifier": "test-db",
        "Role": "arn:aws:iam::123456789012:role/test-role", "UserName": "test-user"}
        '''
        
        # Executar a função
        resources = extract_resources_with_regex(test_data)
        
        # Verificar resultado
        self.assertEqual(resources["AccountId"], ["123456789012"])
        self.assertEqual(resources["InstanceId"], ["i-1234567890abcdef0"])
        self.assertEqual(resources["VolumeId"], ["vol-1234567890abcdef0"])
        self.assertEqual(resources["SecurityGroupId"], ["sg-1234567890abcdef0"])
        self.assertEqual(resources["VPCId"], ["vpc-1234567890abcdef0"])
        self.assertEqual(resources["SubnetId"], ["subnet-1234567890abcdef0"])
        self.assertEqual(resources["LambdaFunctionName"], ["test-lambda"])
        self.assertEqual(resources["BucketName"], ["test-bucket"])
        self.assertEqual(resources["RDSInstanceId"], ["test-db"])
        self.assertEqual(resources["IAMRole"], ["test-role"])
        self.assertEqual(resources["IAMUser"], ["test-user"])

    @patch('builtins.open', new_callable=mock_open)
    def test_generate_html_report(self, mock_file):
        """Testa se generate_html_report gera corretamente o relatório HTML."""
        # Dados de teste
        aws_resources = {
            "AccountId": ["123456789012"],
            "InstanceId": ["i-1234567890abcdef0"],
            "VolumeId": ["vol-1234567890abcdef0"]
        }
        
        pacu_results = [
            {"module": "test_module", "status": "success", "stderr": ""},
            {"module": "test_module2", "status": "error", "stderr": "Error message"}
        ]
        
        output_path = "test_report.html"
        
        # Executar a função
        generate_html_report(aws_resources, pacu_results, output_path)
        
        # Verificar se o arquivo foi aberto para escrita
        mock_file.assert_called_once_with(output_path, 'w')
        
        # Verificar se o conteúdo HTML foi escrito
        handle = mock_file()
        self.assertTrue(handle.write.called)
        
        # Verificar se o conteúdo HTML contém os dados esperados
        html_content = ''.join(call_args[0][0] for call_args in handle.write.call_args_list)
        self.assertIn("123456789012", html_content)
        self.assertIn("i-1234567890abcdef0", html_content)
        self.assertIn("vol-1234567890abcdef0", html_content)
        self.assertIn("test_module", html_content)
        self.assertIn("test_module2", html_content)
        self.assertIn("success", html_content)
        self.assertIn("error", html_content)
        self.assertIn("Error message", html_content)

    @patch('utils.pacu_report.extract_resources_from_db')
    @patch('utils.pacu_report.extract_resources_with_regex')
    @patch('utils.pacu_report.generate_html_report')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    @patch('os.path.exists')
    @patch('json.load')
    def test_generate_report_success(self, mock_json_load, mock_exists, mock_json_dump, 
                                    mock_file, mock_generate_html, mock_extract_regex, 
                                    mock_extract_db):
        """Testa se generate_report gera corretamente o relatório completo."""
        # Configurar mocks
        mock_extract_db.return_value = ([('session1', 'data1')], [('key1', 'data1')])
        mock_extract_regex.return_value = {"AccountId": ["123456789012"]}
        mock_exists.return_value = True
        mock_json_load.return_value = [{"module": "test_module", "status": "success"}]
        
        # Executar a função
        result = generate_report("test_results.json")
        
        # Verificar resultado
        self.assertTrue(result["success"])
        self.assertIn("json_report", result["data"])
        self.assertIn("html_report", result["data"])
        
        # Verificar se os mocks foram chamados corretamente
        mock_extract_db.assert_called_once()
        mock_extract_regex.assert_called_once()
        mock_generate_html.assert_called_once()
        mock_json_dump.assert_called_once()

    @patch('utils.pacu_report.extract_resources_from_db')
    def test_generate_report_error(self, mock_extract_db):
        """Testa se generate_report lida corretamente com erros."""
        # Configurar mock para lançar exceção
        mock_extract_db.side_effect = Exception("Test error")
        
        # Executar a função
        result = generate_report()
        
        # Verificar resultado
        self.assertFalse(result["success"])
        self.assertIsNone(result["data"])
        self.assertIn("Error generating report", result["message"])
        
        # Verificar se o mock foi chamado corretamente
        mock_extract_db.assert_called_once()

if __name__ == '__main__':
    unittest.main()
