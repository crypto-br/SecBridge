#!/usr/bin/env python3
"""
Testes unitários para o módulo prowler_runner.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Adicionar o diretório pai ao path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.prowler_runner import run_prowler

class TestProwlerRunner(unittest.TestCase):
    """Testes para o módulo prowler_runner."""

    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_run_prowler_success(self, mock_exists, mock_run):
        """Testa se run_prowler retorna sucesso quando o Prowler é executado corretamente."""
        # Configurar mocks
        mock_process = MagicMock()
        mock_process.stdout = "ASFF file generated at: /tmp/prowler_report.json"
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        mock_exists.return_value = True
        
        # Executar a função
        result = run_prowler('test_profile')
        
        # Verificar resultado
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['data'])
        self.assertIn('Prowler assessment completed', result['message'])
        
        # Verificar se os mocks foram chamados corretamente
        mock_run.assert_called_once()
        self.assertIn('prowler', mock_run.call_args[0][0][0])
        self.assertIn('test_profile', mock_run.call_args[0][0][4])

    @patch('subprocess.run')
    def test_run_prowler_command_error(self, mock_run):
        """Testa se run_prowler retorna falha quando o comando Prowler falha."""
        # Configurar mock para lançar exceção
        mock_run.side_effect = subprocess.CalledProcessError(1, 'prowler')
        
        # Executar a função
        result = run_prowler('test_profile')
        
        # Verificar resultado
        self.assertFalse(result['success'])
        self.assertIsNone(result['data'])
        self.assertIn('Error executing Prowler command', result['message'])
        
        # Verificar se o mock foi chamado corretamente
        mock_run.assert_called_once()

    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_run_prowler_no_json_found(self, mock_exists, mock_run):
        """Testa se run_prowler retorna falha quando nenhum arquivo JSON é encontrado."""
        # Configurar mocks
        mock_process = MagicMock()
        mock_process.stdout = "Prowler execution completed"
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        mock_exists.return_value = False
        
        # Executar a função
        result = run_prowler('test_profile')
        
        # Verificar resultado
        self.assertFalse(result['success'])
        self.assertIsNone(result['data'])
        self.assertIn('no JSON report was found', result['message'])
        
        # Verificar se os mocks foram chamados corretamente
        mock_run.assert_called_once()

if __name__ == '__main__':
    unittest.main()
