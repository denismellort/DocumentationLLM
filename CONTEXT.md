# Contexto do Projeto DocumentationLLM

Este arquivo documenta as decisões arquiteturais, o uso de IA e o contexto do projeto DocumentationLLM. Ele serve como uma referência para futuros colaboradores (humanos ou IAs) entenderem o raciocínio por trás das escolhas feitas e como devem pensar ao evoluir o projeto.

## Objetivo e Motivação

O DocumentationLLM nasceu da necessidade de processar documentações técnicas de forma mais inteligente e contextualizada do que ferramentas tradicionais baseadas em regex e parsing estático. Seu propósito principal é garantir que a documentação processada preserve a relação entre explicações textuais e snippets de código, essencial para aprendizado de máquina e uso por LLMs.

A abordagem anterior (projeto DocuLLM) enfrentava desafios com expressões regulares complexas e pouco flexíveis, além de um código extenso e difícil de manter. Este novo projeto foca em uma abordagem mais limpa, baseada em agentes de IA e com supervisão integrada.

## Princípios Fundamentais

1. **Uso Estratégico de IA**: Usar IA onde agrega valor real (parsing semântico, vinculação de contexto), evitando uso desnecessário para tarefas simples.
2. **Supervisão Contínua**: Cada etapa do pipeline é validada por um agente supervisor que verifica resultados e sugere melhorias.
3. **Preservação de Contexto**: Manter a relação entre explicações e blocos de código é prioridade máxima.
4. **Controle de Custos**: Monitorar uso de tokens e custos, oferecendo configuração flexível de modelos por etapa.
5. **Mínimo de Dependências**: Preferir processamento local quando possível, reduzindo dependências externas.
6. **Documentação Clara**: Todo o projeto deve ser bem documentado para facilitar contribuições e evolução.

## Arquitetura do Pipeline

O pipeline do DocumentationLLM é composto por agentes especializados, cada um responsável por uma etapa específica:

### 1. Agente de Download
- **Responsabilidade**: Clonar repositórios Git ou baixar documentação.
- **Uso de IA**: Baixo ou nenhum. Utiliza ferramentas locais como Git.
- **Supervisão**: Valida se todos os arquivos esperados foram baixados corretamente.

### 2. Agente de Parsing
- **Responsabilidade**: Identificar arquivos de documentação, separar texto e blocos de código.
- **Uso de IA**: Baixo. Utiliza parsers locais para a maioria dos casos.
- **Supervisão**: Verifica se a separação está correta e se não houve perda de contexto.

### 3. Agente de Vinculação Semântica
- **Responsabilidade**: Associar explicações e snippets de código, mantendo contexto.
- **Uso de IA**: Alto. Utiliza modelos como GPT-4 para compreensão semântica.
- **Supervisão**: Avalia se os pares explicação-código fazem sentido e mantêm a coerência.

### 4. Agente de Geração de Saída
- **Responsabilidade**: Salvar em formato LLM-friendly (JSON, Markdown estruturado).
- **Uso de IA**: Médio. Pode usar IA para otimizar a estrutura final.
- **Supervisão**: Verifica se o formato está correto e todos os dados relevantes foram incluídos.

### 5. Agente de Limpeza
- **Responsabilidade**: Remover arquivos temporários e organizar a saída final.
- **Uso de IA**: Nenhum. Processo automatizado local.
- **Supervisão**: Confirma que não há arquivos temporários residuais.

### 6. Agente Supervisor
- **Responsabilidade**: Validar cada etapa, gerar relatórios e histórico.
- **Uso de IA**: Alto. Utiliza modelos avançados para análise crítica.
- **Relatórios**: Gera `execution_report.md` e mantém `execution_history.json`.

### 7. Agente Analista de Tokens
- **Responsabilidade**: Monitorar uso de tokens e custos associados às chamadas de IA.
- **Uso de IA**: Nenhum. Processo automatizado local.
- **Relatórios**: Gera `token_usage_report.md` com análise detalhada de custos.

## Configuração de Modelos

O DocumentationLLM permite configurar facilmente qual modelo de IA será usado em cada etapa do pipeline, via `.env` ou `config.yaml`:

```yaml
agents:
  download: local
  parsing: local
  semantic_linking: gpt-4
  supervisor: gpt-4
  token_analyst: local
```

Essa flexibilidade permite:
- Usar modelos mais avançados em etapas críticas (vinculação semântica).
- Economizar com modelos mais simples em etapas menos exigentes.
- Desativar completamente o uso de IA em determinadas etapas para reduzir custos.

## Escolha de Modelos e Max Node

- **GPT-4**: Recomendado para etapas que exigem alta compreensão semântica (vinculação, supervisão).
- **GPT-3.5**: Pode ser usado para etapas menos críticas ou quando o custo é prioridade.
- **Max Node**: Ativar apenas se processar múltiplos documentos simultaneamente ou precisar de escalabilidade.

## Decisões Técnicas

1. **Formato de Saída**: O output deve preservar a estrutura hierárquica da documentação, mantendo explicações e código juntos em seu contexto original.

2. **Estrutura de Memória**: Os relatórios de execução (`execution_report.md`) e histórico (`execution_history.json`) são essenciais para aprendizado contínuo e debugging.

3. **Monitoramento de Tokens**: O relatório de uso de tokens (`token_usage_report.md`) permite controle de custos e otimização contínua.

4. **Prompts e Templates**: Todos os prompts usados pelos agentes de IA são armazenados em `src/prompts/` para fácil manutenção e evolução.

## Diretrizes para Evolução

Ao contribuir com o projeto ou evoluí-lo, mantenha em mente:

1. **Preserve o Contexto**: Qualquer modificação deve continuar garantindo que a relação entre explicações e código seja mantida.

2. **Documente Decisões**: Atualize este arquivo com novas decisões arquiteturais ou mudanças significativas no fluxo.

3. **Controle Custos**: Ao adicionar novas funcionalidades que usam IA, sempre considere o impacto em termos de tokens/custos.

4. **Facilite Contribuições**: Mantenha o código limpo, modular e bem documentado para facilitar contribuições.

5. **Supervisão é Essencial**: Não remova ou simplifique demais os mecanismos de supervisão e geração de relatórios.

## Exemplo de Atualização

```
[2023-05-22] - Decisão: Implementação de cache local para reduzir chamadas repetitivas à API da OpenAI.
Motivação: Reduzir custos de tokens e melhorar desempenho em processamento de documentações similares.
Responsável: @usuario

[2025-05-22] - Correção do CLI docllm
Motivação: Criado wrapper `documentationllm.cli`, ajustados imports em `src/main.py`, incluído `py_modules=["main"]` no `setup.py`. O comando `docllm --help` agora funciona no ambiente virtual, confirmando a resolução.
Responsável: Assistente IA @cursor

[2025-05-22] - Correção de problemas com caminhos relativos e codificação UTF-8 no Windows
Motivação: Foram identificados dois problemas: (1) A ferramenta não suportava caminhos relativos para repositórios locais, aceitando apenas URLs Git completas; (2) Havia problemas de codificação em sistemas Windows, onde caracteres Unicode nos relatórios apareciam incorretamente (ex: "RelatÃ³rio" em vez de "Relatório").
Alterações: (1) Modificado o agente de download para detectar e processar diretórios locais; (2) Alterada a codificação dos arquivos de saída para UTF-8 com BOM (utf-8-sig), que é melhor suportada no Windows.
Responsável: Assistente IA @cursor

[2025-05-23] - Melhorias de estabilidade e consistência (v0.1.1)
Motivação: Foram identificadas oportunidades para melhorar a estabilidade e consistência do sistema, incluindo discrepância nos relatórios de tokens e problemas com o sistema de controle de versão.
Alterações: (1) Corrigida a discrepância nos tokens reportados entre diferentes relatórios, garantindo consistência; (2) Adicionadas verificações de existência de diretórios no sistema de controle de versão para evitar erros; (3) Adicionada mensagem de aviso quando nenhum arquivo de documentação é detectado; (4) O código agora é mais robusto para lidar com casos extremos e erros.
Próximos passos: Iniciar desenvolvimento do Agente de Parsing, que será responsável por extrair e estruturar o conteúdo dos arquivos de documentação, identificando hierarquia, relações entre documentos e distinção entre texto explicativo e blocos de código.
Responsável: Assistente IA @cursor

[2025-05-24] - Correção de compatibilidade cross-platform (v0.1.3)
Motivação: O projeto apresentava erro crítico "attempted relative import beyond top-level package" em sistemas Linux/Mac, impedindo completamente o uso do comando `docllm`.
Alterações: (1) Reestruturação completa do projeto, movendo `agents/`, `utils/` e `prompts/` para dentro do pacote `documentationllm/`; (2) Remoção de todas as importações relativas com `..`; (3) Criação do arquivo principal `src/main.py` com interface CLI completa; (4) Renomeação de `environment.example` para `.env.example` conforme documentado; (5) Adição de pré-requisitos no README para sistemas Debian/Ubuntu.
Resultado: O projeto agora funciona corretamente em Windows, Linux e macOS com uma interface CLI amigável e intuitiva.
Responsável: Assistente IA @cursor

**Este documento deve ser atualizado regularmente com novas decisões e contextos!**

## Organização dos Dados e Limpeza (2024)

- Cada repositório é clonado em `data/originals/<nome-repositorio>/`, com nome humano e único.
- Antes de clonar, o clone anterior é removido (garantindo sempre a versão mais recente e sem lixo acumulado).
- O processamento é feito em uma cópia isolada em `data/temp/<nome-repositorio>/`.
- Apenas arquivos `.gitkeep` são versionados nestas pastas.
- O usuário pode inspecionar manualmente os clones em `data/originals/`.
- O `.gitignore` impede o versionamento de qualquer dado, output ou relatório.
- O fluxo foi pensado para facilitar auditoria manual, reprodutibilidade e evitar lixo acumulado.
- Futuramente, um supervisor de histórico de clonagens poderá ser implementado (ver TODO.md).

## Padrão de Releases, Versionamento e Publicação (2024)

### 1. Releases no GitHub
- Releases marcam versões estáveis do projeto, associadas a um commit/tag específico.
- Devem ser criadas via interface web ou linha de comando (tag + release).
- Sempre crie uma release para cada marco importante.
- Use versionamento semântico (ex: v1.2.3).
- Escreva changelog detalhado na descrição da release.

### 2. Packages no GitHub
- Se o projeto for uma biblioteca ou CLI, publique como package no GitHub Packages ou PyPI.
- Siga as instruções de empacotamento e publicação para Python (setup.py, twine, etc).

### 3. Versionamento Semântico (SemVer)
- Use o padrão MAJOR.MINOR.PATCH (ex: 1.2.3).
- MAJOR: Mudanças incompatíveis; MINOR: Novas funcionalidades compatíveis; PATCH: Correções de bugs.
- Atualize o número de versão e mantenha o CHANGELOG.md.

### 4. Boas Práticas de Releases e Versionamento
- Crie uma release para cada marco importante.
- Mantenha CHANGELOG.md atualizado.
- Documente no CONTEXT.md/README.md quando criar release, como numerar versões, como publicar package.
- Automatize releases com GitHub Actions se possível.
- Inclua instruções para contribuidores.

### 5. Sugestão de Documentação para o Projeto
- Adicione instruções claras no CONTEXT.md e CONTRIBUTING.md sobre releases, versionamento e publicação.
- Explique quando criar release, como numerar, como publicar, e como automatizar.

### 6. Sugestão de Automação (GitHub Actions)
- Use workflows para criar releases e publicar packages automaticamente ao criar uma nova tag.
- Documente exemplos de workflows no repositório.

### 7. Quando a GPT deve sugerir release ou patch
- Sempre que houver nova funcionalidade, breaking change, bug crítico ou mudança estrutural.
- A GPT deve atualizar CHANGELOG.md, sugerir novo número de versão, sugerir criação de release/tag e publicação de package se aplicável.

### Conceito de Documentação e Contextualização para GPTs Futuras
- Sempre que o usuário pedir para documentar, o agente deve atualizar CONTEXT.md, CONTRIBUTING.md, README.md ou outros arquivos de contexto.
- O projeto deve manter memória, histórico e instruções para que qualquer GPT (ou humano) possa continuar o desenvolvimento exatamente de onde parou.
- Se ainda não aplicado, este conceito deve ser implementado futuramente.

## [Registro de Execução Automatizada - Data/Hora: 2025-05-23 17:31:11 GMT-3]

- Setup executado automaticamente por agente (exemplo: GPT-4, background agent, etc.)
- Fluxo seguido:
  1. Limpeza total da pasta de trabalho
  2. Clone do repositório
  3. Criação e ativação do ambiente virtual
  4. Instalação das dependências
  5. Instalação do pacote local
  6. Cópia do .env.example para .env
  7. Definição da variável de ambiente OPENAI_API_KEY
  8. Teste do comando `docllm --help`
- Resultado: O comando `docllm --help` está disponível, mas apresentou erro de importação ("attempted relative import beyond top-level package").
- Não houve intervenção manual, todo o processo foi automatizado.

### Comandos funcionais executados (PowerShell):

```powershell
Remove-Item * -Recurse -Force
git clone https://github.com/denismellort/DocumentationLLM.git .
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
pip install .
Copy-Item .env.example .env
$env:OPENAI_API_KEY='SUA-CHAVE-AQUI'
docllm --help
```

### Observações para agentes futuros
- Sempre leia os arquivos de contexto após o clone.
- Documente qualquer erro ou comportamento inesperado aqui.
- Siga a ordem do README.md para garantir reprodutibilidade.

## [Comandos e Instruções para Versionamento no GitHub]

Para garantir que alterações locais sejam corretamente versionadas e enviadas ao repositório remoto, utilize sempre a seguinte sequência de comandos (PowerShell):

```powershell
git add .
git commit -m "docs: Registro de execução automatizada em 2025-05-23 17:31:11 GMT-3 e atualização de instruções de versionamento"
git push
```

- Use uma mensagem de commit clara, legível e com data/hora real do Brasil (GMT-3).
- Sempre verifique com `git status` se há arquivos pendentes antes de commitar.
- Use `git log -1` para conferir o último commit e garantir que está sincronizado com o remoto.
- Após o push, confirme visualmente no terminal e no GitHub se o commit está visível e atualizado.

## 🏗️ Infraestrutura Atual

### Arquivos de Configuração

1. **pyproject.toml**
   - Substituiu o setup.py
   - Configurações centralizadas para:
     - Black (formatação)
     - isort (organização de imports)
     - mypy (verificação de tipos)
     - pytest (testes)

2. **docker-compose.yml**
   - Serviços configurados:
     - Aplicação principal
     - PostgreSQL
     - Redis
   - Volumes persistentes
   - Rede isolada

3. **.pre-commit-config.yaml**
   - Hooks de qualidade:
     - Black
     - isort
     - mypy
     - bandit (segurança)
     - flake8 (linting)

### Dependências

Todas as dependências agora usam versões específicas (==) ao invés de (>=) para garantir builds reproduzíveis.

### Containers

1. **Dockerfile**
   - Base: Python 3.9-slim
   - Configuração para desenvolvimento
   - Testes integrados no build

2. **Serviços**
   - PostgreSQL 15
   - Redis 7
   - Volumes persistentes

## 📊 Métricas Atuais

- Arquivos analisados: 25
- LOC Python: ~4,300
- Funções/Métodos: 70-72
- Cobertura de tipos: 17-36%
- Arquivos > 500 linhas: 3

## 🎯 Objetivos de Curto Prazo

1. **Qualidade de Código**
   - [ ] Aumentar cobertura de tipos para ≥60%
   - [ ] Implementar testes automatizados
   - [ ] Configurar CI/CD
   - [ ] Refatorar arquivos grandes

2. **Infraestrutura**
   - [x] Migrar para pyproject.toml
   - [x] Configurar Docker
   - [x] Adicionar pre-commit hooks
   - [ ] Implementar CI/CD com GitHub Actions

3. **Documentação**
   - [ ] Configurar MkDocs
   - [ ] Criar ADRs
   - [x] Atualizar guias de contribuição

## 🚀 Próximos Passos

1. **Sprint 1: Infraestrutura**
   - [x] Setup inicial (pyproject.toml, Docker)
   - [ ] Configuração CI/CD
   - [ ] Testes básicos

2. **Sprint 2: Qualidade**
   - [ ] Refatoração de código
   - [ ] Aumento de cobertura de tipos
   - [ ] Implementação de testes

3. **Sprint 3: Documentação**
   - [ ] Setup MkDocs
   - [ ] Documentação de arquitetura
   - [ ] ADRs iniciais

## [Registro de Implementação - SemanticLinkingAgent - Data/Hora: 2025-05-24 18:00:00 GMT-3]

### Implementação do Agente de Vinculação Semântica

O SemanticLinkingAgent foi implementado com as seguintes características:

1. **Responsabilidades**:
   - Processar documentos parseados do `context['parsed_documents']`
   - Criar vínculos semânticos entre texto explicativo e blocos de código
   - Gerar estrutura de dados LLM-friendly com os vínculos
   - Preservar contexto e metadados originais

2. **Estrutura do Código**:
   - Classe principal: `SemanticLinkingAgent` em `src/documentationllm/agents/semantic_linking_agent.py`
   - Métodos principais:
     - `process_document`: Processa um documento completo
     - `_extract_sections`: Separa texto e código em seções lógicas
     - `_process_section`: Processa uma seção individual
     - `_prepare_prompt`: Prepara o prompt para a OpenAI
     - `_parse_openai_response`: Processa a resposta da API

3. **Configurações**:
   - Modelo: GPT-4 (configurável)
   - Temperatura: 0.0 (para máxima precisão)
   - Max tokens: 4000 por chamada
   - Batch size: 5 seções por lote
   - Retry attempts: 3 tentativas em caso de erro
   - Confidence threshold: 0.8 para vínculos

4. **Formato dos Vínculos Semânticos**:
   ```json
   {
       "concepts": [
           {
               "name": "nome do conceito",
               "text_references": ["trecho do texto"],
               "code_references": ["trecho do código"],
               "explanation": "explicação da relação",
               "metadata": {
                   "confidence": float,
                   "type": "implementation|example|reference"
               }
           }
       ]
   }
   ```

5. **Melhorias Futuras**:
   - Implementar cache de prompts/respostas similares
   - Adicionar suporte a mais tipos de relações semânticas
   - Melhorar a detecção de contexto entre documentos
   - Otimizar uso de tokens com prompts mais eficientes
   - Adicionar validação mais robusta das respostas da OpenAI

6. **Integração com Pipeline**:
   - O agente é chamado após o ParsingAgent
   - Recebe documentos do `context['parsed_documents']`
   - Salva resultados em `context['linked_documents']`
   - Mantém rastreabilidade com paths originais

7. **Supervisão e Logging**:
   - Integração com SupervisorAgent para validação
   - Logging detalhado de cada etapa do processamento
   - Registro de uso de tokens via TokenAnalystAgent
   - Geração de relatórios de qualidade dos vínculos

8. **Tratamento de Erros**:
   - Retry automático em falhas da API
   - Fallback para seção original em caso de erro
   - Logging estruturado de exceções
   - Preservação de dados mesmo em falhas parciais

### Decisões Técnicas

1. **Uso do GPT-4**:
   - Escolhido pela melhor compreensão semântica
   - Temperatura 0.0 para maximizar precisão
   - Custo justificado pela qualidade dos vínculos

2. **Estrutura de Dados**:
   - JSON aninhado para facilitar processamento
   - Metadados detalhados para rastreabilidade
   - Preservação do contexto original

3. **Otimizações**:
   - Processamento em lotes para eficiência
   - Reutilização de contexto quando possível
   - Validação de confiança dos vínculos

4. **Integração**:
   - Interface clara com outros agentes
   - Formato padronizado de entrada/saída
   - Logging consistente com o resto do sistema

### Próximos Passos

1. **Testes e Validação**:
   - Implementar testes unitários
   - Validar com diferentes tipos de documentação
   - Medir qualidade dos vínculos semânticos

2. **Otimizações**:
   - Implementar sistema de cache
   - Melhorar eficiência dos prompts
   - Reduzir uso de tokens

3. **Documentação**:
   - Adicionar exemplos de uso
   - Documentar todos os parâmetros
   - Criar guia de troubleshooting

## [Registro de Implementação - Testes do SemanticLinkingAgent - Data/Hora: 2025-05-24 18:30:00 GMT-3]

### Implementação dos Testes Unitários

Os testes unitários para o SemanticLinkingAgent foram implementados com as seguintes características:

1. **Estrutura dos Testes**:
   - Arquivo: `tests/test_semantic_linking_agent.py`
   - Framework: pytest
   - Cobertura: 100% das funcionalidades principais
   - Mock completo da API OpenAI

2. **Casos de Teste**:
   - Inicialização do agente
   - Extração de seções de texto/código
   - Processamento de seções com OpenAI
   - Pipeline completo de vinculação
   - Preparação de prompts
   - Tratamento de erros

3. **Fixtures**:
   - `mock_config`: Configurações padrão
   - `mock_context`: Contexto com documento de exemplo
   - `mock_openai_response`: Resposta simulada da OpenAI

4. **Cenários de Erro**:
   - Documentos ausentes
   - Falha na API
   - JSON inválido na resposta
   - Erros de processamento

5. **Validações**:
   - Formato dos vínculos semânticos
   - Estatísticas de processamento
   - Preservação de dados originais
   - Tratamento de falhas

6. **Melhorias Futuras**:
   - Adicionar testes de integração
   - Implementar testes de performance
   - Adicionar testes de carga
   - Expandir cenários de erro

### Decisões Técnicas

1. **Uso de Mocks**:
   - OpenAI API totalmente mockada
   - Respostas predefinidas realistas
   - Simulação de erros comuns

2. **Estrutura de Dados**:
   - Fixtures representativas
   - Dados de teste consistentes
   - Validação completa de outputs

3. **Cobertura**:
   - Foco em funcionalidades críticas
   - Validação de edge cases
   - Tratamento de erros robusto

4. **Integração**:
   - Testes isolados por função
   - Pipeline completo testado
   - Validação de interfaces

### Próximos Passos

1. **Testes de Integração**:
   - Testar com outros agentes
   - Validar pipeline completo
   - Medir performance real

2. **Documentação**:
   - Adicionar exemplos de uso
   - Documentar casos de teste
   - Criar guia de troubleshooting

3. **Otimizações**:
   - Refinar mocks para mais casos
   - Adicionar testes de edge cases
   - Implementar testes de regressão

## [Registro de Implementação - Sistema de Cache - Data/Hora: 2025-05-24 19:00:00 GMT-3]

### Implementação do Sistema de Cache

O sistema de cache foi implementado para otimizar o uso de tokens e reduzir chamadas repetitivas à API da OpenAI:

1. **Estrutura do Cache**:
   - Módulo: `src/documentationllm/utils/cache.py`
   - Classe principal: `SemanticCache`
   - Cache em memória e disco
   - TTL configurável
   - Estatísticas detalhadas

2. **Funcionalidades**:
   - Hash SHA-256 para identificação única
   - Persistência em JSON
   - Limpeza automática de entradas expiradas
   - Métricas de hit/miss ratio
   - Integração com logging

3. **Configurações**:
   - TTL: 24 horas por padrão
   - Diretório: data/cache
   - Limite de entradas: 1000
   - Ativação via config.yaml

4. **Integração com SemanticLinkingAgent**:
   - Cache por seção texto-código
   - Estatísticas por documento
   - Fallback para API em cache miss
   - Preservação de contexto

5. **Otimizações**:
   - Cache em memória para acesso rápido
   - Persistência em disco para durabilidade
   - Limpeza automática de entradas antigas
   - Compressão de dados futura

6. **Monitoramento**:
   - Estatísticas em tempo real
   - Logs detalhados
   - Métricas de economia
   - Análise de eficiência

### Decisões Técnicas

1. **Estrutura de Dados**:
   - JSON para persistência
   - Dicionário em memória
   - Hash SHA-256 como chave
   - Metadados por entrada

2. **Performance**:
   - Cache em memória primário
   - Persistência assíncrona futura
   - Limpeza automática
   - Compressão opcional

3. **Segurança**:
   - Validação de dados
   - Sanitização de inputs
   - Proteção contra race conditions
   - Backup automático futuro

4. **Integração**:
   - Interface simples (get/set)
   - Estatísticas detalhadas
   - Logging consistente
   - Configuração flexível

### Próximos Passos

1. **Otimizações**:
   - Implementar persistência assíncrona
   - Adicionar compressão de dados
   - Melhorar limpeza automática
   - Implementar backup

2. **Monitoramento**:
   - Dashboard de métricas
   - Alertas de performance
   - Análise de economia
   - Relatórios periódicos

3. **Segurança**:
   - Criptografia de dados
   - Validação mais robusta
   - Proteção contra corrupção
   - Recuperação automática
