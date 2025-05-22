# Changelog

Todas as mudanças notáveis no projeto DocumentationLLM serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [0.1.2] - 2023-05-24

### Adicionado
- Sistema completo de logging com rotação de arquivos
- Módulo de segurança com validação de URLs e sanitização de inputs
- Proteção contra ataques de injeção de código e path traversal
- Verificação de integridade de arquivos com hashes MD5
- Coleta e armazenamento de metadados detalhados sobre arquivos processados
- Relatórios avançados com estatísticas de arquivos por tipo, tamanho e data

### Melhorado
- Integração entre todos os agentes com o sistema de logging
- Sistema de sincronização de contagem de tokens entre agentes
- Detecção e correção automática da discrepância na contagem de tokens
- Geração de relatórios mais detalhados com informações sobre arquivos
- Estrutura de logging para API com informações de uso de tokens
- Uso consistente de UTF-8 com BOM para compatibilidade ampla em Windows

### Corrigido
- Discrepância na contagem de tokens entre relatórios (agora sincronizados)
- Barra de progresso para operações longas
- Consistência na geração de relatórios entre sistemas operacionais

## [0.1.1] - 2023-05-23

### Corrigido
- Suporte a caminhos relativos para repositórios locais
- Problemas de codificação UTF-8 no Windows (caracteres acentuados em relatórios)
- Discrepância nos tokens reportados entre diferentes relatórios
- Verificações de existência de diretórios no sistema de controle de versão
- Adicionada mensagem de aviso quando nenhum arquivo de documentação é detectado

### Melhorado
- Consistência nos relatórios de uso de tokens e custos
- Código mais robusto para lidar com casos extremos e erros

## [0.1.0] - 2023-05-22

### Adicionado
- Estrutura inicial do projeto com sistema de agentes
- Implementação de conceitos de supervisão por IA
- Arquitetura para preservação de contexto entre explicações e código
- Sistema de monitoramento de tokens e custos
- Configuração flexível de modelos por etapa
- Documentação inicial (README, CONTEXT, CONTRIBUTING, TODO)

### Conceitos Introduzidos
- Pipeline de agentes com supervisão integrada
- Validação automatizada de etapas
- Geração de relatórios de execução
- Análise de tokens e custos
- Preservação de contexto semântico
