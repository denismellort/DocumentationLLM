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

---

Agradecemos suas contribuições para tornar o DocumentationLLM uma ferramenta melhor para todos!
