"""
CLI entry point para DocumentationLLM.
Delega para o módulo main existente preservando compatibilidade.
"""
import sys
import os
from pathlib import Path

def main():
    """Entry point do CLI docllm."""
    # Adiciona src/ ao PYTHONPATH para permitir imports do main.py
    src_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(src_dir))
    
    # Importa e executa a função main original
    try:
        from main import main as original_main
        return original_main()
    except ImportError as e:
        print(f"Erro ao importar módulo main: {e}")
        print(f"Diretório src: {src_dir}")
        print(f"sys.path: {sys.path[:3]}...")  # mostra primeiros 3 itens
        return 1

if __name__ == "__main__":
    sys.exit(main()) 