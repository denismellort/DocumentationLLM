#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
Agente de Análise de Tokens - DocumentationLLM

Este agente é responsável por monitorar o uso de tokens e custos associados
às chamadas de IA, gerando relatórios detalhados para controle de gastos.
"""

import os
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table

console = Console()

class TokenAnalystAgent:
    """
    Agente responsável por monitorar o uso de tokens e custos,
    gerar relatórios e sugerir otimizações para reduzir gastos.
    """
    
    # Custo aproximado por 1000 tokens para diferentes modelos (em USD)
    MODEL_COSTS = {
        "gpt-4": {
            "input": 0.03,
            "output": 0.06
        },
        "gpt-4-32k": {
            "input": 0.06,
            "output": 0.12
        },
        "gpt-3.5-turbo": {
            "input": 0.0015,
            "output": 0.002
        },
        "gpt-3.5-turbo-16k": {
            "input": 0.003,
            "output": 0.004
        },
        "local": {
            "input": 0,
            "output": 0
        }
    }
    
    def __init__(self, context):
        """
        Inicializa o agente de análise de tokens.
        
        Args:
            context (dict): Contexto de execução atual.
        """
        self.context = context
        self.enable_token_analysis = context["config"]["processing"]["enable_token_analysis"]
        self.logger = context.get("logger")
        
        # Inicializar estatísticas por modelo se não existirem
        if "token_stats" not in context:
            context["token_stats"] = {
                "models": {},
                "steps": {},
                "total_tokens": 0,
                "total_cost": 0.0
            }
            
        # Corrigir a discrepância entre o relatório de token e o relatório de execução
        # Garantindo que o tokens_used no stats global seja consistente com o total no token_stats
        if "token_stats" in context and "total_tokens" in context["token_stats"]:
            context["stats"]["tokens_used"] = context["token_stats"]["total_tokens"]
            if self.logger:
                self.logger.debug(f"Sincronizando contagem de tokens: {context['token_stats']['total_tokens']}")
    
    def log_token_usage(self, step_name, model, input_tokens, output_tokens):
        """
        Registra o uso de tokens de uma chamada de IA.
        
        Args:
            step_name (str): Nome da etapa que fez a chamada.
            model (str): Nome do modelo usado (ex: "gpt-4", "gpt-3.5-turbo").
            input_tokens (int): Número de tokens de entrada.
            output_tokens (int): Número de tokens de saída.
        
        Returns:
            dict: Informações sobre custo e tokens para esta chamada.
        """
        if not self.enable_token_analysis:
            return {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "cost": 0
            }
        
        # Normalizar nome do modelo para encontrar custos
        model_base = model.lower()
        if "gpt-4" in model_base:
            if "32k" in model_base:
                model_key = "gpt-4-32k"
            else:
                model_key = "gpt-4"
        elif "gpt-3.5" in model_base:
            if "16k" in model_base:
                model_key = "gpt-3.5-turbo-16k"
            else:
                model_key = "gpt-3.5-turbo"
        else:
            model_key = "local"
        
        # Calcular custo desta chamada
        input_cost = (input_tokens / 1000) * self.MODEL_COSTS[model_key]["input"]
        output_cost = (output_tokens / 1000) * self.MODEL_COSTS[model_key]["output"]
        total_cost = input_cost + output_cost
        
        # Atualizar estatísticas globais
        self.context["stats"]["tokens_used"] += input_tokens + output_tokens
        self.context["stats"]["estimated_cost"] += total_cost
        
        if self.logger:
            self.logger.debug(
                f"Token usage: {step_name} - {model_key} - " + 
                f"Input: {input_tokens}, Output: {output_tokens}, Total: {input_tokens + output_tokens}"
            )
            
            # Registrar chamada de API com detalhes de tokens
            self.logger.log_api_call(
                api_name="OpenAI",
                endpoint=model_key,
                request_data={"step": step_name},
                token_count={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                    "cost": total_cost
                }
            )
        
        # Atualizar estatísticas detalhadas por modelo
        if model_key not in self.context["token_stats"]["models"]:
            self.context["token_stats"]["models"][model_key] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "cost": 0.0,
                "calls": 0
            }
        
        self.context["token_stats"]["models"][model_key]["input_tokens"] += input_tokens
        self.context["token_stats"]["models"][model_key]["output_tokens"] += output_tokens
        self.context["token_stats"]["models"][model_key]["total_tokens"] += input_tokens + output_tokens
        self.context["token_stats"]["models"][model_key]["cost"] += total_cost
        self.context["token_stats"]["models"][model_key]["calls"] += 1
        
        # Atualizar estatísticas por etapa
        if step_name not in self.context["token_stats"]["steps"]:
            self.context["token_stats"]["steps"][step_name] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "cost": 0.0,
                "calls": 0,
                "models_used": {}
            }
        
        self.context["token_stats"]["steps"][step_name]["input_tokens"] += input_tokens
        self.context["token_stats"]["steps"][step_name]["output_tokens"] += output_tokens
        self.context["token_stats"]["steps"][step_name]["total_tokens"] += input_tokens + output_tokens
        self.context["token_stats"]["steps"][step_name]["cost"] += total_cost
        self.context["token_stats"]["steps"][step_name]["calls"] += 1
        
        # Registrar uso de modelo específico nesta etapa
        if model_key not in self.context["token_stats"]["steps"][step_name]["models_used"]:
            self.context["token_stats"]["steps"][step_name]["models_used"][model_key] = {
                "calls": 0,
                "tokens": 0,
                "cost": 0.0
            }
        
        self.context["token_stats"]["steps"][step_name]["models_used"][model_key]["calls"] += 1
        self.context["token_stats"]["steps"][step_name]["models_used"][model_key]["tokens"] += input_tokens + output_tokens
        self.context["token_stats"]["steps"][step_name]["models_used"][model_key]["cost"] += total_cost
        
        # Atualizar totais
        self.context["token_stats"]["total_tokens"] += input_tokens + output_tokens
        self.context["token_stats"]["total_cost"] += total_cost
        
        # Retornar informações desta chamada
        return {
            "model": model_key,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost
        }
    
    def generate_token_report(self, output_path):
        """
        Gera um relatório detalhado de uso de tokens e custos.
        
        Args:
            output_path (str): Caminho para salvar o relatório.
        """
        if not self.enable_token_analysis:
            return
        
        # Estatísticas
        start_time = self.context["stats"]["start_time"]
        end_time = self.context["stats"]["end_time"] or datetime.now()
        duration = end_time - start_time
        
        # Resolver a discrepância - garantir que os valores sejam consistentes
        # Usar o valor mais alto entre o contexto global e token_stats
        total_tokens = max(
            self.context["stats"]["tokens_used"],
            self.context["token_stats"]["total_tokens"]
        )
        
        # Atualizar ambos os valores para manter consistência
        self.context["stats"]["tokens_used"] = total_tokens
        self.context["token_stats"]["total_tokens"] = total_tokens
        
        total_cost = self.context["stats"]["estimated_cost"]
        
        if self.logger:
            self.logger.info(f"Gerando relatório de tokens - Total: {total_tokens}, Custo: ${total_cost:.4f}")
        
        # Criar relatório em Markdown
        report = f"""# Relatório de Uso de Tokens - DocumentationLLM

## Informações Gerais

- **ID de Execução:** {self.context["execution_id"]}
- **Repositório:** {self.context["repo_url"]}
- **Data de Início:** {start_time.strftime("%Y-%m-%d %H:%M:%S")}
- **Data de Término:** {end_time.strftime("%Y-%m-%d %H:%M:%S")}
- **Duração:** {duration}
- **Total de Tokens:** {total_tokens:,}
- **Custo Total Estimado:** ${total_cost:.4f}

## Uso por Modelo

| Modelo | Chamadas | Tokens de Entrada | Tokens de Saída | Total de Tokens | Custo (USD) |
|--------|----------|-------------------|-----------------|-----------------|-------------|
"""
        
        # Adicionar informações por modelo
        for model, stats in self.context["token_stats"]["models"].items():
            report += f"| {model} | {stats['calls']} | {stats['input_tokens']:,} | {stats['output_tokens']:,} | {stats['total_tokens']:,} | ${stats['cost']:.4f} |\n"
        
        report += """
## Uso por Etapa

| Etapa | Chamadas | Total de Tokens | Custo (USD) | Modelos Utilizados |
|-------|----------|----------------|-------------|-------------------|
"""
        
        # Adicionar informações por etapa
        for step, stats in self.context["token_stats"]["steps"].items():
            # Listar modelos utilizados na etapa
            models_used = ", ".join([f"{model} ({usage['calls']} chamadas)" for model, usage in stats["models_used"].items()])
            report += f"| {step} | {stats['calls']} | {stats['total_tokens']:,} | ${stats['cost']:.4f} | {models_used} |\n"
        
        # Adicionar seção de otimizações sugeridas
        report += """
## Otimizações Sugeridas

"""
        
        # Analisar etapas mais caras e sugerir otimizações
        steps_by_cost = sorted(self.context["token_stats"]["steps"].items(), key=lambda x: x[1]["cost"], reverse=True)
        if steps_by_cost:
            most_expensive_step, most_expensive_stats = steps_by_cost[0]
            
            report += f"### Etapa mais cara: {most_expensive_step}\n\n"
            report += f"Esta etapa consumiu ${most_expensive_stats['cost']:.4f} ({most_expensive_stats['total_tokens']:,} tokens), representando "
            report += f"{(most_expensive_stats['cost'] / total_cost * 100):.1f}% do custo total.\n\n"
            
            # Sugestões específicas para etapas caras
            report += "**Sugestões:**\n\n"
            
            # Se usa GPT-4, sugerir GPT-3.5 para reduzir custos
            if any("gpt-4" in model for model in most_expensive_stats["models_used"]):
                report += "- Considere usar GPT-3.5 em vez de GPT-4 para reduzir custos (até 15x mais barato).\n"
            
            # Sugestões gerais
            report += "- Otimize prompts para serem mais concisos, reduzindo tokens de entrada.\n"
            report += "- Implemente caching para evitar chamadas repetitivas com os mesmos inputs.\n"
            report += "- Reduza o tamanho do contexto quando possível, especialmente em etapas de análise.\n"
            
            # Analisar outras etapas
            if len(steps_by_cost) > 1:
                report += "\n### Outras etapas custosas:\n\n"
                for step, stats in steps_by_cost[1:3]:  # Mostrar as próximas 2 etapas mais caras
                    report += f"- **{step}**: ${stats['cost']:.4f} ({stats['total_tokens']:,} tokens)\n"
        
        # Adicionar análise de economia potencial
        potential_savings = 0
        savings_description = []
        
        # Calcular economia potencial substituindo GPT-4 por GPT-3.5
        for model, stats in self.context["token_stats"]["models"].items():
            if "gpt-4" in model:
                # Custo com GPT-3.5 seria aproximadamente 15x menor
                gpt35_cost = stats["cost"] / 15
                model_savings = stats["cost"] - gpt35_cost
                potential_savings += model_savings
                
                if model_savings > 0.01:  # Só mostrar se a economia for significativa
                    savings_description.append(f"- Substituir {model} por GPT-3.5 economizaria aproximadamente ${model_savings:.4f}.")
        
        if potential_savings > 0:
            report += f"\n### Economia Potencial: ${potential_savings:.4f}\n\n"
            for desc in savings_description:
                report += f"{desc}\n"
        
        # Salvar relatório - Modificado para garantir codificação correta no Windows
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8-sig") as f:
            f.write(report)
        
        # Imprimir resumo no console
        console.print(f"[bold green]Relatório de tokens gerado:[/bold green] {output_path}")
        console.print(f"Total de tokens: {total_tokens:,}")
        console.print(f"Custo total estimado: ${total_cost:.4f}")
        
        if potential_savings > 0:
            console.print(f"[bold yellow]Economia potencial:[/bold yellow] ${potential_savings:.4f}")
    
    def display_summary(self):
        """
        Exibe um resumo do uso de tokens no console.
        """
        if not self.enable_token_analysis:
            console.print("[yellow]Análise de tokens está desabilitada.[/yellow]")
            return
        
        # Resolver a discrepância - usar o valor mais alto
        total_tokens = max(
            self.context["stats"]["tokens_used"],
            self.context["token_stats"]["total_tokens"]
        )
        
        # Atualizar ambos os valores para manter consistência
        self.context["stats"]["tokens_used"] = total_tokens
        self.context["token_stats"]["total_tokens"] = total_tokens
        
        total_cost = self.context["stats"]["estimated_cost"]
        
        # Criar tabela
        table = Table(title="Resumo de Uso de Tokens")
        
        # Adicionar colunas
        table.add_column("Modelo", style="cyan")
        table.add_column("Chamadas", justify="right")
        table.add_column("Tokens", justify="right")
        table.add_column("Custo (USD)", justify="right")
        
        # Adicionar linhas para cada modelo
        sorted_models = sorted(
            self.context["token_stats"]["models"].items(),
            key=lambda x: x[1]["total_tokens"],
            reverse=True
        )
        
        for model, stats in sorted_models:
            table.add_row(
                model,
                f"{stats['calls']}",
                f"{stats['total_tokens']:,}",
                f"${stats['cost']:.4f}"
            )
        
        # Adicionar linha de totais
        table.add_row(
            "[bold]Total[/bold]",
            f"[bold]{sum(m['calls'] for m in self.context['token_stats']['models'].values())}[/bold]",
            f"[bold]{total_tokens:,}[/bold]",
            f"[bold]${total_cost:.4f}[/bold]"
        )
        
        # Exibir no console
        console.print("\n")
        console.print(table)
        console.print("\n")
    
    def run(self):
        """
        Método principal do agente.
        
        Returns:
            dict: Contexto atualizado.
        """
        if not self.enable_token_analysis:
            console.print("[yellow]Análise de tokens está desabilitada.[/yellow]")
            return self.context
        
        # Resolver a discrepância antes de gerar o relatório
        # Verificar se token_stats foi atualizado de alguma forma
        if self.context["token_stats"]["total_tokens"] == 0 and self.context["stats"]["tokens_used"] > 0:
            # Criar uma entrada manual para os tokens registrados
            if "supervisor" not in self.context["token_stats"]["steps"]:
                self.context["token_stats"]["steps"]["supervisor"] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "cost": 0.0,
                    "calls": 0,
                    "models_used": {}
                }
                
            # Assumir que o modelo usado foi o supervisor
            model_key = self.context["config"]["models"]["supervisor"]
            if model_key == "local":
                model_key = "gpt-4"  # Fallback se não tiver modelo definido
                
            # Normalizar nome do modelo
            if "gpt-4" in model_key.lower():
                if "32k" in model_key.lower():
                    model_key = "gpt-4-32k"
                else:
                    model_key = "gpt-4"
            elif "gpt-3.5" in model_key.lower():
                if "16k" in model_key.lower():
                    model_key = "gpt-3.5-turbo-16k"
                else:
                    model_key = "gpt-3.5-turbo"
                    
            # Calcular custo aproximado
            tokens_used = self.context["stats"]["tokens_used"]
            # Assumir uma divisão típica de 70% input, 30% output
            input_tokens = int(tokens_used * 0.7)
            output_tokens = tokens_used - input_tokens
            
            input_cost = (input_tokens / 1000) * self.MODEL_COSTS[model_key]["input"]
            output_cost = (output_tokens / 1000) * self.MODEL_COSTS[model_key]["output"]
            total_cost = input_cost + output_cost
            
            # Atualizar estatísticas
            if model_key not in self.context["token_stats"]["models"]:
                self.context["token_stats"]["models"][model_key] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "cost": 0.0,
                    "calls": 0
                }
                
            self.context["token_stats"]["models"][model_key]["input_tokens"] += input_tokens
            self.context["token_stats"]["models"][model_key]["output_tokens"] += output_tokens
            self.context["token_stats"]["models"][model_key]["total_tokens"] += tokens_used
            self.context["token_stats"]["models"][model_key]["cost"] += total_cost
            self.context["token_stats"]["models"][model_key]["calls"] += 1
            
            # Atualizar estatísticas da etapa
            self.context["token_stats"]["steps"]["supervisor"]["input_tokens"] += input_tokens
            self.context["token_stats"]["steps"]["supervisor"]["output_tokens"] += output_tokens
            self.context["token_stats"]["steps"]["supervisor"]["total_tokens"] += tokens_used
            self.context["token_stats"]["steps"]["supervisor"]["cost"] += total_cost
            self.context["token_stats"]["steps"]["supervisor"]["calls"] += 1
            
            # Registrar uso de modelo específico nesta etapa
            if model_key not in self.context["token_stats"]["steps"]["supervisor"]["models_used"]:
                self.context["token_stats"]["steps"]["supervisor"]["models_used"][model_key] = {
                    "calls": 0,
                    "tokens": 0,
                    "cost": 0.0
                }
                
            self.context["token_stats"]["steps"]["supervisor"]["models_used"][model_key]["calls"] += 1
            self.context["token_stats"]["steps"]["supervisor"]["models_used"][model_key]["tokens"] += tokens_used
            self.context["token_stats"]["steps"]["supervisor"]["models_used"][model_key]["cost"] += total_cost
            
            # Atualizar totais
            self.context["token_stats"]["total_tokens"] = tokens_used
            self.context["token_stats"]["total_cost"] = total_cost
            self.context["stats"]["estimated_cost"] = total_cost
            
            if self.logger:
                self.logger.info(f"Resolvida discrepância de tokens: {tokens_used} tokens, custo: ${total_cost:.4f}")
        
        # Exibir resumo de tokens
        self.display_summary()
        
        # Gerar relatório detalhado
        report_path = os.path.join(self.context["directories"]["processed"], "token_usage_report.md")
        self.generate_token_report(report_path)
        
        return self.context
