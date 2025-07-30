"""
ProtecAI Mini - API FastAPI
Sistema de API para coordenação de proteção offshore com RL

Endpoints para integração com frontend React
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
from rl_protection_coordinator import ProtectionCoordinator

# Inicialização
app = FastAPI(
    title="ProtecAI Mini API",
    description="API para sistema de coordenação de proteção offshore com RL",
    version="1.0.0"
)

# CORS para permitir conexão com frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instância global do coordenador
coordinator = ProtectionCoordinator()

# Modelos Pydantic
class FaultSimulationRequest(BaseModel):
    bus: int
    fault_type: str
    severity: float

class RLTrainingRequest(BaseModel):
    episodes: int = 5
    scenarios: List[Dict] = []

# Endpoints da API

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {"message": "ProtecAI Mini API - Sistema de Proteção Offshore", "status": "operational"}

@app.get("/api/status")
async def get_system_status():
    """Status geral do sistema"""
    try:
        status = coordinator.get_system_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/zones")
async def get_protection_zones():
    """Retorna configuração das zonas de proteção"""
    try:
        zones_data = []
        for zone in coordinator.protection_zones:
            devices_data = []
            for device in zone.devices:
                devices_data.append({
                    "id": device.id,
                    "zone": device.zone,
                    "type": device.type,
                    "location": device.location,
                    "pickup_current": device.pickup_current,
                    "time_delay": device.time_delay,
                    "distance_km": device.distance_km,
                    "status": device.status
                })
            
            zones_data.append({
                "id": zone.id,
                "transformer": zone.transformer,
                "power_mva": zone.power_mva,
                "voltage_kv": zone.voltage_kv,
                "buses": zone.buses,
                "devices": devices_data
            })
        
        return zones_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/simulate-fault")
async def simulate_fault(request: FaultSimulationRequest):
    """Simula falta no sistema IEEE 14-Bus"""
    try:
        # Validações
        if not 1 <= request.bus <= 14:
            raise HTTPException(status_code=400, detail="Bus deve estar entre 1 e 14")
        
        if request.fault_type not in ['3ph', '2ph', '1ph', '2ph_ground']:
            raise HTTPException(status_code=400, detail="Tipo de falta inválido")
        
        if not 0.1 <= request.severity <= 1.0:
            raise HTTPException(status_code=400, detail="Severidade deve estar entre 0.1 e 1.0")
        
        # Executa simulação
        result = coordinator.simulate_fault(
            bus=request.bus,
            fault_type=request.fault_type,
            severity=request.severity
        )
        
        # Converte resultado para formato JSON
        return {
            "fault_location": result.fault_location,
            "fault_type": result.fault_type,
            "fault_current_a": result.fault_current_a,
            "affected_zone": result.affected_zone,
            "coordination_ok": result.coordination_ok,
            "device_responses": result.device_responses,
            "coordination_issues": result.coordination_issues,
            "normative_compliance": result.normative_compliance
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na simulação: {str(e)}")

@app.get("/api/rl/status")
async def get_rl_status():
    """Status do agente de aprendizado por reforço"""
    try:
        status = coordinator.get_rl_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rl/train")
async def train_rl_agent(request: RLTrainingRequest):
    """Treina o agente RL com cenários específicos"""
    try:
        # Cenários padrão se não especificados
        if not request.scenarios:
            request.scenarios = [
                {'bus': 4, 'fault_type': '3ph', 'severity': 0.8},
                {'bus': 7, 'fault_type': '2ph', 'severity': 0.6},
                {'bus': 14, 'fault_type': '1ph', 'severity': 0.5},
                {'bus': 9, 'fault_type': '2ph_ground', 'severity': 0.7},
                {'bus': 12, 'fault_type': '3ph', 'severity': 0.9}
            ]
        
        # Executa treinamento
        result = coordinator.train_rl_agent(
            episodes=request.episodes,
            scenarios=request.scenarios
        )
        
        return {
            "message": "Treinamento RL concluído com sucesso",
            "episodes_completed": result['episodes_completed'],
            "total_episodes": result['total_episodes'],
            "final_epsilon": result['final_epsilon'],
            "training_results": result['results']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no treinamento RL: {str(e)}")

@app.post("/api/rl/optimize")
async def optimize_protection_system(episodes: int = 100):
    """Otimização avançada do sistema de proteção usando RL"""
    try:
        print(f"🚀 Iniciando otimização avançada com {episodes} episódios...")
        
        # Executa otimização avançada
        result = coordinator.optimize_protection_with_rl(episodes=episodes)
        
        return {
            "message": "Otimização avançada concluída com sucesso",
            "episodes_completed": result['episodes_completed'],
            "best_coordination_score": result['best_coordination_score'],
            "final_epsilon": result['final_epsilon'],
            "total_adjustments": result['total_adjustments'],
            "improvement": result['improvement'],
            "optimization_history": result['optimization_history'][-10:],  # Últimos 10 episódios
            "summary": {
                "initial_score": result['optimization_history'][0]['coordination_score'] if result['optimization_history'] else 0,
                "final_score": result['best_coordination_score'],
                "improvement_percentage": (result['improvement'] / result['optimization_history'][0]['coordination_score'] * 100) if result['optimization_history'] and result['optimization_history'][0]['coordination_score'] > 0 else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na otimização avançada: {str(e)}")

@app.get("/api/rl/adjustment-log")
async def get_adjustment_log():
    """Histórico de ajustes realizados pelo RL"""
    try:
        if hasattr(coordinator, 'adjustment_log'):
            return {
                "total_adjustments": len(coordinator.adjustment_log),
                "recent_adjustments": coordinator.adjustment_log[-20:],  # Últimos 20
                "devices_adjusted": list(set([adj['device'] for adj in coordinator.adjustment_log])),
                "summary": {
                    "pickup_adjustments": len([adj for adj in coordinator.adjustment_log if adj['action_type'] in [0, 1]]),
                    "time_adjustments": len([adj for adj in coordinator.adjustment_log if adj['action_type'] in [2, 3]])
                }
            }
        else:
            return {
                "total_adjustments": 0,
                "recent_adjustments": [],
                "devices_adjusted": [],
                "summary": {"pickup_adjustments": 0, "time_adjustments": 0}
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter log de ajustes: {str(e)}")

@app.get("/api/devices")
async def get_all_devices():
    """Lista todos os dispositivos de proteção"""
    try:
        devices_data = []
        for device in coordinator.protection_devices:
            devices_data.append({
                "id": device.id,
                "zone": device.zone,
                "type": device.type,
                "location": device.location,
                "pickup_current": device.pickup_current,
                "time_delay": device.time_delay,
                "distance_km": device.distance_km,
                "coordination_margin": device.coordination_margin,
                "status": device.status
            })
        
        return devices_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check da API"""
    try:
        # Testa componentes críticos
        status = coordinator.get_system_status()
        rl_status = coordinator.get_rl_status()
        
        return {
            "api_status": "healthy",
            "coordinator_status": "operational",
            "rl_agent_status": rl_status['status'],
            "total_devices": status['total_devices'],
            "timestamp": "2025-07-30T16:32:00Z"
        }
    except Exception as e:
        return {
            "api_status": "unhealthy",
            "error": str(e),
            "timestamp": "2025-07-30T16:32:00Z"
        }

@app.get("/api/normative-compliance")
async def get_normative_info():
    """Informações sobre conformidade normativa"""
    return {
        "standards": {
            "IEEE_C37_112": {
                "description": "Proteção e coordenação de sistemas elétricos",
                "coordination_margin": "0.3s mínimo",
                "status": "implementado"
            },
            "IEC_61850": {
                "description": "Comunicação em subestações",
                "goose_timing": "4ms máximo",
                "status": "simulado"
            },
            "NBR_5410": {
                "description": "Instalações elétricas de baixa tensão",
                "selectivity": "DR coordenados",
                "status": "avaliado"
            },
            "API_RP_14C": {
                "description": "Sistemas elétricos offshore",
                "environment": "marinho",
                "status": "considerado"
            }
        },
        "disclaimer": "Sistema em desenvolvimento - validação oficial necessária"
    }

# Endpoint para demonstração ao vivo
@app.post("/api/demo/quick-test")
async def quick_demo():
    """Demonstração rápida do sistema completo"""
    try:
        results = []
        
        # Teste 1: Simulação de falta trifásica
        result1 = coordinator.simulate_fault(bus=4, fault_type='3ph', severity=0.8)
        results.append({
            "test": "Falta trifásica Bus 4",
            "coordination_ok": result1.coordination_ok,
            "fault_current": f"{result1.fault_current_a:.0f} A",
            "affected_zone": result1.affected_zone
        })
        
        # Teste 2: Treinamento RL rápido
        rl_result = coordinator.train_rl_agent(episodes=2)
        results.append({
            "test": "Treinamento RL",
            "episodes": rl_result['episodes_completed'],
            "status": "concluído"
        })
        
        # Teste 3: Status do sistema
        system_status = coordinator.get_system_status()
        results.append({
            "test": "Status do sistema",
            "devices": system_status['total_devices'],
            "zones": system_status['zones'],
            "health": system_status['system_health']
        })
        
        return {
            "demo_status": "sucesso",
            "timestamp": "2025-07-30T16:32:00Z",
            "tests_completed": len(results),
            "results": results,
            "message": "Sistema ProtecAI Mini funcionando corretamente!"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na demonstração: {str(e)}")

# Execução da API
if __name__ == "__main__":
    print("🚀 Iniciando ProtecAI Mini API...")
    print("📍 Acesse: http://localhost:8000")
    print("📖 Documentação: http://localhost:8000/docs")
    
    uvicorn.run(
        "api_protecai:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
