"""
CLI entry point para DocumentationLLM.
Delega para o módulo main existente preservando compatibilidade.
"""
import sys
import os
import importlib.util
from pathlib import Path

def main():
    """Entry point do CLI docllm."""
    try:
        # Encontrar o caminho absoluto para o main.py
        src_dir = Path(__file__).parent.parent.parent
        main_path = src_dir / "src" / "main.py"
        
        if not main_path.exists():
            # Tenta encontrar em outros locais comuns
            alt_path = src_dir / "main.py"
            if alt_path.exists():
                main_path = alt_path
        
        # Importar usando a localização do arquivo
        spec = importlib.util.spec_from_file_location("main", main_path)
        if not spec:
            raise ImportError(f"Não foi possível encontrar o módulo em {main_path}")
        
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)
        
        # Executar a função main
        return main_module.main()
        
    except Exception as e:
        print(f"Erro ao executar DocumentationLLM: {e}")
        print(f"Diretório base: {Path(__file__).parent.parent.parent}")
        print(f"Caminho procurado: {main_path if 'main_path' in locals() else 'desconhecido'}")
        print(f"sys.path: {sys.path[:3]}...")  # mostra primeiros 3 itens
        return 1

if __name__ == "__main__":
    sys.exit(main()) 