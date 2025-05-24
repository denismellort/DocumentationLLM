import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime

import openai
from openai.types.chat import ChatCompletion

from ..utils.config import Config
from ..utils.logging import setup_logger

logger = setup_logger(__name__)

class SemanticLinkingAgent:
    """
    Agente responsável por processar documentos parseados e criar vínculos semânticos
    entre texto explicativo e blocos de código usando a OpenAI.
    """

    def __init__(self, context: Dict):
        """
        Inicializa o SemanticLinkingAgent.

        Args:
            context (Dict): Contexto do pipeline contendo configurações e estado
        """
        self.context = context
        self.config = context["config"]
        self.model = self.config.get("agents.semantic_linking.model", "gpt-4")
        self.temperature = self.config.get("agents.semantic_linking.temperature", 0.0)
        self.max_tokens = self.config.get("agents.semantic_linking.max_tokens", 4000)
        self.batch_size = self.config.get("agents.semantic_linking.batch_size", 5)
        self.retry_attempts = self.config.get("agents.semantic_linking.retry_attempts", 3)
        
        # Garante que a chave da API está configurada
        if not openai.api_key:
            openai.api_key = self.config.get("openai.api_key")
            if not openai.api_key:
                raise ValueError("OpenAI API key não configurada")

    def run(self) -> Dict:
        """
        Executa o processamento de vinculação semântica em todos os documentos parseados.

        Returns:
            Dict: Contexto atualizado com os documentos processados
        """
        try:
            logger.info("Iniciando processamento de vinculação semântica...")
            
            # Verifica se existem documentos parseados
            if not self.context.get("parsed_documents"):
                raise ValueError("Nenhum documento parseado encontrado no contexto")
            
            # Processa cada documento
            linked_documents = []
            total_documents = len(self.context["parsed_documents"])
            
            for i, doc in enumerate(self.context["parsed_documents"], 1):
                logger.info(f"Processando documento {i}/{total_documents}: {doc.get('path', 'unknown')}")
                try:
                    processed_doc = self.process_document(doc)
                    linked_documents.append(processed_doc)
                except Exception as e:
                    logger.error(f"Erro ao processar documento {doc.get('path')}: {e}")
                    # Adiciona o documento original em caso de erro
                    linked_documents.append(doc)
            
            # Atualiza o contexto
            self.context["linked_documents"] = linked_documents
            self.context["semantic_linking_completed"] = True
            
            # Registra estatísticas
            self.context["semantic_linking_stats"] = {
                "total_documents": total_documents,
                "successful_documents": len([d for d in linked_documents if "semantic_links" in d]),
                "failed_documents": len([d for d in linked_documents if "semantic_links" not in d]),
                "model_used": self.model,
                "timestamp": str(datetime.now())
            }
            
            logger.info("Processamento de vinculação semântica concluído com sucesso")
            return self.context
            
        except Exception as e:
            logger.error(f"Erro durante o processamento de vinculação semântica: {e}")
            self.context["semantic_linking_completed"] = False
            raise

    def process_document(self, parsed_document: Dict) -> Dict:
        """
        Processa um documento parseado, criando vínculos semânticos entre texto e código.

        Args:
            parsed_document (Dict): Documento parseado contendo texto e blocos de código

        Returns:
            Dict: Documento processado com vínculos semânticos
        """
        try:
            # Extrai seções de texto e código
            sections = self._extract_sections(parsed_document)
            
            # Processa cada seção para criar vínculos
            linked_sections = []
            for section in sections:
                linked_section = self._process_section(section)
                linked_sections.append(linked_section)
            
            # Monta o documento final com os vínculos
            processed_document = {
                "metadata": parsed_document.get("metadata", {}),
                "linked_sections": linked_sections,
                "original_path": parsed_document.get("path", ""),
                "processing_info": {
                    "model": self.model,
                    "temperature": self.temperature
                }
            }
            
            return processed_document
            
        except Exception as e:
            logger.error(f"Erro ao processar documento: {e}")
            raise

    def _extract_sections(self, parsed_document: Dict) -> List[Dict]:
        """
        Extrai seções de texto e código do documento parseado.

        Args:
            parsed_document (Dict): Documento parseado

        Returns:
            List[Dict]: Lista de seções contendo texto e código
        """
        sections = []
        current_section = {"text": [], "code": []}
        
        for item in parsed_document.get("content", []):
            if item["type"] == "text":
                if current_section["code"] and current_section["text"]:
                    sections.append(current_section.copy())
                    current_section = {"text": [], "code": []}
                current_section["text"].append(item["content"])
            elif item["type"] == "code":
                current_section["code"].append({
                    "content": item["content"],
                    "language": item.get("language", ""),
                    "metadata": item.get("metadata", {})
                })
        
        if current_section["text"] or current_section["code"]:
            sections.append(current_section)
        
        return sections

    def _process_section(self, section: Dict) -> Dict:
        """
        Processa uma seção individual, criando vínculos semânticos entre texto e código.

        Args:
            section (Dict): Seção contendo texto e código

        Returns:
            Dict: Seção processada com vínculos semânticos
        """
        if not section["text"] or not section["code"]:
            return section
        
        # Prepara o prompt para a OpenAI
        prompt = self._prepare_prompt(section)
        
        try:
            # Faz a chamada à API da OpenAI
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um especialista em documentação técnica, focado em criar vínculos semânticos precisos entre texto explicativo e código."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Processa a resposta
            semantic_links = self._parse_openai_response(response)
            
            # Adiciona os vínculos à seção
            processed_section = {
                "text": section["text"],
                "code": section["code"],
                "semantic_links": semantic_links
            }
            
            return processed_section
            
        except Exception as e:
            logger.error(f"Erro ao processar seção com OpenAI: {e}")
            return section

    def _prepare_prompt(self, section: Dict) -> str:
        """
        Prepara o prompt para a OpenAI baseado na seção.

        Args:
            section (Dict): Seção contendo texto e código

        Returns:
            str: Prompt formatado
        """
        text = "\n".join(section["text"])
        code_blocks = [
            f"```{block['language']}\n{block['content']}\n```"
            for block in section["code"]
        ]
        code = "\n\n".join(code_blocks)
        
        prompt = f"""Analise o seguinte texto explicativo e blocos de código, e crie vínculos semânticos precisos entre eles.
        
Texto explicativo:
{text}

Blocos de código:
{code}

Gere um JSON que contenha:
1. Uma lista de conceitos chave do texto
2. Para cada conceito, identifique as linhas de código relacionadas
3. Uma breve explicação de como o código implementa cada conceito
4. Metadados adicionais que ajudem a entender a relação texto-código

Formato esperado:
{{
    "concepts": [
        {{
            "name": "nome do conceito",
            "text_references": ["trecho do texto"],
            "code_references": ["trecho do código"],
            "explanation": "explicação da relação",
            "metadata": {{
                "confidence": float,
                "type": "implementation|example|reference"
            }}
        }}
    ]
}}"""
        
        return prompt

    def _parse_openai_response(self, response: ChatCompletion) -> Dict:
        """
        Processa a resposta da OpenAI e extrai os vínculos semânticos.

        Args:
            response (ChatCompletion): Resposta da OpenAI

        Returns:
            Dict: Vínculos semânticos estruturados
        """
        try:
            content = response.choices[0].message.content
            semantic_links = json.loads(content)
            
            # Valida a estrutura básica
            if not isinstance(semantic_links, dict) or "concepts" not in semantic_links:
                raise ValueError("Resposta da OpenAI não está no formato esperado")
            
            return semantic_links
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar resposta da OpenAI: {e}")
            return {"concepts": []}
        except Exception as e:
            logger.error(f"Erro ao processar resposta da OpenAI: {e}")
            return {"concepts": []}