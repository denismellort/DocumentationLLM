#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitários para lidar com variáveis de ambiente e configuração.
"""

import os
import yaml
from dotenv import load_dotenv
from typing import Dict, Any, Optional

def load_env(env_file: str = None) -> bool:
    """
    Carrega variáveis de ambiente de um arquivo .env.
    
    Args:
        env_file (str, optional): Caminho para o arquivo .env. Se não especificado,
                                 tenta carregar .env no diretório atual.
    
    Returns:
        bool: True se o arquivo foi carregado, False caso contrário.
    """
    if env_file and os.path.exists(env_file):
        return load_dotenv(env_file)
    else:
        return load_dotenv()

def get_api_key(service: str) -> Optional[str]:
    """
    Obtém a chave de API para um serviço específico.
    
    Args:
        service (str): Nome do serviço (openai, langsmith, tavily, etc.).
    
    Returns:
        Optional[str]: Chave de API ou None se não encontrada.
    """
    service = service.upper()
    key_name = f"{service}_API_KEY"
    
    return os.getenv(key_name)

def clean_env_value(value):
    """
    Limpa um valor de variável de ambiente, removendo comentários.
    
    Args:
        value (str): O valor da variável de ambiente.
        
    Returns:
        str: O valor limpo, sem comentários.
    """
    if value is None:
        return None
        
    # Remove comentários (texto após #)
    if '#' in value:
        return value.split('#')[0].strip()
    return value

def load_config(config_file: str = None) -> Dict[str, Any]:
    """
    Carrega configurações de um arquivo YAML.
    
    Args:
        config_file (str, optional): Caminho para o arquivo de configuração.
                                    Se não especificado, retorna configuração padrão.
    
    Returns:
        Dict[str, Any]: Configurações carregadas.
    """
    # Configuração padrão
    config = {
        # Modelos para cada etapa
        "models": {
            "download": clean_env_value(os.getenv("MODEL_DOWNLOAD", "local")),
            "parsing": clean_env_value(os.getenv("MODEL_PARSING", "local")),
            "semantic_linking": clean_env_value(os.getenv("MODEL_SEMANTIC_LINKING", "gpt-4")),
            "output_generation": clean_env_value(os.getenv("MODEL_OUTPUT_GENERATION", "gpt-3.5-turbo")),
            "supervisor": clean_env_value(os.getenv("MODEL_SUPERVISOR", "gpt-4")),
            "token_analyst": clean_env_value(os.getenv("MODEL_TOKEN_ANALYST", "local"))
        },
        # Opções de processamento
        "processing": {
            "enable_supervision": clean_env_value(os.getenv("ENABLE_SUPERVISION", "true")).lower() == "true",
            "enable_token_analysis": clean_env_value(os.getenv("ENABLE_TOKEN_ANALYSIS", "true")).lower() == "true",
            "enable_execution_history": clean_env_value(os.getenv("ENABLE_EXECUTION_HISTORY", "true")).lower() == "true",
            "log_level": clean_env_value(os.getenv("LOG_LEVEL", "info")),
            "max_tokens_per_call": int(clean_env_value(os.getenv("MAX_TOKENS_PER_CALL", "4000")))
        },
        # Opções de escalabilidade
        "scaling": {
            "use_max_node": clean_env_value(os.getenv("USE_MAX_NODE", "false")).lower() == "true",
            "max_concurrent_tasks": int(clean_env_value(os.getenv("MAX_CONCURRENT_TASKS", "1")))
        },
        # Diretórios padrão
        "directories": {
            "originals": "data/originals",
            "processed": "data/processed",
            "temp": "data/temp"
        }
    }
    
    # Se um arquivo de configuração foi especificado, sobrescrever valores padrão
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            yaml_config = yaml.safe_load(f)
            
        # Mesclar configurações do YAML com as padrão
        if yaml_config:
            # Atualizar modelos
            if "models" in yaml_config:
                config["models"].update(yaml_config["models"])
            
            # Atualizar processamento
            if "processing" in yaml_config:
                config["processing"].update(yaml_config["processing"])
            
            # Atualizar escalabilidade
            if "scaling" in yaml_config:
                config["scaling"].update(yaml_config["scaling"])
            
            # Atualizar diretórios
            if "directories" in yaml_config:
                config["directories"].update(yaml_config["directories"])
    
    return config

def save_config(config: Dict[str, Any], output_file: str) -> bool:
    """
    Salva configurações em um arquivo YAML.
    
    Args:
        config (Dict[str, Any]): Configurações a serem salvas.
        output_file (str): Caminho para o arquivo de saída.
    
    Returns:
        bool: True se o arquivo foi salvo com sucesso, False caso contrário.
    """
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar arquivo de configuração: {str(e)}")
        return False

def validate_api_keys() -> Dict[str, bool]:
    """
    Valida se as chaves de API necessárias estão presentes.
    
    Returns:
        Dict[str, bool]: Dicionário com o status de cada chave de API.
    """
    required_keys = {
        "OPENAI": get_api_key("OPENAI"),
        "LANGSMITH": get_api_key("LANGSMITH"),
        "TAVILY": get_api_key("TAVILY"),
        "GOOGLE": get_api_key("GOOGLE"),
        "FIRECRAWL": get_api_key("FIRECRAWL")
    }
    
    # Converter para True/False
    return {k: bool(v) for k, v in required_keys.items()}
