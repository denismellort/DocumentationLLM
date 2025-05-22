# DocumentationLLM

![Versão](https://img.shields.io/badge/versão-0.2.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![Licença](https://img.shields.io/badge/licença-MIT-orange)

**DocumentationLLM**: Processador Inteligente de Documentação para LLMs com Supervisão de IA

## Estado Atual do Projeto

**Versão 0.2.0 - Em Desenvolvimento**

Funcionalidades implementadas:
- ✅ Download de repositórios Git
- ✅ Supervisão por IA das etapas implementadas
- ✅ Análise de tokens e custos
- ✅ Geração de relatórios de execução

Próximos passos:
- ⏳ Parsing de arquivos de documentação
- ⏳ Vinculação semântica de conteúdo
- ⏳ Geração de saída estruturada
- ⏳ Melhorias na análise de tokens

## Visão Geral

O DocumentationLLM é uma ferramenta de código aberto que utiliza IA para baixar, processar e reestruturar documentações técnicas (Markdown, HTML, etc.) de repositórios Git, tornando-as ideais para consumo por Grandes Modelos de Linguagem (LLMs) e aprendizado de máquina. 

Diferentemente de abordagens tradicionais que usam regex e parsing estático, o DocumentationLLM utiliza agentes de IA para compreender e preservar o contexto entre explicações e snippets de código, garantindo que o conteúdo processado mantenha sua coerência semântica.

## Características Principais

- **Pipeline de Agentes Inteligentes**: Cada etapa é executada e supervisionada por agentes de IA especializados.
- **Preservação de Contexto**: Mantém a relação entre explicações e blocos de código, essencial para documentações técnicas.
- **Supervisão Automática**: Cada etapa é validada, com relatórios detalhados e sugestões de melhoria.
- **Análise de Tokens/Custos**: Monitoramento detalhado do uso de tokens e custos associados às chamadas de IA.
- **Configuração Flexível**: Escolha facilmente qual modelo de IA usar em cada etapa do processo.
- **Mínimo de Dependências**: Foco em usar apenas o essencial, com preferência para processamento local quando possível.

## Como Funciona

1. **Download**: Clona o repositório de documentação para processamento local.
2. **Parsing**: Identifica e separa arquivos de documentação, texto e blocos de código.
3. **Vinculação Semântica**: Usa IA para associar explicações e snippets de código, mantendo contexto.
4. **Geração de Saída**: Salva em formato LLM-friendly (JSON/Markdown estruturado).
5. **Relatórios**: Gera logs detalhados, análise de custos e sugestões de melhoria.

## Instalação Completa

### Passo 1: Ambiente Virtual (recomendado)

#### Windows
```powershell
# Crie o ambiente virtual
python -m venv venv

# Ative o ambiente virtual
.\venv\Scripts\activate
```

#### Linux/MacOS
```bash
# Crie o ambiente virtual
python3 -m venv venv

# Ative o ambiente virtual
source venv/bin/activate
```

### Passo 2: Instale as Dependências
```bash
# Instale as dependências necessárias
pip install -r requirements.txt
```

### Passo 3: Instale como Pacote Python (para usar CLI)
```bash
# Instale o projeto como pacote Python
pip install .
```

**Após estes passos você poderá:**
- Usar o comando `docllm` diretamente no terminal (CLI)
- Importar o projeto em outros scripts Python
- Rodar sem especificar caminhos completos

## Uso

Após seguir os passos de instalação acima, você pode usar a ferramenta de duas formas:

```bash
# Usando o CLI (recomendado após instalação completa):
docllm --repo URL_DO_REPOSITÓRIO --output ./data/processed/

# Ou diretamente via Python:
python src/main.py --repo URL_DO_REPOSITÓRIO --output ./data/processed/

# Configuração avançada
python src/main.py --config config.yaml
```

## Estrutura do Projeto

```