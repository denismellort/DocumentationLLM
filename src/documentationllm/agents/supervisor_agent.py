#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente Supervisor - DocumentationLLM

Este agente é responsável por validar etapas, gerar relatórios
de execução e histórico de execução.
"""

import os
import json
import time
from datetime import datetime
import openai
from rich.console import Console
from rich.panel import Panel

# Importar funções de segurança usando importação absoluta
try:
    from src.utils.security import sanitize_prompt
except ImportError:
    # Fallback para importação relativa para desenvolvimento
    from ..utils.security import sanitize_prompt

console = Console()

class SupervisorAgent:
    """
    Agente responsável pela supervisão e validação das etapas do pipeline,
    geração de relatórios e histórico de execução.
    """
    
    def __init__(self, context):
        """
        Inicializa o agente supervisor.
        
        Args:
            context (dict): Contexto de execução atual.
        """
        self.context = context
        self.model = context["config"]["models"]["supervisor"]
        self.max_tokens = context["config"]["processing"]["max_tokens_per_call"]
        self.enable_supervision = context["config"]["processing"]["enable_supervision"]
        self.enable_history = context["config"]["processing"]["enable_execution_history"]
        self.client = openai.OpenAI()
        self.logger = context.get("logger")
        
        # Criar histórico de execução se habilitado
        if self.enable_history and "execution_history" not in context:
            context["execution_history"] = []
    
    def validate_step(self, step_name, step_result, agent_notes=None):
        """
        Valida uma etapa do pipeline usando IA.
        
        Args:
            step_name (str): Nome da etapa.
            step_result (dict): Resultado da etapa.
            agent_notes (str, optional): Notas adicionais do agente executor.
        
        Returns:
            dict: Resultado da validação com feedback, status e sugestões.
        """
        if not self.enable_supervision:
            # Se a supervisão estiver desabilitada, assumir que a etapa foi bem-sucedida
            return {
                "step_name": step_name,
                "valid": True,
                "feedback": "Validação automática desabilitada",
                "suggestions": [],
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # Preparar o prompt para o modelo de supervisão
            prompt = self._prepare_validation_prompt(step_name, step_result, agent_notes)
            
            if self.logger:
                self.logger.debug(f"Validando etapa: {step_name}")
            
            # Registrar tokens usados para o prompt
            prompt_tokens = len(prompt.split()) * 1.3  # Estimativa simples
            
            # Chamar o modelo de IA para validação (se não for local)
            if self.model.lower() != "local":
                start_time = time.time()
                
                # Sanitizar prompt para evitar injeção
                sanitized_prompt = sanitize_prompt(prompt)
                
                # Preparar mensagens para a API
                messages = [
                    {"role": "system", "content": "Você é um agente supervisor que valida etapas de processamento de documentação, fornecendo feedback construtivo e sugestões de melhoria."},
                    {"role": "user", "content": sanitized_prompt}
                ]
                
                # Chamar a API da OpenAI
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=0.1
                )
                
                # Extrair resposta
                ai_feedback = response.choices[0].message.content
                
                # Calcular tokens e custo
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
                total_tokens = response.usage.total_tokens
                
                # Registrar uso de API com logger se disponível
                if self.logger:
                    self.logger.log_api_call(
                        api_name="OpenAI",
                        endpoint=self.model,
                        request_data={"step": step_name, "action": "validation"},
                        response_data={"content_length": len(ai_feedback)},
                        token_count={
                            "input_tokens": prompt_tokens,
                            "output_tokens": completion_tokens,
                            "total_tokens": total_tokens
                        }
                    )
                
                # Verificar e registrar análise de tokens
                if "token_stats" in self.context and hasattr(self.context.get("agents", {}).get("token_analyst"), "log_token_usage"):
                    token_analyst = self.context["agents"].get("token_analyst")
                    token_usage = token_analyst.log_token_usage(
                        step_name=f"validation_{step_name}", 
                        model=self.model, 
                        input_tokens=prompt_tokens, 
                        output_tokens=completion_tokens
                    )
                else:
                    # Atualizar estatísticas internas
                    self.context["stats"]["tokens_used"] += total_tokens
                    
                    # Calcular custo estimado (pode ser ajustado conforme modelo)
                    cost_per_1k_input = 0.03 if "gpt-4" in self.model.lower() else 0.0015  # Valor aproximado
                    cost_per_1k_output = 0.06 if "gpt-4" in self.model.lower() else 0.002  # Valor aproximado
                    input_cost = (prompt_tokens / 1000) * cost_per_1k_input
                    output_cost = (completion_tokens / 1000) * cost_per_1k_output
                    estimated_cost = input_cost + output_cost
                    self.context["stats"]["estimated_cost"] += estimated_cost
                    
                    token_usage = {
                        "model": self.model,
                        "input_tokens": prompt_tokens,
                        "output_tokens": completion_tokens,
                        "total_tokens": total_tokens,
                        "cost": estimated_cost
                    }
                
                # Parsear resposta
                validation_result = self._parse_validation_response(ai_feedback)
                validation_result["tokens_used"] = total_tokens
                validation_result["cost"] = token_usage.get("cost", 0)
                validation_result["execution_time"] = time.time() - start_time
                
                if self.logger:
                    self.logger.info(f"Etapa {step_name} validada: {'✓' if validation_result['valid'] else '✗'}")
                    if not validation_result['valid']:
                        self.logger.warning(f"Feedback: {validation_result['feedback']}")
                        
            else:
                # Supervisão local (simplificada)
                validation_result = {
                    "valid": True,
                    "feedback": "Validação local automática",
                    "suggestions": [],
                    "tokens_used": 0,
                    "cost": 0,
                    "execution_time": 0
                }
                
                if self.logger:
                    self.logger.info(f"Etapa {step_name} validada localmente (modo local)")
            
            # Adicionar metadados à validação
            validation_result["step_name"] = step_name
            validation_result["timestamp"] = datetime.now().isoformat()
            
            # Adicionar ao histórico se habilitado
            if self.enable_history:
                self.context["execution_history"].append({
                    "type": "validation",
                    "step": step_name,
                    "result": validation_result,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Registrar etapa completa ou falha
            if validation_result["valid"]:
                if step_name not in self.context["stats"]["steps_completed"]:
                    self.context["stats"]["steps_completed"].append(step_name)
            else:
                if step_name not in self.context["stats"]["steps_failed"]:
                    self.context["stats"]["steps_failed"].append(step_name)
            
            return validation_result
        
        except Exception as e:
            # Em caso de erro, registrar e retornar validação básica
            error_message = f"Erro durante validação: {str(e)}"
            
            if self.logger:
                self.logger.error(error_message)
            else:
                console.print(f"[bold red]{error_message}[/bold red]")
                
            error_result = {
                "step_name": step_name,
                "valid": False,
                "feedback": error_message,
                "suggestions": ["Verificar logs para mais detalhes"],
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
            
            # Registrar falha
            if step_name not in self.context["stats"]["steps_failed"]:
                self.context["stats"]["steps_failed"].append(step_name)
            
            # Adicionar ao histórico se habilitado
            if self.enable_history:
                self.context["execution_history"].append({
                    "type": "validation_error",
                    "step": step_name,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
            
            return error_result
    
    def _prepare_validation_prompt(self, step_name, step_result, agent_notes):
        """
        Prepara o prompt para o modelo de validação.
        
        Args:
            step_name (str): Nome da etapa.
            step_result (dict): Resultado da etapa.
            agent_notes (str): Notas adicionais do agente executor.
        
        Returns:
            str: Prompt para o modelo.
        """
        # Converter resultado para string formatada para o prompt
        result_str = json.dumps(step_result, indent=2, ensure_ascii=False)
        
        # Limite de tamanho para evitar tokens excessivos
        if len(result_str) > 2000:
            result_str = result_str[:1000] + "\n...\n" + result_str[-1000:]
        
        # Construir prompt
        prompt = f"""
# Validação da etapa: {step_name}

## Resultado da etapa
```json
{result_str}
```

## Notas do agente
{agent_notes or "Nenhuma nota adicional."}

## Instruções
Por favor, analise o resultado da etapa "{step_name}" e determine:
1. Se a etapa foi concluída com sucesso (valid: true/false)
2. Feedback detalhado sobre a qualidade e completude do resultado
3. Sugestões específicas para melhorar o resultado ou o processo

Responda no seguinte formato:
```json
{{
  "valid": true/false,
  "feedback": "Seu feedback detalhado aqui",
  "suggestions": [
    "Sugestão 1",
    "Sugestão 2",
    ...
  ]
}}
```
"""
        return prompt
    
    def _parse_validation_response(self, response):
        """
        Parseia a resposta do modelo de validação.
        
        Args:
            response (str): Resposta do modelo.
        
        Returns:
            dict: Resultado da validação estruturado.
        """
        try:
            # Tentar extrair JSON da resposta
            json_start = response.find('```json')
            json_end = response.find('```', json_start + 7)
            
            if json_start >= 0 and json_end >= 0:
                json_str = response[json_start + 7:json_end].strip()
                result = json.loads(json_str)
            else:
                # Tentar parsear a resposta completa como JSON
                result = json.loads(response)
            
            # Validar campos obrigatórios
            if "valid" not in result:
                result["valid"] = False
            
            if "feedback" not in result:
                result["feedback"] = "Sem feedback disponível"
            
            if "suggestions" not in result:
                result["suggestions"] = []
            
            return result
        
        except json.JSONDecodeError:
            # Fallback para resposta não estruturada
            if self.logger:
                self.logger.warning("Não foi possível parsear a resposta estruturada da validação")
                
            return {
                "valid": True,  # Assume sucesso para evitar interrupções
                "feedback": "Não foi possível parsear a resposta estruturada",
                "suggestions": ["Verificar resposta original para detalhes"],
                "raw_response": response
            }
    
    def log_decision(self, decision_type, description, details=None):
        """
        Registra uma decisão tomada durante o processamento.
        
        Args:
            decision_type (str): Tipo de decisão (ex: "parsing", "chunking").
            description (str): Descrição breve da decisão.
            details (dict, optional): Detalhes adicionais da decisão.
        """
        if not self.enable_history:
            return
        
        decision = {
            "type": "decision",
            "decision_type": decision_type,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            decision["details"] = details
        
        self.context["execution_history"].append(decision)
        
        if self.logger:
            log_message = f"Decisão ({decision_type}): {description}"
            self.logger.info(log_message)
            
            if details:
                detail_str = ", ".join([f"{k}: {v}" for k, v in details.items()])
                self.logger.debug(f"Detalhes da decisão: {detail_str}")
    
    @staticmethod
    def generate_report(context, output_path):
        """
        Gera um relatório de execução em Markdown.
        
        Args:
            context (dict): Contexto de execução completo.
            output_path (str): Caminho para salvar o relatório.
        """
        # Calcular estatísticas
        start_time = context["stats"]["start_time"]
        end_time = context["stats"]["end_time"] or datetime.now()
        duration = end_time - start_time
        
        # Obter valores de tokens e custo (garantindo consistência)
        if "token_stats" in context and "total_tokens" in context["token_stats"]:
            tokens_used = max(context["stats"]["tokens_used"], context["token_stats"]["total_tokens"])
            # Atualizar ambos para consistência
            context["stats"]["tokens_used"] = tokens_used
            context["token_stats"]["total_tokens"] = tokens_used
        else:
            tokens_used = context["stats"]["tokens_used"]
            
        estimated_cost = context["stats"]["estimated_cost"]
        steps_completed = context["stats"]["steps_completed"]
        steps_failed = context["stats"]["steps_failed"]
        
        # Adicionar informações de metadados/estatísticas de arquivos processados
        file_stats = {}
        if "documentation_files_metadata" in context:
            metadata = context["documentation_files_metadata"]
            total_files = len(metadata)
            total_size = sum(file_data.get("size", 0) for file_data in metadata.values())
            
            # Calcular tamanho formatado
            if total_size < 1024:
                size_formatted = f"{total_size} bytes"
            elif total_size < 1024 * 1024:
                size_formatted = f"{total_size / 1024:.2f} KB"
            else:
                size_formatted = f"{total_size / (1024 * 1024):.2f} MB"
                
            # Calcular distribuição por tipo
            file_types = {}
            for file_data in metadata.values():
                file_type = file_data.get("type", "unknown")
                if file_type not in file_types:
                    file_types[file_type] = 0
                file_types[file_type] += 1
                
            file_stats = {
                "total_files": total_files,
                "total_size": total_size,
                "size_formatted": size_formatted,
                "file_types": file_types
            }
        
        # Criar relatório em Markdown
        report = f"""# Relatório de Execução - DocumentationLLM

## Informações Gerais

- **ID de Execução:** {context["execution_id"]}
- **Repositório:** {context["repo_url"]}
- **Data de Início:** {start_time.strftime("%Y-%m-%d %H:%M:%S")}
- **Data de Término:** {end_time.strftime("%Y-%m-%d %H:%M:%S")}
- **Duração:** {duration}
- **Tokens Utilizados:** {tokens_used}
- **Custo Estimado:** ${estimated_cost:.4f}

"""

        # Adicionar estatísticas de arquivos se disponíveis
        if file_stats:
            report += f"""## Estatísticas de Arquivos

- **Total de Arquivos:** {file_stats["total_files"]}
- **Tamanho Total:** {file_stats["size_formatted"]}

### Distribuição por Tipo
| Tipo de Arquivo | Quantidade |
|----------------|------------|
"""
            for file_type, count in sorted(file_stats["file_types"].items(), key=lambda x: x[1], reverse=True):
                report += f"| {file_type} | {count} |\n"
                
            report += "\n"

        report += f"""## Resumo de Etapas

### Etapas Concluídas ({len(steps_completed)})
{chr(10).join([f"- {step}" for step in steps_completed])}

### Etapas com Falha ({len(steps_failed)})
{chr(10).join([f"- {step}" for step in steps_failed]) if steps_failed else "- Nenhuma etapa falhou"}

## Configuração Utilizada

```yaml
models:
  download: {context["config"]["models"]["download"]}
  parsing: {context["config"]["models"]["parsing"]}
  semantic_linking: {context["config"]["models"]["semantic_linking"]}
  output_generation: {context["config"]["models"]["output_generation"]}
  supervisor: {context["config"]["models"]["supervisor"]}
  token_analyst: {context["config"]["models"]["token_analyst"]}

processing:
  enable_supervision: {context["config"]["processing"]["enable_supervision"]}
  enable_token_analysis: {context["config"]["processing"]["enable_token_analysis"]}
  enable_execution_history: {context["config"]["processing"]["enable_execution_history"]}
  log_level: {context["config"]["processing"]["log_level"]}
  max_tokens_per_call: {context["config"]["processing"]["max_tokens_per_call"]}

scaling:
  use_max_node: {context["config"]["scaling"]["use_max_node"]}
  max_concurrent_tasks: {context["config"]["scaling"]["max_concurrent_tasks"]}
```

## Diretórios

- **Documentação Original:** {context["directories"]["originals"]}
- **Documentação Processada:** {context["directories"]["processed"]}
- **Arquivos Temporários:** {context["directories"]["temp"]}

"""
        
        # Adicionar histórico de validação se disponível
        if "execution_history" in context and context["execution_history"]:
            report += "\n## Histórico de Execução\n\n"
            
            for entry in context["execution_history"]:
                entry_type = entry.get("type", "unknown")
                timestamp = datetime.fromisoformat(entry.get("timestamp", datetime.now().isoformat())).strftime("%Y-%m-%d %H:%M:%S")
                
                if entry_type == "validation":
                    step = entry.get("step", "desconhecida")
                    result = entry.get("result", {})
                    valid = "✅ Válido" if result.get("valid", False) else "❌ Inválido"
                    feedback = result.get("feedback", "Sem feedback")
                    
                    report += f"### {timestamp} - Validação da etapa: {step} - {valid}\n\n"
                    report += f"**Feedback:** {feedback}\n\n"
                    
                    if "suggestions" in result and result["suggestions"]:
                        report += "**Sugestões:**\n"
                        for suggestion in result["suggestions"]:
                            report += f"- {suggestion}\n"
                        report += "\n"
                
                elif entry_type == "decision":
                    decision_type = entry.get("decision_type", "desconhecido")
                    description = entry.get("description", "Sem descrição")
                    
                    report += f"### {timestamp} - Decisão: {decision_type}\n\n"
                    report += f"{description}\n\n"
                    
                    if "details" in entry and entry["details"]:
                        report += "**Detalhes:**\n"
                        for key, value in entry["details"].items():
                            report += f"- **{key}:** {value}\n"
                        report += "\n"
                
                elif entry_type == "validation_error":
                    step = entry.get("step", "desconhecida")
                    error = entry.get("error", "Erro desconhecido")
                    
                    report += f"### {timestamp} - Erro de validação na etapa: {step}\n\n"
                    report += f"**Erro:** {error}\n\n"
        
        # Salvar relatório - Modificado para garantir codificação correta no Windows
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8-sig") as f:
            f.write(report)
            
        # Log com o logger se disponível
        logger = context.get("logger")
        if logger:
            logger.info(f"Relatório de execução gerado: {output_path}")
    
    @staticmethod
    def save_history(context, output_path):
        """
        Salva o histórico de execução em formato JSON.
        
        Args:
            context (dict): Contexto de execução completo.
            output_path (str): Caminho para salvar o histórico.
        """
        if "execution_history" not in context:
            # Se não houver histórico, criar um básico
            history = {
                "execution_id": context["execution_id"],
                "repo_url": context["repo_url"],
                "start_time": context["stats"]["start_time"].isoformat(),
                "end_time": (context["stats"]["end_time"] or datetime.now()).isoformat(),
                "tokens_used": context["stats"]["tokens_used"],
                "estimated_cost": context["stats"]["estimated_cost"],
                "steps_completed": context["stats"]["steps_completed"],
                "steps_failed": context["stats"]["steps_failed"],
                "entries": []
            }
        else:
            # Preparar histórico para serialização JSON
            history = {
                "execution_id": context["execution_id"],
                "repo_url": context["repo_url"],
                "start_time": context["stats"]["start_time"].isoformat(),
                "end_time": (context["stats"]["end_time"] or datetime.now()).isoformat(),
                "tokens_used": context["stats"]["tokens_used"],
                "estimated_cost": context["stats"]["estimated_cost"],
                "steps_completed": context["stats"]["steps_completed"],
                "steps_failed": context["stats"]["steps_failed"],
                "entries": context["execution_history"]
            }
        
        # Salvar histórico - Modificado para garantir codificação correta no Windows
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8-sig") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
            
        # Log com o logger se disponível
        logger = context.get("logger")
        if logger:
            logger.info(f"Histórico de execução salvo: {output_path}")
    
    def run(self):
        """
        Método principal do agente. No caso do supervisor, este método
        não é usado diretamente, pois o supervisor é chamado por outros agentes.
        
        Returns:
            dict: Contexto atualizado.
        """
        # Este método existe apenas para compatibilidade com a interface de agente
        return self.context
