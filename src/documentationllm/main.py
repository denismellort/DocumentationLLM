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
from documentationllm.agents.parsing_agent import ParsingAgent
from documentationllm.agents.supervisor_agent import SupervisorAgent
from documentationllm.agents.token_analyst_agent import TokenAnalystAgent
from documentationllm.agents.semantic_linking_agent import SemanticLinkingAgent

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
    print("[DEBUG] OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
    
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
        
        # Garantir que log_level é string
        log_level = config["processing"].get("log_level", "info")
        if isinstance(log_level, dict):
            # Corrigir caso venha como dict por erro de merge/config
            log_level = log_level.get("value", "info")
        if not isinstance(log_level, str):
            log_level = str(log_level)
        print(f"[DEBUG] log_level usado para o logger: {log_level}")
        logger = DocumentationLogger(log_level=log_level)
        # if args.verbose:
        #     logger.set_verbose(True)
        
        # Criar controle de versão
        version_control = VersionControl()
        
        # Mostrar banner inicial
        console.print(Panel(
            f"[bold cyan]Processando:[/bold cyan] {args.source}\n"
            f"[bold cyan]Configuração:[/bold cyan] {args.config}",
            title="[bold green]DocumentationLLM v0.1.3[/bold green]",
            border_style="green"
        ))
        
        # Criar contexto inicial
        context = {
            "config": config,
            "logger": logger,
            "version_control": version_control,
            "execution_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "repo_url": args.source,
            "directories": config["directories"],
            "stats": {
                "tokens_used": 0,
                "estimated_cost": 0.0,
                "steps_completed": [],
                "steps_failed": [],
                "start_time": datetime.now(),
                "end_time": None,
            },
            "token_stats": {
                "models": {},
                "steps": {},
                "total_tokens": 0,
                "total_cost": 0.0
            }
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
        print(f"[cyan][DEBUG] Quantidade de documentos em context['parsed_documents']: {len(context.get('parsed_documents', {}))}")

        # 2.5 Vinculação semântica (IA)
        logger.info("Etapa 2.5: Vinculação semântica (IA)")
        context = semantic_linking_agent.run()
        
        # 3. Análise de tokens
        logger.info("Etapa 3: Análise de tokens")
        context = token_analyst.run()
        
        # 4. Supervisão e relatório final
        logger.info("Etapa 4: Geração de relatório final")
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