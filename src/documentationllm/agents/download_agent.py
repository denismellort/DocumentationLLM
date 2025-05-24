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
import json
from datetime import datetime
from git import Repo, GitCommandError
from urllib.parse import urlparse
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Importar funções de segurança usando importação absoluta
try:
    from src.utils.security import (
        validate_url,
        sanitize_path,
        sanitize_filename,
        is_dangerous_file,
        generate_content_hash
    )
except ImportError:
    # Fallback para importação relativa para desenvolvimento
    from ..utils.security import (
        validate_url,
        sanitize_path,
        sanitize_filename,
        is_dangerous_file,
        generate_content_hash
    )

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
        
        # Verificar se temos logger
        self.logger = context.get("logger")
        
        # Garantir que o diretório temporário exista
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def _validate_url(self):
        """
        Valida a URL do repositório e extrai informações relevantes.
        
        Returns:
            dict: Informações sobre o repositório (tipo, owner, nome, etc).
        """
        # Usar a nova função de validação de URL
        is_valid, error_message = validate_url(self.repo_url)
        
        if not is_valid:
            if self.logger:
                self.logger.error(f"URL inválida: {error_message}")
            else:
                console.print(f"[bold red]URL inválida: {error_message}[/bold red]")
            raise ValueError(f"URL inválida: {error_message}")
        
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
        Clona o repositório Git para o diretório originals/<nome-repositorio> e temp/<nome-repositorio>.
        Apaga o clone anterior se já existir.
        Args:
            repo_info (dict): Informações sobre o repositório.
        Returns:
            str: Caminho para o repositório clonado.
        """
        # Determinar o nome do repositório
        repo_name = repo_info["name"] or "unknown_repo"
        repo_name = sanitize_filename(repo_name)
        # Diretórios alvo
        originals_dir = os.path.join(self.context["config"]["directories"]["originals"], repo_name)
        temp_dir = os.path.join(self.context["config"]["directories"]["temp"], repo_name)
        # Apagar clones anteriores
        if os.path.exists(originals_dir):
            shutil.rmtree(originals_dir)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(originals_dir, exist_ok=True)
        os.makedirs(temp_dir, exist_ok=True)
        # Clonar no originals_dir
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Clonando repositório... [/bold blue]"),
            console=console
        ) as progress:
            progress.add_task("clone", total=None)
            try:
                Repo.clone_from(
                    repo_info["url"],
                    originals_dir,
                    branch=repo_info["branch"],
                    depth=1
                )
                if self.logger:
                    self.logger.info(f"Repositório clonado com sucesso em: {originals_dir}")
                else:
                    console.print(f"[green]Repositório clonado com sucesso em: {originals_dir}[/green]")
                # Copiar para temp_dir para processamento isolado
                shutil.copytree(originals_dir, temp_dir, dirs_exist_ok=True)
                return temp_dir
            except GitCommandError as e:
                if self.logger:
                    self.logger.error(f"Falha ao clonar repositório: {str(e)}")
                raise ValueError(f"Falha ao clonar repositório: {str(e)}")
    
    def _process_documentation_files(self, repo_dir):
        """
        Processa o repositório para identificar arquivos de documentação.
        
        Args:
            repo_dir (str): Caminho para o repositório clonado.
        
        Returns:
            list: Lista de arquivos de documentação encontrados.
        """
        def is_doc_file(filename):
            """Verifica se um arquivo é um arquivo de documentação baseado na extensão."""
            doc_extensions = [
                '.md', '.markdown',  # Markdown
                '.mdx',              # MDX (Markdown com JSX)
                '.rst',              # reStructuredText
                '.txt',              # Texto simples
                '.adoc', '.asciidoc', # AsciiDoc
                '.html', '.htm',     # HTML
                '.wiki',             # Wiki
                '.tex',              # LaTeX
                '.xml',              # XML
                '.csv',              # Dados estruturados
                '.json',             # JSON
                '.yaml', '.yml'      # YAML
            ]
            
            return any(filename.lower().endswith(ext) for ext in doc_extensions)
        
        # Abordagem mais dinâmica para encontrar diretórios de documentação
        def is_likely_doc_dir(dir_path, relative_path):
            """Determina se um diretório provavelmente contém documentação."""
            dir_name = os.path.basename(dir_path).lower()
        
        # Diretórios comuns de documentação
            doc_dir_names = [
                'docs', 'documentation', 'doc', 'wiki', 'help',
                'examples', 'tutorials', 'manual', 'guide', 'guides',
                'reference', 'api-reference', 'learn', 'api'
        ]
            
            # Se o nome do diretório corresponde a um nome típico
            if dir_name in doc_dir_names or any(doc_name in dir_name for doc_name in doc_dir_names):
                return True
                
            # Se o caminho relativo indica um diretório de documentação
            if any(doc_name in relative_path.lower() for doc_name in doc_dir_names):
                return True
                
            # Verificar se contém arquivos de documentação
            doc_files_count = 0
            total_files = 0
            
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                if os.path.isfile(item_path):
                    total_files += 1
                    if is_doc_file(item):
                        doc_files_count += 1
            
            # Se tem pelo menos alguns arquivos e uma proporção significativa é doc
            if total_files > 0 and doc_files_count > 0:
                doc_ratio = doc_files_count / total_files
                if doc_ratio > 0.5 or doc_files_count >= 3:  # Mais de 50% ou pelo menos 3 doc files
                    return True
                    
            return False
        
        found_files = []
        found_files_metadata = {}
        
        # Realizar uma busca inteligente em todo o repositório
        if self.logger:
            self.logger.info("Buscando arquivos de documentação no repositório...")
        else:
            console.print("[blue]Buscando arquivos de documentação no repositório...[/blue]")
        
        # 1. Primeiro verificar a raiz (especialmente README.md e outros arquivos comuns)
        for file in os.listdir(repo_dir):
            file_path = os.path.join(repo_dir, file)
            if os.path.isfile(file_path) and is_doc_file(file):
                found_files.append(file_path)
                # Coletar metadados
                self._collect_file_metadata(file_path, repo_dir, found_files_metadata)
        
        # 2. Buscar em todo o repositório usando heurísticas
        for root, dirs, files in os.walk(repo_dir):
            # Ignorar diretórios ocultos (ex: .git, node_modules, etc.)
            if '/.' in root or '\\.' in root or '/node_modules' in root or '\\node_modules' in root:
                continue
                
            # Calcular caminho relativo para o diretório atual
            rel_path = os.path.relpath(root, repo_dir)
            
            # Verificar se o diretório atual provavelmente contém documentação
            if rel_path != "." and not is_likely_doc_dir(root, rel_path):
                continue  # Pular diretórios que não parecem ser de documentação
                
            # Procurar arquivos de documentação neste diretório
                for file in files:
                    if is_doc_file(file):
                        file_path = os.path.join(root, file)
                    if file_path not in found_files:  # Evitar duplicatas
                        found_files.append(file_path)
                        # Coletar metadados
                        self._collect_file_metadata(file_path, repo_dir, found_files_metadata)
        
        # Salvar metadados no contexto
        self.context["documentation_files_metadata"] = found_files_metadata
        
        # Gerar relatório detalhado de arquivos
        self._generate_files_report(found_files, found_files_metadata, repo_dir)
        
        if self.logger:
            self.logger.info(f"Encontrados {len(found_files)} arquivos de documentação")
        else:
            console.print(f"[green]Encontrados {len(found_files)} arquivos de documentação[/green]")
            
        return found_files
    
    def _collect_file_metadata(self, file_path, repo_dir, metadata_dict):
        """
        Coleta metadados de um arquivo.
        
        Args:
            file_path (str): Caminho completo para o arquivo
            repo_dir (str): Diretório raiz do repositório
            metadata_dict (dict): Dicionário para armazenar metadados
        """
        try:
            # Caminho relativo para o arquivo (para manter consistência)
            rel_path = os.path.relpath(file_path, repo_dir)
            
            # Obter tamanho
            file_size = os.path.getsize(file_path)
            
            # Calcular hash para verificação de integridade
            file_hash = generate_content_hash(open(file_path, 'rb').read())
            
            # Obter última modificação
            mtime = os.path.getmtime(file_path)
            last_modified = datetime.fromtimestamp(mtime).isoformat()
            
            # Determinar tipo de arquivo baseado na extensão
            _, ext = os.path.splitext(file_path)
            file_type = ext.lower().strip('.')
            if not file_type:
                file_type = "unknown"
                
            # Verificar se é potencialmente perigoso
            is_dangerous = is_dangerous_file(os.path.basename(file_path))
            
            # Armazenar metadados
            metadata_dict[rel_path] = {
                "size": file_size,
                "size_formatted": self._format_file_size(file_size),
                "hash": file_hash,
                "last_modified": last_modified,
                "type": file_type,
                "is_dangerous": is_dangerous,
                "absolute_path": file_path
            }
            
            # Log de arquivo processado se tivermos logger
            if self.logger:
                self.logger.log_file_processing(
                    file_path=file_path,
                    file_size=file_size,
                    file_type=file_type,
                    file_hash=file_hash,
                    metadata={
                        "última_modificação": last_modified,
                        "potencialmente_perigoso": is_dangerous
                    }
                )
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erro ao coletar metadados do arquivo {file_path}: {str(e)}")
            else:
                console.print(f"[red]Erro ao coletar metadados do arquivo {file_path}: {str(e)}[/red]")
    
    def _format_file_size(self, size_in_bytes):
        """
        Formata o tamanho do arquivo para exibição.
        
        Args:
            size_in_bytes (int): Tamanho em bytes
            
        Returns:
            str: Tamanho formatado
        """
        if size_in_bytes < 1024:
            return f"{size_in_bytes} bytes"
        elif size_in_bytes < 1024 * 1024:
            return f"{size_in_bytes / 1024:.2f} KB"
        else:
            return f"{size_in_bytes / (1024 * 1024):.2f} MB"
    
    def _generate_files_report(self, files, metadata, repo_dir):
        """
        Gera um relatório detalhado dos arquivos encontrados.
        
        Args:
            files (list): Lista de arquivos
            metadata (dict): Metadados dos arquivos
            repo_dir (str): Diretório raiz do repositório
        """
        # Calcular estatísticas gerais
        total_size = sum(metadata[os.path.relpath(f, repo_dir)]["size"] for f in files)
        file_types = {}
        
        for file_path in files:
            rel_path = os.path.relpath(file_path, repo_dir)
            file_type = metadata[rel_path]["type"]
            
            if file_type not in file_types:
                file_types[file_type] = 0
            file_types[file_type] += 1
        
        # Gerar relatório
        report_path = os.path.join(self.context["directories"]["processed"], "files_report.md")
        
        report = f"""# Relatório de Arquivos - DocumentationLLM

## Informações Gerais

- **ID de Execução:** {self.context["execution_id"]}
- **Repositório:** {self.context["repo_url"]}
- **Total de Arquivos:** {len(files)}
- **Tamanho Total:** {self._format_file_size(total_size)}
- **Data de Processamento:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Distribuição por Tipo

| Tipo de Arquivo | Quantidade |
|----------------|------------|
"""
        
        for file_type, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
            report += f"| {file_type} | {count} |\n"
        
        report += """
## Detalhes dos Arquivos

| Arquivo | Tipo | Tamanho | Última Modificação |
|---------|------|---------|-------------------|
"""
        
        for file_path in sorted(files):
            rel_path = os.path.relpath(file_path, repo_dir)
            file_data = metadata[rel_path]
            
            report += f"| {rel_path} | {file_data['type']} | {file_data['size_formatted']} | {datetime.fromisoformat(file_data['last_modified']).strftime('%Y-%m-%d %H:%M:%S')} |\n"
        
        # Salvar relatório com encoding UTF-8 com BOM
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w", encoding="utf-8-sig") as f:
            f.write(report)
            
        # Salvar também metadados em formato JSON
        json_report_path = os.path.join(self.context["directories"]["processed"], "files_metadata.json")
        with open(json_report_path, "w", encoding="utf-8-sig") as f:
            json.dump({
                "execution_id": self.context["execution_id"],
                "repository": self.context["repo_url"],
                "total_files": len(files),
                "total_size": total_size,
                "total_size_formatted": self._format_file_size(total_size),
                "file_types": file_types,
                "files": metadata
            }, f, ensure_ascii=False, indent=2)
        
        if self.logger:
            self.logger.info(f"Relatório de arquivos gerado em: {report_path}")
            self.logger.info(f"Metadados JSON salvos em: {json_report_path}")
        else:
            console.print(f"[green]Relatório de arquivos gerado em: {report_path}[/green]")
            console.print(f"[green]Metadados JSON salvos em: {json_report_path}[/green]")
    
    def run(self):
        """
        Método principal do agente.
        
        Returns:
            dict: Contexto atualizado com informações do download.
        """
        try:
            if self.logger:
                self.logger.info(f"Iniciando download do repositório: {self.repo_url}")
            else:
                console.print(f"[bold blue]Iniciando download do repositório: {self.repo_url}[/bold blue]")
            
            # Validar URL e extrair informações
            repo_info = self._validate_url()
            
            if self.logger:
                self.logger.info(f"Repositório identificado: {repo_info['type']} - {repo_info['owner']}/{repo_info['name']}")
            else:
                console.print(f"Repositório identificado: [cyan]{repo_info['type']}[/cyan] - [cyan]{repo_info['owner']}/{repo_info['name']}[/cyan]")
            
            # Clonar repositório
            repo_dir = self._clone_repository(repo_info)
            
            # Processar arquivos de documentação
            doc_files = self._process_documentation_files(repo_dir)
            
            # Verificar se encontramos arquivos
            if not doc_files:
                if self.logger:
                    self.logger.warning("Nenhum arquivo de documentação encontrado!")
                else:
                    console.print("[yellow]Nenhum arquivo de documentação encontrado![/yellow]")
            
            # Atualizar contexto
            self.context["repo_info"] = repo_info
            self.context["documentation_files"] = [os.path.relpath(f, repo_dir) for f in doc_files]
            self.context["repository_directory"] = repo_dir
            self.context["originals_directory"] = os.path.dirname(repo_dir)
            self.context["temp_directory"] = repo_dir
            
            # Registro de hora de início/fim para cronometragem
            self.context["download_stats"] = {
                "start_time": self.context["stats"]["start_time"].isoformat(),
                "end_time": datetime.now().isoformat(),
                "files_count": len(doc_files)
            }
            
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

            # Marcar download como concluído
            self.context["download_completed"] = True

            return self.context
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erro no DownloadAgent: {str(e)}")
            
            # Adicionar à lista de etapas que falharam
            if "stats" in self.context and "steps_failed" in self.context["stats"]:
                self.context["stats"]["steps_failed"].append("download")
                
            # Re-lançar exceção para ser tratada no nível superior
            raise
    
    def cleanup(self):
        """
        Limpa os arquivos temporários após o processamento.
        """
        if os.path.exists(self.temp_dir):
            try:
                if self.logger:
                    self.logger.info(f"Limpando diretório temporário: {self.temp_dir}")
                else:
                    console.print(f"[blue]Limpando diretório temporário: {self.temp_dir}[/blue]")
                
                shutil.rmtree(self.temp_dir)
                return True
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Não foi possível limpar o diretório temporário: {str(e)}")
                else:
                    console.print(f"[yellow]Não foi possível limpar o diretório temporário: {str(e)}[/yellow]")
                return False
        return True
