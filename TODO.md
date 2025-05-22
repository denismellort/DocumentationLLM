# Lista de Tarefas - DocumentationLLM

Este arquivo contém um registro de tarefas a serem implementadas e bugs a serem corrigidos no projeto DocumentationLLM.

## Progresso Geral

- [x] Estrutura básica do projeto
- [x] Sistema de download de repositórios
- [x] Sistema de supervisão de agentes
- [x] Sistema de análise de tokens e custos
- [x] Geração de relatórios de execução
- [ ] Implementar sistema de logging completo
- [ ] Pipeline completo de processamento de documentação

## Agentes

### Agente de Download (DownloadAgent)
- [x] Implementação básica de download
- [x] Suporte a repositórios Git
- [x] Identificação automática de arquivos de documentação
- [ ] Suporte a download de documentação de outras fontes (não-Git)
- [ ] Melhorar mecanismo de detecção de documentação relevante

### Agente de Parsing (ParsingAgent)
- [ ] Implementação inicial do parser
- [ ] Extração de texto e blocos de código
- [ ] Identificação de metadados (títulos, seções, etc.)
- [ ] Suporte a diferentes formatos (Markdown, reStructuredText, HTML)

### Agente de Vinculação Semântica (SemanticLinkingAgent)
- [ ] Implementação inicial
- [ ] Conexão com a API OpenAI para vinculação semântica
- [ ] Preservação de contexto entre texto e código
- [ ] Estruturação hierárquica de conteúdo

### Agente de Geração de Saída (OutputGenerationAgent)
- [ ] Implementação inicial
- [ ] Geração de saída em formato LLM-friendly
- [ ] Suporte a JSON estruturado
- [ ] Suporte a Markdown com metadados

### Agente de Limpeza (CleanupAgent)
- [ ] Implementação inicial
- [ ] Remoção de arquivos temporários
- [ ] Organização da saída conforme configuração

### Agente Supervisor (SupervisorAgent)
- [x] Implementação inicial
- [x] Validação de etapas do pipeline
- [x] Geração de relatórios e histórico
- [ ] Sugestões de melhorias mais detalhadas
- [ ] Correção automática de problemas simples

### Agente de Análise de Tokens (TokenAnalystAgent)
- [x] Implementação inicial
- [x] Cálculo de custos por modelo
- [x] Geração de relatórios de uso
- [ ] Sugestões mais detalhadas de otimização
- [ ] Problema: Não está registrando uso real de tokens da API OpenAI

## Funcionalidades Gerais

### Configuração e Setup
- [x] Carregamento de configurações via YAML
- [x] Carregamento de variáveis de ambiente
- [x] Sistema para lidar com comentários nas variáveis de ambiente
- [ ] Validação mais robusta de configurações

### Interface de Linha de Comando
- [x] Argumentos básicos
- [x] Suporte a flags de verbosidade
- [ ] Interface interativa para configuração
- [ ] Barra de progresso melhorada

### Sistema de Controle de Versão
- [x] Criação de snapshots do código
- [x] Rollback para versões anteriores
- [ ] Comparação visual de diferenças

### Logging
- [x] Logger básico
- [x] Colorização de output
- [ ] Rotação de logs
- [ ] Interface web para visualização (futuro)

## Otimização e Melhoria

### Performance
- [ ] Paralelização de downloads
- [ ] Cache de chamadas à API
- [ ] Otimização de prompts para reduzir tokens

### Segurança
- [ ] Sanitização de inputs
- [ ] Validação de URLs
- [ ] Proteção contra injeção de código

### Testes
- [ ] Testes unitários
- [ ] Testes de integração
- [ ] CI/CD setup

## Bugs Conhecidos

- [✓] Problema ao processar variáveis de ambiente com comentários
- [✓] Erro ao tentar baixar repositório com URL incorreta (adicionado tratamento de erro)
- [⚠️] O agente de análise de tokens não está registrando tokens usados corretamente
- [ ] Problemas com encodings em alguns sistemas operacionais
- [✓] Problema: CLI `docllm` falha com `ModuleNotFoundError` - Resolvido criando wrapper documentationllm.cli

---

Este arquivo será atualizado regularmente conforme o projeto evolui e novas ideias surgem.
