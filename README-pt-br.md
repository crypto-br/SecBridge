# SecBridge

**Versão:** 1.2

**Autor:** Luiz Machado (@cryptobr)

## Descrição

SecBridge é uma ferramenta de integração que conecta o [Prowler](https://github.com/prowler-cloud/prowler) e o [Pacu Framework](https://github.com/RhinoSecurityLabs/pacu), permitindo automatizar a avaliação de riscos de segurança em suas contas AWS. A ferramenta verifica riscos usando o Prowler e avalia a explorabilidade desses riscos usando o Pacu, gerando relatórios detalhados.

## Funcionalidades

- **Verificação de Dependências:** Confirma a existência de dependências essenciais como AWS CLI, Python3, Prowler e Pacu.
- **Execução do Prowler:** Executa o Prowler para realizar uma avaliação de segurança na conta AWS especificada.
- **Execução do Pacu Framework:** Permite a execução do Pacu Framework para exploração baseada em categorias específicas.
- **Geração de Relatórios:** Gera relatórios detalhados após a execução do Pacu, incluindo formatos HTML e JSON.
- **Dashboards:** Lança dashboards para visualização dos resultados do Prowler e Pacu.
- **Configuração de Perfil AWS:** Configura perfis AWS-CLI diretamente através da ferramenta com validação de credenciais.
- **Logging Estruturado:** Fornece logging abrangente com diferentes níveis de verbosidade e formatação colorida.
- **Testes Unitários:** Inclui testes automatizados para garantir a qualidade do código.

## Instalação

1. **Clone o Repositório:**
   ```bash
   git clone https://github.com/your-username/secbridge.git
   cd secbridge
   ```

2. **Instale as Dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verifique as Dependências do Sistema:**
   Certifique-se de que AWS CLI, Python3, Prowler e Pacu estão instalados. Você pode verificar e instalar as dependências executando:
   ```bash
   python secbridge.py deps
   ```

## Uso

Você pode executar a ferramenta com diferentes comandos:

- **Verificar Dependências:**
  ```bash
  python secbridge.py deps
  ```

- **Executar Prowler:**
  ```bash
  python secbridge.py prowler
  ```

- **Iniciar Dashboard do Prowler:**
  ```bash
  python secbridge.py prowler-dash
  ```

- **Executar Pacu (Enumeração):**
  ```bash
  python secbridge.py pacu-enum
  ```

- **Executar Pacu (Com Categoria Específica):**
  ```bash
  python secbridge.py pacu
  ```

- **Iniciar Pacu com Prowler (Avaliação Completa):**
  ```bash
  python secbridge.py full
  ```

- **Excluir Sessões do Pacu:**
  ```bash
  python secbridge.py prune-pacu
  ```

- **Iniciar Dashboard do Pacu:**
  ```bash
  python secbridge.py pacu-dash
  ```
  
  Você pode especificar uma porta personalizada:
  ```bash
  python secbridge.py pacu-dash --port 8080
  ```

  ![image](https://github.com/user-attachments/assets/3d40d8f2-1fcb-47a9-ba1e-a69922a1be99)

  ![image](https://github.com/user-attachments/assets/476551c1-20a3-4336-9846-67473d787740)

- **Configurar um Novo Perfil AWS-CLI:**
  ```bash
  python secbridge.py np
  ```

- **Ajuda:**
  ```bash
  python secbridge.py --help
  ```

## Testes

Execute os testes unitários para garantir que tudo está funcionando corretamente:

```bash
pytest tests/
```

## Estrutura do Projeto

```
secbridge/
├── config/
│   └── pacu_modules.json     # Configuração para módulos do Pacu
├── logs/                     # Diretório de arquivos de log
├── reports/                  # Relatórios gerados
│   ├── data/                 # Arquivos de dados JSON
│   └── prowler/              # Relatórios do Prowler
├── tests/                    # Testes unitários
├── utils/                    # Módulos utilitários
│   ├── aws_config.py         # Configuração de perfil AWS
│   ├── dependencies.py       # Verificação de dependências
│   ├── pacu_report.py        # Geração de relatórios para o Pacu
│   ├── pacu_runner.py        # Execução do Pacu
│   └── prowler_runner.py     # Execução do Prowler
├── requirements.txt          # Dependências Python
├── CHANGELOG.md              # Histórico de alterações
├── secbridge.py              # Aplicação principal
└── README.md                 # Documentação
```

## Contribuição

Contribuições são bem-vindas! Se você tem sugestões para melhorias ou encontrou um bug, sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## Contato

Para mais informações ou dúvidas, entre em contato com [Luiz Machado](https://www.linkedin.com/in/luizmachadoaws/).
