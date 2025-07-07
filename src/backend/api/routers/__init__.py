"""
Inicialização dos routers da API ProtecAI Mini.
"""

from . import network
from . import protection
from . import simulation
from . import rl_agent
from . import visualization

__all__ = [
    "network",
    "protection",
    "simulation",
    "rl_agent",
    "visualization"
]
