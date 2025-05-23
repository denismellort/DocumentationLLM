"""
CLI entry point para DocumentationLLM.
Delega para o módulo main existente preservando compatibilidade.
"""
import sys
import os
import importlib.util
import importlib.resources
from pathlib import Path

def main():
    """Entry point do CLI docllm."""
    try:
        # Tentar usar importlib.resources para localizar o pacote
        try:
            import documentationllm
            package_path = Path(documentationllm.__file__).parent.parent
            print(f"Usando pacote instalado em: {package_path}")
            
            # Procurar main.py em locais possíveis relativos ao pacote
            possible_paths = [
                package_path / "src" / "main.py",  # Instalação editable/development
                package_path / "main.py",          # Instalação direta
            ]
            
            # Verificar cada caminho possível
            main_path = None
            for path in possible_paths:
                if path.exists():
                    main_path = path
                    break
                    
            if not main_path:
                # Se não encontrar no pacote instalado, tentar diretamente no diretório atual
                cwd = Path.cwd()
                alt_paths = [
                    cwd / "src" / "main.py",
                    cwd / "main.py"
                ]
                
                for path in alt_paths:
                    if path.exists():
                        main_path = path
                        break
        except (ImportError, AttributeError):
            # Fallback para o método antigo
            src_dir = Path(__file__).parent.parent.parent
            main_path = src_dir / "src" / "main.py"
            
            if not main_path.exists():
                # Tenta encontrar em outros locais comuns
                alt_path = src_dir / "main.py"
                if alt_path.exists():
                    main_path = alt_path
        
        # Verificar se encontramos o arquivo
        if not main_path or not main_path.exists():
            raise ImportError(f"Não foi possível encontrar o módulo main.py em nenhum local esperado")
            
        print(f"Usando main.py em: {main_path}")
            
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