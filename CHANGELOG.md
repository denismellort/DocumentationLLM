# Changelog

Todas as mudanças notáveis deste projeto serão documentadas aqui.

## [Unreleased]
- (Liste aqui o que está em desenvolvimento ou planejado)

## [0.2.0] - 2025-05-23
### Adicionado
- Organização dos diretórios de dados por nome de repositório (humanamente legível)
- Limpeza automática de clones antigos antes de novo download
- .gitignore robusto: apenas .gitkeep é versionado em data/originals, data/temp, data/processed
- Documentação atualizada sobre fluxo de dados, limpeza e reprodutibilidade
- TODO para supervisor de histórico de clonagens
- Padrão de releases, versionamento e contextualização para GPTs e humanos

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
