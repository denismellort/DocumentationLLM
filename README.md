# DocumentationLLM

Sistema para ingestão e análise de documentações com suporte a LLMs.

---

## Pré-requisitos

### Todos os Sistemas
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git

### Linux/Ubuntu
Em sistemas Debian/Ubuntu, você precisará instalar o pacote `python3-venv` antes de criar ambientes virtuais:

```bash
sudo apt update
sudo apt install python3-venv
```

---

## Instalação Completa

### Passo 1: Clone o Repositório

```bash
git clone https://github.com/denismellort/DocumentationLLM.git
cd DocumentationLLM
```

---

### Passo 2: Ambiente Virtual (recomendado)

#### Windows (CMD)
```cmd
python -m venv venv
venv\Scripts\activate
```

#### Windows (PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\activate
```

#### Linux/MacOS
```bash
python3 -m venv venv
source venv/bin/activate
```

**Nota para Linux:** Se você receber um erro sobre `ensurepip`, certifique-se de ter instalado o `python3-venv` conforme descrito nos pré-requisitos.

---

### Passo 3: Instale as Dependências

```bash
pip install -r requirements.txt
```

---

### Passo 4: Instale como Pacote Python (uso via CLI)

```bash
pip install .
```

---

### Passo 5: Configuração do arquivo .env (após instalar tudo)

Após instalar as dependências e preparar o ambiente, configure o arquivo `.env` com suas chaves de API:

Copie o arquivo de exemplo:

#### Windows (CMD)
```cmd
copy .env.example .env
```
#### Windows (PowerShell)
```powershell
Copy-Item .env.example .env
```
#### Linux/MacOS
```bash
cp .env.example .env
```

Edite o arquivo `.env` e preencha com suas chaves de API (Somente OpenAI necessária inicialmente):

```
OPENAI_API_KEY=sua-chave-aqui
LANGSMITH_API_KEY=sua-chave-aqui
TAVILY_API_KEY=sua-chave-aqui
GOOGLE_API_KEY=sua-chave-aqui
FIRECRAWL_API_KEY=sua-chave-aqui
```

Caso não exista um arquivo `.env.example`, crie o arquivo `.env` diretamente com pelo menos a sua chave da OpenAI:

```
OPENAI_API_KEY=sua-chave-aqui
```

---

## Uso

Após a instalação como pacote, você poderá:

- Usar o comando `docllm` diretamente no terminal:
  ```bash
  docllm --repo https://github.com/usuario/repositorio --verbose
  ```

- Importar o projeto em outros scripts Python
- Rodar sem precisar de caminhos absolutos

### Exemplos de Uso

Processar documentação de um repositório GitHub:
```bash
docllm --repo https://github.com/openai/openai-python
```

Processar um subdiretório específico:
```bash
docllm --repo https://github.com/microsoft/playwright/tree/main/docs/
```

Ver todas as opções disponíveis:
```bash
docllm --help
```

## Uso Correto do Pipeline (Cross-Platform)

- Sempre execute o pipeline via CLI usando o comando `docllm` após instalar o pacote:
  ```bash
  docllm --repo https://github.com/usuario/repositorio --verbose
  ```
- **Nunca execute `main.py` diretamente**. Isso pode causar erros de importação, especialmente em Linux/Mac.
- O comando `docllm` garante que todos os imports e paths estejam corretos, independente do sistema operacional.

## Troubleshooting: Erros Comuns de Importação

- **Erro:** `attempted relative import beyond top-level package`
  - **Causa:** Tentativa de rodar `main.py` diretamente, fora do contexto do pacote.
  - **Solução:** Sempre use o comando `docllm` no terminal, nunca rode `python main.py`.

- **Erro:** `ModuleNotFoundError` para agentes ou utils
  - **Causa:** Instalação incompleta ou execução fora do ambiente virtual.
  - **Solução:**
    1. Ative o ambiente virtual (`venv`).
    2. Reinstale o pacote: `pip install .`
    3. Execute novamente via `docllm`.

- **Erro:** `docllm: command not found`
  - **Causa:** O diretório de scripts do Python não está no PATH.
  - **Solução:**
    - No Linux/Mac: adicione `~/.local/bin` ao PATH.
    - No Windows: adicione o caminho do Scripts do venv ao PATH.

## Recursos Destacados

- **Detecção Inteligente de Documentação**: O sistema identifica automaticamente arquivos de documentação independente da estrutura do repositório
- **Suporte a Múltiplos Formatos**: Processa Markdown (.md, .mdx), reStructuredText, HTML, YAML, JSON e outros formatos 
- **Análise de Tokens**: Monitoramento detalhado do uso e custos de tokens
- **Otimização de Recursos**: Limpeza automática de arquivos temporários

---

## Dicas

- Sempre ative o ambiente virtual antes de usar:
  - `venv\Scripts\activate` (CMD)
  - `.\venv\Scripts\activate` (PowerShell)
  - `source venv/bin/activate` (Linux/Mac)

- Para atualizar o pacote após alterações no código:
  ```bash
  pip install . --upgrade
  ``` 

- O arquivo de configuração `config.yaml` na raiz é carregado por padrão, você pode sobreescrevê-lo com a opção `--config`:
  ```bash
  docllm --repo https://github.com/exemplo/repo --config caminho/para/config.yaml
  ``` 

## Organização dos Dados e Limpeza

A partir da versão X.X.X, o DocumentationLLM organiza os repositórios baixados da seguinte forma:

- `data/originals/<nome-repositorio>/` — repositório clonado, sempre atualizado (apaga o anterior se repetir)
- `data/temp/<nome-repositorio>/` — cópia temporária para processamento (limpa ao final)
- `data/processed/<nome-repositorio>/` — resultados processados, relatórios, etc.

**Apenas os arquivos `.gitkeep` são versionados nestas pastas.**

### Limpeza e Reprodutibilidade

- Para garantir reprodutibilidade, apague todo o conteúdo de `data/originals/`, `data/temp/` e `data/processed/` (exceto `.gitkeep`) antes de rodar novamente.
- O pipeline apaga automaticamente o clone anterior de um repositório antes de baixar novamente.
- O usuário pode inspecionar manualmente os clones em `data/originals/` para garantir que o download foi bem-sucedido.

### .gitignore

O projeto inclui um `.gitignore` robusto que impede o versionamento de arquivos de dados, temporários, outputs e relatórios. Apenas a estrutura de pastas é mantida no repositório.

### Exemplo de fluxo limpo

```bash
# Limpe os dados antigos (exceto .gitkeep)
rm -rf data/originals/* data/temp/* data/processed/*
# Rode o pipeline normalmente
python src/main.py --repo https://github.com/openai/openai-python
``` 

## Boas Práticas de Releases, Versionamento e Publicação

- Use versionamento semântico (MAJOR.MINOR.PATCH) para cada release.
- Crie uma release no GitHub para cada marco importante.
- Atualize o CHANGELOG.md e o número de versão antes de cada release.
- Publique packages no GitHub Packages ou PyPI se aplicável.
- Use GitHub Actions para automatizar releases e publicação de packages.
- Sempre documente mudanças relevantes no CONTEXT.md, README.md e CHANGELOG.md.
- Sempre que o usuário pedir para documentar, atualize os arquivos de contexto do projeto.
- O objetivo é garantir continuidade e clareza para qualquer colaborador (humano ou IA).

## Orientação para Inteligências Artificiais e Agentes Automáticos

Se você é uma inteligência artificial, agente autônomo ou ferramenta de automação que está instalando ou configurando este projeto:

- **Leia atentamente todos os arquivos de contexto do projeto** (CONTEXT.md, CHANGELOG.md, TODO.md, CONTRIBUTING.md, config.yaml, etc.) logo após o clone do repositório.
- Utilize essas informações para compreender o histórico, as decisões, as pendências e o funcionamento do projeto.
- Sempre siga a ordem das instruções do README.md para garantir reprodutibilidade.
- Documente qualquer erro ou comportamento inesperado nos arquivos de contexto, para que outros agentes ou humanos possam aprender com a execução anterior.

--- 