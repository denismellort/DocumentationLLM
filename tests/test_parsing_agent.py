#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes para o ParsingAgent
"""

import os
import pytest
from pathlib import Path
from typing import Dict, Any

from documentationllm.agents.parsing_agent import ParsingAgent, ParsedDocument, DocumentSection

# Fixtures
@pytest.fixture
def sample_context() -> Dict[str, Any]:
    """Cria um contexto de teste."""
    return {
        "directories": {
            "temp": "tests/temp",
            "processed": "tests/processed"
        },
        "logger": None
    }

@pytest.fixture
def parsing_agent(sample_context: Dict[str, Any]) -> ParsingAgent:
    """Cria uma instância do ParsingAgent para testes."""
    return ParsingAgent(sample_context)

@pytest.fixture
def sample_markdown() -> str:
    """Retorna um exemplo de conteúdo Markdown para testes."""
    return """---
title: Documento de Teste
author: Equipe de Testes
date: 2025-05-24
---

# Título Principal

Este é um parágrafo introdutório.

## Seção 1

Conteúdo da seção 1.

```python
def hello():
    print("Hello, World!")
```

### Subseção 1.1

Conteúdo da subseção 1.1.

## Seção 2

Conteúdo da seção 2.

```javascript
console.log("Hello!");
```
"""

@pytest.fixture
def setup_test_files(tmp_path: Path) -> None:
    """Configura arquivos de teste."""
    # Criar diretórios
    (tmp_path / "temp").mkdir()
    (tmp_path / "processed").mkdir()
    
    # Criar arquivo de teste
    test_file = tmp_path / "temp" / "test.md"
    test_file.write_text("""# Test Document

This is a test document.

## Section 1

Content of section 1.

```python
print("test")
```
""")

# Testes
def test_parsing_agent_initialization(parsing_agent: ParsingAgent) -> None:
    """Testa a inicialização do ParsingAgent."""
    assert parsing_agent is not None
    assert parsing_agent.supported_extensions['.md'] == parsing_agent._parse_markdown
    assert parsing_agent.supported_extensions['.markdown'] == parsing_agent._parse_markdown

def test_markdown_parsing(parsing_agent: ParsingAgent, sample_markdown: str, tmp_path: Path) -> None:
    """Testa o parsing de conteúdo Markdown."""
    # Criar arquivo temporário
    test_file = tmp_path / "test.md"
    test_file.write_text(sample_markdown)
    
    # Processar arquivo
    result = parsing_agent.process_file(str(test_file))
    
    assert result is not None
    assert isinstance(result, ParsedDocument)
    assert result.title == "Título Principal"
    assert result.file_type == "markdown"
    assert len(result.sections) > 0
    
    # Verificar seções
    main_section = result.sections[0]
    assert main_section.title == "Título Principal"
    assert main_section.level == 1
    assert "parágrafo introdutório" in main_section.content
    
    # Verificar metadados
    assert result.metadata.get("frontmatter") is not None
    assert result.metadata["frontmatter"]["title"] == "Documento de Teste"
    assert result.metadata["frontmatter"]["author"] == "Equipe de Testes"

def test_code_block_extraction(parsing_agent: ParsingAgent, sample_markdown: str, tmp_path: Path) -> None:
    """Testa a extração de blocos de código."""
    # Criar arquivo temporário
    test_file = tmp_path / "test.md"
    test_file.write_text(sample_markdown)
    
    # Processar arquivo
    result = parsing_agent.process_file(str(test_file))
    
    assert result is not None
    
    # Encontrar seção com bloco de código Python
    python_section = None
    for section in result.sections:
        if "python" in str(section.code_blocks).lower():
            python_section = section
            break
    
    assert python_section is not None
    assert len(python_section.code_blocks) > 0
    assert "print" in python_section.code_blocks[0]["code"]
    assert python_section.code_blocks[0]["language"] == "python"

def test_section_hierarchy(parsing_agent: ParsingAgent, sample_markdown: str, tmp_path: Path) -> None:
    """Testa a hierarquia de seções."""
    # Criar arquivo temporário
    test_file = tmp_path / "test.md"
    test_file.write_text(sample_markdown)
    
    # Processar arquivo
    result = parsing_agent.process_file(str(test_file))
    
    assert result is not None
    
    # Verificar estrutura hierárquica
    sections = result.sections
    assert len(sections) > 0
    
    # Encontrar seção 1
    section1 = None
    for section in sections:
        if section.title == "Seção 1":
            section1 = section
            break
    
    assert section1 is not None
    assert section1.level == 2
    assert len(section1.subsections) > 0
    assert section1.subsections[0].title == "Subseção 1.1"
    assert section1.subsections[0].level == 3

def test_unsupported_format(parsing_agent: ParsingAgent, tmp_path: Path) -> None:
    """Testa o comportamento com formato não suportado."""
    # Criar arquivo temporário
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test content")
    
    # Tentar processar arquivo
    result = parsing_agent.process_file(str(test_file))
    
    assert result is None

def test_invalid_file_path(parsing_agent: ParsingAgent) -> None:
    """Testa o comportamento com caminho de arquivo inválido."""
    result = parsing_agent.process_file("nonexistent/file.md")
    assert result is None

def test_batch_processing(parsing_agent: ParsingAgent, setup_test_files: None, tmp_path: Path) -> None:
    """Testa o processamento em lote de arquivos."""
    # Criar múltiplos arquivos
    files = []
    for i in range(3):
        file_path = tmp_path / "temp" / f"test_{i}.md"
        file_path.write_text(f"# Test {i}\n\nContent {i}")
        files.append(str(file_path))
    
    # Processar arquivos
    results = parsing_agent.process_files(files)
    
    assert len(results) == 3
    for file_path, doc in results.items():
        assert isinstance(doc, ParsedDocument)
        assert doc.title.startswith("Test")

def test_result_saving(parsing_agent: ParsingAgent, sample_markdown: str, tmp_path: Path) -> None:
    """Testa o salvamento dos resultados."""
    # Configurar diretórios no contexto
    parsing_agent.processed_dir = tmp_path / "processed"
    parsing_agent.processed_dir.mkdir(exist_ok=True)
    
    # Criar e processar arquivo
    test_file = tmp_path / "test.md"
    test_file.write_text(sample_markdown)
    
    doc = parsing_agent.process_file(str(test_file))
    assert doc is not None  # Garantir que temos um documento válido
    
    processed_docs: Dict[str, ParsedDocument] = {
        str(test_file): doc
    }
    
    # Salvar resultados
    parsing_agent.save_results(processed_docs)
    
    # Verificar arquivo de saída
    output_file = parsing_agent.processed_dir / "parsed_documents" / "test.json"
    assert output_file.exists()
    
    # Verificar conteúdo do JSON
    import json
    with open(output_file) as f:
        data = json.load(f)
    
    assert data["title"] == "Título Principal"
    assert len(data["sections"]) > 0