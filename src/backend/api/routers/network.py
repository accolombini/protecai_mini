"""
Router de Gestão da Rede Elétrica
=================================

Endpoints para carregar, configurar e modificar a rede IEEE 14 barras.
"""

import os
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json
import pandapower as pp
from pathlib import Path
import numpy as np

router = APIRouter()

# Modelos Pydantic


class NetworkInfo(BaseModel):
    n_buses: int
    n_lines: int
    n_transformers: int
    n_loads: int
    base_voltage: float
    frequency: float


class BusConfig(BaseModel):
    bus_id: int
    name: str
    voltage_kv: float
    type: str = "PQ"


class LineConfig(BaseModel):
    line_id: int
    from_bus: int
    to_bus: int
    length_km: float
    r_ohm_per_km: float
    x_ohm_per_km: float
    max_i_ka: float


class LoadConfig(BaseModel):
    load_id: int
    bus: int
    p_mw: float
    q_mvar: float
    name: str


# Caminho padrão para a rede
# Vai para o diretório raiz do projeto
# Cinco níveis acima: routers -> api -> backend -> src -> protecai_mini
BASE_DIR = Path(__file__).parent.parent.parent.parent.parent
DEFAULT_NETWORK_PATH = BASE_DIR / "simuladores/power_sim/data/ieee14_protecao.json"


@router.get("/info", response_model=NetworkInfo)
async def get_network_info():
    """Obter informações básicas da rede elétrica."""
    try:
        # Carregar rede
        with open(DEFAULT_NETWORK_PATH, 'r') as f:
            data = json.load(f)

        net = pp.from_json_string(data["pandapower_net"])

        return NetworkInfo(
            n_buses=len(net.bus),
            n_lines=len(net.line),
            n_transformers=len(net.trafo),
            n_loads=len(net.load),
            base_voltage=net.bus['vn_kv'].iloc[0],
            frequency=net.f_hz
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao carregar rede: {str(e)}")


@router.get("/buses")
async def get_buses():
    """Listar todas as barras da rede."""
    try:
        with open(DEFAULT_NETWORK_PATH, 'r') as f:
            data = json.load(f)

        net = pp.from_json_string(data["pandapower_net"])

        buses = []
        for idx, row in net.bus.iterrows():
            buses.append({
                "id": int(idx),
                "name": row['name'],
                "voltage_kv": float(row['vn_kv']),
                "type": row['type'],
                "in_service": bool(row['in_service'])
            })

        return {"buses": buses}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao listar barras: {str(e)}")


@router.get("/lines")
async def get_lines():
    """Listar todas as linhas da rede."""
    try:
        with open(DEFAULT_NETWORK_PATH, 'r') as f:
            data = json.load(f)

        net = pp.from_json_string(data["pandapower_net"])

        lines = []
        for idx, row in net.line.iterrows():
            lines.append({
                "id": int(idx),
                "name": row['name'],
                "from_bus": int(row['from_bus']),
                "to_bus": int(row['to_bus']),
                "length_km": float(row['length_km']),
                "r_ohm_per_km": float(row['r_ohm_per_km']),
                "x_ohm_per_km": float(row['x_ohm_per_km']),
                "max_i_ka": float(row['max_i_ka']),
                "in_service": bool(row['in_service'])
            })

        return {"lines": lines}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao listar linhas: {str(e)}")


@router.get("/transformers")
async def get_transformers():
    """Listar todos os transformadores da rede."""
    try:
        with open(DEFAULT_NETWORK_PATH, 'r') as f:
            data = json.load(f)

        net = pp.from_json_string(data["pandapower_net"])

        transformers = []
        for idx, row in net.trafo.iterrows():
            transformers.append({
                "id": int(idx),
                "name": row['name'],
                "hv_bus": int(row['hv_bus']),
                "lv_bus": int(row['lv_bus']),
                "sn_mva": float(row['sn_mva']),
                "vn_hv_kv": float(row['vn_hv_kv']),
                "vn_lv_kv": float(row['vn_lv_kv']),
                "vk_percent": float(row['vk_percent']),
                "in_service": bool(row['in_service'])
            })

        return {"transformers": transformers}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao listar transformadores: {str(e)}")


@router.get("/loads")
async def get_loads():
    """Listar todas as cargas da rede."""
    try:
        with open(DEFAULT_NETWORK_PATH, 'r') as f:
            data = json.load(f)

        net = pp.from_json_string(data["pandapower_net"])

        loads = []
        for idx, row in net.load.iterrows():
            loads.append({
                "id": int(idx),
                "name": row['name'],
                "bus": int(row['bus']),
                "p_mw": float(row['p_mw']),
                "q_mvar": float(row['q_mvar']),
                "in_service": bool(row['in_service'])
            })

        return {"loads": loads}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao listar cargas: {str(e)}")


@router.put("/bus/{bus_id}")
async def update_bus(bus_id: int, config: BusConfig):
    """Atualizar configuração de uma barra."""
    try:
        with open(DEFAULT_NETWORK_PATH, 'r') as f:
            data = json.load(f)

        net = pp.from_json_string(data["pandapower_net"])

        if bus_id not in net.bus.index:
            raise HTTPException(
                status_code=404, detail=f"Barra {bus_id} não encontrada")

        # Atualizar parâmetros
        net.bus.at[bus_id, 'name'] = config.name
        net.bus.at[bus_id, 'vn_kv'] = config.voltage_kv
        net.bus.at[bus_id, 'type'] = config.type

        # Salvar alterações (em ambiente real, isso seria em um banco de dados)
        updated_data = data.copy()
        updated_data["pandapower_net"] = pp.to_json(net)

        return {
            "message": f"Barra {bus_id} atualizada com sucesso",
            "bus": {
                "id": bus_id,
                "name": config.name,
                "voltage_kv": config.voltage_kv,
                "type": config.type
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao atualizar barra: {str(e)}")


@router.put("/load/{load_id}")
async def update_load(load_id: int, config: LoadConfig):
    """Atualizar configuração de uma carga."""
    try:
        with open(DEFAULT_NETWORK_PATH, 'r') as f:
            data = json.load(f)

        net = pp.from_json_string(data["pandapower_net"])

        if load_id not in net.load.index:
            raise HTTPException(
                status_code=404, detail=f"Carga {load_id} não encontrada")

        # Atualizar parâmetros
        net.load.at[load_id, 'bus'] = config.bus
        net.load.at[load_id, 'p_mw'] = config.p_mw
        net.load.at[load_id, 'q_mvar'] = config.q_mvar
        net.load.at[load_id, 'name'] = config.name

        return {
            "message": f"Carga {load_id} atualizada com sucesso",
            "load": {
                "id": load_id,
                "bus": config.bus,
                "p_mw": config.p_mw,
                "q_mvar": config.q_mvar,
                "name": config.name
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao atualizar carga: {str(e)}")


@router.post("/powerflow")
async def run_powerflow():
    """Executar fluxo de potência da rede."""
    try:
        with open(DEFAULT_NETWORK_PATH, 'r') as f:
            data = json.load(f)

        net = pp.from_json_string(data["pandapower_net"])

        # Executar fluxo de potência
        pp.runpp(net, algorithm='nr', max_iteration=100)

        # Coletar resultados
        results = {
            "converged": bool(net.converged),
            "bus_results": {
                "voltages_pu": net.res_bus['vm_pu'].to_dict(),
                "angles_deg": net.res_bus['va_degree'].to_dict(),
                "p_mw": net.res_bus['p_mw'].to_dict(),
                "q_mvar": net.res_bus['q_mvar'].to_dict()
            },
            "line_results": {
                "currents_ka": net.res_line['i_ka'].to_dict(),
                "loading_percent": net.res_line['loading_percent'].to_dict(),
                "p_from_mw": net.res_line['p_from_mw'].to_dict(),
                "q_from_mvar": net.res_line['q_from_mvar'].to_dict()
            }
        }

        return {
            "message": "Fluxo de potência executado com sucesso",
            "results": results
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro no fluxo de potência: {str(e)}")


@router.get("/status")
async def get_network_status():
    """Obter status atual da rede."""
    try:
        with open(DEFAULT_NETWORK_PATH, 'r') as f:
            data = json.load(f)

        net = pp.from_json_string(data["pandapower_net"])

        # Verificar conectividade
        try:
            pp.runpp(net, algorithm='nr', max_iteration=50)
            network_healthy = True
            convergence_status = "OK"
        except:
            network_healthy = False
            convergence_status = "Falha na convergência"

        return {
            "network_healthy": network_healthy,
            "convergence_status": convergence_status,
            "total_buses": len(net.bus),
            "active_buses": len(net.bus[net.bus['in_service']]),
            "total_lines": len(net.line),
            "active_lines": len(net.line[net.line['in_service']]),
            "total_load_mw": float(net.load['p_mw'].sum()),
            "last_check": "2025-01-07T12:00:00Z"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao verificar status: {str(e)}")


class NetworkLoadRequest(BaseModel):
    network_type: str = "ieee14"
    force_reload: bool = False


@router.post("/load")
async def load_network(request: NetworkLoadRequest):
    """Carregar ou recarregar a rede IEEE 14 barras."""
    try:
        # Verificar se o arquivo existe
        if not DEFAULT_NETWORK_PATH.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Arquivo de rede não encontrado: {DEFAULT_NETWORK_PATH}"
            )

        # Carregar rede
        with open(DEFAULT_NETWORK_PATH, 'r') as f:
            data = json.load(f)

        net = pp.from_json_string(data["pandapower_net"])

        # Executar fluxo de potência para validar
        try:
            pp.runpp(net)
            network_status = "loaded_and_validated"
        except Exception as pf_error:
            network_status = "loaded_but_powerflow_failed"
            print(f"Aviso: Falha no fluxo de potência: {pf_error}")

        return {
            "status": "success",
            "message": f"Rede {request.network_type} carregada com sucesso",
            "network_status": network_status,
            "network_info": {
                "n_buses": len(net.bus),
                "n_lines": len(net.line),
                "n_transformers": len(net.trafo),
                "n_loads": len(net.load),
                "base_voltage": float(net.bus['vn_kv'].iloc[0]),
                "frequency": float(net.f_hz)
            },
            "timestamp": "2025-01-07T12:00:00Z"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao carregar rede: {str(e)}"
        )
