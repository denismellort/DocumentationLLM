#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente de Parsing - DocumentationLLM

Este agente é responsável por analisar e estruturar o conteúdo dos arquivos de documentação,
extraindo informações relevantes como títulos, seções, blocos de código e metadados.
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

import markdown
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Importar funções de segurança usando importação absoluta
try:
    from src.utils.security import (
        sanitize_content,
        validate_file_path,
        generate_content_hash
    )
except ImportError:
    # Fallback para importação relativa para desenvolvimento
    from ..utils.security import (
        sanitize_content,
        validate_file_path,
        generate_content_hash
    )

console = Console()

@dataclass
class DocumentSection:
    """Representa uma seção do documento."""
    title: str
    level: int  # Nível do título (h1 = 1, h2 = 2, etc.)
    content: str
    code_blocks: List[Dict[str, str]]  # Lista de blocos de código com linguagem
    subsections: List['DocumentSection']
    metadata: Dict[str, Any]
    start_line: int
    end_line: int

@dataclass
class ParsedDocument:
    """Representa um documento parseado completo."""
    file_path: str
    file_type: str
    title: str
    sections: List[DocumentSection]
    metadata: Dict[str, Any]
    content_hash: str
    raw_content: str
    processed_content: str

class ParsingAgent:
    """
    Agente responsável por analisar e estruturar o conteúdo dos arquivos de documentação.
    """
    
    def __init__(self, context: Dict[str, Any]):
        """
        Inicializa o agente de parsing.
        
        Args:
            context: Contexto de execução atual.
        """
        self.context = context
        self.logger = context.get("logger")
        self.processed_dir = Path(context["directories"]["processed"])
        self.temp_dir = Path(context["directories"]["temp"])
        
        # Criar diretórios necessários
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar extensões suportadas
        self.supported_extensions = {
            '.md': self._parse_markdown,
            '.markdown': self._parse_markdown,
            '.mdx': self._parse_markdown,
            '.rst': self._parse_rst,
            '.txt': self._parse_text,
            '.html': self._parse_html,
            '.htm': self._parse_html
        }
    
    def _parse_markdown(self, content: str, file_path: str) -> ParsedDocument:
        """
        Processa um arquivo Markdown.
        
        Args:
            content: Conteúdo do arquivo
            file_path: Caminho do arquivo
            
        Returns:
            ParsedDocument: Documento processado
        """
        # Converter Markdown para HTML para facilitar o parsing
        html = markdown.markdown(
            content,
            extensions=[
                'fenced_code',
                'tables',
                'toc',
                'meta',
                'sane_lists',
                'smarty'
            ]
        )
        
        # Usar BeautifulSoup para parsing estruturado
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extrair título principal
        title = self._extract_title(soup, file_path)
        
        # Extrair seções
        sections = self._extract_sections(soup)
        
        # Extrair metadados
        metadata = self._extract_metadata(soup, content)
        
        # Gerar hash do conteúdo
        content_hash = generate_content_hash(content.encode())
        
        return ParsedDocument(
            file_path=file_path,
            file_type='markdown',
            title=title,
            sections=sections,
            metadata=metadata,
            content_hash=content_hash,
            raw_content=content,
            processed_content=html
        )
    
    def _parse_rst(self, content: str, file_path: str) -> ParsedDocument:
        """
        Processa um arquivo reStructuredText.
        
        Args:
            content: Conteúdo do arquivo
            file_path: Caminho do arquivo
            
        Returns:
            ParsedDocument: Documento processado
        """
        # TODO: Implementar parsing de RST
        raise NotImplementedError("Parsing de RST ainda não implementado")
    
    def _parse_text(self, content: str, file_path: str) -> ParsedDocument:
        """
        Processa um arquivo de texto simples.
        
        Args:
            content: Conteúdo do arquivo
            file_path: Caminho do arquivo
            
        Returns:
            ParsedDocument: Documento processado
        """
        # TODO: Implementar parsing de texto
        raise NotImplementedError("Parsing de texto ainda não implementado")
    
    def _parse_html(self, content: str, file_path: str) -> ParsedDocument:
        """
        Processa um arquivo HTML.
        
        Args:
            content: Conteúdo do arquivo
            file_path: Caminho do arquivo
            
        Returns:
            ParsedDocument: Documento processado
        """
        # TODO: Implementar parsing de HTML
        raise NotImplementedError("Parsing de HTML ainda não implementado")
    
    def _extract_title(self, soup: BeautifulSoup, file_path: str) -> str:
        """
        Extrai o título do documento.
        
        Args:
            soup: Objeto BeautifulSoup do documento
            file_path: Caminho do arquivo para fallback
            
        Returns:
            str: Título do documento
        """
        # Tentar encontrar o primeiro h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        # Fallback para nome do arquivo
        return Path(file_path).stem.replace('_', ' ').title()
    
    def _extract_sections(self, soup: BeautifulSoup) -> List[DocumentSection]:
        """
        Extrai as seções do documento.
        
        Args:
            soup: Objeto BeautifulSoup do documento
            
        Returns:
            List[DocumentSection]: Lista de seções
        """
        sections = []
        current_section = None
        
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'pre', 'code']):
            # Se é um cabeçalho
            if tag.name.startswith('h'):
                level = int(tag.name[1])
                title = tag.get_text().strip()
                
                # Criar nova seção
                new_section = DocumentSection(
                    title=title,
                    level=level,
                    content="",
                    code_blocks=[],
                    subsections=[],
                    metadata={},
                    start_line=0,  # TODO: Implementar tracking de linhas
                    end_line=0
                )
                
                # Adicionar à hierarquia correta
                if not current_section or level <= current_section.level:
                    sections.append(new_section)
                    current_section = new_section
                else:
                    current_section.subsections.append(new_section)
                    current_section = new_section
            
            # Se é conteúdo
            elif current_section:
                if tag.name == 'pre' or tag.name == 'code':
                    # Extrair bloco de código
                    code = tag.get_text().strip()
                    language = tag.get('class', ['text'])[0] if tag.get('class') else 'text'
                    current_section.code_blocks.append({
                        'language': language,
                        'code': code
                    })
                else:
                    # Adicionar texto ao conteúdo da seção
                    content = tag.get_text().strip()
                    if content:
                        current_section.content += content + "\n"
        
        return sections
    
    def _extract_metadata(self, soup: BeautifulSoup, raw_content: str) -> Dict[str, Any]:
        """
        Extrai metadados do documento.
        
        Args:
            soup: Objeto BeautifulSoup do documento
            raw_content: Conteúdo original do arquivo
            
        Returns:
            Dict[str, Any]: Metadados extraídos
        """
        metadata = {
            'word_count': len(raw_content.split()),
            'char_count': len(raw_content),
            'heading_count': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
            'code_block_count': len(soup.find_all(['pre', 'code'])),
            'processed_at': datetime.now().isoformat()
        }
        
        # Extrair tags YAML frontmatter se existirem
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n', raw_content, re.DOTALL)
        if frontmatter_match:
            try:
                import yaml
                frontmatter = yaml.safe_load(frontmatter_match.group(1))
                metadata['frontmatter'] = frontmatter
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Erro ao processar frontmatter: {str(e)}")
        
        return metadata
    
    def process_file(self, file_path: str) -> Optional[ParsedDocument]:
        """
        Processa um arquivo de documentação.
        
        Args:
            file_path: Caminho para o arquivo
            
        Returns:
            Optional[ParsedDocument]: Documento processado ou None se houver erro
        """
        try:
            # Validar caminho do arquivo
            if not validate_file_path(file_path):
                raise ValueError(f"Caminho de arquivo inválido: {file_path}")
            
            # Determinar extensão
            ext = Path(file_path).suffix.lower()
            
            # Verificar se formato é suportado
            if ext not in self.supported_extensions:
                if self.logger:
                    self.logger.warning(f"Formato não suportado: {ext}")
                return None
            
            # Ler conteúdo do arquivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Sanitizar conteúdo
            content = sanitize_content(content)
            
            # Processar arquivo
            parser = self.supported_extensions[ext]
            return parser(content, file_path)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erro ao processar arquivo {file_path}: {str(e)}")
            else:
                console.print(f"[red]Erro ao processar arquivo {file_path}: {str(e)}[/red]")
            return None
    
    def process_files(self, files: List[str]) -> Dict[str, ParsedDocument]:
        """
        Processa uma lista de arquivos de documentação.
        
        Args:
            files: Lista de caminhos de arquivos
            
        Returns:
            Dict[str, ParsedDocument]: Documentos processados
        """
        processed_docs = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Processando documentos... [/bold blue]"),
            console=console
        ) as progress:
            task = progress.add_task("parse", total=len(files))
            
            for file_path in files:
                if doc := self.process_file(file_path):
                    processed_docs[file_path] = doc
                progress.advance(task)
        
        return processed_docs
    
    def save_results(self, processed_docs: Dict[str, ParsedDocument]) -> None:
        """
        Salva os resultados do processamento.
        
        Args:
            processed_docs: Dicionário de documentos processados
        """
        # Criar diretório para resultados
        results_dir = self.processed_dir / "parsed_documents"
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Salvar cada documento
        for file_path, doc in processed_docs.items():
            # Criar nome do arquivo de saída
            rel_path = Path(file_path).relative_to(self.temp_dir)
            output_path = results_dir / f"{rel_path.stem}.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Converter seções para dicionário
            def section_to_dict(section: DocumentSection) -> Dict[str, Any]:
                return {
                    'title': section.title,
                    'level': section.level,
                    'content': section.content,
                    'code_blocks': section.code_blocks,
                    'subsections': [section_to_dict(s) for s in section.subsections],
                    'metadata': section.metadata,
                    'start_line': section.start_line,
                    'end_line': section.end_line
                }
            
            # Criar dicionário do documento
            doc_dict = {
                'file_path': str(rel_path),
                'file_type': doc.file_type,
                'title': doc.title,
                'sections': [section_to_dict(s) for s in doc.sections],
                'metadata': doc.metadata,
                'content_hash': doc.content_hash
            }
            
            # Salvar como JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(doc_dict, f, ensure_ascii=False, indent=2)
            
            if self.logger:
                self.logger.info(f"Documento processado salvo em: {output_path}")
    
    def run(self) -> Dict[str, Any]:
        """
        Executa o agente de parsing.
        
        Returns:
            Dict[str, Any]: Contexto atualizado
        """
        try:
            # Obter lista de arquivos do contexto
            files = self.context.get("documentation_files", [])
            
            if not files:
                if self.logger:
                    self.logger.warning("Nenhum arquivo de documentação encontrado no contexto")
                else:
                    console.print("[yellow]Nenhum arquivo de documentação encontrado no contexto[/yellow]")
                return self.context
            
            # Processar arquivos
            processed_docs = self.process_files(files)
            
            # Salvar resultados
            self.save_results(processed_docs)
            # Log de depuração para mostrar arquivos parseados
            console.print(f"[magenta][DEBUG] Arquivos parseados pelo ParsingAgent: {list(processed_docs.keys())}[/magenta]")
            # Garantir que o contexto seja atualizado com os documentos processados em memória
            self.context["parsed_documents"] = processed_docs
            self.context["parsing_completed"] = True
            
            return self.context
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erro durante o parsing: {str(e)}")
            else:
                console.print(f"[red]Erro durante o parsing: {str(e)}[/red]")
            
            self.context["parsing_completed"] = False
            return self.context