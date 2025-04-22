#!/usr/bin/env python3
"""
Testes unitários para o módulo aws_config.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import configparser

# Adicionar o diretório pai ao path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.aws_config import configure_profile

class TestAwsConfig(unittest.TestCase):
    """Testes para o módulo aws_config."""

    @patch('boto3.Session')
    @patch('configparser.ConfigParser')
    @patch('builtins.input')
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_configure_profile_success(self, mock_makedirs, mock_exists, mock_input, 
                                      mock_configparser, mock_session):
        """Testa se configure_profile configura corretamente um perfil AWS."""
        # Configurar mocks
        mock_input.side_effect = ['test_profile', 'test_access_key', 'test_secret_key', 'us-east-1']
        mock_exists.return_value = True
        
        mock_sts = MagicMock()
        mock_sts.get_caller_identity.return_value = {'Account': '123456789012'}
        
        mock_session_instance = MagicMock()
        mock_session_instance.client.return_value = mock_sts
        mock_session.return_value = mock_session_instance
        
        mock_config = MagicMock()
        mock_config_parser = MagicMock()
        mock_configparser.return_value = mock_config
        
        # Executar a função
        result = configure_profile()
        
        # Verificar resultado
        self.assertTrue(result)
        
        # Verificar se os mocks foram chamados corretamente
        mock_input.assert_any_call("What is the profile name? ")
        mock_input.assert_any_call("Enter the Access Key: ")
        mock_input.assert_any_call("Enter the Secret Key: ")
        mock_input.assert_any_call("What is the region? ")
        
        mock_session.assert_called_once_with(
            aws_access_key_id='test_access_key',
            aws_secret_access_key='test_secret_key',
            region_name='us-east-1'
        )
        
        mock_session_instance.client.assert_called_once_with('sts')
        mock_sts.get_caller_identity.assert_called_once()

    @patch('boto3.Session')
    @patch('builtins.input')
    def test_configure_profile_invalid_credentials(self, mock_input, mock_session):
        """Testa se configure_profile falha com credenciais inválidas."""
        # Configurar mocks
        mock_input.side_effect = ['test_profile', 'invalid_access_key', 'invalid_secret_key', 'us-east-1']
        
        mock_session_instance = MagicMock()
        mock_session_instance.client.side_effect = Exception("Invalid credentials")
        mock_session.return_value = mock_session_instance
        
        # Executar a função
        result = configure_profile()
        
        # Verificar resultado
        self.assertFalse(result)
        
        # Verificar se os mocks foram chamados corretamente
        mock_input.assert_any_call("What is the profile name? ")
        mock_input.assert_any_call("Enter the Access Key: ")
        mock_input.assert_any_call("Enter the Secret Key: ")
        mock_input.assert_any_call("What is the region? ")
        
        mock_session.assert_called_once_with(
            aws_access_key_id='invalid_access_key',
            aws_secret_access_key='invalid_secret_key',
            region_name='us-east-1'
        )

if __name__ == '__main__':
    unittest.main()
