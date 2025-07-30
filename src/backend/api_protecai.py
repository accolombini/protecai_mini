#!/usr/bin/env python3
"""
API FastAPI para ProtecAI Mini - Sistema de Coordenação de Proteção
Conecta frontend React com backend RL de coordenação
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
import json
from datetime import datetime
import logging

# Import do coordenador RL
try:
    from rl_protection_coordinator import ProtectionCoordinator, BasicRLAgent
except ImportError:
    # Fallback se módulo não encontrado
    print("AVISO: Módulo RL não encontrado, usando mock")
    ProtectionCoordinator = None
    BasicRLAgent = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialização FastAPI
app = FastAPI(
    title="ProtecAI Mini API",
    description="API para coordenação de proteção IEEE 14-Bus com RL",
    version="1.0.0"
)

# CORS para desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class FaultSimulationRequest(BaseModel):
    bus: int
    fault_type: str  # 3ph, 2ph, 1ph, 2ph_ground
    severity: float  # 0.1 to 1.0

class FaultSimulationResponse(BaseModel):
    fault_location: str
    fault_type: str
    fault_current_a: float
    affected_zone: str
    coordination_ok: bool
    device_responses: List[Dict]
    coordination_issues: List[Dict]
    analysis_time: str
    normative_compliance: Dict

class SystemStatus(BaseModel):
    total_devices: int
    active_devices: int
    zones: int
    system_health: str
    last_update: str
    rl_agent_status: str
    uptime: str

class ProtectionDevice(BaseModel):
    id: str
    zone: str
    type: str
    location: str
    pickup_current: float
    time_delay: float
    distance_km: float
    status: str

class RLTrainingRequest(BaseModel):
    episodes: int
    scenarios: List[Dict]

# Instância global do coordenador
coordinator_instance = None
rl_agent_instance = None

def get_coordinator():
    """Obtém instância do coordenador, criando se necessário"""
    global coordinator_instance, rl_agent_instance
    
    if coordinator_instance is None:
        if ProtectionCoordinator is not None:
            coordinator_instance = ProtectionCoordinator()
            rl_agent_instance = BasicRLAgent(coordinator_instance)
            logger.info("Coordenador RL inicializado com sucesso")
        else:
            logger.warning("Coordenador RL não disponível - usando mock")
            return None
    
    return coordinator_instance

def get_rl_agent():
    """Obtém instância do agente RL"""
    global rl_agent_instance
    get_coordinator()  # Garante inicialização
    return rl_agent_instance

# Mock data para quando RL não está disponível
MOCK_ZONES = [
    {
        "id": "Z1",
        "transformer": "TR1 - Bus 0→4",
        "power_mva": 25,
        "voltage_kv": 13.8,
        "buses": [0, 4, 5, 6, 7, 9],
        "devices": [
            {
                "id": "RELE_87T_TR1",
                "zone": "Z1",
                "type": "87T",
                "location": "TR1",
                "pickup_current": 0.15,
                "time_delay": 0.02,
                "distance_km": 0,
                "status": "active"
            },
            {
                "id": "RELE_50_51_L4_5",
                "zone": "Z1", 
                "type": "50/51",
                "location": "Bus 4-5",
                "pickup_current": 1.25,
                "time_delay": 0.5,
                "distance_km": 2.5,
                "status": "active"
            },
            {
                "id": "RELE_67_B4",
                "zone": "Z1",
                "type": "67", 
                "location": "Bus 4",
                "pickup_current": 1.1,
                "time_delay": 0.8,
                "distance_km": 0,
                "status": "active"
            },
            {
                "id": "RELE_27_59_B7",
                "zone": "Z1",
                "type": "27/59",
                "location": "Bus 7", 
                "pickup_current": 0.85,
                "time_delay": 1.0,
                "distance_km": 3.2,
                "status": "active"
            }
        ]
    },
    {
        "id": "Z2",
        "transformer": "TR2 - Bus 1→5", 
        "power_mva": 25,
        "voltage_kv": 13.8,
        "buses": [1, 5, 8, 10, 11, 12, 13, 14],
        "devices": [
            {
                "id": "RELE_87T_TR2",
                "zone": "Z2",
                "type": "87T", 
                "location": "TR2",
                "pickup_current": 0.15,
                "time_delay": 0.02,
                "distance_km": 0,
                "status": "active"
            },
            {
                "id": "RELE_50_51_L5_6",
                "zone": "Z2",
                "type": "50/51",
                "location": "Bus 5-6",
                "pickup_current": 1.3,
                "time_delay": 0.6, 
                "distance_km": 1.8,
                "status": "active"
            },
            {
                "id": "RELE_67_B5",
                "zone": "Z2",
                "type": "67",
                "location": "Bus 5",
                "pickup_current": 1.15,
                "time_delay": 0.9,
                "distance_km": 0,
                "status": "active"
            },
            {
                "id": "RELE_27_59_B14",
                "zone": "Z2",
                "type": "27/59",
                "location": "Bus 14",
                "pickup_current": 0.8,
                "time_delay": 1.2,
                "distance_km": 4.1,
                "status": "active"
            }
        ]
    }
]

# Rotas da API

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "ProtecAI Mini API",
        "version": "1.0.0",
        "status": "operational",
        "coordinator_available": get_coordinator() is not None
    }

@app.get("/api/status", response_model=SystemStatus)
async def get_system_status():
    """Obtém status atual do sistema"""
    coordinator = get_coordinator()
    
    if coordinator is not None:
        status = coordinator.get_protection_status()
        return SystemStatus(
            total_devices=status['total_devices'],
            active_devices=status['active_devices'],
            zones=status['zones'],
            system_health=status['system_health'],
            last_update=status['last_update'],
            rl_agent_status="operational",
            uptime="2h 45m"
        )
    else:
        # Mock response
        return SystemStatus(
            total_devices=8,
            active_devices=8,
            zones=2,
            system_health="healthy",
            last_update=datetime.now().isoformat(),
            rl_agent_status="mock_mode",
            uptime="2h 45m"
        )

@app.get("/api/zones")
async def get_protection_zones():
    """Obtém configuração das zonas de proteção"""
    coordinator = get_coordinator()
    
    if coordinator is not None:
        zones_data = []
        for zone in coordinator.zones:
            zone_dict = {
                "id": zone.id,
                "transformer": zone.transformer,
                "power_mva": zone.power_mva,
                "voltage_kv": zone.voltage_kv,
                "buses": zone.buses,
                "devices": [
                    {
                        "id": device.id,
                        "zone": device.zone,
                        "type": device.type,
                        "location": device.location,
                        "pickup_current": device.pickup_current,
                        "time_delay": device.time_delay,
                        "distance_km": device.distance_km,
                        "status": device.status
                    }
                    for device in zone.devices
                ]
            }
            zones_data.append(zone_dict)
        return zones_data
    else:
        return MOCK_ZONES

@app.post("/api/simulate-fault", response_model=FaultSimulationResponse)
async def simulate_fault(request: FaultSimulationRequest):
    """Simula falta no sistema"""
    coordinator = get_coordinator()
    
    # Validações
    if not (1 <= request.bus <= 14):
        raise HTTPException(status_code=400, detail="Bus deve estar entre 1 e 14")
    
    if request.fault_type not in ['3ph', '2ph', '1ph', '2ph_ground']:
        raise HTTPException(status_code=400, detail="Tipo de falta inválido")
    
    if not (0.1 <= request.severity <= 1.0):
        raise HTTPException(status_code=400, detail="Severidade deve estar entre 0.1 e 1.0")
    
    if coordinator is not None:
        try:
            result = coordinator.simulate_fault(
                request.bus, 
                request.fault_type, 
                request.severity
            )
            
            return FaultSimulationResponse(**result)
            
        except Exception as e:
            logger.error(f"Erro na simulação: {e}")
            raise HTTPException(status_code=500, detail=f"Erro na simulação: {str(e)}")
    else:
        # Mock response para desenvolvimento
        mock_result = {
            "fault_location": f"Bus {request.bus}",
            "fault_type": request.fault_type,
            "fault_current_a": 2500.0 * request.severity,
            "affected_zone": "Z1" if request.bus <= 7 else "Z2",
            "coordination_ok": request.severity < 0.7,
            "device_responses": [
                {
                    "device_id": "RELE_87T_TR1",
                    "type": "87T",
                    "should_operate": request.severity > 0.3,
                    "operating_time": 0.02,
                    "pickup_current": 0.15,
                    "coordination_ok": True
                },
                {
                    "device_id": "RELE_50_51_L4_5", 
                    "type": "50/51",
                    "should_operate": request.severity > 0.4,
                    "operating_time": 0.5,
                    "pickup_current": 1.25,
                    "coordination_ok": True
                }
            ],
            "coordination_issues": [] if request.severity < 0.7 else [
                {
                    "device1": "RELE_50_51_L4_5",
                    "device2": "RELE_67_B4", 
                    "margin": 0.2,
                    "required": 0.3
                }
            ],
            "analysis_time": datetime.now().isoformat(),
            "normative_compliance": {
                "IEEE_C37_112": {
                    "coordination_margins": request.severity < 0.7,
                    "selectivity": True,
                    "issues": []
                },
                "IEC_61850": {
                    "communication_timing": True,
                    "goose_performance": True,
                    "issues": []
                },
                "NBR_5410": {
                    "protection_people": True,
                    "selectivity_dr": True,
                    "issues": []
                },
                "API_RP_14C": {
                    "offshore_environment": True,
                    "redundancy": False,
                    "fail_safe": True,
                    "issues": ["Sistema em desenvolvimento"]
                }
            }
        }
        
        return FaultSimulationResponse(**mock_result)

@app.post("/api/rl/train")
async def train_rl_agent(request: RLTrainingRequest):
    """Treina agente RL com cenários específicos"""
    rl_agent = get_rl_agent()
    
    if rl_agent is not None:
        try:
            # Converte cenários para formato esperado
            scenarios = []
            for scenario in request.scenarios:
                scenarios.append((
                    scenario.get('bus', 4),
                    scenario.get('fault_type', '3ph'),
                    scenario.get('severity', 0.5)
                ))
            
            # Treina episódios
            training_results = []
            for episode in range(request.episodes):
                avg_reward = rl_agent.train_episode(scenarios)
                training_results.append({
                    "episode": episode + 1,
                    "avg_reward": avg_reward,
                    "epsilon": rl_agent.epsilon
                })
            
            return {
                "status": "success",
                "episodes_trained": request.episodes,
                "final_epsilon": rl_agent.epsilon,
                "total_episodes": rl_agent.episodes,
                "training_results": training_results
            }
            
        except Exception as e:
            logger.error(f"Erro no treinamento RL: {e}")
            raise HTTPException(status_code=500, detail=f"Erro no treinamento: {str(e)}")
    else:
        # Mock response
        return {
            "status": "mock_mode",
            "episodes_trained": request.episodes,
            "final_epsilon": 0.1,
            "total_episodes": request.episodes,
            "training_results": [
                {
                    "episode": i + 1,
                    "avg_reward": 10.0 - i * 0.5,
                    "epsilon": 0.1 - i * 0.01
                }
                for i in range(request.episodes)
            ]
        }

@app.get("/api/rl/status")
async def get_rl_status():
    """Obtém status do agente RL"""
    rl_agent = get_rl_agent()
    
    if rl_agent is not None:
        state = rl_agent.get_state()
        return {
            "status": "operational",
            "episodes": rl_agent.episodes,
            "max_episodes": rl_agent.max_episodes,
            "learning_rate": rl_agent.learning_rate,
            "epsilon": rl_agent.epsilon,
            "state_size": len(state),
            "action_space_size": rl_agent.get_action_space_size()
        }
    else:
        return {
            "status": "mock_mode",
            "episodes": 150,
            "max_episodes": 1000,
            "learning_rate": 0.001,
            "epsilon": 0.08,
            "state_size": 16,
            "action_space_size": 16
        }

@app.get("/api/normative-compliance")
async def get_normative_compliance():
    """Obtém status de conformidade normativa"""
    return {
        "IEEE_C37_112": {
            "status": "in_development",
            "coordination_margins": "pending_validation",
            "selectivity": "pending_validation",
            "issues": ["Requer validação com estudos de coordenação reais"]
        },
        "IEC_61850": {
            "status": "not_implemented",
            "goose_messages": "not_configured",
            "mms_protocol": "not_active",
            "issues": ["Protocolo de comunicação não implementado"]
        },
        "NBR_5410": {
            "status": "partial_compliance",
            "protection_people": "to_verify",
            "dr_coordination": "to_calculate",
            "issues": ["Coordenação com dispositivos DR pendente"]
        },
        "API_RP_14C": {
            "status": "not_certified",
            "offshore_environment": "to_validate",
            "redundancy": "not_implemented",
            "fail_safe": "basic_implementation",
            "issues": ["Certificação offshore pendente", "Redundância não implementada"]
        },
        "overall_status": "development_phase",
        "next_steps": [
            "Implementar protocolo IEC 61850",
            "Validar coordenação IEEE C37.112",
            "Certificar para ambiente offshore API RP 14C",
            "Implementar redundância e fail-safe"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Iniciando ProtecAI Mini API...")
    
    # Inicializa coordenador na startup
    coordinator = get_coordinator()
    if coordinator:
        logger.info("Sistema de coordenação inicializado com sucesso")
    else:
        logger.warning("Executando em modo mock - coordenador RL não disponível")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        reload=True
    )
