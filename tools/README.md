# Ferramentas Auxiliares do DocumentationLLM

Este diretório contém ferramentas auxiliares para ajudar no desenvolvimento e manutenção do DocumentationLLM.

## Ferramentas Disponíveis

### Gerenciador de Versões (`version_manager.py`)

Ferramenta para criar snapshots do código e restaurar versões anteriores. Facilita o desenvolvimento com segurança, permitindo voltar facilmente a versões anteriores que funcionavam corretamente.

**Uso:**

```bash
# Criar novo snapshot
python tools/version_manager.py create "Descrição do snapshot"

# Listar snapshots existentes
python tools/version_manager.py list
python tools/version_manager.py list --verbose

# Comparar dois snapshots
python tools/version_manager.py compare v_20250522_123456 v_20250523_123456

# Restaurar código para um snapshot específico
python tools/version_manager.py rollback v_20250522_123456

# Simular restauração sem modificar arquivos
python tools/version_manager.py rollback v_20250522_123456 --dry-run

# Interface interativa (sem argumentos)
python tools/version_manager.py
```

## Como Adicionar Novas Ferramentas

1. Crie um novo script Python neste diretório.
2. Mantenha a ferramenta independente e bem documentada.
3. Inclua uma seção neste README explicando sua ferramenta.
4. Mantenha um padrão de interface consistente.

## Diretrizes para Desenvolvimento de Ferramentas

- Ferramentas devem ser autocontidas e realizar uma tarefa específica.
- Documente claramente o propósito e uso da ferramenta.
- Forneça ajuda via linha de comando (`--help`).
- Trate erros graciosamente e mostre mensagens descritivas.
- Teste a ferramenta antes de comitá-la. 