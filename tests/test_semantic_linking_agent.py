import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from openai.types.chat import ChatCompletion, ChatCompletionMessage, Choice

from documentationllm.agents.semantic_linking_agent import SemanticLinkingAgent

@pytest.fixture
def mock_config():
    return {
        "agents": {
            "semantic_linking": {
                "model": "gpt-4",
                "temperature": 0.0,
                "max_tokens": 4000,
                "batch_size": 5,
                "retry_attempts": 3
            }
        },
        "openai": {
            "api_key": "test-key"
        }
    }

@pytest.fixture
def mock_context(mock_config):
    return {
        "config": mock_config,
        "parsed_documents": [
            {
                "path": "test/doc1.md",
                "content": [
                    {
                        "type": "text",
                        "content": "This is a test function that adds two numbers."
                    },
                    {
                        "type": "code",
                        "content": "def add(a, b):\n    return a + b",
                        "language": "python"
                    }
                ]
            }
        ]
    }

@pytest.fixture
def mock_openai_response():
    return ChatCompletion(
        id="test-id",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content=json.dumps({
                        "concepts": [
                            {
                                "name": "Addition Function",
                                "text_references": ["This is a test function that adds two numbers."],
                                "code_references": ["def add(a, b):", "    return a + b"],
                                "explanation": "The code implements a simple addition function as described in the text.",
                                "metadata": {
                                    "confidence": 0.95,
                                    "type": "implementation"
                                }
                            }
                        ]
                    }),
                    role="assistant"
                )
            )
        ],
        created=1234567890,
        model="gpt-4",
        object="chat.completion",
        usage={"completion_tokens": 100, "prompt_tokens": 50, "total_tokens": 150}
    )

def test_init(mock_context):
    """Testa a inicialização do SemanticLinkingAgent."""
    agent = SemanticLinkingAgent(mock_context)
    assert agent.model == "gpt-4"
    assert agent.temperature == 0.0
    assert agent.max_tokens == 4000
    assert agent.batch_size == 5
    assert agent.retry_attempts == 3

def test_extract_sections(mock_context):
    """Testa a extração de seções de texto e código."""
    agent = SemanticLinkingAgent(mock_context)
    doc = mock_context["parsed_documents"][0]
    sections = agent._extract_sections(doc)
    
    assert len(sections) == 1
    assert sections[0]["text"] == ["This is a test function that adds two numbers."]
    assert sections[0]["code"][0]["content"] == "def add(a, b):\n    return a + b"
    assert sections[0]["code"][0]["language"] == "python"

@patch("openai.chat.completions.create")
def test_process_section(mock_create, mock_context, mock_openai_response):
    """Testa o processamento de uma seção com chamada à OpenAI."""
    mock_create.return_value = mock_openai_response
    
    agent = SemanticLinkingAgent(mock_context)
    section = {
        "text": ["This is a test function that adds two numbers."],
        "code": [{
            "content": "def add(a, b):\n    return a + b",
            "language": "python"
        }]
    }
    
    result = agent._process_section(section)
    
    assert "text" in result
    assert "code" in result
    assert "semantic_links" in result
    assert len(result["semantic_links"]["concepts"]) == 1
    assert result["semantic_links"]["concepts"][0]["name"] == "Addition Function"
    assert result["semantic_links"]["concepts"][0]["metadata"]["confidence"] == 0.95

@patch("openai.chat.completions.create")
def test_run_pipeline(mock_create, mock_context, mock_openai_response):
    """Testa a execução completa do pipeline de vinculação semântica."""
    mock_create.return_value = mock_openai_response
    
    agent = SemanticLinkingAgent(mock_context)
    result = agent.run()
    
    assert result["semantic_linking_completed"] is True
    assert "linked_documents" in result
    assert len(result["linked_documents"]) == 1
    assert "semantic_linking_stats" in result
    assert result["semantic_linking_stats"]["total_documents"] == 1
    assert result["semantic_linking_stats"]["successful_documents"] == 1

def test_prepare_prompt(mock_context):
    """Testa a preparação do prompt para a OpenAI."""
    agent = SemanticLinkingAgent(mock_context)
    section = {
        "text": ["This is a test function that adds two numbers."],
        "code": [{
            "content": "def add(a, b):\n    return a + b",
            "language": "python"
        }]
    }
    
    prompt = agent._prepare_prompt(section)
    
    assert "This is a test function that adds two numbers." in prompt
    assert "```python" in prompt
    assert "def add(a, b):" in prompt
    assert "return a + b" in prompt
    assert "Gere um JSON" in prompt

def test_error_handling_no_documents(mock_context):
    """Testa o tratamento de erro quando não há documentos parseados."""
    mock_context["parsed_documents"] = []
    agent = SemanticLinkingAgent(mock_context)
    
    with pytest.raises(ValueError, match="Nenhum documento parseado encontrado no contexto"):
        agent.run()

@patch("openai.chat.completions.create")
def test_error_handling_api_failure(mock_create, mock_context):
    """Testa o tratamento de erro quando a API da OpenAI falha."""
    mock_create.side_effect = Exception("API Error")
    
    agent = SemanticLinkingAgent(mock_context)
    result = agent.run()
    
    assert result["semantic_linking_completed"] is True
    assert len(result["linked_documents"]) == 1
    assert "semantic_links" not in result["linked_documents"][0]
    assert result["semantic_linking_stats"]["failed_documents"] == 1

def test_parse_openai_response_invalid_json(mock_context):
    """Testa o tratamento de resposta inválida da OpenAI."""
    agent = SemanticLinkingAgent(mock_context)
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "invalid json"
    
    result = agent._parse_openai_response(mock_response)
    assert result == {"concepts": []}