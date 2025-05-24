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

# Importar os agentes
from documentationllm.agents.download_agent import DownloadAgent
from documentationllm.agents.supervisor_agent import SupervisorAgent
from documentationllm.agents.token_analyst_agent import TokenAnalystAgent

# Importar utilitários
from documentationllm.utils.env_utils import load_config
from documentationllm.utils.logger import DocumentationLogger
from documentationllm.utils.version_control import VersionControl

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ... restante do código igual ao src/main.py ... 

# -----------------------------------------------
# Função principal exposta para o CLI
# -----------------------------------------------

def main() -> int:
    """Ponto de entrada principal para o DocumentationLLM."""
    # Carregar variáveis de ambiente
    load_dotenv()
    
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
        version="DocumentationLLM v0.1.3"
    )
    
    args = parser.parse_args()
    
    # Inicializar console
    console = Console()
    
    # Se nenhuma fonte foi fornecida, mostrar ajuda
    if not args.source:
        console.print(Panel(
            "[bold yellow]DocumentationLLM v0.1.3[/bold yellow]\n\n"
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
        config = load_config(args.config)
        
        # Inicializar logger
        logger = DocumentationLogger(config)
        if args.verbose:
            logger.set_verbose(True)
        
        # Criar controle de versão
        version_control = VersionControl(config, logger)
        
        # Mostrar banner inicial
        console.print(Panel(
            f"[bold cyan]Processando:[/bold cyan] {args.source}\n"
            f"[bold cyan]Configuração:[/bold cyan] {args.config}",
            title="[bold green]DocumentationLLM v0.1.3[/bold green]",
            border_style="green"
        ))
        
        # Executar pipeline
        logger.info("Iniciando pipeline de processamento...")
        
        # Por enquanto, apenas executa o agente de download
        # TODO: Implementar pipeline completo
        download_agent = DownloadAgent(config, logger, version_control)
        result = download_agent.execute(source=args.source)
        
        if result:
            console.print("[bold green]✓[/bold green] Pipeline executado com sucesso!")
        else:
            console.print("[bold red]✗[/bold red] Pipeline falhou!")
            return 1
            
    except Exception as e:
        console.print(f"[bold red]Erro:[/bold red] {str(e)}")
        return 1
    
    return 0


# Executa quando rodado diretamente: `python -m documentationllm.main`
if __name__ == "__main__":  # pragma: no cover
    sys.exit(main()) 