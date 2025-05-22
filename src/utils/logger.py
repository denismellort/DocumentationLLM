#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de logging para o DocumentationLLM.

Este módulo fornece funcionalidades de logging avançadas, incluindo:
- Logs em console com cores
- Logs em arquivo com rotação
- Níveis diferentes de logging
- Suporte a debug de comunicação com APIs
"""

import os
import json
import logging
import hashlib
from datetime import datetime
from logging.handlers import RotatingFileHandler
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

# Configuração global
console = Console()

# Registro de problemas internos conhecidos
KNOWN_ISSUES = [
    {
        "issue_id": "TOKEN_ANALYST_001",
        "severity": "medium",
        "component": "TokenAnalystAgent",
        "description": "O agente de análise de tokens não está registrando corretamente o uso de tokens da API OpenAI.",
        "cause": "Etapas intermediárias do pipeline (parsing, semantic_linking, etc.) estão comentadas no código.",
        "impact": "Relatórios de uso de tokens mostram valores incorretos (geralmente zero).",
        "workaround": "Implementar chamadas de logging de tokens explícitas em cada etapa que usa a API OpenAI.",
        "status": "pending",
        "created_at": "2025-05-22"
    }
]

class DocumentationLogger:
    """
    Classe para gerenciar logs da aplicação com suporte a console e arquivo.
    """
    
    # Níveis de log
    LEVELS = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }
    
    # Tamanho máximo dos arquivos de log (10MB)
    MAX_LOG_SIZE = 10 * 1024 * 1024
    
    # Número máximo de backups de logs
    MAX_LOG_BACKUPS = 5
    
    def __init__(self, 
                 log_level="info", 
                 enable_file_logging=False, 
                 log_dir="logs", 
                 execution_id=None,
                 enable_console=True,
                 enable_api_logging=False,
                 log_rotation=True,
                 verbose_exceptions=True):
        """
        Inicializa o logger.
        
        Args:
            log_level (str): Nível de log (debug, info, warning, error, critical).
            enable_file_logging (bool): Se True, habilita logs em arquivo.
            log_dir (str): Diretório para armazenar logs.
            execution_id (str): ID da execução atual.
            enable_console (bool): Se True, habilita logs no console.
            enable_api_logging (bool): Se True, habilita logs detalhados de APIs.
            log_rotation (bool): Se True, habilita rotação de arquivos de log.
            verbose_exceptions (bool): Se True, exibe detalhes completos de exceções.
        """
        self.log_level = self.LEVELS.get(log_level.lower(), logging.INFO)
        self.enable_file_logging = enable_file_logging
        self.log_dir = log_dir
        self.execution_id = execution_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.enable_console = enable_console
        self.enable_api_logging = enable_api_logging
        self.log_rotation = log_rotation
        self.verbose_exceptions = verbose_exceptions
        
        # Criar logger
        self.logger = logging.getLogger("DocumentationLLM")
        self.logger.setLevel(self.log_level)
        self.logger.handlers = []  # Limpar handlers para evitar duplicação
        
        # Configurar formatação
        log_format = "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
        
        # Handler para console usando Rich
        if enable_console:
            console_handler = RichHandler(
                rich_tracebacks=True,
                markup=True,
                show_path=False,
                omit_repeated_times=False,
                tracebacks_show_locals=verbose_exceptions,
            )
            console_handler.setLevel(self.log_level)
            self.logger.addHandler(console_handler)
        
        # Handler para arquivo
        if enable_file_logging:
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"{self.execution_id}.log")
            
            if log_rotation:
                file_handler = RotatingFileHandler(
                    log_file, 
                    maxBytes=self.MAX_LOG_SIZE, 
                    backupCount=self.MAX_LOG_BACKUPS,
                    encoding="utf-8-sig"
                )
            else:
                file_handler = logging.FileHandler(log_file, encoding="utf-8-sig")
                
            file_handler.setLevel(self.log_level)
            file_formatter = logging.Formatter(log_format)
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
            
            # Criar arquivo separado para logs de API se habilitado
            if enable_api_logging:
                api_log_file = os.path.join(log_dir, f"{self.execution_id}_api.log")
                self.api_log_file = api_log_file
                
                # Criar handler com rotação para API logs
                if log_rotation:
                    self.api_file_handler = RotatingFileHandler(
                        api_log_file, 
                        maxBytes=self.MAX_LOG_SIZE, 
                        backupCount=self.MAX_LOG_BACKUPS,
                        encoding="utf-8-sig"
                    )
                    # Não adicionar ao logger principal, será usado separadamente
                else:
                    # Garantir que o arquivo existe
                    with open(api_log_file, "w", encoding="utf-8-sig") as f:
                        f.write(f"# API Logs - DocumentationLLM\n")
                        f.write(f"# Execution ID: {self.execution_id}\n")
                        f.write(f"# Start Time: {datetime.now().isoformat()}\n\n")
                    
            # Registrar problemas conhecidos
            known_issues_file = os.path.join(log_dir, "known_issues.log")
            if not os.path.exists(known_issues_file):
                with open(known_issues_file, "w", encoding="utf-8-sig") as f:
                    f.write("# Problemas Conhecidos - DocumentationLLM\n\n")
                    for issue in KNOWN_ISSUES:
                        f.write(f"## {issue['issue_id']}: {issue['component']}\n")
                        f.write(f"- **Severidade**: {issue['severity']}\n")
                        f.write(f"- **Descrição**: {issue['description']}\n")
                        f.write(f"- **Causa**: {issue['cause']}\n")
                        f.write(f"- **Impacto**: {issue['impact']}\n")
                        f.write(f"- **Solução Temporária**: {issue['workaround']}\n")
                        f.write(f"- **Status**: {issue['status']}\n")
                        f.write(f"- **Criado em**: {issue['created_at']}\n\n")
        else:
            self.api_log_file = None
            
        # Criar logger de depuração para chamadas de API
        if enable_api_logging:
            self.api_logger = logging.getLogger("DocumentationLLM.api")
            self.api_logger.setLevel(logging.DEBUG)  # Sempre debug para APIs
            self.api_logger.propagate = False  # Não propagar para o logger pai
            
            # Adicionar handler de arquivo se habilitado
            if enable_file_logging and hasattr(self, 'api_file_handler'):
                api_formatter = logging.Formatter("%(asctime)s [API] %(message)s")
                self.api_file_handler.setFormatter(api_formatter)
                self.api_logger.addHandler(self.api_file_handler)
            
            # Adicionar console handler se habilitado e em modo debug
            if enable_console and self.log_level <= logging.DEBUG:
                api_console_handler = RichHandler(
                    rich_tracebacks=True,
                    markup=True,
                    show_path=False,
                    omit_repeated_times=False,
                )
                api_console_handler.setLevel(logging.DEBUG)
                self.api_logger.addHandler(api_console_handler)
    
    def get_child_logger(self, name):
        """
        Obtém um logger filho com um nome específico.
        
        Args:
            name (str): Nome do logger filho.
            
        Returns:
            logging.Logger: Logger filho.
        """
        return logging.getLogger(f"DocumentationLLM.{name}")
    
    def debug(self, message, *args, **kwargs):
        """Log debug message."""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message, *args, **kwargs):
        """Log info message."""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message, *args, **kwargs):
        """Log warning message."""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message, *args, **kwargs):
        """Log error message."""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message, *args, **kwargs):
        """Log critical message."""
        self.logger.critical(message, *args, **kwargs)
    
    def log_rich(self, panel_content, title=None, style="green"):
        """
        Exibe um painel formatado usando Rich no console.
        
        Args:
            panel_content (str): Conteúdo do painel.
            title (str, optional): Título do painel.
            style (str, optional): Estilo do painel.
        """
        if self.enable_console:
            console.print(Panel(panel_content, title=title, style=style))
        
        # Também registrar no log de arquivo, se habilitado
        if self.enable_file_logging:
            if title:
                self.logger.info(f"--- {title} ---")
            self.logger.info(panel_content)
    
    def log_code(self, code, language="python", title=None):
        """
        Exibe código formatado e com syntax highlighting usando Rich.
        
        Args:
            code (str): Código a ser exibido.
            language (str, optional): Linguagem do código.
            title (str, optional): Título para o bloco de código.
        """
        if self.enable_console:
            syntax = Syntax(code, language, theme="monokai", line_numbers=True)
            if title:
                console.print(f"[bold]{title}[/bold]")
            console.print(syntax)
        
        # Também registrar no log de arquivo, se habilitado
        if self.enable_file_logging:
            if title:
                self.logger.info(f"--- {title} ---")
            self.logger.info(f"```{language}\n{code}\n```")
    
    def log_api_call(self, api_name, endpoint, request_data, response_data=None, error=None, token_count=None):
        """
        Registra detalhes de uma chamada de API.
        
        Args:
            api_name (str): Nome da API (ex: "OpenAI", "GitHub").
            endpoint (str): Endpoint específico chamado.
            request_data (dict): Dados da requisição.
            response_data (dict, optional): Dados da resposta, se disponível.
            error (Exception, optional): Erro, se ocorreu.
            token_count (dict, optional): Contagem de tokens (input, output, total).
        """
        if not self.enable_api_logging:
            return
        
        timestamp = datetime.now().isoformat()
        
        # Conteúdo do log
        log_entry = {
            "timestamp": timestamp,
            "api": api_name,
            "endpoint": endpoint,
            "request": request_data
        }
        
        if response_data:
            log_entry["response"] = response_data
        
        if error:
            log_entry["error"] = str(error)
            
        if token_count:
            log_entry["tokens"] = token_count
        
        # Log usando o logger específico de API
        if hasattr(self, 'api_logger'):
            message = f"{api_name} - {endpoint}"
            if error:
                self.api_logger.error(f"API ERROR: {message} - {str(error)}")
            else:
                self.api_logger.debug(f"API CALL: {message}")
                if token_count:
                    self.api_logger.info(
                        f"API TOKENS: {message} - " +
                        f"Input: {token_count.get('input_tokens', 0)}, " +
                        f"Output: {token_count.get('output_tokens', 0)}, " +
                        f"Total: {token_count.get('total_tokens', 0)}"
                    )
        
        # Log em arquivo separado para APIs (método antigo, para compatibilidade)
        if self.enable_file_logging and self.api_log_file and not hasattr(self, 'api_file_handler'):
            with open(self.api_log_file, "a", encoding="utf-8-sig") as f:
                f.write(f"## {timestamp} - {api_name} - {endpoint}\n\n")
                f.write(f"### Request\n```json\n{json.dumps(request_data, indent=2, ensure_ascii=False)}\n```\n\n")
                
                if response_data:
                    f.write(f"### Response\n```json\n{json.dumps(response_data, indent=2, ensure_ascii=False)}\n```\n\n")
                
                if error:
                    f.write(f"### Error\n```\n{error}\n```\n\n")
                    
                if token_count:
                    f.write(f"### Token Usage\n")
                    f.write(f"- Input Tokens: {token_count.get('input_tokens', 0)}\n")
                    f.write(f"- Output Tokens: {token_count.get('output_tokens', 0)}\n")
                    f.write(f"- Total Tokens: {token_count.get('total_tokens', 0)}\n")
                    if 'cost' in token_count:
                        f.write(f"- Estimated Cost: ${token_count.get('cost', 0):.6f}\n")
                
                f.write("---\n\n")
        
        # Log básico também no log principal
        if error:
            self.error(f"API Error: {api_name} - {endpoint} - {str(error)}")
        else:
            self.debug(f"API Call: {api_name} - {endpoint}")
    
    def log_step_start(self, step_name):
        """
        Registra o início de uma etapa do pipeline.
        
        Args:
            step_name (str): Nome da etapa.
        """
        self.log_rich(f"Iniciando etapa: {step_name}", title="Início de Etapa", style="blue")
    
    def log_step_end(self, step_name, status="sucesso", details=None):
        """
        Registra o fim de uma etapa do pipeline.
        
        Args:
            step_name (str): Nome da etapa.
            status (str): Status da conclusão (sucesso/falha).
            details (str, opcional): Detalhes adicionais.
        """
        style = "green" if status == "sucesso" else "red"
        content = f"Etapa {step_name} concluída com {status}"
        
        if details:
            content += f"\n\n{details}"
            
        self.log_rich(content, title="Fim de Etapa", style=style)
        
    def log_file_processing(self, file_path, file_size, file_type, file_hash=None, metadata=None):
        """
        Registra informações detalhadas sobre um arquivo processado.
        
        Args:
            file_path (str): Caminho do arquivo
            file_size (int): Tamanho do arquivo em bytes
            file_type (str): Tipo do arquivo (ex: "markdown", "python")
            file_hash (str, optional): Hash do arquivo para verificação
            metadata (dict, optional): Metadados adicionais sobre o arquivo
        """
        # Calcular hash MD5 se não fornecido
        if not file_hash and os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
            except Exception as e:
                file_hash = f"Erro ao calcular hash: {str(e)}"
                
        # Formatar tamanho
        if file_size < 1024:
            size_formatted = f"{file_size} bytes"
        elif file_size < 1024 * 1024:
            size_formatted = f"{file_size / 1024:.2f} KB"
        else:
            size_formatted = f"{file_size / (1024 * 1024):.2f} MB"
            
        # Obter última modificação
        last_modified = ""
        if os.path.exists(file_path):
            try:
                mtime = os.path.getmtime(file_path)
                last_modified = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            except:
                last_modified = "Desconhecido"
        
        # Log básico
        self.info(f"Arquivo processado: {os.path.basename(file_path)} ({size_formatted})")
        
        # Log detalhado em nível debug
        details = [
            f"Caminho: {file_path}",
            f"Tamanho: {size_formatted}",
            f"Tipo: {file_type}",
            f"Última modificação: {last_modified}",
            f"Hash MD5: {file_hash}"
        ]
        
        if metadata:
            for key, value in metadata.items():
                details.append(f"{key}: {value}")
                
        self.debug("Detalhes do arquivo:\n" + "\n".join(f"- {d}" for d in details))
        
    def create_progress_bar(self, description, total=None):
        """
        Cria uma barra de progresso para operações de longa duração.
        
        Args:
            description (str): Descrição da operação
            total (int, optional): Total de passos (None para progresso indeterminado)
            
        Returns:
            tuple: (Progress object, task_id) para atualização
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        )
        
        task_id = progress.add_task(description, total=total)
        return progress, task_id
        
    @staticmethod
    def get_known_issues():
        """
        Retorna a lista de problemas conhecidos.
        
        Returns:
            list: Lista de problemas conhecidos.
        """
        return KNOWN_ISSUES 