"""
Módulo de logging do DocumentationLLM.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Configura um logger com formatação padrão.

    Args:
        name (str): Nome do logger
        level (Optional[int]): Nível de logging (padrão: INFO)

    Returns:
        logging.Logger: Logger configurado
    """
    if level is None:
        level = logging.INFO
    
    # Cria o logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove handlers existentes
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Cria o handler de console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Define o formato
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
    )
    console_handler.setFormatter(formatter)
    
    # Adiciona o handler
    logger.addHandler(console_handler)
    
    # Cria o diretório de logs se não existir
    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Cria o handler de arquivo
    file_handler = logging.FileHandler(
        logs_dir / f"{name.replace('.', '_')}.log",
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Adiciona o handler
    logger.addHandler(file_handler)
    
    return logger