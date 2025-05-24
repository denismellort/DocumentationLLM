# Changelog

Todas as mudanças notáveis deste projeto serão documentadas aqui.

## [Unreleased]
### Adicionado
- Implementação inicial do ParsingAgent para processamento de documentação
- Suporte a parsing de arquivos Markdown com extração de estrutura
- Funções de segurança aprimoradas para processamento de conteúdo
- Integração do ParsingAgent no pipeline principal
- Novas dependências: markdown, beautifulsoup4, docutils

### Modificado
- Refatoração do módulo de segurança com novas funções
- Atualização do pipeline principal para incluir etapa de parsing
- Melhorias na estrutura de logging e tratamento de erros

## [0.2.0] - 2025-05-23
### Adicionado
- Organização dos diretórios de dados por nome de repositório (humanamente legível)
- Limpeza automática de clones antigos antes de novo download
- .gitignore robusto: apenas .gitkeep é versionado em data/originals, data/temp, data/processed
- Documentação atualizada sobre fluxo de dados, limpeza e reprodutibilidade
- TODO para supervisor de histórico de clonagens
- Padrão de releases, versionamento e contextualização para GPTs e humanos

## [0.1.3] - 2025-05-24

### Corrigido
- **Problema crítico de importação em Linux/Mac**: Reestruturado o projeto movendo `agents/`, `utils/` e `prompts/` para dentro do pacote `documentationllm/`
- **Importações relativas removidas**: Eliminadas todas as importações relativas com `..` que causavam erro "attempted relative import beyond top-level package"
- **Nome do arquivo de configuração**: Renomeado `environment.example` para `.env.example` conforme documentado no README
- **Interface CLI melhorada**: Agora o comando `docllm` mostra uma interface amigável quando executado sem argumentos
- **Compatibilidade cross-platform**: O projeto agora funciona corretamente em Windows, Linux e macOS

### Adicionado
- **Pré-requisitos no README**: Documentada a necessidade de instalar `python3-venv` em sistemas Debian/Ubuntu
- **Arquivo principal `src/main.py`**: Criado arquivo principal do pipeline com interface completa

### Alterado
- **Estrutura de diretórios**: Reorganizada para seguir as melhores práticas de empacotamento Python
- **Arquivo `cli.py` simplificado**: Removida lógica de tratamento de erros desnecessária

## [0.1.2] - 2025-05-22
### Adicionado
- Detecção inteligente e dinâmica de diretórios de documentação
- Suporte para arquivos .mdx (Markdown com JSX)
- Limpeza automática de arquivos temporários após processamento
- Carregamento automático do arquivo config.yaml da raiz

### Modificado
- Melhorada a estratégia de busca de arquivos de documentação com análise heurística
- Corrigida a geração de relatório de tokens quando não há tokens usados
- Ajustado o CLI para melhor localização do main.py independente da forma de instalação

### Corrigido
- Problema na detecção de documentação em repositórios com estruturas não convencionais
- Bug do caminho incorreto no CLI após instalação como pacote
- Valor fixo incorreto de custo quando não há tokens
- Diretórios temporários não eram limpos após o processamento

## [0.1.0] - 2025-05-21
### Adicionado
- Versão inicial do projeto
- Download de repositórios Git
- Identificação e processamento básico de arquivos de documentação
- Geração de relatórios iniciais

## [0.1.4] - 2025-05-24

### Adicionado
- Implementação completa do SemanticLinkingAgent
  - Processamento de documentos parseados com GPT-4
  - Vinculação semântica entre texto e código
  - Configurações flexíveis via config.yaml
  - Integração com pipeline principal
  - Logging detalhado e tratamento de erros
  - Estatísticas de processamento
- Novas configurações no config.yaml para o SemanticLinkingAgent
- Documentação atualizada no CONTEXT.md

### Alterado
- Pipeline principal agora inclui etapa de vinculação semântica
- Ordem das etapas ajustada para acomodar o novo agente
- Melhorias na documentação e logs

### Corrigido
- Problemas de tipagem no SemanticLinkingAgent
- Integração com outros agentes no pipeline
