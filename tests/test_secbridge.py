#!/usr/bin/env python3
"""
Testes unitários para o módulo principal secbridge.py.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import click
from click.testing import CliRunner

# Adicionar o diretório pai ao path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import secbridge

class TestSecBridge(unittest.TestCase):
    """Testes para o módulo principal secbridge.py."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.runner = CliRunner()

    @patch('secbridge.check_deps')
    def test_deps_command(self, mock_check_deps):
        """Testa se o comando deps executa corretamente."""
        # Configurar mock
        mock_check_deps.return_value = {"success": True, "message": "All dependencies installed"}
        
        # Executar o comando
        with patch('secbridge.logging'):  # Evitar logs durante o teste
            result = self.runner.invoke(secbridge.cli, ['deps'])
        
        # Verificar resultado
        self.assertEqual(result.exit_code, 0)
        mock_check_deps.assert_called_once()

    @patch('secbridge.run_prowler')
    @patch('builtins.input')
    def test_prowler_command(self, mock_input, mock_run_prowler):
        """Testa se o comando prowler executa corretamente."""
        # Configurar mocks
        mock_input.return_value = "test_profile"
        mock_run_prowler.return_value = {"success": True, "message": "Prowler executed successfully", "data": "report.json"}
        
        # Executar o comando
        with patch('secbridge.logging'):  # Evitar logs durante o teste
            result = self.runner.invoke(secbridge.cli, ['prowler'])
        
        # Verificar resultado
        self.assertEqual(result.exit_code, 0)
        mock_input.assert_called_once()
        mock_run_prowler.assert_called_once_with("test_profile")

    @patch('secbridge.run_command')
    def test_prowler_dash_command(self, mock_run_command):
        """Testa se o comando prowler-dash executa corretamente."""
        # Configurar mock
        mock_run_command.return_value = {"success": True, "message": "Dashboard started"}
        
        # Executar o comando
        with patch('secbridge.logging'):  # Evitar logs durante o teste
            result = self.runner.invoke(secbridge.cli, ['prowler-dash'])
        
        # Verificar resultado
        self.assertEqual(result.exit_code, 0)
        mock_run_command.assert_called_once_with(["prowler", "dashboard"], "iniciando Dashboard do Prowler")

    @patch('secbridge.run_command')
    @patch('secbridge.run_pacu')
    @patch('secbridge.generate_report')
    @patch('builtins.input')
    def test_pacu_enum_command(self, mock_input, mock_generate_report, mock_run_pacu, mock_run_command):
        """Testa se o comando pacu-enum executa corretamente."""
        # Configurar mocks
        mock_input.side_effect = ["test_profile", "test_session"]
        mock_run_pacu.return_value = {"success": True, "message": "Pacu executed", "data": "report.json"}
        mock_generate_report.return_value = {"success": True, "data": {"html_report": "report.html"}}
        mock_run_command.return_value = {"success": True}
        
        # Executar o comando
        with patch('secbridge.logging'):  # Evitar logs durante o teste
            result = self.runner.invoke(secbridge.cli, ['pacu-enum'])
        
        # Verificar resultado
        self.assertEqual(result.exit_code, 0)
        mock_input.assert_any_call("Digite o perfil do AWS-CLI que deseja utilizar: ")
        mock_input.assert_any_call("Digite o nome da sessão para iniciar o PACU: ")
        mock_run_pacu.assert_called_once_with("test_profile", "test_session", "category_enum")
        mock_generate_report.assert_called_once_with("report.json")

    @patch('secbridge.run_command')
    @patch('secbridge.run_pacu')
    @patch('builtins.input')
    def test_pacu_command(self, mock_input, mock_run_pacu, mock_run_command):
        """Testa se o comando pacu executa corretamente."""
        # Configurar mocks
        mock_input.side_effect = ["test_profile", "test_session", "category_exploit"]
        mock_run_pacu.return_value = {"success": True, "message": "Pacu executed", "data": "report.json"}
        mock_run_command.return_value = {"success": True}
        
        # Executar o comando
        with patch('secbridge.logging'):  # Evitar logs durante o teste
            result = self.runner.invoke(secbridge.cli, ['pacu'])
        
        # Verificar resultado
        self.assertEqual(result.exit_code, 0)
        mock_input.assert_any_call("Digite o perfil do AWS-CLI que deseja utilizar: ")
        mock_input.assert_any_call("Digite o nome da sessão para iniciar o PACU: ")
        mock_input.assert_any_call("Digite a categoria desejada para iniciar o PACU: ")
        mock_run_pacu.assert_called_once_with("test_profile", "test_session", "category_exploit")

    @patch('secbridge.run_command')
    def test_prune_pacu_command(self, mock_run_command):
        """Testa se o comando prune-pacu executa corretamente."""
        # Configurar mock
        mock_run_command.return_value = {"success": True, "message": "Pacu sessions deleted"}
        
        # Executar o comando
        with patch('secbridge.logging'):  # Evitar logs durante o teste
            result = self.runner.invoke(secbridge.cli, ['prune-pacu'])
        
        # Verificar resultado
        self.assertEqual(result.exit_code, 0)
        mock_run_command.assert_called_once()
        self.assertIn("~/.local/share/pacu/*", mock_run_command.call_args[0][0][2])

    @patch('secbridge.run_command')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    def test_pacu_dash_command(self, mock_mkdir, mock_exists, mock_run_command):
        """Testa se o comando pacu-dash executa corretamente."""
        # Configurar mocks
        mock_exists.return_value = False
        mock_run_command.return_value = {"success": True, "message": "Dashboard started"}
        
        # Executar o comando
        with patch('secbridge.logging'):  # Evitar logs durante o teste
            result = self.runner.invoke(secbridge.cli, ['pacu-dash', '--port', '8080'])
        
        # Verificar resultado
        self.assertEqual(result.exit_code, 0)
        mock_exists.assert_called_once()
        mock_mkdir.assert_called_once()
        mock_run_command.assert_called_once()
        self.assertIn("8080", mock_run_command.call_args[0][0][3])

    @patch('secbridge.run_command')
    @patch('secbridge.run_prowler')
    @patch('secbridge.run_pacu')
    @patch('secbridge.generate_report')
    @patch('builtins.input')
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='{"findings": []}')
    @patch('os.path.exists')
    def test_full_command(self, mock_exists, mock_open, mock_input, mock_generate_report, 
                         mock_run_pacu, mock_run_prowler, mock_run_command):
        """Testa se o comando full executa corretamente."""
        # Configurar mocks
        mock_input.side_effect = ["test_profile", "test_session"]
        mock_run_prowler.return_value = {"success": True, "message": "Prowler executed", "data": "prowler_report.json"}
        mock_run_pacu.return_value = {"success": True, "message": "Pacu executed", "data": "pacu_report.json"}
        mock_generate_report.return_value = {"success": True, "data": {"html_report": "report.html"}}
        mock_run_command.return_value = {"success": True}
        mock_exists.return_value = True
        
        # Executar o comando
        with patch('secbridge.logging'):  # Evitar logs durante o teste
            result = self.runner.invoke(secbridge.cli, ['full'])
        
        # Verificar resultado
        self.assertEqual(result.exit_code, 0)
        mock_input.assert_any_call("Digite o perfil do AWS-CLI que deseja utilizar: ")
        mock_input.assert_any_call("Digite o nome da sessão: ")
        mock_run_prowler.assert_called_once_with("test_profile")
        mock_run_pacu.assert_called_once_with("test_profile", "test_session", "category_enum")
        mock_generate_report.assert_called_once_with("pacu_report.json")

    @patch('secbridge.configure_profile')
    def test_np_command(self, mock_configure_profile):
        """Testa se o comando np executa corretamente."""
        # Configurar mock
        mock_configure_profile.return_value = True
        
        # Executar o comando
        with patch('secbridge.logging'):  # Evitar logs durante o teste
            result = self.runner.invoke(secbridge.cli, ['np'])
        
        # Verificar resultado
        self.assertEqual(result.exit_code, 0)
        mock_configure_profile.assert_called_once()

    @patch('secbridge.setup_logging')
    def test_main_function(self, mock_setup_logging):
        """Testa se a função main executa corretamente."""
        # Configurar mock
        mock_setup_logging.return_value = "log_file.log"
        
        # Executar a função com patch para evitar a execução real do CLI
        with patch('secbridge.cli') as mock_cli:
            secbridge.main()
        
        # Verificar se os mocks foram chamados corretamente
        mock_setup_logging.assert_called_once()
        mock_cli.assert_called_once()

if __name__ == '__main__':
    unittest.main()
