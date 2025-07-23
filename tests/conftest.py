"""
Configuração global para testes do ProtecAI Mini.
Fixtures e configurações compartilhadas entre todos os testes.
"""

import logging
from src.backend.api.main import app
import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from pathlib import Path
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, AsyncGenerator

# Adicionar src ao path para imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


# Configurações de teste
TEST_HOST = "http://testserver"
TEST_PORT = 8000


@pytest.fixture(scope="session")
def event_loop():
    """Criar event loop para testes async."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_client():
    """Cliente de teste síncrono para FastAPI."""
    with TestClient(app) as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Cliente de teste assíncrono para FastAPI."""
    from fastapi.testclient import TestClient

    # Usar TestClient para testes async também
    with TestClient(app) as sync_client:
        # Criar um wrapper async que usa o TestClient internamente
        class AsyncTestClient:
            def __init__(self, client):
                self._client = client

            async def post(self, url, **kwargs):
                return self._client.post(url, **kwargs)

            async def get(self, url, **kwargs):
                return self._client.get(url, **kwargs)

            async def put(self, url, **kwargs):
                return self._client.put(url, **kwargs)

            async def delete(self, url, **kwargs):
                return self._client.delete(url, **kwargs)

        yield AsyncTestClient(sync_client)


@pytest.fixture
def sample_voltage_measurements():
    """Dados de exemplo para medições de tensão."""
    return {
        "bus_1": {"magnitude": 1.06, "angle": 0.0},
        "bus_2": {"magnitude": 1.045, "angle": -4.98},
        "bus_3": {"magnitude": 1.01, "angle": -12.72},
        "bus_4": {"magnitude": 1.019, "angle": -10.33},
        "bus_5": {"magnitude": 1.02, "angle": -8.78},
        "bus_6": {"magnitude": 1.07, "angle": -14.22},
        "bus_7": {"magnitude": 1.062, "angle": -13.37},
        "bus_8": {"magnitude": 1.09, "angle": -13.36},
        "bus_9": {"magnitude": 1.056, "angle": -14.94},
        "bus_10": {"magnitude": 1.051, "angle": -15.1},
        "bus_11": {"magnitude": 1.057, "angle": -14.79},
        "bus_12": {"magnitude": 1.055, "angle": -15.07},
        "bus_13": {"magnitude": 1.05, "angle": -15.16},
        "bus_14": {"magnitude": 1.036, "angle": -16.04}
    }


@pytest.fixture
def sample_current_measurements():
    """Dados de exemplo para medições de corrente."""
    return {
        "line_1_2": {"magnitude": 1.568, "angle": -4.98},
        "line_1_5": {"magnitude": 0.757, "angle": -5.77},
        "line_2_3": {"magnitude": 0.728, "angle": -7.26},
        "line_2_4": {"magnitude": 0.563, "angle": -3.72},
        "line_2_5": {"magnitude": 0.416, "angle": -1.22},
        "line_3_4": {"magnitude": 0.234, "angle": 2.54},
        "line_4_5": {"magnitude": 0.107, "angle": 5.89},
        "line_6_11": {"magnitude": 0.075, "angle": -16.78},
        "line_6_12": {"magnitude": 0.078, "angle": -25.37},
        "line_6_13": {"magnitude": 0.177, "angle": -22.07},
        "line_7_8": {"magnitude": 0.000, "angle": 0.0},
        "line_7_9": {"magnitude": 0.281, "angle": -16.15},
        "line_9_10": {"magnitude": 0.052, "angle": -21.74},
        "line_9_14": {"magnitude": 0.094, "angle": -27.18},
        "line_10_11": {"magnitude": 0.038, "angle": -23.13},
        "line_12_13": {"magnitude": 0.016, "angle": -22.62},
        "line_13_14": {"magnitude": 0.056, "angle": -28.94}
    }


@pytest.fixture
def sample_sequence_of_events():
    """Sequência de eventos típica para teste."""
    base_time = datetime.now()
    return [
        {
            "timestamp": (base_time + timedelta(milliseconds=0)).isoformat(),
            "event": "fault_detected",
            "location": "line_6_13",
            "severity": "high"
        },
        {
            "timestamp": (base_time + timedelta(milliseconds=125)).isoformat(),
            "event": "relay_pickup",
            "relay_id": "51_6",
            "pickup_value": 1.25
        },
        {
            "timestamp": (base_time + timedelta(milliseconds=328)).isoformat(),
            "event": "relay_operated",
            "relay_id": "51_6",
            "operating_time": 0.203
        },
        {
            "timestamp": (base_time + timedelta(milliseconds=425)).isoformat(),
            "event": "breaker_opened",
            "breaker_id": "CB_6",
            "opening_time": 0.097
        },
        {
            "timestamp": (base_time + timedelta(milliseconds=500)).isoformat(),
            "event": "fault_cleared",
            "location": "line_6_13",
            "clearing_time": 0.5
        }
    ]


@pytest.fixture
def sample_protection_settings():
    """Configurações de proteção típicas para teste."""
    return {
        "relay_6": {
            "pickup": 1.2,
            "time_dial": 0.5,
            "curve": "very_inverse",
            "instantaneous": 8.0,
            "enabled": True
        },
        "relay_13": {
            "pickup": 1.15,
            "time_dial": 0.6,
            "curve": "very_inverse",
            "instantaneous": 7.5,
            "enabled": True
        },
        "relay_11": {
            "pickup": 1.1,
            "time_dial": 0.7,
            "curve": "extremely_inverse",
            "instantaneous": 7.0,
            "enabled": True
        },
        "relay_12": {
            "pickup": 1.25,
            "time_dial": 0.45,
            "curve": "very_inverse",
            "instantaneous": 8.5,
            "enabled": True
        }
    }


@pytest.fixture
def sample_fault_location_request(
    sample_voltage_measurements,
    sample_current_measurements,
    sample_sequence_of_events,
    sample_protection_settings
):
    """Requisição completa para análise de localização de faltas."""
    return {
        "voltage_measurements": sample_voltage_measurements,
        "current_measurements": sample_current_measurements,
        "sequence_of_events": sample_sequence_of_events,
        "protection_settings": sample_protection_settings,
        "fault_type": "phase_to_ground",
        "network_configuration": "normal"
    }


@pytest.fixture
def sample_ieee14_network():
    """Configuração da rede IEEE 14 barras."""
    return {
        "buses": {
            "bus_1": {"type": "swing", "voltage": 1.06, "angle": 0.0},
            "bus_2": {"type": "generator", "voltage": 1.045, "angle": -4.98},
            "bus_3": {"type": "generator", "voltage": 1.01, "angle": -12.72},
            "bus_6": {"type": "generator", "voltage": 1.07, "angle": -14.22},
            "bus_8": {"type": "generator", "voltage": 1.09, "angle": -13.36}
        },
        "lines": {
            "line_1_2": {"from_bus": 1, "to_bus": 2, "r": 0.01938, "x": 0.05917},
            "line_1_5": {"from_bus": 1, "to_bus": 5, "r": 0.05403, "x": 0.22304},
            "line_2_3": {"from_bus": 2, "to_bus": 3, "r": 0.04699, "x": 0.19797},
            "line_2_4": {"from_bus": 2, "to_bus": 4, "r": 0.05811, "x": 0.17632},
            "line_2_5": {"from_bus": 2, "to_bus": 5, "r": 0.05695, "x": 0.17388},
            "line_3_4": {"from_bus": 3, "to_bus": 4, "r": 0.06701, "x": 0.17103},
            "line_4_5": {"from_bus": 4, "to_bus": 5, "r": 0.01335, "x": 0.04211},
            "line_6_11": {"from_bus": 6, "to_bus": 11, "r": 0.09498, "x": 0.1989},
            "line_6_12": {"from_bus": 6, "to_bus": 12, "r": 0.12291, "x": 0.25581},
            "line_6_13": {"from_bus": 6, "to_bus": 13, "r": 0.06615, "x": 0.13027},
            "line_7_8": {"from_bus": 7, "to_bus": 8, "r": 0.0, "x": 0.17615},
            "line_7_9": {"from_bus": 7, "to_bus": 9, "r": 0.0, "x": 0.11001},
            "line_9_10": {"from_bus": 9, "to_bus": 10, "r": 0.03181, "x": 0.08450},
            "line_9_14": {"from_bus": 9, "to_bus": 14, "r": 0.12711, "x": 0.27038},
            "line_10_11": {"from_bus": 10, "to_bus": 11, "r": 0.08205, "x": 0.19207},
            "line_12_13": {"from_bus": 12, "to_bus": 13, "r": 0.22092, "x": 0.19988},
            "line_13_14": {"from_bus": 13, "to_bus": 14, "r": 0.17093, "x": 0.34802}
        },
        "loads": {
            "load_2": {"bus": 2, "p": 0.217, "q": 0.127},
            "load_3": {"bus": 3, "p": 0.942, "q": 0.19},
            "load_4": {"bus": 4, "p": 0.478, "q": -0.039},
            "load_5": {"bus": 5, "p": 0.076, "q": 0.016},
            "load_6": {"bus": 6, "p": 0.112, "q": 0.075},
            "load_9": {"bus": 9, "p": 0.295, "q": 0.166},
            "load_10": {"bus": 10, "p": 0.09, "q": 0.058},
            "load_11": {"bus": 11, "p": 0.035, "q": 0.018},
            "load_12": {"bus": 12, "p": 0.061, "q": 0.016},
            "load_13": {"bus": 13, "p": 0.135, "q": 0.058},
            "load_14": {"bus": 14, "p": 0.149, "q": 0.05}
        }
    }


@pytest.fixture
def sample_rl_training_config():
    """Configuração para treinamento RL."""
    return {
        "algorithm": "DQN",
        "learning_rate": 0.001,
        "batch_size": 32,
        "target_update_frequency": 100,
        "exploration_rate": 0.1,
        "exploration_decay": 0.995,
        "memory_size": 10000,
        "episodes": 1000,
        "max_steps_per_episode": 200,
        "reward_function": "coordination_quality",
        "state_features": [
            "voltage_magnitude",
            "current_magnitude",
            "pickup_settings",
            "coordination_margins"
        ]
    }


@pytest.fixture(scope="session")
def test_database():
    """Setup de banco de dados para testes."""
    # Para testes, podemos usar SQLite in-memory
    db_config = {
        "database_url": "sqlite:///./test_protecai.db",
        "echo": False,
        "pool_pre_ping": True
    }
    return db_config


@pytest.fixture
def mock_time_now():
    """Mock do tempo atual para testes consistentes."""
    return datetime(2025, 7, 15, 14, 30, 0)

# Fixtures para validação de resposta


@pytest.fixture
def expected_fault_location_response_structure():
    """Estrutura esperada da resposta de localização de faltas."""
    return {
        "fault_location": dict,
        "impact_zones": list,
        "protection_response": dict,
        "accuracy_confidence": float,
        "alternative_locations": list,
        "recommendations": list
    }


@pytest.fixture
def expected_ai_insights_response_structure():
    """Estrutura esperada da resposta de insights da IA."""
    return {
        "comparisons": list,
        "consolidation": dict,
        "business_impact": dict,
        "timestamp": str
    }


@pytest.fixture
def expected_executive_summary_response_structure():
    """Estrutura esperada do resumo executivo."""
    return {
        "period": str,
        "overall_status": str,
        "system_health_score": float,
        "coordination_quality_score": float,
        "safety_compliance_score": float,
        "operational_efficiency": float,
        "key_achievements": list,
        "critical_issues": list,
        "recommendations": list,
        "financial_impact": dict,
        "ai_contribution_summary": str,
        "next_period_priorities": list
    }


# Configuração de logging para testes
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Supressão de logs verbose durante testes
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
