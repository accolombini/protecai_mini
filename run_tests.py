# run_tests.py
"""
Executa todos os testes do projeto, garantindo que a raiz esteja no PYTHONPATH.
"""

import os
import sys
import pytest

# Garante que a raiz do projeto esteja no PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    # Executa os testes na pasta tests/
    exit(pytest.main([
        "tests",            # pasta com os testes
        "--maxfail=1",      # para facilitar o debug
        "--disable-warnings",
        "-q"                # saída silenciosa e limpa
    ]))
