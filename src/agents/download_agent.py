#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente de Download - DocumentationLLM

Este agente é responsável por baixar a documentação de um repositório Git,
processando os parâmetros de URL e configurando o ambiente para o processamento.
"""

import os
import shutil
import re
from git import Repo, GitCommandError
from urllib.parse import urlparse
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class DownloadAgent:
    """
    Agente responsável por clonar repositórios Git ou baixar documentações
    de outras fontes para processamento local.
    """
    
    def __init__(self, context):
        """
        Inicializa o agente de download.
        
        Args:
            context (dict): Contexto de execução atual.
        """
        self.context = context
        self.repo_url = context["repo_url"]
        self.target_dir = context["directories"]["originals"]
        self.temp_dir = os.path.join(context["directories"]["temp"], "download")
        
        # Garantir que o diretório temporário exista
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def _validate_url(self):
        """
        Valida a URL do repositório e extrai informações relevantes.
        
        Returns:
            dict: Informações sobre o repositório (tipo, owner, nome, etc).
        """
        # Verificar se é um caminho local
        if os.path.exists(self.repo_url) or os.path.exists(os.path.abspath(self.repo_url)):
            # Determinar o caminho absoluto
            abs_path = os.path.abspath(self.repo_url)
            
            # Verificar se é um diretório
            if os.path.isdir(abs_path):
                repo_name = os.path.basename(abs_path)
                
                return {
                    "url": abs_path,
                    "type": "local",
                    "hostname": "local",
                    "path": abs_path,
                    "owner": "local",
                    "name": repo_name,
                    "branch": None
                }
        
        # Validar URL básica
        parsed_url = urlparse(self.repo_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError(f"URL inválida: {self.repo_url}")
        
        # Extrair informações do repositório
        repo_info = {
            "url": self.repo_url,
            "type": "unknown",
            "hostname": parsed_url.netloc,
            "path": parsed_url.path.strip("/"),
            "owner": None,
            "name": None,
            "branch": "main"  # Default
        }
        
        # Identificar tipo de repositório e extrair informações específicas
        if "github.com" in parsed_url.netloc:
            repo_info["type"] = "github"
            
            # Extrair owner/name do caminho
            path_parts = repo_info["path"].split("/")
            if len(path_parts) >= 2:
                repo_info["owner"] = path_parts[0]
                repo_info["name"] = path_parts[1]
                
                # Verificar se há uma branch específica
                if len(path_parts) >= 4 and path_parts[2] == "tree":
                    repo_info["branch"] = path_parts[3]
        
        elif "gitlab.com" in parsed_url.netloc:
            repo_info["type"] = "gitlab"
            
            # Extrair owner/name do caminho
            path_parts = repo_info["path"].split("/")
            if len(path_parts) >= 2:
                repo_info["owner"] = path_parts[0]
                repo_info["name"] = path_parts[1]
                
                # Verificar se há uma branch específica
                if len(path_parts) >= 4 and path_parts[2] == "tree":
                    repo_info["branch"] = path_parts[3]
        
        elif "bitbucket.org" in parsed_url.netloc:
            repo_info["type"] = "bitbucket"
            
            # Extrair owner/name do caminho
            path_parts = repo_info["path"].split("/")
            if len(path_parts) >= 2:
                repo_info["owner"] = path_parts[0]
                repo_info["name"] = path_parts[1]
                
                # Verificar se há uma branch específica
                if len(path_parts) >= 4 and path_parts[2] == "src":
                    repo_info["branch"] = path_parts[3]
        
        # Validar se conseguimos extrair informações básicas
        if not repo_info["name"]:
            console.print(f"[yellow]Aviso: Não foi possível extrair o nome do repositório da URL.[/yellow]")
            # Usar o último componente do caminho como nome, se disponível
            if repo_info["path"]:
                repo_info["name"] = repo_info["path"].split("/")[-1]
        
        return repo_info
    
    def _clone_repository(self, repo_info):
        """
        Clona o repositório Git para o diretório temporário.
        
        Args:
            repo_info (dict): Informações sobre o repositório.
        
        Returns:
            str: Caminho para o repositório clonado.
        """
        # Verificar se é um repositório local
        if repo_info["type"] == "local":
            console.print(f"[green]Repositório local encontrado em: {repo_info['url']}[/green]")
            return repo_info["url"]
        
        # Limpar diretório temporário, se existir
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Determinar o diretório para o clone
        repo_name = repo_info["name"] or "unknown_repo"
        clone_dir = os.path.join(self.temp_dir, repo_name)
        
        # Clonar o repositório
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Clonando repositório... [/bold blue]"),
            console=console
        ) as progress:
            progress.add_task("clone", total=None)
            
            try:
                # Clonar apenas o branch especificado e com profundidade 1 para economia de tempo/espaço
                Repo.clone_from(
                    repo_info["url"],
                    clone_dir,
                    branch=repo_info["branch"],
                    depth=1
                )
                
                console.print(f"[green]Repositório clonado com sucesso em: {clone_dir}[/green]")
                return clone_dir
            
            except GitCommandError as e:
                # Tentar clonar sem especificar branch, caso o anterior falhe
                if "Remote branch not found" in str(e):
                    console.print(f"[yellow]Branch '{repo_info['branch']}' não encontrada. Tentando clonar a branch padrão...[/yellow]")
                    
                    try:
                        Repo.clone_from(
                            repo_info["url"],
                            clone_dir,
                            depth=1
                        )
                        
                        console.print(f"[green]Repositório clonado com sucesso em: {clone_dir}[/green]")
                        return clone_dir
                    
                    except GitCommandError as e2:
                        raise ValueError(f"Falha ao clonar repositório: {str(e2)}")
                else:
                    raise ValueError(f"Falha ao clonar repositório: {str(e)}")
    
    def _process_documentation_files(self, repo_dir):
        """
        Processa e copia os arquivos de documentação do repositório para o diretório alvo.
        
        Args:
            repo_dir (str): Caminho para o repositório clonado.
        
        Returns:
            list: Lista de arquivos de documentação processados.
        """
        # Padrões para identificar arquivos de documentação
        doc_patterns = [
            r'.*\.md$',          # Markdown
            r'.*\.mdx$',         # MDX (Markdown with JSX)
            r'.*\.rst$',         # reStructuredText
            r'.*\.txt$',         # Text files
            r'.*\.html$',        # HTML
            r'.*\.htm$',         # HTM
            r'.*\.ipynb$',       # Jupyter Notebook
            r'.*\.(doc|docx)$',  # Word
            r'.*\.pdf$'          # PDF
        ]
        
        # Diretórios comuns de documentação
        doc_dirs = [
            'docs',
            'doc',
            'documentation',
            'wiki',
            'examples',
            'tutorials',
            'guide',
            'guides',
            'manual',
            'manuals'
        ]
        
        # Lista para armazenar os arquivos encontrados
        found_files = []
        
        # Função auxiliar para verificar se um arquivo corresponde aos padrões de documentação
        def is_doc_file(filename):
            return any(re.match(pattern, filename.lower()) for pattern in doc_patterns)
        
        # Buscar arquivos de documentação
        console.print("[blue]Procurando arquivos de documentação...[/blue]")
        
        # 1. Buscar em diretórios específicos
        for doc_dir in doc_dirs:
            dir_path = os.path.join(repo_dir, doc_dir)
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                for root, _, files in os.walk(dir_path):
                    for file in files:
                        if is_doc_file(file):
                            found_files.append(os.path.join(root, file))
        
        # 2. Buscar na raiz (especialmente README.md e outros arquivos comuns)
        for file in os.listdir(repo_dir):
            file_path = os.path.join(repo_dir, file)
            if os.path.isfile(file_path) and is_doc_file(file):
                found_files.append(file_path)
        
        # Se não encontrarmos nada nos diretórios específicos, buscar em todo o repositório
        if not found_files:
            console.print("[yellow]Nenhum arquivo de documentação encontrado em diretórios convencionais. Buscando em todo o repositório...[/yellow]")
            
            for root, _, files in os.walk(repo_dir):
                # Ignorar diretórios ocultos (ex: .git)
                if '/.' in root or '\\.' in root:
                    continue
                    
                for file in files:
                    if is_doc_file(file):
                        found_files.append(os.path.join(root, file))
        
        # Copiar arquivos encontrados para o diretório alvo
        if found_files:
            console.print(f"[green]Encontrados {len(found_files)} arquivos de documentação.[/green]")
            
            for source_file in found_files:
                # Calcular caminho relativo ao diretório do repositório
                rel_path = os.path.relpath(source_file, repo_dir)
                # Construir caminho no diretório alvo
                target_file = os.path.join(self.target_dir, rel_path)
                
                # Garantir que o diretório de destino exista
                os.makedirs(os.path.dirname(target_file), exist_ok=True)
                
                # Copiar o arquivo
                shutil.copy2(source_file, target_file)
            
            console.print(f"[green]Arquivos copiados para: {self.target_dir}[/green]")
        else:
            console.print("[red]Nenhum arquivo de documentação encontrado.[/red]")
        
        return found_files
    
    def run(self):
        """
        Método principal do agente.
        
        Returns:
            dict: Contexto atualizado com informações do download.
        """
        try:
            console.print(f"[bold blue]Iniciando download do repositório: {self.repo_url}[/bold blue]")
            
            # Validar URL e extrair informações
            repo_info = self._validate_url()
            console.print(f"Repositório identificado: [cyan]{repo_info['type']}[/cyan] - [cyan]{repo_info['owner']}/{repo_info['name']}[/cyan]")
            
            # Clonar repositório
            repo_dir = self._clone_repository(repo_info)
            
            # Processar arquivos de documentação
            doc_files = self._process_documentation_files(repo_dir)
            
            # Atualizar contexto
            self.context["repo_info"] = repo_info
            self.context["documentation_files"] = [os.path.relpath(f, repo_dir) for f in doc_files]
            
            # Adicionar ao histórico, se habilitado
            if self.context["config"]["processing"]["enable_execution_history"]:
                self.context["execution_history"].append({
                    "type": "download",
                    "repo_url": self.repo_url,
                    "repo_info": repo_info,
                    "files_count": len(doc_files),
                    "timestamp": self.context["stats"]["start_time"].isoformat()
                })
            
            # Adicionar à lista de etapas concluídas
            self.context["stats"]["steps_completed"].append("download")
            
            return self.context
        
        except Exception as e:
            console.print(f"[bold red]Erro durante o download: {str(e)}[/bold red]")
            
            # Adicionar à lista de etapas com falha
            self.context["stats"]["steps_failed"].append("download")
            
            # Adicionar ao histórico, se habilitado
            if self.context["config"]["processing"]["enable_execution_history"]:
                self.context["execution_history"].append({
                    "type": "error",
                    "step": "download",
                    "error": str(e),
                    "timestamp": self.context["stats"]["start_time"].isoformat()
                })
            
            raise
