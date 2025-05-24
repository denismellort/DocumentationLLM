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
from datetime import datetime
from pathlib import Path

import yaml
from rich.console import Console
from rich.panel import Panel

# Importar os agentes
from documentationllm.agents.download_agent import DownloadAgent
from documentationllm.agents.parsing_agent import ParsingAgent
from documentationllm.agents.semantic_linking_agent import SemanticLinkingAgent
from documentationllm.agents.supervisor_agent import SupervisorAgent
from documentationllm.agents.token_analyst_agent import TokenAnalystAgent

# Importar utilitários
from documentationllm.utils.config import Config
from documentationllm.utils.logging import setup_logger

# Configurar logger
logger = setup_logger(__name__)

def main() -> int:
    """Ponto de entrada principal para o DocumentationLLM."""
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(
        description="DocumentationLLM - Processador Inteligente de Documentação para LLMs"
    )
    parser.add_argument(
        "source",
        nargs="?",
        help="URL do repositório Git ou caminho local para processar"
    )
    parser.add_argument(
        "-c", "--config",
        default="config.yaml",
        help="Arquivo de configuração (padrão: config.yaml)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Modo verboso"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="DocumentationLLM v0.1.0"
    )
    
    args = parser.parse_args()
    
    # Inicializar console
    console = Console()
    
    # Se nenhuma fonte foi fornecida, mostrar ajuda
    if not args.source:
        console.print(Panel(
            "[bold yellow]DocumentationLLM v0.1.0[/bold yellow]\n\n"
            "Processador Inteligente de Documentação para LLMs com Supervisão de IA\n\n"
            "[cyan]Uso:[/cyan]\n"
            "  docllm <url-ou-caminho> [opções]\n\n"
            "[cyan]Exemplos:[/cyan]\n"
            "  docllm https://github.com/usuario/repo.git\n"
            "  docllm ./meu-projeto-local\n"
            "  docllm . -v\n\n"
            "[cyan]Para mais informações:[/cyan]\n"
            "  docllm --help",
            title="[bold green]Bem-vindo ao DocumentationLLM![/bold green]",
            border_style="green"
        ))
        return 0
    
    try:
        # Carregar configurações
        config = Config(args.config)
        
        # Ajustar nível de log se modo verboso
        if args.verbose:
            logger.setLevel("DEBUG")
        
        # Mostrar banner inicial
        console.print(Panel(
            f"[bold cyan]Processando:[/bold cyan] {args.source}\n"
            f"[bold cyan]Configuração:[/bold cyan] {args.config}",
            title="[bold green]DocumentationLLM v0.1.0[/bold green]",
            border_style="green"
        ))
        
        # Criar contexto inicial
        context = {
            "config": config,
            "execution_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "repo_url": args.source,
            "directories": config.get("directories")
        }
        
        # Inicializar agentes
        download_agent = DownloadAgent(context)
        parsing_agent = ParsingAgent(context)
        semantic_linking_agent = SemanticLinkingAgent(context)
        supervisor_agent = SupervisorAgent(context)
        token_analyst = TokenAnalystAgent(context)
        
        # Executar pipeline
        logger.info("Iniciando pipeline de processamento...")
        
        # 1. Download e identificação de arquivos
        logger.info("Etapa 1: Download e identificação de arquivos")
        context = download_agent.run()
        if not context.get("download_completed"):
            raise Exception("Falha na etapa de download")
        
        # 2. Parsing e estruturação
        logger.info("Etapa 2: Parsing e estruturação dos documentos")
        context = parsing_agent.run()
        if not context.get("parsing_completed"):
            raise Exception("Falha na etapa de parsing")
        
        # 3. Vinculação semântica
        logger.info("Etapa 3: Vinculação semântica entre texto e código")
        context = semantic_linking_agent.run()
        if not context.get("semantic_linking_completed"):
            raise Exception("Falha na etapa de vinculação semântica")
        
        # 4. Análise de tokens
        logger.info("Etapa 4: Análise de tokens")
        context = token_analyst.run()
        
        # 5. Supervisão e relatório final
        logger.info("Etapa 5: Geração de relatório final")
        context = supervisor_agent.run()
        
        console.print("[bold green]✓[/bold green] Pipeline executado com sucesso!")
        return 0
            
    except Exception as e:
        console.print(f"[bold red]Erro:[/bold red] {str(e)}")
        if args.verbose:
            import traceback
            console.print(traceback.format_exc())
        return 1

# Executa quando rodado diretamente
if __name__ == "__main__":  # pragma: no cover
    sys.exit(main()) 