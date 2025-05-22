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

**Este documento deve ser atualizado regularmente com novas decisões e contextos!**
