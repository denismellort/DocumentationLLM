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
from datetime import datetime
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.syntax import Syntax

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
    
    def __init__(self, 
                 log_level="info", 
                 enable_file_logging=False, 
                 log_dir="logs", 
                 execution_id=None,
                 enable_console=True,
                 enable_api_logging=False):
        """
        Inicializa o logger.
        
        Args:
            log_level (str): Nível de log (debug, info, warning, error, critical).
            enable_file_logging (bool): Se True, habilita logs em arquivo.
            log_dir (str): Diretório para armazenar logs.
            execution_id (str): ID da execução atual.
            enable_console (bool): Se True, habilita logs no console.
            enable_api_logging (bool): Se True, habilita logs detalhados de APIs.
        """
        self.log_level = self.LEVELS.get(log_level.lower(), logging.INFO)
        self.enable_file_logging = enable_file_logging
        self.log_dir = log_dir
        self.execution_id = execution_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.enable_console = enable_console
        self.enable_api_logging = enable_api_logging
        
        # Criar logger
        self.logger = logging.getLogger("DocumentationLLM")
        self.logger.setLevel(self.log_level)
        self.logger.handlers = []  # Limpar handlers para evitar duplicação
        
        # Configurar formatação
        log_format = "%(asctime)s [%(levelname)s] %(message)s"
        
        # Handler para console usando Rich
        if enable_console:
            console_handler = RichHandler(
                rich_tracebacks=True,
                markup=True,
                show_path=False,
                omit_repeated_times=False,
            )
            console_handler.setLevel(self.log_level)
            self.logger.addHandler(console_handler)
        
        # Handler para arquivo
        if enable_file_logging:
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"{self.execution_id}.log")
            
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(self.log_level)
            file_formatter = logging.Formatter(log_format)
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
            
            # Criar arquivo separado para logs de API se habilitado
            if enable_api_logging:
                api_log_file = os.path.join(log_dir, f"{self.execution_id}_api.log")
                self.api_log_file = api_log_file
                
                # Garantir que o arquivo existe
                with open(api_log_file, "w", encoding="utf-8") as f:
                    f.write(f"# API Logs - DocumentationLLM\n")
                    f.write(f"# Execution ID: {self.execution_id}\n")
                    f.write(f"# Start Time: {datetime.now().isoformat()}\n\n")
                    
            # Registrar problemas conhecidos
            known_issues_file = os.path.join(log_dir, "known_issues.log")
            if not os.path.exists(known_issues_file):
                with open(known_issues_file, "w", encoding="utf-8") as f:
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
    
    def log_api_call(self, api_name, endpoint, request_data, response_data=None, error=None):
        """
        Registra detalhes de uma chamada de API.
        
        Args:
            api_name (str): Nome da API (ex: "OpenAI", "GitHub").
            endpoint (str): Endpoint específico chamado.
            request_data (dict): Dados da requisição.
            response_data (dict, optional): Dados da resposta, se disponível.
            error (Exception, optional): Erro, se ocorreu.
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
        
        # Log no console, se habilitado e em nível debug
        if self.enable_console and self.log_level <= logging.DEBUG:
            if error:
                console.print(f"[bold red]API Error: {api_name} - {endpoint}[/bold red]")
                console.print(f"[red]{error}[/red]")
            else:
                console.print(f"[bold blue]API Call: {api_name} - {endpoint}[/bold blue]")
        
        # Log em arquivo separado para APIs
        if self.enable_file_logging and self.api_log_file:
            with open(self.api_log_file, "a", encoding="utf-8") as f:
                f.write(f"## {timestamp} - {api_name} - {endpoint}\n\n")
                f.write(f"### Request\n```json\n{json.dumps(request_data, indent=2, ensure_ascii=False)}\n```\n\n")
                
                if response_data:
                    f.write(f"### Response\n```json\n{json.dumps(response_data, indent=2, ensure_ascii=False)}\n```\n\n")
                
                if error:
                    f.write(f"### Error\n```\n{error}\n```\n\n")
                
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
        
    @staticmethod
    def get_known_issues():
        """
        Retorna a lista de problemas conhecidos.
        
        Returns:
            list: Lista de problemas conhecidos.
        """
        return KNOWN_ISSUES 