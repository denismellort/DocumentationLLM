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
    from src.agents.download_agent import DownloadAgent
    from src.agents.supervisor_agent import SupervisorAgent
    from src.agents.token_analyst_agent import TokenAnalystAgent

    # Importar utilitários
    from src.utils.env_utils import load_config
    from src.utils.logger import DocumentationLogger
    from src.utils.version_control import VersionControl
except ImportError:
    # Fallback para desenvolvimento (importação relativa)
    from agents.download_agent import DownloadAgent
    # from agents.parsing_agent import ParsingAgent
    # from agents.semantic_linking_agent import SemanticLinkingAgent
    # from agents.output_generation_agent import OutputGenerationAgent
    # from agents.cleanup_agent import CleanupAgent
    from agents.supervisor_agent import SupervisorAgent
    from agents.token_analyst_agent import TokenAnalystAgent

    # Importar utilitários
    from utils.env_utils import load_config
    from utils.logger import DocumentationLogger
    from utils.version_control import VersionControl

# Configuração inicial
console = Console()
load_dotenv()

# Configuração global para o logger
logger = None

def create_execution_context(config, repo_url, output_dir=None):
    """
    Cria o contexto de execução para o pipeline.
    
    Args:
        config (dict): Configurações carregadas.
        repo_url (str): URL do repositório de documentação.
        output_dir (str, optional): Diretório de saída personalizado.
    
    Returns:
        dict: Contexto de execução.
    """
    # Criar um ID de execução único
    execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if logger:
        logger.info(f"Criando contexto de execução ID: {execution_id}")
    else:
        # Fallback para console básico se o logger não estiver configurado
        console.print(f"[blue]Criando contexto de execução ID: {execution_id}[/blue]")
        print(f"DEBUG: Criando contexto de execução ID: {execution_id}")
    
    # Definir diretórios para esta execução
    originals_dir = config["directories"]["originals"]
    processed_dir = output_dir or config["directories"]["processed"]
    temp_dir = config["directories"]["temp"]
    
    # Criar subdiretórios específicos para esta execução
    execution_originals_dir = os.path.join(originals_dir, execution_id)
    execution_processed_dir = os.path.join(processed_dir, execution_id)
    execution_temp_dir = os.path.join(temp_dir, execution_id)
    
    # Garantir que os diretórios existam
    os.makedirs(execution_originals_dir, exist_ok=True)
    os.makedirs(execution_processed_dir, exist_ok=True)
    os.makedirs(execution_temp_dir, exist_ok=True)
    
    # Criar contexto de execução
    context = {
        "execution_id": execution_id,
        "repo_url": repo_url,
        "directories": {
            "originals": execution_originals_dir,
            "processed": execution_processed_dir,
            "temp": execution_temp_dir
        },
        "config": config,
        "stats": {
            "tokens_used": 0,
            "estimated_cost": 0.0,
            "start_time": datetime.now(),
            "end_time": None,
            "steps_completed": [],
            "steps_failed": []
        },
        "execution_history": [],
        "logger": logger
    }
    
    return context

def run_pipeline(context):
    """
    Executa o pipeline completo de processamento de documentação.
    
    Args:
        context (dict): Contexto de execução.
    
    Returns:
        bool: True se a execução foi bem-sucedida, False caso contrário.
    """
    if logger:
        logger.log_rich(
            f"Iniciando processamento do repositório: [bold]{context['repo_url']}[/bold]",
            title="Pipeline Iniciado",
            style="green"
        )
    else:
        print(f"Iniciando pipeline para repositório: {context['repo_url']}")
        console.print(Panel.fit(
            f"[bold green]DocumentationLLM[/bold green] - Iniciando processamento do repositório: [bold]{context['repo_url']}[/bold]",
            title="Pipeline Iniciado",
            subtitle=f"ID: {context['execution_id']}"
        ))
    
    try:
        # 1. Download do repositório
        if logger:
            logger.log_step_start("download")
        else:
            print("Etapa 1: Download do repositório")
            
        download_agent = DownloadAgent(context)
        context = download_agent.run()
        
        # Verificar se foram encontrados arquivos de documentação
        if not context.get("documentation_files") or len(context.get("documentation_files", [])) == 0:
            mensagem = "Aviso: Nenhum arquivo de documentação foi detectado no repositório."
            if logger:
                logger.warning(mensagem)
            else:
                console.print(f"[yellow]{mensagem}[/yellow]")
                
        # Validar etapa de download (se supervisão estiver habilitada)
        if context["config"]["processing"]["enable_supervision"]:
            if logger:
                logger.info("Validando etapa de download")
            else:
                print("Validando etapa de download")
                
            supervisor = SupervisorAgent(context)
            validation = supervisor.validate_step(
                "download",
                {"status": "success", "repo_url": context["repo_url"], "files_count": len(context.get("documentation_files", []))},
                "Download do repositório concluído."
            )
            
            # Se a validação falhar, adicionar aviso ao log
            if not validation["valid"]:
                if logger:
                    logger.warning(f"Aviso na validação do download: {validation['feedback']}")
                else:
                    console.print(f"[yellow]Aviso na validação do download: {validation['feedback']}[/yellow]")
        
        # 2. Parsing de arquivos (descomentado quando implementado)
        # parsing_agent = ParsingAgent(context)
        # context = parsing_agent.run()
        
        # 3. Vinculação semântica (descomentado quando implementado)
        # semantic_linking_agent = SemanticLinkingAgent(context)
        # context = semantic_linking_agent.run()
        
        # 4. Geração de saída (descomentado quando implementado)
        # output_generation_agent = OutputGenerationAgent(context)
        # context = output_generation_agent.run()
        
        # 5. Limpeza (descomentado quando implementado)
        # cleanup_agent = CleanupAgent(context)
        # context = cleanup_agent.run()
        
        # 6. Análise de tokens (se habilitado)
        if context["config"]["processing"]["enable_token_analysis"]:
            if logger:
                logger.log_step_start("token_analysis")
            else:
                print("Etapa 6: Análise de tokens")
                
            token_analyst_agent = TokenAnalystAgent(context)
            context = token_analyst_agent.run()
        
        # Registrar tempo de término
        context["stats"]["end_time"] = datetime.now()
        
        # Exibir resumo da execução
        duration = context["stats"]["end_time"] - context["stats"]["start_time"]
        
        if logger:
            logger.log_rich(
                f"[bold green]Processamento concluído com sucesso![/bold green]\n"
                f"Duração: {duration}\n"
                f"Tokens utilizados: {context['stats']['tokens_used']}\n"
                f"Custo estimado: ${context['stats']['estimated_cost']:.4f}\n"
                f"Saída salva em: [bold]{context['directories']['processed']}[/bold]",
                title="Pipeline Concluído",
                style="green"
            )
        else:
            print(f"Processamento concluído em: {duration}")
            console.print(Panel.fit(
                f"[bold green]Processamento concluído com sucesso![/bold green]\n"
                f"Duração: {duration}\n"
                f"Tokens utilizados: {context['stats']['tokens_used']}\n"
                f"Custo estimado: ${context['stats']['estimated_cost']:.4f}\n"
                f"Saída salva em: [bold]{context['directories']['processed']}[/bold]",
                title="Pipeline Concluído",
                subtitle=f"ID: {context['execution_id']}"
            ))
        
        return True
    
    except Exception as e:
        # Registrar tempo de término
        context["stats"]["end_time"] = datetime.now()
        
        # Exibir erro
        if logger:
            logger.error(f"Erro durante o processamento: {str(e)}")
            logger.log_rich(
                f"[bold red]Erro durante o processamento:[/bold red]\n{str(e)}",
                title="Pipeline Interrompido",
                style="red"
            )
        else:
            print(f"ERRO: {str(e)}")
            console.print(Panel.fit(
                f"[bold red]Erro durante o processamento:[/bold red]\n{str(e)}",
                title="Pipeline Interrompido",
                subtitle=f"ID: {context['execution_id']}"
            ))
        
        return False
    
    finally:
        # Gerar relatórios de execução, se habilitado
        if context["config"]["processing"]["enable_execution_history"]:
            report_path = os.path.join(context["directories"]["processed"], "execution_report.md")
            history_path = os.path.join(context["directories"]["processed"], "execution_history.json")
            
            # Gerar relatórios de execução
            if logger:
                logger.info("Gerando relatórios de execução")
            else:
                print("Gerando relatórios de execução")
                
            SupervisorAgent.generate_report(context, report_path)
            SupervisorAgent.save_history(context, history_path)
            
            if logger:
                logger.info(f"Relatório de execução salvo em: {report_path}")
                logger.info(f"Histórico de execução salvo em: {history_path}")
            else:
                console.print(f"Relatório de execução salvo em: [bold]{report_path}[/bold]")
                console.print(f"Histórico de execução salvo em: [bold]{history_path}[/bold]")

def parse_arguments():
    """
    Processa os argumentos da linha de comando.
    
    Returns:
        argparse.Namespace: Argumentos processados.
    """
    parser = argparse.ArgumentParser(
        description="DocumentationLLM - Processador Inteligente de Documentação para LLMs com Supervisão de IA"
    )
    
    # Argumentos principais
    parser.add_argument(
        "--repo", "-r",
        help="URL do repositório Git com a documentação a ser processada"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Diretório para salvar a saída processada (opcional)"
    )
    
    parser.add_argument(
        "--config", "-c",
        help="Caminho para arquivo de configuração YAML (opcional)"
    )
    
    # Argumentos de logging
    log_group = parser.add_argument_group('Logging')
    log_group.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Ativar modo verboso com logs detalhados"
    )
    
    log_group.add_argument(
        "--debug",
        action="store_true",
        help="Ativar modo debug com logs extremamente detalhados"
    )
    
    log_group.add_argument(
        "--log-file",
        action="store_true",
        help="Salvar logs em arquivos"
    )
    
    log_group.add_argument(
        "--log-api",
        action="store_true",
        help="Registrar todas as chamadas de API"
    )
    
    log_group.add_argument(
        "--log-dir",
        default="logs",
        help="Diretório para salvar logs (padrão: logs)"
    )
    
    # Argumentos de versionamento
    version_group = parser.add_argument_group('Controle de Versão')
    version_group.add_argument(
        "--create-snapshot",
        action="store_true",
        help="Criar snapshot do código antes da execução"
    )
    
    version_group.add_argument(
        "--rollback",
        help="Fazer rollback para um snapshot específico"
    )
    
    version_group.add_argument(
        "--list-snapshots",
        action="store_true",
        help="Listar todos os snapshots disponíveis"
    )
    
    version_group.add_argument(
        "--compare-snapshots",
        nargs=2,
        metavar=("SNAPSHOT1", "SNAPSHOT2"),
        help="Comparar dois snapshots"
    )
    
    version_group.add_argument(
        "--version-dir",
        default=".version_control",
        help="Diretório para armazenar snapshots (padrão: .version_control)"
    )
    
    return parser.parse_args()

def setup_logging(args):
    """
    Configura o sistema de logging com base nos argumentos fornecidos.
    
    Args:
        args (argparse.Namespace): Argumentos processados.
    
    Returns:
        DocumentationLogger: Instância do logger configurado.
    """
    # Determinar nível de log
    if args.debug:
        log_level = "debug"
    elif args.verbose:
        log_level = "info"
    else:
        log_level = "warning"
    
    # Instanciar logger
    return DocumentationLogger(
        log_level=log_level,
        enable_file_logging=args.log_file,
        log_dir=args.log_dir,
        enable_console=True,
        enable_api_logging=args.log_api
    )

def handle_version_control(args):
    """
    Manipula operações de controle de versão com base nos argumentos.
    
    Args:
        args (argparse.Namespace): Argumentos processados.
    
    Returns:
        bool: True para continuar a execução, False para encerrar.
    """
    # Inicializar sistema de controle de versão
    vc = VersionControl(base_dir=args.version_dir)
    
    # Listar snapshots
    if args.list_snapshots:
        snapshots = vc.list_versions()
        if not snapshots:
            console.print("[yellow]Nenhum snapshot encontrado.[/yellow]")
        else:
            console.print("[bold]Snapshots disponíveis:[/bold]")
            for snapshot in snapshots:
                console.print(f"[green]ID: {snapshot['id']}[/green]")
                console.print(f"  Descrição: {snapshot['description']}")
                console.print(f"  Data: {snapshot['timestamp']}")
                console.print(f"  Arquivos: {snapshot['files_count']}")
                console.print("")
        
        # Encerrar após listar
        return False
    
    # Comparar snapshots
    if args.compare_snapshots:
        snapshot1, snapshot2 = args.compare_snapshots
        report = vc.compare_versions(snapshot1, snapshot2)
        
        if not report["success"]:
            console.print(f"[red]Erro: {report['message']}[/red]")
            return False
        
        console.print(f"[bold]Comparação: {report['version1']} vs {report['version2']}[/bold]")
        
        # Contar diferenças por tipo
        diffs_by_status = {}
        for diff in report["diffs"]:
            status = diff["status"]
            if status not in diffs_by_status:
                diffs_by_status[status] = 0
            diffs_by_status[status] += 1
        
        # Exibir resumo
        for status, count in diffs_by_status.items():
            console.print(f"[blue]{status}[/blue]: {count} arquivos")
        
        # Exibir detalhes sob demanda
        if input("Exibir detalhes? (s/n): ").lower() == 's':
            for diff in report["diffs"]:
                console.print(f"[bold]{diff['file']}[/bold]: {diff['status']}")
                if diff["status"] == "modified" and "diff" in diff:
                    console.print(diff["diff"])
                console.print("")
        
        return False
    
    # Fazer rollback
    if args.rollback:
        # Confirmar antes de fazer rollback
        console.print(f"[yellow]Aviso: Você está prestes a reverter o código para o snapshot {args.rollback}.[/yellow]")
        console.print("[yellow]Esta operação sobrescreverá os arquivos atuais.[/yellow]")
        
        if input("Continuar? (s/n): ").lower() != 's':
            console.print("[blue]Operação cancelada pelo usuário.[/blue]")
            return False
        
        # Executar rollback
        report = vc.rollback(args.rollback)
        
        if not report["success"]:
            console.print(f"[red]Erro: {report['message']}[/red]")
            return False
        
        console.print(f"[green]Rollback concluído para snapshot {args.rollback}.[/green]")
        console.print(f"[green]Descrição: {report['description']}[/green]")
        console.print(f"[green]{len(report['files_restored'])} arquivos restaurados.[/green]")
        
        if report['files_not_found']:
            console.print(f"[yellow]Aviso: {len(report['files_not_found'])} arquivos não foram encontrados no backup.[/yellow]")
        
        return False
    
    # Criar snapshot
    if args.create_snapshot:
        description = input("Digite uma descrição para este snapshot: ")
        snapshot_id = vc.create_snapshot(description)
        console.print(f"[green]Snapshot criado: {snapshot_id}[/green]")
    
    # Continuar a execução normal
    return True

def main():
    """
    Função principal do programa.
    """
    global logger
    
    # Processar argumentos da linha de comando
    args = parse_arguments()
    
    # Configurar logging se solicitado
    if args.verbose or args.debug or args.log_file or args.log_api:
        logger = setup_logging(args)
        logger.info("Logging configurado")
    
    # Lidar com operações de controle de versão
    if args.list_snapshots or args.compare_snapshots or args.rollback or args.create_snapshot:
        if not handle_version_control(args):
            return 0
    
    # Verificar se temos um repositório para processar
    if not args.repo:
        if logger:
            logger.error("URL do repositório não especificada")
        else:
            console.print("[bold red]Erro: URL do repositório não especificada[/bold red]")
            print("Use --repo URL_DO_REPOSITORIO para indicar qual repositório processar")
        
        return 1
    
    # Configurar ambiente
    config = load_config(args.config)
    
    if logger:
        logger.info("Configuração carregada")
    else:
        print("Configuração carregada")
    
    # Criar contexto de execução
    context = create_execution_context(config, args.repo, args.output)
    
    # Executar pipeline
    success = run_pipeline(context)
    
    # Retornar código de saída
    if logger:
        logger.info(f"Finalizando com status: {'sucesso' if success else 'falha'}")
    else:
        print(f"Finalizando com status: {'sucesso' if success else 'falha'}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
