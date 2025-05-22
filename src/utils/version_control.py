#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de controle de versão para o DocumentationLLM.

Este módulo fornece funcionalidades para:
- Criar snapshots do código atual
- Restaurar versões anteriores (rollback)
- Comparar versões do código
"""

import os
import json
import shutil
import datetime
import hashlib
from pathlib import Path
import glob
import difflib
from rich.console import Console

console = Console()

class VersionControl:
    """
    Gerenciador de versões para código-fonte do DocumentationLLM.
    Permite criar backups e realizar rollback quando necessário.
    """
    
    def __init__(self, base_dir=".version_control", max_versions=10):
        """
        Inicializa o sistema de controle de versão.
        
        Args:
            base_dir (str): Diretório para armazenar versões.
            max_versions (int): Número máximo de versões a manter.
        """
        self.base_dir = base_dir
        self.max_versions = max_versions
        self.versions_file = os.path.join(base_dir, "versions.json")
        
        # Garantir que o diretório existe
        os.makedirs(base_dir, exist_ok=True)
        
        # Carregar histórico de versões ou criar novo
        if os.path.exists(self.versions_file):
            with open(self.versions_file, "r", encoding="utf-8") as f:
                self.versions = json.load(f)
        else:
            self.versions = {
                "current_version": None,
                "snapshots": []
            }
            self._save_versions()
    
    def create_snapshot(self, description, source_dirs=None, include_patterns=None, exclude_patterns=None):
        """
        Cria um snapshot do código atual.
        
        Args:
            description (str): Descrição da versão.
            source_dirs (list): Lista de diretórios a incluir.
            include_patterns (list): Padrões de arquivos a incluir (ex: ["*.py", "*.md"]).
            exclude_patterns (list): Padrões de arquivos a excluir.
        
        Returns:
            str: ID da versão criada.
        """
        # Definir valores padrão
        if source_dirs is None:
            source_dirs = ["src", "tests"]
            
        if include_patterns is None:
            include_patterns = ["*.py", "*.md", "*.yaml", "*.yml", "*.json"]
            
        if exclude_patterns is None:
            exclude_patterns = ["__pycache__/*", "*.pyc", "*.pyo", "*.pyd"]
        
        # Criar ID único para esta versão
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        version_id = f"v_{timestamp}"
        
        # Diretório para esta versão
        version_dir = os.path.join(self.base_dir, version_id)
        os.makedirs(version_dir, exist_ok=True)
        
        # Coletar arquivos para backup
        files_to_backup = []
        for source_dir in source_dirs:
            if not os.path.exists(source_dir):
                console.print(f"[yellow]Aviso: Diretório {source_dir} não existe e será ignorado.[/yellow]")
                continue
                
            for include_pattern in include_patterns:
                pattern = os.path.join(source_dir, "**", include_pattern)
                files = glob.glob(pattern, recursive=True)
                
                # Filtrar arquivos excluídos
                for file_path in files:
                    if not any(file_path.endswith(exclude) for exclude in exclude_patterns):
                        files_to_backup.append(file_path)
        
        # Criar metadados do arquivo
        file_metadata = []
        
        # Copiar arquivos para o diretório de versão
        for file_path in files_to_backup:
            # Manter a mesma estrutura de diretórios
            rel_path = os.path.relpath(file_path)
            backup_path = os.path.join(version_dir, rel_path)
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # Copiar arquivo
            shutil.copy2(file_path, backup_path)
            
            # Calcular hash para comparação futura
            file_hash = self._calculate_file_hash(file_path)
            
            # Registrar metadados
            file_metadata.append({
                "path": rel_path,
                "hash": file_hash,
                "size": os.path.getsize(file_path),
                "modified": datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            })
        
        # Registrar nova versão
        snapshot = {
            "id": version_id,
            "timestamp": timestamp,
            "description": description,
            "files_count": len(files_to_backup),
            "files": file_metadata
        }
        
        self.versions["snapshots"].append(snapshot)
        self.versions["current_version"] = version_id
        
        # Limitar o número de versões
        if len(self.versions["snapshots"]) > self.max_versions:
            # Remover versão mais antiga
            oldest = self.versions["snapshots"].pop(0)
            oldest_dir = os.path.join(self.base_dir, oldest["id"])
            if os.path.exists(oldest_dir):
                shutil.rmtree(oldest_dir)
        
        # Salvar histórico atualizado
        self._save_versions()
        
        console.print(f"[green]Snapshot criado: [bold]{version_id}[/bold] - {description}[/green]")
        console.print(f"[green]Backup de {len(files_to_backup)} arquivos em {len(source_dirs)} diretórios.[/green]")
        
        return version_id
    
    def rollback(self, version_id=None, dry_run=False):
        """
        Restaura o código para uma versão específica.
        
        Args:
            version_id (str, optional): ID da versão para restaurar. Se None, usa a anterior.
            dry_run (bool): Se True, apenas simula o rollback sem fazer alterações.
        
        Returns:
            dict: Relatório da operação de rollback.
        """
        # Encontrar versão para restaurar
        if version_id is None:
            # Se não especificado, restaurar para a versão anterior
            if len(self.versions["snapshots"]) < 2:
                return {"success": False, "message": "Não há versão anterior para restaurar."}
                
            current_index = next((i for i, s in enumerate(self.versions["snapshots"]) 
                                if s["id"] == self.versions["current_version"]), -1)
            
            if current_index <= 0:
                return {"success": False, "message": "Não foi possível identificar a versão anterior."}
                
            version_to_restore = self.versions["snapshots"][current_index - 1]
            version_id = version_to_restore["id"]
        else:
            # Encontrar versão específica
            version_to_restore = next((s for s in self.versions["snapshots"] if s["id"] == version_id), None)
            
            if not version_to_restore:
                return {"success": False, "message": f"Versão {version_id} não encontrada."}
        
        # Diretório da versão a restaurar
        restore_dir = os.path.join(self.base_dir, version_id)
        if not os.path.exists(restore_dir):
            return {"success": False, "message": f"Diretório da versão {version_id} não encontrado."}
        
        console.print(f"[bold blue]Restaurando versão: {version_id} - {version_to_restore['description']}[/bold blue]")
        
        # Preparar relatório
        report = {
            "version": version_id,
            "description": version_to_restore["description"],
            "files_restored": [],
            "files_not_found": [],
            "success": True
        }
        
        # Restaurar cada arquivo
        for file_info in version_to_restore["files"]:
            source_path = os.path.join(restore_dir, file_info["path"])
            target_path = file_info["path"]
            
            # Verificar se o arquivo de backup existe
            if not os.path.exists(source_path):
                report["files_not_found"].append(file_info["path"])
                console.print(f"[yellow]Aviso: Arquivo de backup não encontrado: {source_path}[/yellow]")
                continue
            
            # Em modo dry_run, apenas registrar o que seria feito
            if dry_run:
                report["files_restored"].append({
                    "path": file_info["path"],
                    "status": "would_restore"
                })
                continue
            
            # Garantir que o diretório de destino existe
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            # Restaurar o arquivo
            try:
                shutil.copy2(source_path, target_path)
                report["files_restored"].append({
                    "path": file_info["path"],
                    "status": "restored"
                })
            except Exception as e:
                report["files_restored"].append({
                    "path": file_info["path"],
                    "status": "error",
                    "error": str(e)
                })
                console.print(f"[red]Erro ao restaurar {target_path}: {str(e)}[/red]")
        
        if not dry_run:
            # Atualizar versão atual
            self.versions["current_version"] = version_id
            self._save_versions()
            
            console.print(f"[green]Rollback concluído. {len(report['files_restored'])} arquivos restaurados.[/green]")
        else:
            console.print(f"[blue]Simulação de rollback concluída. {len(report['files_restored'])} arquivos seriam restaurados.[/blue]")
        
        return report
    
    def list_versions(self):
        """
        Lista todas as versões disponíveis.
        
        Returns:
            list: Lista de versões disponíveis.
        """
        return self.versions["snapshots"]
    
    def get_current_version(self):
        """
        Retorna a versão atual.
        
        Returns:
            dict: Informações sobre a versão atual.
        """
        if not self.versions["current_version"]:
            return None
            
        return next((v for v in self.versions["snapshots"] if v["id"] == self.versions["current_version"]), None)
    
    def compare_versions(self, version_id1, version_id2=None):
        """
        Compara duas versões do código.
        
        Args:
            version_id1 (str): ID da primeira versão.
            version_id2 (str, optional): ID da segunda versão. Se None, compara com a versão atual no sistema.
        
        Returns:
            dict: Relatório de diferenças.
        """
        # Encontrar primeira versão
        version1 = next((s for s in self.versions["snapshots"] if s["id"] == version_id1), None)
        if not version1:
            return {"success": False, "message": f"Versão {version_id1} não encontrada."}
        
        # Diretório da primeira versão
        dir1 = os.path.join(self.base_dir, version_id1)
        
        # Comparar com versão no sistema ou outra versão arquivada
        if version_id2 is None:
            # Comparar com arquivos atuais no sistema
            files_to_compare = [f["path"] for f in version1["files"]]
            
            diffs = []
            for file_path in files_to_compare:
                backup_path = os.path.join(dir1, file_path)
                
                # Verificar se os arquivos existem
                if not os.path.exists(backup_path):
                    diffs.append({
                        "file": file_path,
                        "status": "backup_missing"
                    })
                    continue
                    
                if not os.path.exists(file_path):
                    diffs.append({
                        "file": file_path,
                        "status": "current_missing"
                    })
                    continue
                
                # Comparar conteúdo
                try:
                    with open(backup_path, 'r', encoding='utf-8') as f1, open(file_path, 'r', encoding='utf-8') as f2:
                        diff = list(difflib.unified_diff(
                            f1.readlines(), 
                            f2.readlines(),
                            fromfile=f"v{version_id1}/{file_path}",
                            tofile=f"current/{file_path}"
                        ))
                        
                        if diff:
                            diffs.append({
                                "file": file_path,
                                "status": "modified",
                                "diff": "".join(diff)
                            })
                        else:
                            diffs.append({
                                "file": file_path,
                                "status": "identical"
                            })
                except Exception as e:
                    diffs.append({
                        "file": file_path,
                        "status": "error",
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "version1": version_id1,
                "version2": "current",
                "diffs": diffs
            }
        else:
            # Comparar com outra versão
            version2 = next((s for s in self.versions["snapshots"] if s["id"] == version_id2), None)
            if not version2:
                return {"success": False, "message": f"Versão {version_id2} não encontrada."}
                
            dir2 = os.path.join(self.base_dir, version_id2)
            
            # Encontrar todos os arquivos em ambas as versões
            files1 = {f["path"] for f in version1["files"]}
            files2 = {f["path"] for f in version2["files"]}
            all_files = files1.union(files2)
            
            diffs = []
            for file_path in all_files:
                path1 = os.path.join(dir1, file_path)
                path2 = os.path.join(dir2, file_path)
                
                # Verificar existência
                if not os.path.exists(path1):
                    diffs.append({
                        "file": file_path,
                        "status": "only_in_version2"
                    })
                    continue
                
                if not os.path.exists(path2):
                    diffs.append({
                        "file": file_path,
                        "status": "only_in_version1"
                    })
                    continue
                
                # Comparar conteúdo
                try:
                    with open(path1, 'r', encoding='utf-8') as f1, open(path2, 'r', encoding='utf-8') as f2:
                        diff = list(difflib.unified_diff(
                            f1.readlines(), 
                            f2.readlines(),
                            fromfile=f"v{version_id1}/{file_path}",
                            tofile=f"v{version_id2}/{file_path}"
                        ))
                        
                        if diff:
                            diffs.append({
                                "file": file_path,
                                "status": "modified",
                                "diff": "".join(diff)
                            })
                        else:
                            diffs.append({
                                "file": file_path,
                                "status": "identical"
                            })
                except Exception as e:
                    diffs.append({
                        "file": file_path,
                        "status": "error",
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "version1": version_id1,
                "version2": version_id2,
                "diffs": diffs
            }
    
    def _calculate_file_hash(self, file_path):
        """
        Calcula o hash MD5 de um arquivo.
        
        Args:
            file_path (str): Caminho do arquivo.
            
        Returns:
            str: Hash MD5 em formato hexadecimal.
        """
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            buf = f.read(65536)  # Ler em blocos de 64k
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()
    
    def _save_versions(self):
        """
        Salva o histórico de versões no arquivo.
        """
        with open(self.versions_file, "w", encoding="utf-8") as f:
            json.dump(self.versions, f, indent=2, ensure_ascii=False) 