# SecBridge

**Versão:** 1.0

**Autor:** Luiz Machado (@cryptobr)

## Descrição

SecBridge é uma ferramenta de integração que conecta o [Prowler](https://github.com/prowler-cloud/prowler) e o [Pacu Framework](https://github.com/RhinoSecurityLabs/pacu), permitindo que você automatize a verificação de riscos de segurança em suas contas AWS. A ferramenta verifica riscos usando o Prowler e avalia a explotabilidade desses riscos usando o Pacu, gerando relatórios detalhados.

## Funcionalidades

- **Verificação de Dependências:** Confirma a existência de dependências essenciais como AWS CLI, Python3, Prowler e Pacu.
- **Execução do Prowler:** Executa o Prowler para realizar uma verificação de segurança na conta AWS especificada.
- **Execução do Pacu Framework:** Permite a execução do Pacu Framework para exploração baseada em categorias específicas.
- **Geração de Relatórios:** Gera relatórios detalhados após a execução do Pacu.
- **Dashboards:** Inicia dashboards para visualização dos resultados do Prowler e do Pacu.
- **Configuração de Perfis AWS:** Configura perfis AWS-CLI diretamente pela ferramenta.

## Instalação

1. **Clone o Repositório:**
   ```bash
   git clone https://github.com/seu-usuario/secbridge.git
   cd secbridge
   ```

2. **Instale as Dependências:**
   Certifique-se de ter o AWS CLI, Python3, Prowler e Pacu instalados. Você pode verificar as dependências executando:
   ```bash
   python secbridge.py --deps
   ```

## Utilização

Você pode executar a ferramenta com diferentes opções, dependendo de sua necessidade:

- **Verificar Dependências:**
  ```bash
  python secbridge.py --deps
  ```

- **Executar o Prowler:**
  ```bash
  python secbridge.py --prowler
  ```

- **Iniciar o Dashboard do Prowler:**
  ```bash
  python secbridge.py --prowler-dash
  ```

- **Executar o Pacu (Enumeração):**
  ```bash
  python secbridge.py --pacu-enum
  ```

- **Executar o Pacu (Todas as Categorias):**
  ```bash
  python secbridge.py --pacu
  ```

- **Iniciar o Pacu com Prowler:**
  ```bash
  python secbridge.py --full
  ```

- **Deletar Sessões do Pacu:**
  ```bash
  python secbridge.py --prune-pacu
  ```

- **Iniciar o Dashboard do Pacu:**
  ```bash
  python secbridge.py --pacu-dash
  ```

- **Configurar um Novo Perfil AWS-CLI:**
  ```bash
  python secbridge.py --np
  ```

- **Ajuda:**
  ```bash
  python secbridge.py --help
  ```

## Contribuição

Contribuições são bem-vindas! Se você tem sugestões de melhorias ou encontrou algum bug, sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## Contato

Para mais informações ou perguntas, entre em contato com [Luiz Machado](https://github.com/cryptobr).


Este `README.md` fornece uma visão geral completa da ferramenta SecBridge, incluindo como instalá-la, usá-la, e como contribuir.
