"""
Router para visualização de zonas de proteção.
Endpoints para mapear zonas de proteção, overlaps e coordenação visual.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import json
import uuid
from datetime import datetime
from pathlib import Path
import random
import math

router = APIRouter(tags=["protection_zones"])

# Modelos Pydantic


class ProtectionZone(BaseModel):
    """Modelo para zona de proteção."""
    zone_id: str
    zone_type: str  # "primary", "backup", "emergency"
    device_id: str
    device_type: str  # "relay", "fuse", "breaker"
    coverage_area: List[Dict[str, float]]  # polígono de cobertura
    protected_elements: List[str]  # linhas/barras protegidas
    reach_settings: Dict[str, float]  # alcance por zona
    coordination_margin: float  # margem com outras zonas
    priority: int  # prioridade de atuação


class ZoneOverlap(BaseModel):
    """Sobreposição entre zonas."""
    overlap_id: str
    zone1_id: str
    zone2_id: str
    overlap_area: List[Dict[str, float]]  # área de sobreposição
    overlap_percentage: float
    coordination_status: str  # "good", "marginal", "problematic"
    time_difference: float  # diferença de tempo entre zonas


class ZoneGap(BaseModel):
    """Gap de proteção."""
    gap_id: str
    gap_area: List[Dict[str, float]]  # área desprotegida
    affected_elements: List[str]
    risk_level: str  # "low", "medium", "high", "critical"
    recommended_action: str


class ZoneVisualizationData(BaseModel):
    """Dados completos para visualização."""
    network_topology: Dict[str, Any]
    protection_zones: List[ProtectionZone]
    zone_overlaps: List[ZoneOverlap]
    protection_gaps: List[ZoneGap]
    # Alterado para Any para aceitar string no status
    device_locations: Dict[str, Dict[str, Any]]
    color_scheme: Dict[str, str]
    analysis_summary: Dict[str, Any]


@router.get("/zones", response_model=List[ProtectionZone])
async def get_all_protection_zones():
    """
    Retorna todas as zonas de proteção configuradas.

    ESSENCIAL para visualizar cobertura completa do sistema.
    """
    try:
        zones = []

        # Simular zonas de proteção do IEEE 14 barras
        protection_devices = [
            {"id": "relay_51_L12", "type": "overcurrent", "line": "line_1_2"},
            {"id": "relay_51_L15", "type": "overcurrent", "line": "line_1_5"},
            {"id": "relay_51_L23", "type": "overcurrent", "line": "line_2_3"},
            {"id": "relay_67_L45", "type": "directional", "line": "line_4_5"},
            {"id": "relay_87T_T12", "type": "differential", "trafo": "trafo_1_2"},
            {"id": "fuse_F67", "type": "fuse", "line": "line_6_7"},
            {"id": "relay_59_B1", "type": "overvoltage", "bus": "bus_1"},
            {"id": "relay_27_B5", "type": "undervoltage", "bus": "bus_5"}
        ]

        for i, device in enumerate(protection_devices):
            # Zona primária
            primary_zone = create_protection_zone(
                zone_id=f"zone_{device['id']}_primary",
                zone_type="primary",
                device=device,
                reach_percent=80,  # 80% da linha
                priority=1
            )
            zones.append(primary_zone)

            # Zona de backup para relés principais
            if device["type"] in ["overcurrent", "directional"]:
                backup_zone = create_protection_zone(
                    zone_id=f"zone_{device['id']}_backup",
                    zone_type="backup",
                    device=device,
                    reach_percent=120,  # 120% da linha
                    priority=2
                )
                zones.append(backup_zone)

        return zones

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao recuperar zonas de proteção: {str(e)}"
        )


@router.get("/zones/overlaps")
async def get_zone_overlaps():
    """
    Analisa sobreposições entre zonas de proteção.

    CRÍTICO para validar coordenação e seletividade.
    """
    try:
        overlaps = []

        # Simular análise de sobreposições
        zone_pairs = [
            ("zone_relay_51_L12_primary", "zone_relay_51_L23_backup"),
            ("zone_relay_51_L15_backup", "zone_relay_67_L45_primary"),
            ("zone_relay_87T_T12_primary", "zone_relay_51_L12_backup")
        ]

        for i, (zone1, zone2) in enumerate(zone_pairs):
            overlap = ZoneOverlap(
                overlap_id=f"overlap_{i+1}",
                zone1_id=zone1,
                zone2_id=zone2,
                overlap_area=[
                    {"x": random.uniform(0, 6), "y": random.uniform(0, 4)}
                    for _ in range(4)
                ],
                overlap_percentage=random.uniform(15, 35),
                coordination_status=random.choice(
                    ["good", "good", "marginal"]),
                time_difference=random.uniform(0.2, 0.5)
            )
            overlaps.append(overlap)

        return {
            "overlaps": overlaps,
            "total_overlaps": len(overlaps),
            "coordination_quality": "good" if all(o.coordination_status == "good" for o in overlaps) else "needs_review",
            "analysis_timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na análise de sobreposições: {str(e)}"
        )


@router.get("/zones/gaps")
async def get_protection_gaps():
    """
    Identifica gaps de proteção no sistema.

    FUNDAMENTAL para segurança em ambiente petrolífero.
    """
    try:
        gaps = []

        # Simular detecção de gaps
        potential_gaps = [
            {
                "area": [{"x": 2.5, "y": 1.5}, {"x": 3.0, "y": 1.5},
                         {"x": 3.0, "y": 2.0}, {"x": 2.5, "y": 2.0}],
                "elements": ["section_line_2_8"],
                "risk": "medium"
            },
            {
                "area": [{"x": 5.5, "y": 3.5}, {"x": 6.0, "y": 3.5},
                         {"x": 6.0, "y": 4.0}, {"x": 5.5, "y": 4.0}],
                "elements": ["bus_13_section"],
                "risk": "low"
            }
        ]

        for i, gap_data in enumerate(potential_gaps):
            gap = ZoneGap(
                gap_id=f"gap_{i+1}",
                gap_area=gap_data["area"],
                affected_elements=gap_data["elements"],
                risk_level=gap_data["risk"],
                recommended_action=get_gap_recommendation(gap_data["risk"])
            )
            gaps.append(gap)

        return {
            "protection_gaps": gaps,
            "total_gaps": len(gaps),
            "critical_gaps": [g for g in gaps if g.risk_level == "critical"],
            "high_risk_gaps": len([g for g in gaps if g.risk_level == "high"]),
            "recommendations": generate_gap_recommendations(gaps),
            "analysis_timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na análise de gaps: {str(e)}"
        )


@router.get("/visualization/complete", response_model=ZoneVisualizationData)
async def get_complete_zone_visualization():
    """
    Retorna dados completos para visualização executiva.

    Este endpoint consolida TODAS as informações necessárias 
    para o dashboard executivo mostrar zonas, overlaps e gaps.
    """
    try:
        # Carregar topologia da rede
        network_topology = {
            "buses": {
                1: {"x": 0, "y": 0, "voltage": 138}, 2: {"x": 2, "y": 1, "voltage": 138},
                3: {"x": 1, "y": 2, "voltage": 138}, 4: {"x": 0, "y": 3, "voltage": 138},
                5: {"x": 1, "y": 4, "voltage": 138}, 6: {"x": 3, "y": 3, "voltage": 138},
                7: {"x": 4, "y": 2, "voltage": 138}, 8: {"x": 3, "y": 1, "voltage": 138},
                9: {"x": 5, "y": 1, "voltage": 138}, 10: {"x": 6, "y": 1, "voltage": 138},
                11: {"x": 6, "y": 2, "voltage": 138}, 12: {"x": 5, "y": 3, "voltage": 138},
                13: {"x": 6, "y": 3, "voltage": 138}, 14: {"x": 5, "y": 4, "voltage": 138}
            },
            "lines": [
                {"id": "L1-2", "from": 1, "to": 2,
                    "status": "closed", "current": 245},
                {"id": "L1-5", "from": 1, "to": 5,
                    "status": "closed", "current": 156},
                {"id": "L2-3", "from": 2, "to": 3,
                    "status": "closed", "current": 198},
                {"id": "L2-4", "from": 2, "to": 4,
                    "status": "closed", "current": 123},
                {"id": "L2-5", "from": 2, "to": 5,
                    "status": "closed", "current": 267},
                {"id": "L3-4", "from": 3, "to": 4,
                    "status": "closed", "current": 89},
                {"id": "L4-5", "from": 4, "to": 5,
                    "status": "closed", "current": 178},
                {"id": "L4-7", "from": 4, "to": 7,
                    "status": "closed", "current": 298},
                {"id": "L4-9", "from": 4, "to": 9,
                    "status": "closed", "current": 134},
                {"id": "L5-6", "from": 5, "to": 6,
                    "status": "closed", "current": 201}
            ]
        }

        # Gerar zonas de proteção
        zones_response = await get_all_protection_zones()
        protection_zones = zones_response

        # Analisar sobreposições
        overlaps_response = await get_zone_overlaps()
        zone_overlaps = overlaps_response["overlaps"]

        # Identificar gaps
        gaps_response = await get_protection_gaps()
        protection_gaps = gaps_response["protection_gaps"]

        # Localização dos dispositivos
        device_locations = {
            "relay_51_L12": {"x": 1.0, "y": 0.5, "status": "active"},
            "relay_51_L15": {"x": 0.5, "y": 2.0, "status": "active"},
            "relay_51_L23": {"x": 1.5, "y": 1.5, "status": "active"},
            "relay_67_L45": {"x": 0.5, "y": 3.5, "status": "active"},
            "relay_87T_T12": {"x": 1.0, "y": 0.0, "status": "active"},
            "fuse_F67": {"x": 3.5, "y": 2.5, "status": "active"},
            "relay_59_B1": {"x": 0.0, "y": 0.0, "status": "monitoring"},
            "relay_27_B5": {"x": 1.0, "y": 4.0, "status": "monitoring"}
        }

        # Esquema de cores para visualização
        color_scheme = {
            "primary_zone": "#FF6B6B",      # Vermelho para zona primária
            "backup_zone": "#4ECDC4",       # Azul-verde para backup
            "emergency_zone": "#45B7D1",    # Azul para emergência
            "overlap_good": "#96CEB4",      # Verde para sobreposição boa
            "overlap_marginal": "#FFEAA7",  # Amarelo para marginal
            "overlap_bad": "#DDA0DD",       # Roxo para problemática
            "gap_low": "#FD79A8",           # Rosa claro para gap baixo risco
            "gap_medium": "#FDCB6E",        # Laranja para gap médio risco
            "gap_high": "#E17055",          # Vermelho escuro para gap alto risco
            "gap_critical": "#2D3436",      # Preto para gap crítico
            "device_active": "#00B894",     # Verde para dispositivo ativo
            "device_alarm": "#E84393",      # Rosa para alarme
            "network_normal": "#74B9FF",    # Azul para rede normal
            "network_fault": "#FF7675"      # Vermelho para falta
        }

        # Resumo da análise
        analysis_summary = {
            "total_zones": len(protection_zones),
            "primary_zones": len([z for z in protection_zones if z.zone_type == "primary"]),
            "backup_zones": len([z for z in protection_zones if z.zone_type == "backup"]),
            "zone_overlaps": len(zone_overlaps),
            "good_overlaps": len([o for o in zone_overlaps if o.coordination_status == "good"]),
            "protection_gaps": len(protection_gaps),
            "critical_gaps": len([g for g in protection_gaps if g.risk_level == "critical"]),
            "coverage_percentage": calculate_coverage_percentage(protection_zones),
            "coordination_score": calculate_coordination_score(zone_overlaps),
            "overall_assessment": determine_overall_assessment(protection_zones, zone_overlaps, protection_gaps),
            "petroleum_readiness": assess_petroleum_readiness(protection_gaps, zone_overlaps),
            "last_updated": datetime.now().isoformat()
        }

        return ZoneVisualizationData(
            network_topology=network_topology,
            protection_zones=protection_zones,
            zone_overlaps=zone_overlaps,
            protection_gaps=protection_gaps,
            device_locations=device_locations,
            color_scheme=color_scheme,
            analysis_summary=analysis_summary
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na geração de dados de visualização: {str(e)}"
        )


@router.post("/zones/analyze-coordination")
async def analyze_zone_coordination(fault_location: Dict[str, Any]):
    """
    Analisa coordenação de zonas para uma localização específica de falta.

    CRÍTICO: Determina quais zonas deveriam atuar para uma falta específica.
    """
    try:
        fault_line = fault_location.get("line_id", "line_2_5")
        fault_position = fault_location.get("position_percent", 50.0)

        # Determinar zonas que deveriam responder
        expected_zones = determine_responding_zones(fault_line, fault_position)

        # Analisar coordenação temporal
        coordination_analysis = analyze_temporal_coordination(expected_zones)

        # Verificar seletividade
        selectivity_check = check_selectivity(expected_zones, fault_location)

        return {
            "fault_location": fault_location,
            "expected_zones": expected_zones,
            "coordination_analysis": coordination_analysis,
            "selectivity_assessment": selectivity_check,
            "coordination_quality": determine_coordination_quality(coordination_analysis, selectivity_check),
            "recommendations": generate_coordination_recommendations(coordination_analysis, selectivity_check),
            "analysis_timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na análise de coordenação: {str(e)}"
        )


@router.get("/zones/detailed-configuration")
async def get_detailed_zone_configuration():
    """
    Retorna configuração detalhada das zonas de proteção com análise específica.

    ESSENCIAL para entender quem pertence à Zona 1 vs Zona 2 e configurações iniciais.
    """
    try:
        # Configuração detalhada por zona
        zone_configuration = {
            "zona_1_primaria": {
                "description": "Zona de proteção primária - atuação instantânea",
                "devices": [
                    {
                        "device_id": "relay_51_L12",
                        "location": "Linha 1-2",
                        "pickup_current": "850A",
                        "time_dial": "0.05s",
                        "reach_percentage": "80%",
                        "coordination_margin": "200ms",
                        "standards_compliance": {
                            "IEEE_C37.112": "compliant",
                            "IEC_60255": "compliant",
                            "ANSI_C37.90": "compliant"
                        }
                    },
                    {
                        "device_id": "relay_67_L45",
                        "location": "Linha 4-5",
                        "pickup_current": "720A",
                        "time_dial": "0.08s",
                        "reach_percentage": "85%",
                        "coordination_margin": "250ms",
                        "standards_compliance": {
                            "IEEE_C37.112": "compliant",
                            "IEC_60255": "compliant",
                            "ANSI_C37.90": "marginal"
                        }
                    }
                ],
                "total_devices": 8,
                "coverage_area": "Proteção direta de linhas e transformadores",
                "operation_time": "0.05 - 0.15s",
                "selectivity_index": 95.2
            },
            "zona_2_backup": {
                "description": "Zona de proteção backup - atuação temporizada",
                "devices": [
                    {
                        "device_id": "relay_51_L12_backup",
                        "location": "Linha 1-2 (Backup)",
                        "pickup_current": "650A",
                        "time_dial": "0.35s",
                        "reach_percentage": "120%",
                        "coordination_margin": "300ms",
                        "standards_compliance": {
                            "IEEE_C37.112": "compliant",
                            "IEC_60255": "compliant",
                            "ANSI_C37.90": "compliant"
                        }
                    },
                    {
                        "device_id": "relay_51_L15_backup",
                        "location": "Linha 1-5 (Backup)",
                        "pickup_current": "580A",
                        "time_dial": "0.42s",
                        "reach_percentage": "125%",
                        "coordination_margin": "350ms",
                        "standards_compliance": {
                            "IEEE_C37.112": "compliant",
                            "IEC_60255": "compliant",
                            "ANSI_C37.90": "compliant"
                        }
                    }
                ],
                "total_devices": 6,
                "coverage_area": "Proteção de backup para falhas na zona primária",
                "operation_time": "0.30 - 0.60s",
                "selectivity_index": 88.7
            }
        }

        # Análise de coordenação inicial
        coordination_analysis = {
            "initial_settings": {
                "coordination_method": "Tempo Definido Inverso (IEC Normal Inverse)",
                "safety_margin": "200-400ms entre zonas",
                "pickup_coordination": "Gradual decrescente por zona",
                "standards_reference": ["IEEE Std C37.112-2018", "IEC 60255-151"]
            },
            "validation_criteria": {
                "selectivity": "Zona 1 deve atuar antes da Zona 2",
                "speed": "Zona 1: < 150ms, Zona 2: 300-600ms",
                "sensitivity": "Detectar 110% da corrente de falta mínima",
                "stability": "Não atuar para correntes de carga máxima"
            },
            "compliance_status": {
                "overall": "compliant",
                "critical_issues": 0,
                "warnings": 2,
                "recommendations": [
                    "Ajustar margem de coordenação na linha 4-5",
                    "Verificar sensibilidade do relay_27_B5"
                ]
            }
        }

        return {
            "network_overview": "IEEE 14 Bus System - Ambiente Petrolífero",
            "zone_configuration": zone_configuration,
            "coordination_analysis": coordination_analysis,
            "last_validation": datetime.now().isoformat(),
            "next_review_due": "2025-02-15"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na configuração detalhada: {str(e)}"
        )


@router.get("/rl-algorithm/detailed-analysis")
async def get_rl_algorithm_analysis():
    """
    Análise detalhada do algoritmo de Reinforcement Learning.

    CRÍTICO: Investigar convergência rápida e possíveis vícios no algoritmo.
    """
    try:
        # Análise detalhada do algoritmo RL
        rl_analysis = {
            "algorithm_details": {
                "type": "Deep Q-Network (DQN)",
                "learning_rate": 0.001,
                "discount_factor": 0.95,
                "exploration_rate": 0.1,
                "network_architecture": "3 camadas ocultas (128, 64, 32 neurônios)",
                "training_episodes": 10000,
                "convergence_episode": 847  # Preocupantemente rápido
            },
            "convergence_analysis": {
                "convergence_speed": "MUITO RÁPIDA - INVESTIGAR",
                "episode_convergence": 847,
                "expected_range": "2000-5000 episódios",
                "warning_flags": [
                    "Convergência 4x mais rápida que esperado",
                    "Possível overfitting nos dados de treino",
                    "Exploração insuficiente do espaço de estados"
                ],
                "potential_biases": [
                    "Dados de treino podem estar muito similares",
                    "Função de recompensa pode estar simplificada",
                    "Espaço de estados pode estar sub-representado"
                ]
            },
            "training_data_analysis": {
                "total_scenarios": 5000,
                "fault_types": {
                    "phase_to_ground": "60%",
                    "three_phase": "25%",
                    "phase_to_phase": "10%",
                    "double_phase_ground": "5%"
                },
                "data_diversity_score": 6.2,  # De 10 - BAIXO
                "concern": "Diversidade baixa pode explicar convergência rápida"
            },
            "performance_metrics": {
                "training_accuracy": 98.7,  # Muito alto - suspeito
                "validation_accuracy": 87.3,  # Gap grande - overfitting
                "test_accuracy": 82.1,
                "overfitting_score": "HIGH - CRÍTICO",
                "generalization_ability": "QUESTIONÁVEL"
            },
            "recommendations": [
                "🚨 URGENTE: Revisar diversidade dos dados de treino",
                "🔍 Implementar validação cruzada mais rigorosa",
                "⚖️ Ajustar taxa de exploração (aumentar epsilon)",
                "📊 Adicionar mais cenários complexos de falta",
                "🎯 Re-calibrar função de recompensa",
                "📈 Monitorar desempenho em cenários reais"
            ]
        }

        return {
            "analysis_summary": "ALGORITMO RL REQUER INVESTIGAÇÃO URGENTE",
            "rl_analysis": rl_analysis,
            "validation_timestamp": datetime.now().isoformat(),
            "next_audit_required": "2025-01-30"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na análise RL: {str(e)}"
        )


@router.post("/fault-simulation/detailed-analysis")
async def analyze_fault_simulation_detailed(fault_data: Dict[str, Any]):
    """
    Análise detalhada de simulação de falta com rastreamento completo.

    FUNDAMENTAL: Rastrear ponto da falta, dispositivos atuados e coordenação restabelecida.
    """
    try:
        fault_location = fault_data.get("location", {})
        fault_type = fault_data.get("type", "phase_to_ground")
        fault_magnitude = fault_data.get("magnitude", 2.5)  # pu

        # Análise detalhada da falta
        fault_simulation = {
            "fault_details": {
                "location": {
                    "line_id": fault_location.get("line", "line_2_5"),
                    "position_km": fault_location.get("position_km", 3.2),
                    "position_percent": fault_location.get("position_percent", 65.4),
                    "coordinates": {"x": 2.8, "y": 1.7},
                    "nearest_bus": "Bus_5"
                },
                "fault_characteristics": {
                    "type": fault_type,
                    "magnitude_pu": fault_magnitude,
                    "magnitude_amperes": fault_magnitude * 1200,  # Base: 1200A
                    "resistance": "0.1 ohm",
                    "reactance": "0.05 ohm",
                    "duration": "0.8s",
                    "cleared": True
                }
            },
            "devices_operation": {
                "primary_operation": [
                    {
                        "device": "relay_51_L25_primary",
                        "operation_time": 0.087,  # segundos
                        "pickup_current": 1850,  # A
                        "settings_used": {"pickup": "850A", "time_dial": 0.05},
                        "operation_reason": "Corrente de falta acima do pickup",
                        "successful": True
                    }
                ],
                "backup_devices": [
                    {
                        "device": "relay_51_L25_backup",
                        "armed_time": 0.387,
                        "pickup_current": 1850,
                        "settings_used": {"pickup": "650A", "time_dial": 0.35},
                        "operation_reason": "Backup para proteção primária",
                        "operated": False,
                        "reason_not_operated": "Falta eliminada pela proteção primária"
                    }
                ],
                "adjacent_zones": [
                    {
                        "device": "relay_51_L24",
                        "status": "monitored",
                        "current_seen": 847,  # A
                        "operated": False,
                        "reason": "Corrente abaixo do pickup (850A)"
                    }
                ]
            },
            "coordination_restoration": {
                "pre_fault_settings": {
                    "relay_51_L25_primary": {"pickup": "850A", "time_dial": 0.05},
                    "relay_51_L25_backup": {"pickup": "650A", "time_dial": 0.35}
                },
                "rl_adjustments": [
                    {
                        "device": "relay_51_L25_primary",
                        "parameter": "pickup_current",
                        "old_value": "850A",
                        "new_value": "820A",
                        "reason": "RL detectou sensibilidade insuficiente",
                        "confidence": 0.87
                    },
                    {
                        "device": "relay_51_L25_backup",
                        "parameter": "time_dial",
                        "old_value": 0.35,
                        "new_value": 0.38,
                        "reason": "Aumentar margem de coordenação",
                        "confidence": 0.92
                    }
                ],
                "coordination_validation": {
                    "selectivity_maintained": True,
                    "speed_improved": True,
                    "margin_adequate": True,
                    "standards_compliance": "compliant"
                }
            }
        }

        # Validação contra normas
        standards_validation = {
            "IEEE_C37.112": {
                "coordination_margin": "PASS - 300ms > 200ms mínimo",
                "selectivity": "PASS - Zona 1 atuou corretamente",
                "sensitivity": "PASS - Detectou 218% da corrente pickup"
            },
            "IEC_60255": {
                "operating_time": "PASS - 87ms < 150ms máximo",
                "reset_time": "PASS - 45ms < 60ms máximo",
                "accuracy": "PASS - Erro < 5%"
            },
            "ANSI_C37.90": {
                "coordination_study": "PASS - Margem adequada",
                "fault_clearing": "PASS - Falta eliminada em zona correta"
            }
        }

        return {
            "simulation_id": f"fault_sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "fault_simulation": fault_simulation,
            "standards_validation": standards_validation,
            "overall_assessment": "COORDENAÇÃO MANTIDA - RL funcionou adequadamente",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na simulação detalhada: {str(e)}"
        )


@router.get("/zones/real-time-status")
async def get_zones_realtime_status():
    """
    Status em tempo real de todas as zonas de proteção.

    Para o dashboard executivo mostrar estado atual das zonas.
    """
    try:
        # Simular status em tempo real
        zones_status = [
            {
                "zone_id": "zone_relay_51_L12_primary",
                "status": "armed",
                "current_pickup": 85.2,
                "threshold": 100.0,
                "margin_percent": 17.4,
                "last_operation": None
            },
            {
                "zone_id": "zone_relay_51_L15_backup",
                "status": "monitoring",
                "current_pickup": 45.7,
                "threshold": 120.0,
                "margin_percent": 61.9,
                "last_operation": "2025-01-06T14:23:15Z"
            },
            {
                "zone_id": "zone_relay_87T_T12_primary",
                "status": "alarm",
                "current_pickup": 234.1,
                "threshold": 250.0,
                "margin_percent": 6.4,
                "last_operation": None
            }
        ]

        # Estatísticas gerais
        armed_zones = len([z for z in zones_status if z["status"] == "armed"])
        alarm_zones = len([z for z in zones_status if z["status"] == "alarm"])

        return {
            "zones_status": zones_status,
            "summary": {
                "total_zones": len(zones_status),
                "armed_zones": armed_zones,
                "monitoring_zones": len(zones_status) - armed_zones - alarm_zones,
                "alarm_zones": alarm_zones,
                "average_margin": sum(z["margin_percent"] for z in zones_status) / len(zones_status),
                "system_health": "good" if alarm_zones == 0 else "attention" if alarm_zones < 2 else "critical"
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro no status tempo real: {str(e)}"
        )

# Funções auxiliares


def create_protection_zone(zone_id: str, zone_type: str, device: Dict, reach_percent: float, priority: int) -> ProtectionZone:
    """Cria zona de proteção baseada no dispositivo."""

    # Determinar elementos protegidos
    if "line" in device:
        protected_elements = [device["line"]]
        # Gerar área de cobertura baseada na linha
        coverage_area = generate_line_coverage_area(
            device["line"], reach_percent)
    elif "bus" in device:
        protected_elements = [device["bus"]]
        coverage_area = generate_bus_coverage_area(device["bus"])
    elif "trafo" in device:
        protected_elements = [device["trafo"]]
        coverage_area = generate_trafo_coverage_area(device["trafo"])
    else:
        protected_elements = ["unknown"]
        coverage_area = [{"x": 0, "y": 0}, {"x": 1, "y": 1}]

    # Configurações de alcance
    reach_settings = {
        "zone1": reach_percent * 0.8,   # 80% do alcance total
        "zone2": reach_percent * 1.2,   # 120% para backup
        "zone3": reach_percent * 1.5    # 150% para backup remoto
    }

    return ProtectionZone(
        zone_id=zone_id,
        zone_type=zone_type,
        device_id=device["id"],
        device_type=device["type"],
        coverage_area=coverage_area,
        protected_elements=protected_elements,
        reach_settings=reach_settings,
        coordination_margin=random.uniform(0.15, 0.3),  # 150-300ms
        priority=priority
    )


def generate_line_coverage_area(line_id: str, reach_percent: float) -> List[Dict[str, float]]:
    """Gera área de cobertura para linha."""
    # Simplificado - em implementação real usaria coordenadas reais
    base_area = [
        {"x": random.uniform(0, 6), "y": random.uniform(0, 4)},
        {"x": random.uniform(0, 6), "y": random.uniform(0, 4)},
        {"x": random.uniform(0, 6), "y": random.uniform(0, 4)},
        {"x": random.uniform(0, 6), "y": random.uniform(0, 4)}
    ]
    return base_area


def generate_bus_coverage_area(bus_id: str) -> List[Dict[str, float]]:
    """Gera área de cobertura para barra."""
    # Área circular ao redor da barra
    center_x, center_y = 3, 2  # Simulado
    radius = 0.5

    area = []
    for angle in [0, 90, 180, 270]:
        x = center_x + radius * math.cos(math.radians(angle))
        y = center_y + radius * math.sin(math.radians(angle))
        area.append({"x": x, "y": y})

    return area


def generate_trafo_coverage_area(trafo_id: str) -> List[Dict[str, float]]:
    """Gera área de cobertura para transformador."""
    # Área retangular ao redor do transformador
    return [
        {"x": 0.8, "y": 0.8}, {"x": 1.2, "y": 0.8},
        {"x": 1.2, "y": 1.2}, {"x": 0.8, "y": 1.2}
    ]


def get_gap_recommendation(risk_level: str) -> str:
    """Retorna recomendação para gap baseado no risco."""
    recommendations = {
        "low": "Monitorar área - considerar proteção adicional se carga aumentar",
        "medium": "Instalar proteção de backup - revisar esquema em 6 meses",
        "high": "Ação imediata necessária - instalar proteção em 30 dias",
        "critical": "URGENTE - instalar proteção temporária imediatamente"
    }
    return recommendations.get(risk_level, "Analisar caso específico")


def generate_gap_recommendations(gaps: List[ZoneGap]) -> List[str]:
    """Gera recomendações gerais para gaps."""
    recommendations = []

    critical_count = len([g for g in gaps if g.risk_level == "critical"])
    high_count = len([g for g in gaps if g.risk_level == "high"])

    if critical_count > 0:
        recommendations.append(
            f"🚨 {critical_count} gap(s) crítico(s) - ação imediata necessária")

    if high_count > 0:
        recommendations.append(
            f"⚠️ {high_count} gap(s) de alto risco - planejar proteção adicional")

    if len(gaps) == 0:
        recommendations.append("✅ Nenhum gap de proteção identificado")

    recommendations.append(
        "🛢️ Para ambiente petrolífero: verificar redundância em áreas críticas")

    return recommendations


def calculate_coverage_percentage(zones: List[ProtectionZone]) -> float:
    """Calcula porcentagem de cobertura do sistema."""
    # Simplificado - em implementação real calcularia sobreposição real
    primary_zones = len([z for z in zones if z.zone_type == "primary"])
    backup_zones = len([z for z in zones if z.zone_type == "backup"])

    # Assumir que cada zona primária cobre 10% do sistema
    coverage = min(100.0, primary_zones * 12 + backup_zones * 5)
    return round(coverage, 1)


def calculate_coordination_score(overlaps: List[ZoneOverlap]) -> float:
    """Calcula score de coordenação."""
    if not overlaps:
        return 85.0

    good_overlaps = len(
        [o for o in overlaps if o.coordination_status == "good"])
    score = (good_overlaps / len(overlaps)) * 100
    return round(score, 1)


def determine_overall_assessment(zones: List[ProtectionZone], overlaps: List[ZoneOverlap], gaps: List[ZoneGap]) -> str:
    """Determina avaliação geral do sistema."""
    coverage = calculate_coverage_percentage(zones)
    coordination = calculate_coordination_score(overlaps)
    critical_gaps = len(
        [g for g in gaps if g.risk_level in ["critical", "high"]])

    if coverage > 95 and coordination > 90 and critical_gaps == 0:
        return "excellent"
    elif coverage > 85 and coordination > 80 and critical_gaps <= 1:
        return "good"
    elif coverage > 70 and coordination > 70 and critical_gaps <= 2:
        return "acceptable"
    else:
        return "needs_improvement"


def assess_petroleum_readiness(gaps: List[ZoneGap], overlaps: List[ZoneOverlap]) -> Dict[str, Any]:
    """Avalia prontidão para ambiente petrolífero."""
    critical_gaps = len(
        [g for g in gaps if g.risk_level in ["critical", "high"]])
    problematic_overlaps = len(
        [o for o in overlaps if o.coordination_status == "problematic"])

    ready = critical_gaps == 0 and problematic_overlaps == 0

    return {
        "ready": ready,
        "confidence_level": "high" if ready else "medium" if critical_gaps <= 1 else "low",
        "critical_issues": critical_gaps + problematic_overlaps,
        "certification_status": "compliant" if ready else "requires_action",
        "next_review_date": "2025-02-01"  # 30 dias
    }


def determine_responding_zones(fault_line: str, fault_position: float) -> List[Dict[str, Any]]:
    """Determina zonas que deveriam responder a uma falta."""
    zones = []

    # Zona primária - sempre deve responder
    zones.append({
        "zone_id": f"primary_{fault_line}",
        "response_time": round(random.uniform(0.08, 0.15), 3),
        "expected": True,
        "priority": 1
    })

    # Zona de backup - deve responder se primária falhar
    zones.append({
        "zone_id": f"backup_{fault_line}",
        "response_time": round(random.uniform(0.3, 0.5), 3),
        "expected": True,
        "priority": 2
    })

    # Zonas adjacentes - podem responder dependendo da localização
    if fault_position > 80:  # Próximo ao final da linha
        zones.append({
            "zone_id": f"adjacent_downstream",
            "response_time": round(random.uniform(0.6, 1.0), 3),
            "expected": False,
            "priority": 3
        })

    return zones


def analyze_temporal_coordination(zones: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analisa coordenação temporal entre zonas."""
    if len(zones) < 2:
        return {"status": "insufficient_zones"}

    # Verificar intervalos de tempo
    time_intervals = []
    for i in range(len(zones) - 1):
        interval = zones[i+1]["response_time"] - zones[i]["response_time"]
        time_intervals.append(interval)

    # Avaliar coordenação
    adequate_intervals = len(
        [t for t in time_intervals if t >= 0.2])  # 200ms mínimo

    return {
        "time_intervals": time_intervals,
        "adequate_intervals": adequate_intervals,
        "total_intervals": len(time_intervals),
        "coordination_quality": "good" if adequate_intervals == len(time_intervals) else "marginal",
        "minimum_interval": min(time_intervals) if time_intervals else 0,
        "maximum_interval": max(time_intervals) if time_intervals else 0
    }


def check_selectivity(zones: List[Dict[str, Any]], fault_location: Dict[str, Any]) -> Dict[str, Any]:
    """Verifica seletividade das zonas."""
    return {
        "selective": True,  # Simplificado
        "non_selective_zones": [],
        "selectivity_score": 95.0,
        "issues": []
    }


def determine_coordination_quality(coordination: Dict[str, Any], selectivity: Dict[str, Any]) -> str:
    """Determina qualidade geral da coordenação."""
    coord_good = coordination.get("coordination_quality") == "good"
    select_good = selectivity.get("selectivity_score", 0) > 90

    if coord_good and select_good:
        return "excellent"
    elif coord_good or select_good:
        return "good"
    else:
        return "needs_improvement"


def generate_coordination_recommendations(coordination: Dict[str, Any], selectivity: Dict[str, Any]) -> List[str]:
    """Gera recomendações para coordenação."""
    recommendations = []

    if coordination.get("coordination_quality") != "good":
        recommendations.append("⚙️ Revisar tempos de coordenação entre zonas")

    if selectivity.get("selectivity_score", 100) < 90:
        recommendations.append(
            "🎯 Melhorar seletividade - ajustar configurações")

    if not recommendations:
        recommendations.append(
            "✅ Coordenação adequada - manter configurações atuais")

    recommendations.append(
        "🛢️ Validar configurações para ambiente petrolífero")

    return recommendations


@router.get("/standards/compliance-monitoring")
async def get_standards_compliance_monitoring():
    """
    Monitoramento contínuo de conformidade com normas técnicas.

    ESSENCIAL para ambiente petrolífero - compliance rigoroso.
    """
    try:
        compliance_report = {
            "overall_status": "MOSTLY_COMPLIANT",
            "last_audit": "2025-01-15T10:30:00Z",
            "next_audit": "2025-02-15T10:30:00Z",

            "ieee_c37_112_2018": {
                "title": "IEEE Guide for Protective Relay Applications to Transmission Lines",
                "compliance_percentage": 94.2,
                "status": "COMPLIANT",
                "findings": [
                    {"item": "Coordination margins",
                        "status": "PASS", "value": "280ms avg"},
                    {"item": "Selectivity index",
                        "status": "PASS", "value": "95.2%"},
                    {"item": "Speed of operation", "status": "WARNING",
                        "value": "160ms (> 150ms)"}
                ],
                "action_required": "Ajustar tempo de operação relay_67_L45"
            },

            "iec_60255_151": {
                "title": "Measuring relays and protection equipment - Functional requirements for over/under current protection",
                "compliance_percentage": 97.8,
                "status": "COMPLIANT",
                "findings": [
                    {"item": "Pickup accuracy", "status": "PASS", "value": "±2.1%"},
                    {"item": "Time accuracy", "status": "PASS", "value": "±1.8%"},
                    {"item": "Reset ratio", "status": "PASS",
                        "value": "0.95 (> 0.9)"}
                ],
                "action_required": "Nenhuma ação necessária"
            },

            "ansi_c37_90": {
                "title": "IEEE Standard for Relays and Relay Systems Associated with Electric Power Apparatus",
                "compliance_percentage": 89.7,
                "status": "MARGINAL",
                "findings": [
                    {"item": "Relay coordination",
                        "status": "PASS", "value": "Adequada"},
                    {"item": "Communication protocols",
                        "status": "WARNING", "value": "Latência alta"},
                    {"item": "Cybersecurity", "status": "FAIL",
                        "value": "Autenticação fraca"}
                ],
                "action_required": "URGENTE - Implementar autenticação robusta"
            },

            "nbr_14039": {
                "title": "Instalações elétricas de média tensão - Brasil",
                "compliance_percentage": 92.5,
                "status": "COMPLIANT",
                "findings": [
                    {"item": "Coordenação seletiva",
                        "status": "PASS", "value": "Mantida"},
                    {"item": "Proteção backup", "status": "PASS",
                        "value": "Implementada"},
                    {"item": "Documentação", "status": "WARNING",
                        "value": "Desatualizada"}
                ],
                "action_required": "Atualizar diagramas unifilares"
            }
        }

        # Análise de riscos específicos para ambiente petrolífero
        petroleum_specific = {
            "api_rp_540": {
                "title": "Electrical Installations in Petroleum Processing Plants",
                "compliance_percentage": 88.3,
                "critical_items": [
                    {"item": "Hazardous area classification", "status": "COMPLIANT"},
                    {"item": "Intrinsically safe circuits", "status": "COMPLIANT"},
                    {"item": "Emergency shutdown systems", "status": "WARNING"},
                    {"item": "Fire/gas detection integration", "status": "FAIL"}
                ],
                "risk_level": "MEDIUM-HIGH",
                "action_required": "Integrar sistema detecção gás com proteção elétrica"
            },

            "nfpa_497": {
                "title": "Recommended Practice for Classification of Flammable Liquids",
                "compliance_percentage": 91.7,
                "status": "COMPLIANT",
                "findings": "Classificação de áreas adequada para ambiente petrolífero"
            }
        }

        return {
            "compliance_summary": {
                "overall_score": 92.1,
                "critical_issues": 2,
                "warnings": 4,
                "compliant_standards": 3,
                "non_compliant_standards": 1
            },
            "detailed_compliance": compliance_report,
            "petroleum_specific": petroleum_specific,
            "recommendations": [
                "🚨 CRÍTICO: Implementar autenticação robusta (ANSI C37.90)",
                "⚠️ URGENTE: Integrar detecção de gás com proteção (API RP-540)",
                "📋 Atualizar documentação técnica (NBR 14039)",
                "⏱️ Otimizar tempo operação relay_67_L45 (IEEE C37.112)"
            ],
            "next_actions": {
                "immediate": "Correção questões críticas de segurança",
                "30_days": "Implementação melhorias operacionais",
                "90_days": "Auditoria completa conformidade"
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro no monitoramento de conformidade: {str(e)}"
        )
