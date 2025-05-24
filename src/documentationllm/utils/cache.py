"""
Módulo de cache para otimizar chamadas à OpenAI.
Implementa um sistema de cache em memória e em disco para reduzir
o número de chamadas repetitivas à API.
"""

import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, Optional, Union
from datetime import datetime, timedelta

from ..utils.logging import setup_logger

logger = setup_logger(__name__)

class SemanticCache:
    """
    Cache para respostas da OpenAI, otimizando chamadas repetitivas
    e reduzindo custos com tokens.
    """
    
    def __init__(self, config: Dict):
        """
        Inicializa o cache semântico.

        Args:
            config (Dict): Configuração do projeto
        """
        self.config = config
        self.cache_dir = Path(config.get("directories.cache", "data/cache"))
        self.cache_ttl = timedelta(
            hours=config.get("cache.ttl_hours", 24)
        )
        self.memory_cache: Dict[str, Dict] = {}
        
        # Garante que o diretório de cache existe
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Carrega cache do disco
        self._load_cache()
    
    def _compute_hash(self, text: str, code: str) -> str:
        """
        Calcula o hash de uma combinação texto-código.

        Args:
            text (str): Texto explicativo
            code (str): Código fonte

        Returns:
            str: Hash SHA-256 da combinação
        """
        content = f"{text}\n{code}".encode("utf-8")
        return hashlib.sha256(content).hexdigest()
    
    def _load_cache(self) -> None:
        """Carrega o cache do disco para a memória."""
        try:
            cache_file = self.cache_dir / "semantic_cache.json"
            if cache_file.exists():
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                    
                # Filtra entradas expiradas
                now = datetime.now()
                valid_entries = {
                    k: v for k, v in cache_data.items()
                    if datetime.fromisoformat(v["timestamp"]) + self.cache_ttl > now
                }
                
                self.memory_cache = valid_entries
                logger.info(f"Cache carregado com {len(valid_entries)} entradas válidas")
            
        except Exception as e:
            logger.error(f"Erro ao carregar cache: {e}")
            self.memory_cache = {}
    
    def _save_cache(self) -> None:
        """Salva o cache da memória para o disco."""
        try:
            cache_file = self.cache_dir / "semantic_cache.json"
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(self.memory_cache, f, indent=2)
            logger.info(f"Cache salvo com {len(self.memory_cache)} entradas")
            
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")
    
    def get(self, text: str, code: str) -> Optional[Dict]:
        """
        Busca uma resposta no cache.

        Args:
            text (str): Texto explicativo
            code (str): Código fonte

        Returns:
            Optional[Dict]: Resposta cacheada ou None se não encontrada
        """
        cache_key = self._compute_hash(text, code)
        
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            timestamp = datetime.fromisoformat(entry["timestamp"])
            
            # Verifica se a entrada expirou
            if timestamp + self.cache_ttl > datetime.now():
                logger.info("Cache hit!")
                return entry["response"]
            else:
                logger.info("Cache expired, removing entry")
                del self.memory_cache[cache_key]
                self._save_cache()
        
        return None
    
    def set(self, text: str, code: str, response: Dict) -> None:
        """
        Adiciona uma resposta ao cache.

        Args:
            text (str): Texto explicativo
            code (str): Código fonte
            response (Dict): Resposta da OpenAI
        """
        cache_key = self._compute_hash(text, code)
        
        self.memory_cache[cache_key] = {
            "timestamp": datetime.now().isoformat(),
            "response": response
        }
        
        # Salva no disco a cada nova entrada
        self._save_cache()
    
    def clear(self) -> None:
        """Limpa todo o cache em memória e em disco."""
        self.memory_cache = {}
        try:
            cache_file = self.cache_dir / "semantic_cache.json"
            if cache_file.exists():
                cache_file.unlink()
            logger.info("Cache limpo com sucesso")
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
    
    def get_stats(self) -> Dict:
        """
        Retorna estatísticas do cache.

        Returns:
            Dict: Estatísticas do cache
        """
        total_entries = len(self.memory_cache)
        now = datetime.now()
        valid_entries = sum(
            1 for entry in self.memory_cache.values()
            if datetime.fromisoformat(entry["timestamp"]) + self.cache_ttl > now
        )
        
        return {
            "total_entries": total_entries,
            "valid_entries": valid_entries,
            "expired_entries": total_entries - valid_entries,
            "cache_ttl_hours": self.cache_ttl.total_seconds() / 3600
        }