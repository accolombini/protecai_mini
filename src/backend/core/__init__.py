"""
ProtecAI Mini - Core Module
Módulo principal do sistema de proteção elétrica
"""

from .protecao_eletrica import ProtecaoEletrica, criar_sistema_protecao

__all__ = [
    'ProtecaoEletrica',
    'criar_sistema_protecao'
]
