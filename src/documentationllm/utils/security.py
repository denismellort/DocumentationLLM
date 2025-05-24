#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de segurança para o DocumentationLLM.

Este módulo fornece funções para garantir a segurança do projeto, incluindo:
- Validação de URLs
- Sanitização de inputs
- Proteção contra path traversal
- Proteção contra injeção em chamadas de API
"""

import os
import re
import hashlib
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path

# Lista de domínios confiáveis para repositórios
TRUSTED_DOMAINS = [
    "github.com",
    "gitlab.com",
    "bitbucket.org",
    "git.example.com"  # Adicionar domínios internos conforme necessário
]

# Padrões de arquivo potencialmente perigosos
DANGEROUS_FILE_PATTERNS = [
    r"\.exe$",
    r"\.dll$",
    r"\.sh$",
    r"\.bat$",
    r"\.cmd$",
    r"\.ps1$",
    r"\.vbs$",
    r"\.js$"
]

def validate_url(url: str) -> Tuple[bool, str]:
    """
    Valida uma URL ou caminho local.
    
    Args:
        url: URL ou caminho a ser validado
        
    Returns:
        Tuple[bool, str]: (é_válido, mensagem_de_erro)
    """
    # Se for um caminho local
    if os.path.exists(url):
        return True, "Caminho local válido"
    
    # Validar URL
    try:
        result = urlparse(url)
        if all([result.scheme, result.netloc]):
            return True, "URL válida"
        return False, "URL malformada"
    except Exception as e:
        return False, str(e)

def sanitize_path(path: str) -> str:
    """
    Sanitiza um caminho de arquivo/diretório.
    
    Args:
        path: Caminho a ser sanitizado
        
    Returns:
        str: Caminho sanitizado
    """
    # Remover caracteres perigosos
    path = re.sub(r'[<>:"|?*]', '', path)
    
    # Converter para Path e resolver
    return str(Path(path).resolve())

def sanitize_filename(filename: str) -> str:
    """
    Sanitiza um nome de arquivo.
    
    Args:
        filename: Nome do arquivo a ser sanitizado
        
    Returns:
        str: Nome de arquivo sanitizado
    """
    # Remover caracteres perigosos
    filename = re.sub(r'[<>:"|?*]', '', filename)
    
    # Limitar comprimento
    max_length = 255
    if len(filename) > max_length:
        base, ext = os.path.splitext(filename)
        filename = base[:max_length-len(ext)] + ext
    
    return filename

def sanitize_content(content: str) -> str:
    """
    Sanitiza o conteúdo de um arquivo.
    
    Args:
        content: Conteúdo a ser sanitizado
        
    Returns:
        str: Conteúdo sanitizado
    """
    # Remover caracteres de controle, exceto newlines e tabs
    content = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', content)
    
    # Normalizar quebras de linha
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    
    return content

def validate_file_path(file_path: Union[str, Path]) -> bool:
    """
    Valida um caminho de arquivo.
    
    Args:
        file_path: Caminho do arquivo a ser validado
        
    Returns:
        bool: True se o caminho é válido
    """
    try:
        path = Path(file_path).resolve()
        return path.exists() and path.is_file()
    except Exception:
        return False

def is_dangerous_file(filename: str) -> bool:
    """
    Verifica se um arquivo é potencialmente perigoso.
    
    Args:
        filename: Nome do arquivo a verificar
        
    Returns:
        bool: True se o arquivo é potencialmente perigoso
    """
    dangerous_extensions = {
        '.exe', '.dll', '.so', '.dylib',  # Executáveis
        '.bat', '.cmd', '.sh',            # Scripts
        '.jar', '.war',                   # Java
        '.php', '.asp', '.aspx',          # Web
        '.cgi', '.pl',                    # Perl
        '.py', '.pyc',                    # Python
        '.rb',                            # Ruby
        '.js',                            # JavaScript
    }
    
    return Path(filename).suffix.lower() in dangerous_extensions

def generate_content_hash(content: Union[str, bytes]) -> str:
    """
    Gera um hash SHA-256 do conteúdo.
    
    Args:
        content: Conteúdo para gerar hash
        
    Returns:
        str: Hash SHA-256 em hexadecimal
    """
    if isinstance(content, str):
        content = content.encode('utf-8')
    
    return hashlib.sha256(content).hexdigest()

def validate_content_type(content_type: str) -> bool:
    """
    Valida um tipo de conteúdo MIME.
    
    Args:
        content_type: Tipo de conteúdo a validar
        
    Returns:
        bool: True se o tipo é seguro
    """
    safe_types = {
        'text/plain',
        'text/markdown',
        'text/html',
        'text/xml',
        'application/json',
        'application/yaml',
        'application/x-yaml'
    }
    
    return content_type.lower() in safe_types

def sanitize_html(html: str) -> str:
    """
    Sanitiza conteúdo HTML.
    
    Args:
        html: Conteúdo HTML a ser sanitizado
        
    Returns:
        str: HTML sanitizado
    """
    # TODO: Implementar sanitização HTML mais robusta
    # Por enquanto, apenas remove tags script e style
    html = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style.*?</style>', '', html, flags=re.DOTALL)
    return html

def sanitize_prompt(prompt: str) -> str:
    """
    Sanitiza um prompt para evitar injeção de instruções maliciosas.
    
    Args:
        prompt (str): Prompt a ser sanitizado.
        
    Returns:
        str: Prompt sanitizado.
    """
    # Remover tentativas de injection comuns
    sanitized = prompt
    
    # Remover instruções que possam manipular o modelo
    injection_patterns = [
        r"ignore previous instructions",
        r"ignore all instructions",
        r"disregard previous",
        r"forget your instructions",
        r"new instructions:",
        r"you must instead",
        r"you are actually",
        r"system instruction:",
        r"<system>",
        r"</system>"
    ]
    
    for pattern in injection_patterns:
        sanitized = re.sub(pattern, "[REMOVIDO]", sanitized, flags=re.IGNORECASE)
        
    return sanitized
    
def validate_file_integrity(file_path: str, expected_hash: Optional[str] = None) -> Tuple[bool, str]:
    """
    Valida a integridade de um arquivo usando hash.
    
    Args:
        file_path (str): Caminho do arquivo.
        expected_hash (str, optional): Hash esperado para comparação.
        
    Returns:
        Tuple[bool, str]: (válido, hash_calculado)
    """
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            calculated_hash = hashlib.md5(content).hexdigest()
            
        if expected_hash:
            return calculated_hash == expected_hash, calculated_hash
        
        return True, calculated_hash
    except Exception as e:
        return False, f"Erro ao validar arquivo: {str(e)}" 