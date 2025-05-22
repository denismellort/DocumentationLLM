#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Versões do DocumentationLLM

Este script oferece uma interface simples para:
- Criar snapshots do código
- Listar snapshots disponíveis
- Comparar snapshots
- Restaurar código para versões anteriores

Pode ser usado independentemente do programa principal.
"""

import os
import sys
import argparse
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from utils.version_control import VersionControl
    console = Console()
except ImportError:
    print("Erro ao importar módulos necessários.")
    print("Certifique-se de executar este script do diretório raiz do projeto.")
    sys.exit(1)

def create_snapshot(vc, description=None):
    """
    Cria um snapshot do código atual.
    
    Args:
        vc (VersionControl): Instância do controlador de versões.
        description (str, optional): Descrição para o snapshot.
    """
    if not description:
        description = Prompt.ask("Digite uma descrição para este snapshot")
    
    snapshot_id = vc.create_snapshot(description)
    
    console.print(f"[green]✓[/green] Snapshot criado: [bold]{snapshot_id}[/bold]")
    console.print(f"   Descrição: {description}")
    console.print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def list_snapshots(vc, verbose=False):
    """
    Lista todos os snapshots disponíveis.
    
    Args:
        vc (VersionControl): Instância do controlador de versões.
        verbose (bool): Se True, exibe detalhes extras.
    """
    snapshots = vc.list_versions()
    
    if not snapshots:
        console.print("[yellow]Nenhum snapshot encontrado.[/yellow]")
        return
    
    # Obter versão atual
    current_version = vc.get_current_version()
    current_id = current_version["id"] if current_version else None
    
    # Criar tabela
    table = Table(title="Snapshots Disponíveis")
    
    table.add_column("ID", style="cyan")
    table.add_column("Timestamp", style="magenta")
    table.add_column("Descrição")
    table.add_column("Arquivos", justify="right")
    if verbose:
        table.add_column("Detalhes")
    
    # Adicionar linhas
    for snapshot in snapshots:
        # Destacar versão atual
        is_current = snapshot["id"] == current_id
        id_str = f"[green]{snapshot['id']} ★[/green]" if is_current else snapshot["id"]
        
        row = [
            id_str,
            snapshot["timestamp"],
            snapshot["description"],
            str(snapshot["files_count"])
        ]
        
        if verbose:
            # Calcular tamanho total
            total_size = sum(file.get("size", 0) for file in snapshot.get("files", []))
            details = f"Tamanho: {total_size / 1024:.1f} KB"
            row.append(details)
        
        table.add_row(*row)
    
    console.print(table)

def compare_snapshots(vc, version1, version2=None):
    """
    Compara dois snapshots.
    
    Args:
        vc (VersionControl): Instância do controlador de versões.
        version1 (str): ID do primeiro snapshot.
        version2 (str, optional): ID do segundo snapshot. Se None, compara com código atual.
    """
    # Se não especificou segunda versão, comparar com a atual
    version2_str = version2 or "código atual"
    
    console.print(f"[bold]Comparando:[/bold] {version1} vs {version2_str}")
    
    report = vc.compare_versions(version1, version2)
    
    if not report["success"]:
        console.print(f"[red]Erro: {report['message']}[/red]")
        return
    
    # Agrupar por status
    grouped = {}
    for diff in report["diffs"]:
        status = diff["status"]
        if status not in grouped:
            grouped[status] = []
        grouped[status].append(diff)
    
    # Mostrar resumo
    console.print("\n[bold]Resumo de diferenças:[/bold]")
    
    table = Table()
    table.add_column("Status", style="cyan")
    table.add_column("Arquivos", justify="right")
    
    for status, files in grouped.items():
        table.add_row(status, str(len(files)))
    
    console.print(table)
    
    # Perguntar se deseja ver detalhes
    if not grouped:
        console.print("[green]Sem diferenças encontradas.[/green]")
        return
    
    show_details = Confirm.ask("Deseja ver detalhes das diferenças?")
    if not show_details:
        return
    
    # Mostrar detalhes
    for status, files in grouped.items():
        console.print(f"\n[bold cyan]{status}[/bold cyan] ({len(files)} arquivos):")
        
        for diff in files:
            console.print(f"  • {diff['file']}")
            
            if status == "modified" and "diff" in diff and Confirm.ask(f"    Ver diff de {diff['file']}?"):
                console.print(diff["diff"])

def do_rollback(vc, version_id=None, dry_run=False):
    """
    Restaura o código para um snapshot específico.
    
    Args:
        vc (VersionControl): Instância do controlador de versões.
        version_id (str, optional): ID do snapshot. Se None, usa a versão anterior.
        dry_run (bool): Se True, apenas simula sem fazer alterações.
    """
    # Se não especificou versão, listar snapshots
    if not version_id:
        list_snapshots(vc)
        version_id = Prompt.ask("Digite o ID do snapshot para restaurar")
    
    # Confirmar operação
    console.print(f"[yellow]Aviso: Você está prestes a reverter o código para o snapshot {version_id}.[/yellow]")
    console.print("[yellow]Esta operação sobrescreverá os arquivos atuais.[/yellow]")
    
    if not Confirm.ask("Deseja continuar?"):
        console.print("[blue]Operação cancelada pelo usuário.[/blue]")
        return
    
    # Executar rollback
    if dry_run:
        console.print("[bold]Simulando rollback (dry-run)...[/bold]")
    else:
        console.print("[bold]Executando rollback...[/bold]")
    
    report = vc.rollback(version_id, dry_run)
    
    if not report["success"]:
        console.print(f"[red]Erro: {report['message']}[/red]")
        return
    
    # Mostrar resultado
    if dry_run:
        console.print(f"[green]Simulação concluída. {len(report['files_restored'])} arquivos seriam restaurados.[/green]")
    else:
        console.print(f"[green]Rollback concluído. {len(report['files_restored'])} arquivos restaurados.[/green]")
    
    # Mostrar detalhes
    if report["files_not_found"]:
        console.print(f"[yellow]Aviso: {len(report['files_not_found'])} arquivos não foram encontrados no backup.[/yellow]")
        if Confirm.ask("Deseja ver quais arquivos faltaram?"):
            for file in report["files_not_found"]:
                console.print(f"  • {file}")

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Gerenciador de Versões para DocumentationLLM")
    
    parser.add_argument(
        "--version-dir", "-d",
        default=".version_control",
        help="Diretório para armazenar snapshots (padrão: .version_control)")
    
    # Subcomandos
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")
    
    # Comando: create
    create_parser = subparsers.add_parser("create", help="Criar novo snapshot")
    create_parser.add_argument("description", nargs="?", help="Descrição do snapshot")
    
    # Comando: list
    list_parser = subparsers.add_parser("list", help="Listar snapshots")
    list_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Mostrar informações detalhadas")
    
    # Comando: compare
    compare_parser = subparsers.add_parser("compare", help="Comparar snapshots")
    compare_parser.add_argument("version1", help="ID do primeiro snapshot")
    compare_parser.add_argument("version2", nargs="?", help="ID do segundo snapshot (opcional)")
    
    # Comando: rollback
    rollback_parser = subparsers.add_parser("rollback", help="Restaurar para snapshot")
    rollback_parser.add_argument("version", nargs="?", help="ID do snapshot a restaurar")
    rollback_parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Simulação (não modifica arquivos)")
    
    args = parser.parse_args()
    
    # Inicializar controle de versão
    vc = VersionControl(base_dir=args.version_dir)
    
    # Executar comando
    if args.command == "create":
        create_snapshot(vc, args.description)
    
    elif args.command == "list":
        list_snapshots(vc, args.verbose)
    
    elif args.command == "compare":
        compare_snapshots(vc, args.version1, args.version2)
    
    elif args.command == "rollback":
        do_rollback(vc, args.version, args.dry_run)
    
    else:
        # Se nenhum comando fornecido, mostrar menu interativo
        console.print("[bold]Gerenciador de Versões do DocumentationLLM[/bold]")
        console.print("Escolha uma opção:")
        console.print("1. Criar snapshot")
        console.print("2. Listar snapshots")
        console.print("3. Comparar snapshots")
        console.print("4. Restaurar snapshot")
        console.print("0. Sair")
        
        choice = Prompt.ask("Opção", choices=["0", "1", "2", "3", "4"], default="0")
        
        if choice == "1":
            create_snapshot(vc)
        elif choice == "2":
            list_snapshots(vc, True)
        elif choice == "3":
            list_snapshots(vc, False)
            v1 = Prompt.ask("Digite o ID do primeiro snapshot")
            v2 = Prompt.ask("Digite o ID do segundo snapshot (opcional, deixe em branco para comparar com o código atual)",
                           default="")
            compare_snapshots(vc, v1, v2 if v2 else None)
        elif choice == "4":
            do_rollback(vc)

if __name__ == "__main__":
    main() 