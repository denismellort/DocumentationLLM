"""
CLI entry point para DocumentationLLM.
Executa diretamente documentationllm.main:main.
"""
import sys

def main():
    try:
        from documentationllm.main import main as real_main
        return real_main()
    except Exception as e:
        print(f"Erro ao executar DocumentationLLM: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 