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

### Passo 2: Configuração do arquivo .env

Copie o arquivo de exemplo e edite conforme suas chaves:

```bash
cp .env.example .env
```

Abra o arquivo `.env` e preencha as variáveis necessárias, por exemplo:
```
OPENAI_API_KEY=sua-chave-aqui
LANGSMITH_API_KEY=sua-chave-aqui
TAVILY_API_KEY=sua-chave-aqui
GOOGLE_API_KEY=sua-chave-aqui
FIRECRAWL_API_KEY=sua-chave-aqui
```

### Passo 3: Instale as Dependências
```bash
# Instale as dependências necessárias
pip install -r requirements.txt
```

### Passo 4: Instale como Pacote Python (para usar CLI)
```bash
# Instale o projeto como pacote Python
pip install .
```

**Após estes passos você poderá:**
- Usar o comando `docllm` diretamente no terminal (CLI)
- Importar o projeto em outros scripts Python
- Rodar sem especificar caminhos completos 