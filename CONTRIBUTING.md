# Contribuindo para o DocumentationLLM

Agradecemos seu interesse em contribuir para o DocumentationLLM! Este documento fornece diretrizes para contribuir com o projeto, focando no uso inteligente de IA e na manutenção da qualidade do código.

## Código de Conduta

Este projeto e todos os participantes estão sujeitos ao nosso Código de Conduta. Ao participar, espera-se que você mantenha este código.

## Princípios de Contribuição

1. **Uso Estratégico de IA**: Adicione chamadas de IA apenas onde agregam valor real. Prefira soluções locais para tarefas simples.

2. **Supervisão e Validação**: Mantenha os mecanismos de supervisão, log e validação. Eles são essenciais para o projeto.

3. **Preservação de Contexto**: Qualquer modificação deve continuar garantindo que a relação entre explicações e código seja mantida.

4. **Documentação Clara**: Documente bem seu código e atualize `CONTEXT.md` com novas decisões arquiteturais.

5. **Código Limpo e Testável**: Escreva código limpo, modular e com testes automatizados.

## Como Contribuir

### Reportando Bugs

* Verifique se o bug já não foi reportado procurando na seção de Issues do GitHub.
* Se você não encontrar um issue aberto abordando o problema, abra um novo.
* Inclua um título claro e uma descrição detalhada, com o máximo de informações relevantes possível.
* Se possível, inclua um exemplo de código ou caso de teste que demonstre o problema.

### Sugerindo Melhorias

* Abra um novo issue descrevendo sua sugestão.
* Explique por que essa funcionalidade seria útil e como ela poderia ser implementada.
* Discuta as implicações da mudança, especialmente em termos de uso de IA e custos.

### Pull Requests

1. Faça um fork do repositório.
2. Crie uma branch para sua feature (`git checkout -b feature/nome-da-feature`).
3. Faça commit das suas alterações (`git commit -am 'Adiciona nova feature'`).
4. Faça push para a branch (`git push origin feature/nome-da-feature`).
5. Abra um Pull Request.

### Critérios para Aceitação de Pull Requests

Para que um Pull Request seja aceito, ele deve:

1. Seguir os padrões de código do projeto (PEP 8 para Python).
2. Incluir testes para novas funcionalidades.
3. Atualizar a documentação relevante.
4. Passar em todos os testes automatizados.
5. Ser revisado e aprovado por pelo menos um mantenedor.
6. Justificar qualquer nova dependência ou uso adicional de IA.

## Padrões de Código

* Siga o estilo de código PEP 8.
* Escreva docstrings para todas as funções, classes e métodos.
* Mantenha o código limpo e legível.
* Adicione testes para novas funcionalidades.

## Estrutura do Projeto

```
DocumentationLLM/
├── data/                # Diretórios de dados
│   ├── originals/       # Documentação original
│   ├── processed/       # Saída processada
│   └── temp/            # Arquivos temporários
├── src/                 # Código-fonte principal
│   ├── agents/          # Agentes do pipeline
│   ├── utils/           # Funções utilitárias
│   └── prompts/         # Templates de prompts para IA
└── tests/               # Testes unitários e de integração
```

## Diretrizes para Uso de IA

### Quando Usar IA

* **Use IA para**: Compreensão semântica, vinculação de contexto, análise crítica.
* **Evite IA para**: Parsing simples, operações de arquivo, tarefas algorítmicas diretas.

### Como Documentar Uso de IA

Ao adicionar uma nova funcionalidade que usa IA, documente:

1. Qual modelo é recomendado (ex: GPT-4, GPT-3.5).
2. Estimativa de tokens por chamada.
3. Justificativa para o uso de IA vs. solução local.
4. Se há opção de fallback local em caso de falha na API.

## Processo de Desenvolvimento

1. Escolha um issue para trabalhar ou crie um novo.
2. Discuta a abordagem com os mantenedores.
3. Implemente sua solução.
4. Adicione testes.
5. Atualize a documentação se necessário.
6. Envie um Pull Request.

## Diretrizes para Templates de Prompts

Ao criar ou modificar templates de prompts em `src/prompts/`:

1. Seja claro e específico sobre o que você espera do modelo.
2. Inclua exemplos de entrada/saída quando possível.
3. Documente parâmetros recomendados (temperatura, top_p, etc.).
4. Considere otimizações para reduzir tokens sem perder qualidade.

## Contato

Se você tiver dúvidas ou precisar de ajuda, abra um issue ou entre em contato com a equipe pelo e-mail [email].

## Padrão de Releases, Versionamento e Publicação

- Sempre use versionamento semântico (MAJOR.MINOR.PATCH).
- Crie uma release para cada marco importante ou mudança relevante.
- Atualize o CHANGELOG.md e o número de versão no código antes de criar uma release.
- Publique packages no GitHub Packages ou PyPI se o projeto for uma biblioteca ou CLI.
- Use GitHub Actions para automatizar releases e publicação de packages sempre que possível.
- Documente cada release e mudança relevante no CONTEXT.md e README.md.
- Sempre que o usuário pedir para documentar, atualize os arquivos de contexto do projeto.
- O objetivo é garantir que qualquer GPT (ou humano) possa continuar o projeto exatamente de onde parou, com histórico e instruções claras.

---

Agradecemos suas contribuições para tornar o DocumentationLLM uma ferramenta melhor para todos!

# Guia de Contribuição

## 🔄 Processo de Pull Request

### O que é um Pull Request?
Um Pull Request (PR) é uma proposta de mudança no código que permite que outros desenvolvedores revisem suas alterações antes de serem incorporadas ao projeto principal. É como dizer "Ei, fiz algumas mudanças aqui, podem dar uma olhada?".

### Por que usamos Pull Requests?
1. **Revisão de Código**: Permite que outros desenvolvedores revisem suas mudanças
2. **Qualidade**: Garante que o código segue os padrões do projeto
3. **Documentação**: Registra o histórico de mudanças
4. **Integração**: Permite testes automatizados antes da integração

### Como criar um Pull Request

1. **Clone o Repositório**:
   ```bash
   git clone [URL_DO_REPOSITÓRIO]
   cd [NOME_DO_PROJETO]
   ```

2. **Crie uma Branch**:
   ```bash
   git checkout -b feature/sua-feature
   ```

3. **Faça suas Mudanças**:
   - Escreva/modifique o código
   - Adicione/atualize testes
   - Atualize a documentação

4. **Commit das Mudanças**:
   ```bash
   git add .
   git commit -m "feat: descrição da sua mudança"
   ```

5. **Push para o GitHub**:
   ```bash
   git push origin feature/sua-feature
   ```

6. **Crie o Pull Request**:
   - Vá para o GitHub
   - Clique em "New Pull Request"
   - Selecione sua branch
   - Preencha a descrição
   - Clique em "Create Pull Request"

### Estrutura do Pull Request

Todo PR deve incluir:

1. **Título**: Breve descrição do que foi feito
2. **Descrição**: Explicação detalhada das mudanças
3. **Checklist**:
   - [ ] Testes adicionados/atualizados
   - [ ] Documentação atualizada
   - [ ] Código formatado (Black/isort)
   - [ ] Type hints adicionados
   - [ ] Revisado por pelo menos 1 desenvolvedor

### Processo de Revisão

1. **Revisores**: Pelo menos 1 desenvolvedor deve aprovar
2. **CI/CD**: Todos os testes devem passar
3. **Formatação**: Código deve seguir padrões (Black/isort)
4. **Tipos**: Mypy deve passar sem erros

### Após a Aprovação

1. O PR será mesclado na branch principal
2. A branch feature será deletada
3. As mudanças serão deployadas automaticamente

## 🛠️ Ambiente de Desenvolvimento

### Configuração Inicial

1. **Dependências**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   .\venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Pre-commit**:
   ```bash
   pre-commit install
   ```

3. **Docker** (opcional):
   ```bash
   docker-compose up -d
   ```

### Testes

```bash
pytest
```

### Formatação

```bash
black .
isort .
```

## 📝 Convenções

### Commits

Seguimos o padrão Conventional Commits:

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Manutenção

### Branches

- `feature/*`: Novas funcionalidades
- `fix/*`: Correções
- `docs/*`: Documentação
- `refactor/*`: Refatoração

## ⚠️ Notas Importantes

1. Nunca faça commit direto na branch principal
2. Mantenha os PRs pequenos e focados
3. Escreva testes para novas funcionalidades
4. Atualize a documentação quando necessário
5. Use type hints em código novo
