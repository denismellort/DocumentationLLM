# DocumentationLLM

Sistema para ingestão e análise de documentações com suporte a LLMs.

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

---

### Passo 3: Configuração do arquivo .env

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

Edite o arquivo `.env` e preencha com suas chaves de API (Somente OpenAI necessaria inicialmente):

```
OPENAI_API_KEY=sua-chave-aqui
LANGSMITH_API_KEY=sua-chave-aqui
TAVILY_API_KEY=sua-chave-aqui
GOOGLE_API_KEY=sua-chave-aqui
FIRECRAWL_API_KEY=sua-chave-aqui
```

---

### Passo 4: Instale as Dependências

```bash
pip install -r requirements.txt
```

---

### Passo 5: Instale como Pacote Python (uso via CLI)

```bash
pip install .
```

---

## Uso

Após a instalação como pacote, você poderá:

- Usar o comando `docllm` diretamente no terminal:
  ```bash
  docllm --help
  ```
- Importar o projeto em outros scripts Python
- Rodar sem precisar de caminhos absolutos

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