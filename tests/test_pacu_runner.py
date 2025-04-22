#!/usr/bin/env python3
"""
Testes unitários para o módulo pacu_runner.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import json

# Adicionar o diretório pai ao path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.pacu_runner import load_module_categories, execute_pacu_module, run_pacu

class TestPacuRunner(unittest.TestCase):
    """Testes para o módulo pacu_runner."""

    @patch('builtins.open', new_callable=mock_open, read_data='{"category_enum": ["module1", "module2"]}')
    @patch('pathlib.Path.exists')
    def test_load_module_categories_success(self, mock_exists, mock_file):
        """Testa se load_module_categories carrega corretamente as categorias de módulos."""
        # Configurar mock
        mock_exists.return_value = True
        
        # Executar a função
        categories = load_module_categories()
        
        # Verificar resultado
        self.assertIn("category_enum", categories)
        self.assertEqual(categories["category_enum"], ["module1", "module2"])
        
        # Verificar se os mocks foram chamados corretamente
        mock_exists.assert_called_once()
        mock_file.assert_called_once_with('config/pacu_modules.json', 'r')

    @patch('pathlib.Path.exists')
    def test_load_module_categories_file_not_found(self, mock_exists):
        """Testa se load_module_categories retorna um dicionário vazio quando o arquivo não existe."""
        # Configurar mock
        mock_exists.return_value = False
        
        # Executar a função
        categories = load_module_categories()
        
        # Verificar resultado
        self.assertEqual(categories, {})
        
        # Verificar se o mock foi chamado corretamente
        mock_exists.assert_called_once()

    @patch('subprocess.Popen')
    def test_execute_pacu_module_success(self, mock_popen):
        """Testa se execute_pacu_module executa corretamente um módulo do Pacu."""
        # Configurar mock
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("Success output", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        # Executar a função
        result = execute_pacu_module("test_session", "test_module", "test_profile")
        
        # Verificar resultado
        self.assertEqual(result["module"], "test_module")
        self.assertEqual(result["stdout"], "Success output")
        self.assertEqual(result["stderr"], "")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["return_code"], 0)
        
        # Verificar se os mocks foram chamados corretamente
        mock_popen.assert_called_once()
        self.assertIn("test_session", mock_popen.call_args[0][0])
        self.assertIn("test_module", mock_popen.call_args[0][0])
        self.assertIn("test_profile", mock_popen.call_args[0][0])
        mock_process.communicate.assert_called_once_with(input="y\n")

    @patch('subprocess.Popen')
    def test_execute_pacu_module_with_args(self, mock_popen):
        """Testa se execute_pacu_module passa corretamente argumentos adicionais."""
        # Configurar mock
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("Success output", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        # Executar a função
        result = execute_pacu_module("test_session", "test_module", "test_profile", "--regions us-east-1")
        
        # Verificar resultado
        self.assertEqual(result["status"], "success")
        
        # Verificar se os mocks foram chamados corretamente
        mock_popen.assert_called_once()
        cmd_args = mock_popen.call_args[0][0]
        self.assertIn("--module-args", cmd_args)
        self.assertIn("--regions us-east-1", cmd_args)

    @patch('subprocess.Popen')
    def test_execute_pacu_module_access_denied(self, mock_popen):
        """Testa se execute_pacu_module lida corretamente com erros de permissão."""
        # Configurar mock
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("", "AccessDeniedException: Access denied")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        
        # Executar a função
        result = execute_pacu_module("test_session", "test_module", "test_profile")
        
        # Verificar resultado
        self.assertEqual(result["stderr"], "Module cannot be executed due to lack of permission")
        self.assertEqual(result["status"], "error")
        
        # Verificar se os mocks foram chamados corretamente
        mock_popen.assert_called_once()

    @patch('subprocess.Popen')
    def test_execute_pacu_module_error(self, mock_popen):
        """Testa se execute_pacu_module lida corretamente com erros gerais."""
        # Configurar mock para lançar exceção
        mock_popen.side_effect = Exception("Test error")
        
        # Executar a função
        result = execute_pacu_module("test_session", "test_module", "test_profile")
        
        # Verificar resultado
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["stderr"], "Test error")
        self.assertEqual(result["return_code"], -1)
        
        # Verificar se o mock foi chamado corretamente
        mock_popen.assert_called_once()

    @patch('utils.pacu_runner.load_module_categories')
    @patch('utils.pacu_runner.execute_pacu_module')
    @patch('subprocess.run')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_run_pacu_category_enum(self, mock_json_dump, mock_file, mock_makedirs, 
                                   mock_subprocess_run, mock_execute_module, mock_load_categories):
        """Testa se run_pacu executa corretamente a categoria de enumeração."""
        # Configurar mocks
        mock_load_categories.return_value = {
            "category_enum": ["module1", "module2"],
            "special_modules": {"module1": True}
        }
        
        mock_execute_module.return_value = {
            "module": "test_module",
            "stdout": "Success output",
            "stderr": "",
            "status": "success",
            "return_code": 0
        }
        
        # Executar a função
        result = run_pacu("test_profile", "test_session", "category_enum")
        
        # Verificar resultado
        self.assertTrue(result["success"])
        self.assertIn("pacu_report.json", result["data"])
        
        # Verificar se os mocks foram chamados corretamente
        mock_load_categories.assert_called_once()
        self.assertEqual(mock_execute_module.call_count, 2)  # Um para cada módulo na categoria
        mock_subprocess_run.assert_called_once()  # Para ativar a sessão
        mock_makedirs.assert_called_once()
        mock_json_dump.assert_called_once()

    @patch('utils.pacu_runner.load_module_categories')
    @patch('utils.pacu_runner.execute_pacu_module')
    @patch('subprocess.run')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_run_pacu_custom_category(self, mock_json_dump, mock_file, mock_makedirs, 
                                     mock_subprocess_run, mock_execute_module, mock_load_categories):
        """Testa se run_pacu executa corretamente uma categoria personalizada."""
        # Configurar mocks
        mock_load_categories.return_value = {
            "category_exploit": ["exploit_module1", "exploit_module2"]
        }
        
        mock_execute_module.return_value = {
            "module": "exploit_module",
            "stdout": "Success output",
            "stderr": "",
            "status": "success",
            "return_code": 0
        }
        
        # Executar a função
        result = run_pacu("test_profile", "test_session", "category_exploit")
        
        # Verificar resultado
        self.assertTrue(result["success"])
        
        # Verificar se os mocks foram chamados corretamente
        mock_load_categories.assert_called_once()
        self.assertEqual(mock_execute_module.call_count, 2)  # Um para cada módulo na categoria
        mock_subprocess_run.assert_called_once()  # Para ativar a sessão

    @patch('utils.pacu_runner.load_module_categories')
    @patch('utils.pacu_runner.execute_pacu_module')
    @patch('subprocess.run')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_run_pacu_unknown_category(self, mock_json_dump, mock_file, mock_makedirs, 
                                      mock_subprocess_run, mock_execute_module, mock_load_categories):
        """Testa se run_pacu lida corretamente com categorias desconhecidas."""
        # Configurar mocks
        mock_load_categories.return_value = {
            "category_enum": ["module1", "module2"]
        }
        
        mock_execute_module.return_value = {
            "module": "single_module",
            "stdout": "Success output",
            "stderr": "",
            "status": "success",
            "return_code": 0
        }
        
        # Executar a função
        result = run_pacu("test_profile", "test_session", "unknown_category")
        
        # Verificar resultado
        self.assertTrue(result["success"])
        
        # Verificar se os mocks foram chamados corretamente
        mock_load_categories.assert_called_once()
        mock_execute_module.assert_called_once_with("test_session", "unknown_category", "test_profile")
        mock_subprocess_run.assert_called_once()  # Para ativar a sessão

if __name__ == '__main__':
    unittest.main()
