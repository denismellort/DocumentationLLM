#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DocumentationLLM - Processador Inteligente de Documentação para LLMs com Supervisão de IA

Este é o arquivo principal que coordena o pipeline de processamento de documentação.
Cada etapa é executada por um agente especializado, com supervisão integrada
e análise de tokens/custos.
"""

import os
import sys
import argparse
import yaml
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar os agentes conforme forem implementados
try:
    # Primeiro tenta como módulo instalado
    from documentationllm.agents.download_agent import DownloadAgent
    from documentationllm.agents.supervisor_agent import SupervisorAgent
    from documentationllm.agents.token_analyst_agent import TokenAnalystAgent

    # Importar utilitários
    from documentationllm.utils.env_utils import load_config
    from documentationllm.utils.logger import DocumentationLogger
    from documentationllm.utils.version_control import VersionControl
except ImportError:
    # Fallback para desenvolvimento (importação relativa)
    from ..agents.download_agent import DownloadAgent
    # from ..agents.parsing_agent import ParsingAgent
    # from ..agents.semantic_linking_agent import SemanticLinkingAgent
    # from ..agents.output_generation_agent import OutputGenerationAgent
    # from ..agents.cleanup_agent import CleanupAgent
    from ..agents.supervisor_agent import SupervisorAgent
    from ..agents.token_analyst_agent import TokenAnalystAgent

    # Importar utilitários
    from ..utils.env_utils import load_config
    from ..utils.logger import DocumentationLogger
    from ..utils.version_control import VersionControl

# ... restante do código igual ao src/main.py ... 