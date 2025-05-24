#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente de Vinculação Semântica - DocumentationLLM

Recebe documentos parseados, gera prompts para a OpenAI API para vincular explicações e blocos de código, e salva o output LLM-friendly.
"""

import os
import json
from datetime import datetime
from rich.console import Console

try:
    import openai
except ImportError:
    openai = None

console = Console()

class SemanticLinkingAgent:
    def __init__(self, context):
        self.context = context
        self.model = context["config"]["models"].get("semantic_linking", "gpt-4")
        self.max_tokens = context["config"]["processing"].get("max_tokens_per_call", 4000)
        self.documents = context.get("parsed_documents", {})
        self.logger = context.get("logger")
        self.output_dir = os.path.join(context["directories"]["processed"], "llm_friendly")
        os.makedirs(self.output_dir, exist_ok=True)

    def _build_prompt(self, doc):
        # Prompt simples para MVP: peça para associar cada seção de texto ao(s) bloco(s) de código mais relevante(s)
        return f"""
Você é um agente de vinculação semântica. Dado o seguinte documento de documentação técnica, associe cada explicação textual ao(s) bloco(s) de código mais relevante(s), mantendo o máximo de contexto.

Documento:
Título: {doc.title}
Seções:
{json.dumps([s.title for s in doc.sections], ensure_ascii=False)}

Para cada seção, gere um JSON:
{{
  "section": <título>,
  "explanation": <texto>,
  "code_blocks": [<blocos de código>]
}}
"""

    def run(self):
        if not openai:
            console.print("[red]openai não instalado. Instale com 'pip install openai'.[/red]")
            return self.context
        results = {}
        doc_count = len(self.documents)
        console.print(f"[cyan][DEBUG] SemanticLinkingAgent: processando {doc_count} documentos.[/cyan]")
        for file_path, doc in self.documents.items():
            console.print(f"[cyan][DEBUG] Documento: {file_path} | Título: {getattr(doc, 'title', 'N/A')}[/cyan]")
            prompt = self._build_prompt(doc)
            if self.logger:
                self.logger.info(f"Prompt OpenAI para {file_path}:\n{prompt}")
            else:
                console.print(f"[yellow]Prompt OpenAI para {file_path}:[/yellow]\n{prompt}")
            try:
                response = openai.OpenAI().chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Você é um agente de vinculação semântica de documentação."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.max_tokens,
                    temperature=0.2
                )
                content = response.choices[0].message.content
                results[file_path] = content
                # Salvar output LLM-friendly
                out_path = os.path.join(self.output_dir, os.path.basename(file_path) + ".llm.json")
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(str(content))
                if self.logger:
                    self.logger.info(f"Output LLM-friendly salvo em: {out_path}")
                else:
                    console.print(f"[green]Output LLM-friendly salvo em: {out_path}[/green]")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Erro na chamada OpenAI para {file_path}: {e}")
                else:
                    console.print(f"[red]Erro na chamada OpenAI para {file_path}: {e}[/red]")
        self.context["llm_friendly_outputs"] = results
        return self.context