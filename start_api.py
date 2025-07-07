#!/usr/bin/env python3
"""
Script para iniciar a API ProtecAI Mini.
"""

import uvicorn
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Inicia a API ProtecAI Mini."""
    print("🔋 Iniciando API ProtecAI Mini")
    print("=" * 40)
    print("📡 Endereço: http://localhost:8000")
    print("📚 Documentação: http://localhost:8000/docs")
    print("🔄 Documentação alternativa: http://localhost:8000/redoc")
    print("=" * 40)

    # Configuração do servidor
    config = {
        "app": "src.backend.api.main:app",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": True,
        "reload_dirs": ["src"],
        "log_level": "info"
    }

    # Iniciar servidor
    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
