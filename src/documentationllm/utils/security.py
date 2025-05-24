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

def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Valida uma URL para garantir que é segura para uso.
    
    Args:
        url (str): URL a ser validada.
        
    Returns:
        Tuple[bool, Optional[str]]: (válido, mensagem de erro)
    """
    # Verificar se é um repositório local
    if os.path.exists(url) or os.path.exists(os.path.abspath(url)):
        abs_path = os.path.abspath(url)
        if os.path.isdir(abs_path):
            return True, None
        else:
            return False, "O caminho local existe mas não é um diretório"
    
    # Validar URL básica
    try:
        parsed_url = urlparse(url)
        
        # Verificar se tem scheme e netloc
        if not parsed_url.scheme or not parsed_url.netloc:
            return False, "URL inválida: faltam componentes obrigatórios"
            
        # Verificar se o scheme é seguro (http, https, git)
        if parsed_url.scheme not in ['http', 'https', 'git', 'ssh']:
            return False, f"Esquema de URL não suportado: {parsed_url.scheme}"
            
        # Verificar se o domínio é confiável
        domain_trusted = False
        for trusted_domain in TRUSTED_DOMAINS:
            if trusted_domain in parsed_url.netloc:
                domain_trusted = True
                break
                
        if not domain_trusted and parsed_url.scheme != 'ssh':
            return False, f"Domínio não confiável: {parsed_url.netloc}"
            
        return True, None
        
    except Exception as e:
        return False, f"Erro ao validar URL: {str(e)}"
        
def sanitize_path(path: str) -> str:
    """
    Sanitiza um caminho de arquivo para prevenir path traversal.
    
    Args:
        path (str): Caminho a ser sanitizado.
        
    Returns:
        str: Caminho sanitizado.
    """
    # Normalizar o caminho
    normalized = os.path.normpath(path)
    
    # Remover componentes que possam causar path traversal
    while '../' in normalized or '..\\' in normalized:
        normalized = normalized.replace('../', '/')
        normalized = normalized.replace('..\\', '\\')
        
    # Garantir que não começa com ..
    if normalized.startswith('..'):
        normalized = normalized[2:]
        if normalized.startswith('/') or normalized.startswith('\\'):
            normalized = normalized[1:]
            
    return normalized
    
def sanitize_filename(filename: str) -> str:
    """
    Sanitiza um nome de arquivo para remover caracteres perigosos.
    
    Args:
        filename (str): Nome do arquivo a ser sanitizado.
        
    Returns:
        str: Nome do arquivo sanitizado.
    """
    # Remover caracteres não seguros
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
    
    # Remover espaços extras e pontos
    sanitized = sanitized.strip()
    sanitized = re.sub(r'\.+$', '', sanitized)
    
    return sanitized
    
def is_dangerous_file(filename: str) -> bool:
    """
    Verifica se um arquivo é potencialmente perigoso baseado na extensão.
    
    Args:
        filename (str): Nome do arquivo a ser verificado.
        
    Returns:
        bool: True se o arquivo for potencialmente perigoso.
    """
    for pattern in DANGEROUS_FILE_PATTERNS:
        if re.search(pattern, filename, re.IGNORECASE):
            return True
            
    return False
    
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
    
def generate_content_hash(content: Union[str, bytes]) -> str:
    """
    Gera hash de conteúdo para verificação de integridade.
    
    Args:
        content (Union[str, bytes]): Conteúdo para gerar hash.
        
    Returns:
        str: Hash MD5 do conteúdo.
    """
    if isinstance(content, str):
        content = content.encode('utf-8')
        
    return hashlib.md5(content).hexdigest()
    
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