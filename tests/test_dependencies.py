#!/usr/bin/env python3
"""
Testes unitários para o módulo de dependências.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Adicionar o diretório pai ao path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.dependencies import command_exists, detect_os, check_deps

class TestDependencies(unittest.TestCase):
    """Testes para o módulo de dependências."""

    @patch('subprocess.run')
    def test_command_exists_true(self, mock_run):
        """Testa se command_exists retorna True quando o comando existe."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        result = command_exists('test_command')
        
        self.assertTrue(result)
        mock_run.assert_called_once_with(['which', 'test_command'], 
                                         stdout=unittest.mock.ANY, 
                                         stderr=unittest.mock.ANY)

    @patch('subprocess.run')
    def test_command_exists_false(self, mock_run):
        """Testa se command_exists retorna False quando o comando não existe."""
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_run.return_value = mock_process
        
        result = command_exists('nonexistent_command')
        
        self.assertFalse(result)
        mock_run.assert_called_once_with(['which', 'nonexistent_command'], 
                                         stdout=unittest.mock.ANY, 
                                         stderr=unittest.mock.ANY)

    @patch('platform.system')
    @patch('subprocess.check_output')
    def test_detect_os_linux_debian(self, mock_check_output, mock_system):
        """Testa se detect_os identifica corretamente uma distribuição Debian."""
        mock_system.return_value = 'Linux'
        mock_check_output.return_value = 'Ubuntu\n'
        
        result = detect_os()
        
        self.assertEqual(result, 'Debian')
        mock_system.assert_called_once()
        mock_check_output.assert_called_once_with(['lsb_release', '-is'], text=True)

    @patch('platform.system')
    @patch('subprocess.check_output')
    def test_detect_os_linux_redhat(self, mock_check_output, mock_system):
        """Testa se detect_os identifica corretamente uma distribuição RedHat."""
        mock_system.return_value = 'Linux'
        mock_check_output.return_value = 'Fedora\n'
        
        result = detect_os()
        
        self.assertEqual(result, 'RedHat')
        mock_system.assert_called_once()
        mock_check_output.assert_called_once_with(['lsb_release', '-is'], text=True)

    @patch('platform.system')
    def test_detect_os_macos(self, mock_system):
        """Testa se detect_os identifica corretamente macOS."""
        mock_system.return_value = 'Darwin'
        
        result = detect_os()
        
        self.assertEqual(result, 'macOS')
        mock_system.assert_called_once()

    @patch('platform.system')
    def test_detect_os_unsupported(self, mock_system):
        """Testa se detect_os retorna None para sistemas não suportados."""
        mock_system.return_value = 'Windows'
        
        result = detect_os()
        
        self.assertIsNone(result)
        mock_system.assert_called_once()

    @patch('utils.dependencies.command_exists')
    @patch('utils.dependencies.detect_os')
    def test_check_deps_all_installed(self, mock_detect_os, mock_command_exists):
        """Testa se check_deps retorna sucesso quando todas as dependências estão instaladas."""
        mock_detect_os.return_value = 'Debian'
        mock_command_exists.return_value = True
        
        result = check_deps()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Todas as dependências estão instaladas corretamente.')
        mock_detect_os.assert_called_once()
        # command_exists deve ser chamado para cada dependência
        self.assertEqual(mock_command_exists.call_count, 4)

if __name__ == '__main__':
    unittest.main()
