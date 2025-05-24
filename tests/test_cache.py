"""
Testes unitários para o sistema de cache do DocumentationLLM.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, mock_open

from documentationllm.utils.cache import SemanticCache

@pytest.fixture
def mock_config():
    return {
        "directories": {
            "cache": "data/cache"
        },
        "cache": {
            "ttl_hours": 24,
            "enabled": True,
            "max_entries": 1000
        }
    }

@pytest.fixture
def mock_cache_data():
    now = datetime.now()
    return {
        "test_key_1": {
            "timestamp": (now - timedelta(hours=12)).isoformat(),
            "response": {
                "concepts": [
                    {
                        "name": "Test Concept",
                        "text_references": ["test text"],
                        "code_references": ["test code"],
                        "explanation": "test explanation",
                        "metadata": {
                            "confidence": 0.95,
                            "type": "implementation"
                        }
                    }
                ]
            }
        },
        "test_key_2": {
            "timestamp": (now - timedelta(hours=48)).isoformat(),  # Expirado
            "response": {
                "concepts": []
            }
        }
    }

def test_init(mock_config, tmp_path):
    """Testa a inicialização do cache."""
    with patch("pathlib.Path.mkdir") as mock_mkdir:
        cache = SemanticCache(mock_config)
        assert cache.cache_ttl == timedelta(hours=24)
        assert isinstance(cache.memory_cache, dict)
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

def test_compute_hash():
    """Testa a geração de hash para texto e código."""
    cache = SemanticCache({"directories": {"cache": "test"}})
    hash1 = cache._compute_hash("test text", "test code")
    hash2 = cache._compute_hash("test text", "test code")
    hash3 = cache._compute_hash("different text", "test code")
    
    assert hash1 == hash2  # Mesmo conteúdo = mesmo hash
    assert hash1 != hash3  # Conteúdo diferente = hash diferente
    assert isinstance(hash1, str)
    assert len(hash1) == 64  # SHA-256 = 64 caracteres

@patch("builtins.open", new_callable=mock_open)
@patch("json.load")
def test_load_cache(mock_json_load, mock_file_open, mock_config, mock_cache_data):
    """Testa o carregamento do cache do disco."""
    mock_json_load.return_value = mock_cache_data
    
    with patch("pathlib.Path.exists", return_value=True):
        cache = SemanticCache(mock_config)
        assert len(cache.memory_cache) == 1  # Apenas entrada não expirada
        assert "test_key_1" in cache.memory_cache
        assert "test_key_2" not in cache.memory_cache  # Expirado

@patch("builtins.open", new_callable=mock_open)
@patch("json.dump")
def test_save_cache(mock_json_dump, mock_file_open, mock_config):
    """Testa o salvamento do cache em disco."""
    cache = SemanticCache(mock_config)
    cache.memory_cache = {"test": {"timestamp": "2025-01-01T00:00:00", "response": {}}}
    
    cache._save_cache()
    mock_json_dump.assert_called_once()
    assert mock_file_open.call_args[0][0].endswith("semantic_cache.json")

def test_get_set(mock_config):
    """Testa as operações get e set do cache."""
    cache = SemanticCache(mock_config)
    
    # Set
    text = "test text"
    code = "test code"
    response = {"concepts": [{"name": "test"}]}
    cache.set(text, code, response)
    
    # Get - Hit
    cached = cache.get(text, code)
    assert cached == response
    
    # Get - Miss
    missing = cache.get("different text", code)
    assert missing is None

def test_clear(mock_config):
    """Testa a limpeza do cache."""
    cache = SemanticCache(mock_config)
    cache.memory_cache = {"test": {"timestamp": "2025-01-01T00:00:00", "response": {}}}
    
    with patch("pathlib.Path.exists", return_value=True), \
         patch("pathlib.Path.unlink") as mock_unlink:
        cache.clear()
        assert len(cache.memory_cache) == 0
        mock_unlink.assert_called_once()

def test_get_stats(mock_config, mock_cache_data):
    """Testa a geração de estatísticas do cache."""
    cache = SemanticCache(mock_config)
    cache.memory_cache = mock_cache_data
    
    stats = cache.get_stats()
    assert stats["total_entries"] == 2
    assert stats["valid_entries"] == 1
    assert stats["expired_entries"] == 1
    assert stats["cache_ttl_hours"] == 24

def test_error_handling(mock_config):
    """Testa o tratamento de erros do cache."""
    cache = SemanticCache(mock_config)
    
    # Erro ao carregar
    with patch("builtins.open", side_effect=Exception("Test error")):
        cache._load_cache()
        assert len(cache.memory_cache) == 0
    
    # Erro ao salvar
    with patch("builtins.open", side_effect=Exception("Test error")):
        cache._save_cache()  # Não deve levantar exceção
    
    # Erro ao limpar
    with patch("pathlib.Path.unlink", side_effect=Exception("Test error")):
        cache.clear()  # Não deve levantar exceção
        assert len(cache.memory_cache) == 0

def test_cache_expiration(mock_config):
    """Testa a expiração de entradas do cache."""
    cache = SemanticCache(mock_config)
    
    # Entrada recente
    now = datetime.now()
    cache.memory_cache["recent"] = {
        "timestamp": now.isoformat(),
        "response": {"test": "data"}
    }
    
    # Entrada expirada
    cache.memory_cache["expired"] = {
        "timestamp": (now - timedelta(hours=48)).isoformat(),
        "response": {"test": "old_data"}
    }
    
    # Testa get em entrada recente
    assert cache.get("recent text", "recent code") is None  # Hash diferente
    
    # Testa get em entrada expirada
    assert cache.get("expired text", "expired code") is None
    assert "expired" not in cache.memory_cache  # Deve ser removida

def test_cache_persistence(mock_config, tmp_path):
    """Testa a persistência do cache entre instâncias."""
    cache_dir = tmp_path / "cache"
    mock_config["directories"]["cache"] = str(cache_dir)
    
    # Primeira instância
    cache1 = SemanticCache(mock_config)
    cache1.set("test text", "test code", {"test": "data"})
    
    # Segunda instância
    cache2 = SemanticCache(mock_config)
    assert cache2.get("test text", "test code") == {"test": "data"}