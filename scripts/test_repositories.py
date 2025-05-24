#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar o DocumentationLLM com múltiplos repositórios.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from documentationllm.main import main

def test_repository(url: str) -> dict:
    """
    Testa um repositório e retorna os resultados.
    
    Args:
        url: URL do repositório
        
    Returns:
        dict: Resultados do teste
    """
    start_time = datetime.now()
    
    # Configurar argumentos
    sys.argv = [sys.argv[0], url, '-v']
    
    # Executar processamento
    exit_code = main()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Coletar resultados
    processed_dir = Path('data/processed')
    results = {
        'url': url,
        'success': exit_code == 0,
        'duration': duration,
        'files_processed': 0,
        'total_size': 0,
        'error': None
    }
    
    # Ler metadados se existirem
    metadata_file = processed_dir / 'files_metadata.json'
    if metadata_file.exists():
        try:
            with open(metadata_file) as f:
                metadata = json.load(f)
                results['files_processed'] = metadata.get('total_files', 0)
                results['total_size'] = metadata.get('total_size', 0)
        except Exception as e:
            results['error'] = str(e)
    
    return results

def main_test():
    """Função principal de teste."""
    console = Console()
    
    # Repositórios para testar
    repositories = [
        "https://github.com/openai/openai-python",
        "https://github.com/microsoft/playwright/tree/main/docs/",
        "https://github.com/puppeteer/puppeteer/tree/main/docs/"
    ]
    
    # Criar tabela de resultados
    table = Table(title="Resultados dos Testes")
    table.add_column("Repositório", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Arquivos", justify="right")
    table.add_column("Tamanho Total", justify="right")
    table.add_column("Duração (s)", justify="right")
    
    # Testar cada repositório
    all_results = []
    for repo in repositories:
        console.print(f"\n[bold cyan]Testando:[/bold cyan] {repo}")
        results = test_repository(repo)
        all_results.append(results)
        
        # Adicionar à tabela
        table.add_row(
            repo,
            "✓" if results['success'] else "✗",
            str(results['files_processed']),
            f"{results['total_size'] / 1024 / 1024:.2f} MB",
            f"{results['duration']:.2f}"
        )
    
    # Mostrar resultados
    console.print("\n")
    console.print(table)
    
    # Salvar relatório
    report_file = Path('data/processed/test_report.md')
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Relatório de Testes - DocumentationLLM\n\n")
        f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for result in all_results:
            f.write(f"## {result['url']}\n\n")
            f.write(f"- Status: {'Sucesso' if result['success'] else 'Falha'}\n")
            f.write(f"- Arquivos Processados: {result['files_processed']}\n")
            f.write(f"- Tamanho Total: {result['total_size'] / 1024 / 1024:.2f} MB\n")
            f.write(f"- Duração: {result['duration']:.2f} segundos\n")
            if result['error']:
                f.write(f"- Erro: {result['error']}\n")
            f.write("\n")
    
    console.print(f"\n[green]Relatório salvo em:[/green] {report_file}")

if __name__ == '__main__':
    main_test()