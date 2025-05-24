"""
CLI entry point para DocumentationLLM.
"""
import sys
from documentationllm.main import main

def cli():
    """Entry point para o comando docllm."""
    sys.exit(main())

if __name__ == "__main__":
    cli() 