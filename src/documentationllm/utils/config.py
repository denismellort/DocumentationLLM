"""
Módulo de configuração do DocumentationLLM.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
from dotenv import load_dotenv

class Config:
    """
    Classe para gerenciar configurações do DocumentationLLM.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Inicializa a configuração.

        Args:
            config_file (Optional[str]): Caminho para o arquivo de configuração
        """
        # Carrega variáveis de ambiente
        load_dotenv()
        
        # Configurações padrão
        self.config: Dict[str, Any] = {
            "directories": {
                "originals": "data/originals",
                "processed": "data/processed",
                "temp": "data/temp",
                "cache": "data/cache"
            },
            "agents": {
                "semantic_linking": {
                    "model": "gpt-4",
                    "temperature": 0.0,
                    "max_tokens": 4000,
                    "batch_size": 5,
                    "retry_attempts": 3,
                    "confidence_threshold": 0.8
                }
            },
            "cache": {
                "ttl_hours": 24,
                "enabled": True,
                "max_entries": 1000
            },
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY")
            }
        }
        
        # Carrega configurações do arquivo
        if config_file:
            self._load_config(config_file)
    
    def _load_config(self, config_file: str) -> None:
        """
        Carrega configurações de um arquivo YAML.

        Args:
            config_file (str): Caminho para o arquivo de configuração
        """
        config_path = Path(config_file)
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    self._merge_configs(self.config, file_config)
    
    def _merge_configs(self, base: Dict, update: Dict) -> None:
        """
        Mescla configurações recursivamente.

        Args:
            base (Dict): Configuração base
            update (Dict): Configuração a ser mesclada
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém um valor da configuração.

        Args:
            key (str): Chave da configuração (pode ser aninhada com pontos)
            default (Any): Valor padrão se a chave não existir

        Returns:
            Any: Valor da configuração ou valor padrão
        """
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Define um valor na configuração.

        Args:
            key (str): Chave da configuração (pode ser aninhada com pontos)
            value (Any): Valor a ser definido
        """
        keys = key.split(".")
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self, config_file: str) -> None:
        """
        Salva a configuração em um arquivo YAML.

        Args:
            config_file (str): Caminho para o arquivo de configuração
        """
        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.config, f, default_flow_style=False)