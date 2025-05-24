# Lista de Tarefas - DocumentationLLM

Este arquivo contém um registro de tarefas a serem implementadas e bugs a serem corrigidos no projeto DocumentationLLM.

## Progresso Geral

- [x] Estrutura básica do projeto
- [x] Sistema de download de repositórios
- [x] Sistema de supervisão de agentes
- [x] Sistema de análise de tokens e custos
- [x] Geração de relatórios de execução
- [x] Implementar sistema de logging completo
- [ ] Pipeline completo de processamento de documentação

## Agentes

### Agente de Download (DownloadAgent)
- [x] Implementação básica de download
- [x] Suporte a repositórios Git
- [x] Identificação automática de arquivos de documentação
- [x] Coletar metadados detalhados sobre arquivos processados
- [ ] Suporte a download de documentação de outras fontes (não-Git)
- [ ] Melhorar mecanismo de detecção de documentação relevante

### Agente de Parsing (ParsingAgent)
- [x] Implementação inicial do parser
- [x] Extração de texto e blocos de código
- [x] Identificação de metadados (títulos, seções, etc.)
- [x] Suporte a diferentes formatos (Markdown)
- [x] Estruturação hierárquica do conteúdo extraído
- [ ] Suporte a reStructuredText
- [ ] Suporte a HTML
- [ ] Suporte a texto plano
- [ ] Detecção de relações entre documentos
- [ ] Implementar tracking de linhas para seções
- [ ] Melhorar sanitização de HTML
- [ ] Adicionar suporte a mais metadados
- [ ] Otimizar processamento de documentos grandes

### Agente de Vinculação Semântica (SemanticLinkingAgent)
- [x] Implementação inicial
- [x] Conexão com a API OpenAI para vinculação semântica
- [x] Preservação de contexto entre texto e código
- [x] Estruturação hierárquica de conteúdo
- [x] Implementar cache de prompts/respostas
- [ ] Otimizar uso de tokens
- [ ] Adicionar mais tipos de relações semânticas
- [ ] Melhorar detecção de contexto entre documentos

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
- [x] Integração com sistema de logging
- [ ] Sugestões de melhorias mais detalhadas
- [ ] Correção automática de problemas simples

### Agente de Análise de Tokens (TokenAnalystAgent)
- [x] Implementação inicial
- [x] Cálculo de custos por modelo
- [x] Geração de relatórios de uso
- [x] Correção da discrepância de contagem de tokens
- [ ] Sugestões mais detalhadas de otimização

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
- [x] Verificação de existência de diretórios
- [ ] Comparação visual de diferenças

### Logging
- [x] Logger básico
- [x] Colorização de output
- [x] Rotação de logs
- [x] Logging detalhado de arquivos processados
- [x] Logging estruturado de chamadas de API
- [ ] Interface web para visualização (futuro)

## Otimização e Melhoria

### Performance
- [ ] Paralelização de downloads
- [ ] Cache de chamadas à API
- [ ] Otimização de prompts para reduzir tokens

### Segurança
- [x] Sanitização de inputs
- [x] Validação de URLs
- [x] Proteção contra injeção de código
- [x] Verificação de integridade de arquivos

### Testes
- [x] Testes unitários para SemanticLinkingAgent
- [x] Mock da API OpenAI
- [x] Testes de tratamento de erros
- [ ] Testes de integração
- [ ] Testes de performance
- [ ] Testes de carga
- [ ] CI/CD setup

## Bugs Conhecidos

- [✓] Problema ao processar variáveis de ambiente com comentários
- [✓] Erro ao tentar baixar repositório com URL incorreta (adicionado tratamento de erro)
- [✓] O agente de análise de tokens não está registrando tokens usados corretamente
- [✓] Problemas com encodings em alguns sistemas operacionais
- [✓] Problema: CLI `docllm` falha com `ModuleNotFoundError` - Resolvido criando wrapper documentationllm.cli
- [✓] Codificação incorreta de caracteres Unicode em relatórios no Windows (exibindo "RelatÃ³rio" em vez de "Relatório") - Resolvido usando UTF-8 com BOM
- [✓] Caminho relativo para repositórios não funciona (apenas URLs de Git completas são aceitas) - Resolvido com suporte a diretórios locais
- [✓] Discrepância nos tokens reportados (relatório de token mostra 0 enquanto relatório de execução mostra 433) - Resolvido com sistema de sincronização de contagem

## Melhorias Propostas

- [✓] Adicionar suporte completo para caminhos relativos de repositórios locais
- [✓] Corrigir problemas de codificação em sistemas Windows
- [✓] Registrar corretamente o tempo de execução de cada etapa para otimização
- [✓] Melhorar a detecção de codificação UTF-8 nos relatórios gerados
- [✓] Adicionar mais detalhes nos relatórios sobre arquivos processados (nome, tamanho, tipo)
- [ ] Implementar a etapa de parsing de documentação (atualmente apenas download funciona)
- [ ] Priorizar suporte a formatos Markdown e HTML no parser

## Próximos Passos

### Implementação do Agente de Parsing
1. [ ] Desenvolver estrutura base do agente
2. [ ] Implementar detecção de formato (Markdown, reStructuredText, HTML)
3. [ ] Desenvolver parser específico para Markdown
4. [ ] Extrair e estruturar conteúdo (títulos, subtítulos, parágrafos, listas, blocos de código)
5. [ ] Processar metadados e referências cruzadas entre documentos
6. [ ] Integrar com o pipeline existente

### Aprimoramento de Segurança
1. [x] Implementar validação robusta de URLs
2. [x] Sanitização de inputs para evitar injeções
3. [x] Proteção contra path traversal
4. [x] Validação de integridade de arquivos
5. [ ] Adicionar testes de penetração para validar segurança

### Implementar supervisor de histórico de clonagens
- [ ] Implementar supervisor de histórico de clonagens: registrar em memória/arquivo quantas vezes cada repositório foi clonado e em quais datas, para uso futuro por uma IA administradora.

### Sistema de Cache
- [x] Implementação básica do cache
- [x] Cache em memória e disco
- [x] TTL configurável
- [x] Estatísticas e métricas
- [x] Integração com SemanticLinkingAgent
- [ ] Persistência assíncrona
- [ ] Compressão de dados
- [ ] Backup automático
- [ ] Dashboard de métricas

---

## [Automação e Execução por Agentes]

- Manter sempre atualizada a sequência de comandos funcionais para setup e uso do projeto.
- Documentar execuções automatizadas, erros e aprendizados nos arquivos de contexto (CONTEXT.md, CHANGELOG.md, etc.).
- Garantir que o README.md oriente agentes a lerem os arquivos de contexto após o clone.
- Registrar qualquer erro de importação, instalação ou execução para facilitar troubleshooting por agentes futuros.

---

Este arquivo será atualizado regularmente conforme o projeto evolui e novas ideias surgem.
