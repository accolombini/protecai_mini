"""
Router para treinamento e consulta do agente de Reinforcement Learning.
Endpoints para configuração, treinamento e aplicação do agente RL.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import json
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
import subprocess
import os

router = APIRouter(tags=["reinforcement_learning"])

# Modelos Pydantic para validação


class RLTrainingConfig(BaseModel):
    episodes: int = 1000
    learning_rate: float = 0.001
    discount_factor: float = 0.95
    epsilon_start: float = 1.0
    epsilon_end: float = 0.1
    epsilon_decay: float = 0.995
    reward_weights: Optional[Dict[str, float]] = {
        "coordination": 0.4,
        "response_time": 0.3,
        "selectivity": 0.3
    }
    network_architecture: Optional[Dict[str, Any]] = {
        "hidden_layers": [128, 64],
        "activation": "relu",
        "optimizer": "adam"
    }


class RLAction(BaseModel):
    action_type: str  # "adjust_pickup", "adjust_time", "enable_disable"
    device_id: str
    parameter: str
    value: float


class RLState(BaseModel):
    fault_current: float
    fault_location: int
    system_loading: float
    protection_settings: Dict[str, Any]
    network_topology: Dict[str, Any]


class RLTrainingResult(BaseModel):
    model_config = {"protected_namespaces": ()}

    training_id: str
    status: str
    episodes_completed: int
    total_episodes: int
    current_reward: float
    average_reward: float
    best_reward: float
    convergence_status: str
    saved_model_path: Optional[str] = None


# Armazenamento em memória dos treinamentos
training_storage = {}
model_storage = {}

# Caminhos
RL_SCRIPT_PATH = Path("simuladores/power_sim/rl_protection_agent.py")
MODEL_SAVE_PATH = Path("simuladores/power_sim/models")
DATA_PATH = Path("simuladores/power_sim/data/ieee14_protecao.json")


def ensure_model_directory():
    """Garante que o diretório de modelos existe."""
    MODEL_SAVE_PATH.mkdir(parents=True, exist_ok=True)


async def run_rl_training(training_id: str, config: RLTrainingConfig):
    """Executa treinamento RL em background."""
    try:
        # Atualizar status
        training_storage[training_id]["status"] = "running"
        training_storage[training_id]["start_time"] = datetime.now()

        ensure_model_directory()

        # Preparar configuração para o script
        training_config = {
            "episodes": config.episodes,
            "learning_rate": config.learning_rate,
            "discount_factor": config.discount_factor,
            "epsilon_start": config.epsilon_start,
            "epsilon_end": config.epsilon_end,
            "epsilon_decay": config.epsilon_decay,
            "reward_weights": config.reward_weights,
            "network_architecture": config.network_architecture,
            "output_model_path": str(MODEL_SAVE_PATH / f"model_{training_id}.pkl")
        }

        # Salvar configuração
        config_path = MODEL_SAVE_PATH / f"config_{training_id}.json"
        with open(config_path, 'w') as f:
            json.dump(training_config, f, indent=2)

        # Executar script de treinamento
        cmd = [
            "python", str(RL_SCRIPT_PATH),
            "--config", str(config_path),
            "--training_id", training_id
        ]

        # Simular treinamento (substituir por execução real)
        await simulate_training(training_id, config)

        # Atualizar status final
        training_storage[training_id]["status"] = "completed"
        training_storage[training_id]["end_time"] = datetime.now()

    except Exception as e:
        training_storage[training_id]["status"] = "failed"
        training_storage[training_id]["error_message"] = str(e)
        training_storage[training_id]["end_time"] = datetime.now()


async def simulate_training(training_id: str, config: RLTrainingConfig):
    """Simula processo de treinamento RL."""
    episodes = config.episodes

    # Inicializar métricas
    training_storage[training_id]["episodes_completed"] = 0
    training_storage[training_id]["current_reward"] = 0.0
    training_storage[training_id]["rewards_history"] = []
    training_storage[training_id]["loss_history"] = []

    # Simular episódios de treinamento
    for episode in range(episodes):
        # Simular progresso
        await asyncio.sleep(0.01)  # Simular tempo de treinamento

        # Simular métricas de treinamento
        base_reward = 50.0
        noise = (episode / episodes) * 30.0  # Melhoria ao longo do tempo
        episode_reward = base_reward + noise + ((-1) ** episode) * 5.0

        training_storage[training_id]["episodes_completed"] = episode + 1
        training_storage[training_id]["current_reward"] = episode_reward
        training_storage[training_id]["rewards_history"].append(episode_reward)

        # Simular perda
        loss = max(0.1, 2.0 - (episode / episodes) * 1.8)
        training_storage[training_id]["loss_history"].append(loss)

        # Calcular métricas
        rewards = training_storage[training_id]["rewards_history"]
        training_storage[training_id]["average_reward"] = sum(
            rewards) / len(rewards)
        training_storage[training_id]["best_reward"] = max(rewards)

        # Verificar convergência
        if episode > 100:
            recent_rewards = rewards[-50:]
            if len(set([round(r, 1) for r in recent_rewards])) <= 3:
                training_storage[training_id]["convergence_status"] = "converged"
            else:
                training_storage[training_id]["convergence_status"] = "training"

        # Parar se convergiu
        if training_storage[training_id].get("convergence_status") == "converged":
            break

    # Salvar modelo simulado
    model_path = MODEL_SAVE_PATH / f"model_{training_id}.json"
    model_data = {
        "training_id": training_id,
        "episodes": training_storage[training_id]["episodes_completed"],
        "final_reward": training_storage[training_id]["current_reward"],
        "config": config.dict(),
        "trained_at": datetime.now().isoformat()
    }

    with open(model_path, 'w') as f:
        json.dump(model_data, f, indent=2)

    training_storage[training_id]["saved_model_path"] = str(model_path)

    # Registrar modelo
    model_storage[training_id] = {
        "id": training_id,
        "name": f"RL_Model_{training_id[:8]}",
        "path": str(model_path),
        "created_at": datetime.now(),
        "performance": {
            "episodes": training_storage[training_id]["episodes_completed"],
            "final_reward": training_storage[training_id]["current_reward"],
            "average_reward": training_storage[training_id]["average_reward"],
            "best_reward": training_storage[training_id]["best_reward"]
        }
    }


@router.post("/train")
async def start_training(background_tasks: BackgroundTasks, config: RLTrainingConfig):
    """Inicia treinamento do agente RL."""
    training_id = str(uuid.uuid4())

    # Criar registro do treinamento
    training_record = {
        "id": training_id,
        "status": "queued",
        "config": config.dict(),
        "created_at": datetime.now(),
        "start_time": None,
        "end_time": None,
        "episodes_completed": 0,
        "total_episodes": config.episodes,
        "current_reward": 0.0,
        "average_reward": 0.0,
        "best_reward": 0.0,
        "convergence_status": "not_started",
        "saved_model_path": None,
        "error_message": None
    }

    training_storage[training_id] = training_record

    # Executar treinamento em background
    background_tasks.add_task(run_rl_training, training_id, config)

    return {
        "training_id": training_id,
        "status": "queued",
        "message": "Treinamento iniciado com sucesso"
    }


@router.get("/training/status/{training_id}")
async def get_training_status(training_id: str):
    """Obtém status do treinamento."""
    if training_id not in training_storage:
        raise HTTPException(
            status_code=404, detail="Treinamento não encontrado")

    training = training_storage[training_id]

    return {
        "id": training["id"],
        "status": training["status"],
        "episodes_completed": training["episodes_completed"],
        "total_episodes": training["total_episodes"],
        "current_reward": training["current_reward"],
        "average_reward": training["average_reward"],
        "best_reward": training["best_reward"],
        "convergence_status": training["convergence_status"],
        "progress": (training["episodes_completed"] / training["total_episodes"]) * 100,
        "error_message": training.get("error_message")
    }


@router.get("/training/progress/{training_id}")
async def get_training_progress(training_id: str):
    """Obtém progresso detalhado do treinamento."""
    if training_id not in training_storage:
        raise HTTPException(
            status_code=404, detail="Treinamento não encontrado")

    training = training_storage[training_id]

    return {
        "id": training["id"],
        "status": training["status"],
        "episodes_completed": training["episodes_completed"],
        "rewards_history": training.get("rewards_history", []),
        "loss_history": training.get("loss_history", []),
        "current_reward": training["current_reward"],
        "average_reward": training["average_reward"],
        "best_reward": training["best_reward"],
        "convergence_status": training["convergence_status"]
    }


@router.get("/training/list")
async def list_trainings():
    """Lista todos os treinamentos."""
    trainings = []
    for train_id, train_data in training_storage.items():
        trainings.append({
            "id": train_id,
            "status": train_data["status"],
            "created_at": train_data["created_at"],
            "episodes_completed": train_data["episodes_completed"],
            "total_episodes": train_data["total_episodes"],
            "best_reward": train_data["best_reward"],
            "convergence_status": train_data["convergence_status"]
        })

    return {
        "trainings": trainings,
        "total": len(trainings)
    }


@router.delete("/training/{training_id}")
async def delete_training(training_id: str):
    """Remove um treinamento."""
    if training_id not in training_storage:
        raise HTTPException(
            status_code=404, detail="Treinamento não encontrado")

    # Remover arquivos do modelo se existirem
    if training_storage[training_id].get("saved_model_path"):
        try:
            model_path = Path(
                training_storage[training_id]["saved_model_path"])
            if model_path.exists():
                model_path.unlink()
        except:
            pass

    del training_storage[training_id]

    # Remover do storage de modelos também
    if training_id in model_storage:
        del model_storage[training_id]

    return {"message": "Treinamento removido com sucesso"}


@router.get("/models")
async def list_models():
    """Lista todos os modelos treinados."""
    models = []
    for model_id, model_data in model_storage.items():
        models.append({
            "id": model_id,
            "name": model_data["name"],
            "created_at": model_data["created_at"],
            "performance": model_data["performance"]
        })

    return {
        "models": models,
        "total": len(models)
    }


@router.get("/models/{model_id}")
async def get_model_details(model_id: str):
    """Obtém detalhes de um modelo específico."""
    if model_id not in model_storage:
        raise HTTPException(status_code=404, detail="Modelo não encontrado")

    return model_storage[model_id]


@router.post("/models/{model_id}/predict")
async def predict_with_model(model_id: str, state: RLState):
    """Faz predição usando um modelo treinado."""
    if model_id not in model_storage:
        raise HTTPException(status_code=404, detail="Modelo não encontrado")

    model_data = model_storage[model_id]

    # Simular predição
    await asyncio.sleep(0.1)  # Simular tempo de processamento

    # Análise do estado
    fault_severity = "high" if state.fault_current > 5000 else "medium" if state.fault_current > 2000 else "low"

    # Gerar ações recomendadas
    actions = []

    # Ação para ajuste de pickup
    if fault_severity == "high":
        actions.append({
            "action_type": "adjust_pickup",
            "device_id": f"relay_{state.fault_location}",
            "parameter": "pickup_current",
            "value": min(state.fault_current * 0.8, 1000),
            "confidence": 0.95
        })

    # Ação para ajuste de tempo
    if state.system_loading > 0.8:
        actions.append({
            "action_type": "adjust_time",
            "device_id": f"relay_{state.fault_location}",
            "parameter": "time_delay",
            "value": 0.1,
            "confidence": 0.87
        })

    # Análise de coordenação
    coordination_score = 0.9 if fault_severity == "low" else 0.7

    return {
        "model_id": model_id,
        "prediction": {
            "recommended_actions": actions,
            "coordination_score": coordination_score,
            "fault_severity": fault_severity,
            "system_stability": "stable" if state.system_loading < 0.9 else "critical",
            "confidence": 0.88
        },
        "state_analysis": {
            "fault_current": state.fault_current,
            "fault_location": state.fault_location,
            "system_loading": state.system_loading,
            "critical_elements": [state.fault_location] if fault_severity == "high" else []
        }
    }


@router.post("/models/{model_id}/optimize")
async def optimize_protection_settings(model_id: str, optimization_targets: Dict[str, float]):
    """Otimiza configurações de proteção usando o modelo."""
    if model_id not in model_storage:
        raise HTTPException(status_code=404, detail="Modelo não encontrado")

    # Simular otimização
    await asyncio.sleep(0.5)

    # Carregar dados da rede
    try:
        with open(DATA_PATH, 'r') as f:
            network_data = json.load(f)
    except:
        raise HTTPException(
            status_code=500, detail="Erro ao carregar dados da rede")

    # Gerar configurações otimizadas
    optimized_settings = {}

    devices = network_data.get("protection_devices", {})
    for device_type, device_list in devices.items():
        if device_type == "reles":
            for relay in device_list:
                relay_id = relay.get("id", "")

                # Otimizar pickup
                current_pickup = relay.get("pickup_current", 100)
                target_selectivity = optimization_targets.get(
                    "selectivity", 0.9)
                optimized_pickup = current_pickup * \
                    (1 + (target_selectivity - 0.5) * 0.2)

                # Otimizar tempo
                current_time = relay.get("time_delay", 0.5)
                target_speed = optimization_targets.get("response_time", 0.8)
                optimized_time = current_time * \
                    (1 - (target_speed - 0.5) * 0.3)

                optimized_settings[relay_id] = {
                    "pickup_current": round(optimized_pickup, 2),
                    "time_delay": round(max(0.05, optimized_time), 3),
                    "improvement_score": 0.85 + (target_selectivity * 0.15)
                }

    return {
        "model_id": model_id,
        "optimization_targets": optimization_targets,
        "optimized_settings": optimized_settings,
        "expected_improvements": {
            "coordination_score": 0.92,
            "selectivity": optimization_targets.get("selectivity", 0.9),
            "response_time": optimization_targets.get("response_time", 0.8),
            "overall_performance": 0.88
        }
    }


@router.post("/models/{model_id}/apply")
async def apply_optimized_settings(model_id: str, settings: Dict[str, Dict[str, float]]):
    """Aplica configurações otimizadas na rede."""
    if model_id not in model_storage:
        raise HTTPException(status_code=404, detail="Modelo não encontrado")

    try:
        # Carregar dados da rede
        with open(DATA_PATH, 'r') as f:
            network_data = json.load(f)

        # Aplicar configurações
        devices = network_data.get("protection_devices", {})
        applied_settings = {}

        for device_type, device_list in devices.items():
            if device_type == "reles":
                for relay in device_list:
                    relay_id = relay.get("id", "")
                    if relay_id in settings:
                        new_settings = settings[relay_id]

                        # Aplicar novos valores
                        relay.update(new_settings)
                        applied_settings[relay_id] = new_settings

        # Salvar dados atualizados
        with open(DATA_PATH, 'w') as f:
            json.dump(network_data, f, indent=2)

        return {
            "model_id": model_id,
            "applied_settings": applied_settings,
            "total_devices_updated": len(applied_settings),
            "status": "success",
            "message": "Configurações aplicadas com sucesso"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao aplicar configurações: {str(e)}")


@router.get("/performance/metrics")
async def get_performance_metrics():
    """Obtém métricas de performance dos modelos."""
    metrics = {
        "total_models": len(model_storage),
        "total_trainings": len(training_storage),
        "successful_trainings": sum(1 for t in training_storage.values() if t["status"] == "completed"),
        "failed_trainings": sum(1 for t in training_storage.values() if t["status"] == "failed"),
        "average_episodes": sum(t["episodes_completed"] for t in training_storage.values()) / len(training_storage) if training_storage else 0,
        "best_overall_reward": max((t["best_reward"] for t in training_storage.values()), default=0)
    }

    return metrics


@router.get("/config/default")
async def get_default_config():
    """Obtém configuração padrão para treinamento."""
    return {
        "episodes": 1000,
        "learning_rate": 0.001,
        "discount_factor": 0.95,
        "epsilon_start": 1.0,
        "epsilon_end": 0.1,
        "epsilon_decay": 0.995,
        "reward_weights": {
            "coordination": 0.4,
            "response_time": 0.3,
            "selectivity": 0.3
        },
        "network_architecture": {
            "hidden_layers": [128, 64],
            "activation": "relu",
            "optimizer": "adam"
        }
    }


@router.get("/status")
async def get_rl_system_status():
    """Obtém status geral do sistema de Reinforcement Learning."""
    # Simular status do sistema RL
    return {
        "system_status": "operational",
        "agent_loaded": True,
        "model_count": len(model_storage),
        "active_trainings": len([t for t in training_storage.values() if t["status"] == "running"]),
        "total_trainings": len(training_storage),
        "last_training_date": max([t["created_at"] for t in training_storage.values()], default=None),
        "available_algorithms": ["DQN", "A3C", "PPO", "DDPG"],
        "environment_status": "ready",
        "gpu_available": False,  # Detectar automaticamente em implementação real
        "memory_usage": "45%"
    }


@router.get("/training/status")
async def get_training_system_status():
    """Obtém status geral do sistema de treinamento."""
    running_trainings = [
        t for t in training_storage.values() if t["status"] == "running"]
    completed_trainings = [
        t for t in training_storage.values() if t["status"] == "completed"]
    failed_trainings = [
        t for t in training_storage.values() if t["status"] == "failed"]

    return {
        "training_system_status": "operational",
        "total_trainings": len(training_storage),
        "running_trainings": len(running_trainings),
        "completed_trainings": len(completed_trainings),
        "failed_trainings": len(failed_trainings),
        "queue_size": len(running_trainings),
        "average_training_time": "12.5 minutes",  # Calcular baseado em dados reais
        "success_rate": f"{(len(completed_trainings)/(len(training_storage) or 1))*100:.1f}%"
    }
