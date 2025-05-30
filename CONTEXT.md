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

[2025-05-24T02:13:41.902826] Iniciando download do repositório: https://github.com/microsoft/playwright/tree/main/docs/

[2025-05-24T02:13:41.903645] Repositório identificado: github - microsoft/playwright

[2025-05-24T02:13:49.151831] Repositório clonado em: data/temp/playwright

[2025-05-24T02:13:49.151883] Buscando arquivos de documentação em subdiretório: data/temp/playwright/docs

[2025-05-24T02:13:49.155578] Arquivos de documentação encontrados: 0

[2025-05-24T02:14:55.178971] Iniciando download do repositório: https://github.com/microsoft/playwright/tree/main/docs/

[2025-05-24T02:14:55.179767] Repositório identificado: github - microsoft/playwright

[2025-05-24T02:15:01.839255] Repositório clonado em: data/temp/playwright

[2025-05-24T02:15:01.839309] Buscando arquivos de documentação em subdiretório: data/temp/playwright/docs

[2025-05-24T02:15:01.965574] Arquivos de documentação encontrados: 172

[2025-05-24T02:16:21.247277] Iniciando download do repositório: https://github.com/openai/openai-python

[2025-05-24T02:16:21.248037] Repositório identificado: github - openai/openai-python

[2025-05-24T02:16:22.287252] Repositório clonado em: data/temp/openai-python

[2025-05-24T02:16:22.301136] Arquivos de documentação encontrados: 10

[2025-05-24T02:20:35.997542] Iniciando download do repositório: https://github.com/openai/openai-python

[2025-05-24T02:20:35.998297] Repositório identificado: github - openai/openai-python

[2025-05-24T02:20:37.000270] Repositório clonado em: data/temp/openai-python

[2025-05-24T02:20:37.014506] Arquivos de documentação encontrados: 10

[2025-05-24T02:22:12.440051] Iniciando download do repositório: https://github.com/openai/openai-python

[2025-05-24T02:22:12.440799] Repositório identificado: github - openai/openai-python

[2025-05-24T02:22:13.527072] Repositório clonado em: data/temp/openai-python

[2025-05-24T02:22:13.540876] Arquivos de documentação encontrados: 10

[2025-05-24T02:37:41.940076] Iniciando download do repositório: https://github.com/openai/openai-python

[2025-05-24T02:37:41.940789] Repositório identificado: github - openai/openai-python

[2025-05-24T02:37:42.967319] Repositório clonado em: data/temp/openai-python

[2025-05-24T02:37:42.981466] Arquivos de documentação encontrados: 10

[2025-05-24T02:39:36.418817] Iniciando download do repositório: https://github.com/openai/openai-python

[2025-05-24T02:39:36.419602] Repositório identificado: github - openai/openai-python

[2025-05-24T02:39:37.428627] Repositório clonado em: data/temp/openai-python

[2025-05-24T02:39:37.445606] Arquivos de documentação encontrados: 10
