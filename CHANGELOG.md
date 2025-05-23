# Changelog

## [Unreleased] - Próximas Atualizações

- Sistema de análise semântica de documentos
- Pipeline de transformação e formatação unificada
- Integração com bases de conhecimento
- Melhorias na geração de embeddings

## [0.1.3] - 2025-05-22

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

## [0.1.2] - 2025-05-10

### Adicionado
- Análise de custos de tokens mais detalhada
- Integração com supervisor para validação de etapas
- Relatórios de execução em markdown e json

### Modificado
- Melhorada a detecção de arquivos de documentação
- Refatorado sistema de logging para mais detalhes

### Corrigido
- Problemas de codificação em arquivos processados
- Bugs relacionados à validação de URLs malformadas
- Extração incorreta de informações de certos repositórios

## [0.1.1] - 2025-04-20

### Adicionado
- CLI com argumentos configuráveis
- Sistema de logging aprimorado
- Gerenciamento de versões e snapshots

### Corrigido
- Problemas de compatibilidade em diferentes sistemas operacionais
- Bugs na extração de metadados de arquivos grandes
- Questões de segurança na manipulação de arquivos externos

## [0.1.0] - 2025-04-01

### Adicionado
- Funcionalidade básica de download de repositórios Git
- Processamento e identificação de arquivos de documentação
- Geração de relatório de arquivos
- Estrutura inicial do pipeline de análise

## [X.X.X] - 2024-05-23

### Adicionado
- Organização dos diretórios de dados por nome de repositório (humanamente legível)
- Limpeza automática de clones antigos antes de novo download
- .gitignore robusto: apenas .gitkeep é versionado em data/originals, data/temp, data/processed
- Documentação atualizada sobre fluxo de dados, limpeza e reprodutibilidade
- TODO para supervisor de histórico de clonagens
