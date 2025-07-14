#!/usr/bin/env python3
"""
Script para testar a lógica de severidade em diferentes cenários.
"""
import json
import sys
import os
from pathlib import Path
import importlib.util

# Importação direta usando importlib


def load_protection_module():
    """Carrega o módulo protection dinamicamente."""
    current_dir = Path(__file__).parent.parent
    protection_file = current_dir / "src" / \
        "backend" / "api" / "routers" / "protection.py"

    spec = importlib.util.spec_from_file_location(
        "protection", protection_file)
    protection_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(protection_module)

    return protection_module


try:
    # Carregar módulo dinamicamente
    protection = load_protection_module()
    simulate_equipment_failure_scenario = protection.simulate_equipment_failure_scenario
    assess_scenario_compliance = protection.assess_scenario_compliance

    print("=== TESTE DE LÓGICA DE SEVERIDADE - FALHA DE EQUIPAMENTO ===")

    severities = [0.0, 0.5, 1.0]  # 0%, 50%, 100%

    for severity in severities:
        print(f"\n🔥 TESTANDO SEVERIDADE: {severity*100:.0f}%")
        print("="*50)

        # Teste cenário de falha de equipamento
        failure_result = simulate_equipment_failure_scenario(
            "Bus_07", severity, True, 1000)

        # Extrair métricas importantes
        power_interrupted = failure_result["system_impact"]["power_interrupted"]
        restoration_time = failure_result["system_impact"]["restoration_time"]
        clearance_time = failure_result["fault_analysis"]["clearance_time"]
        severity_level = failure_result["fault_analysis"]["severity_level"]

        print(f"Potência Interrompida: {power_interrupted}")
        print(f"Tempo de Restauração: {restoration_time}")
        print(f"Tempo de Limpeza: {clearance_time*1000:.0f}ms")
        print(f"Nível de Severidade: {severity_level}")

        # Teste compliance
        compliance = assess_scenario_compliance(failure_result, True)
        print(f"\n📊 COMPLIANCE RESULTS:")
        print(f"Score Geral: {compliance['overall_score']:.3f}")
        print(f"Padrões Atendidos: {len(compliance['standards_met'])}/4")

        for std_name, std_data in compliance['standards_evaluation'].items():
            status = "✅ CONFORME" if std_data['compliant'] else "❌ NÃO CONFORME"
            print(f"  {std_name}: {std_data['score']:.3f} - {status}")

        print(
            f"Status Geral: {'✅ APROVADO' if len(compliance['standards_met']) >= 4 else '❌ REPROVADO'}")

except Exception as e:
    print(f"Erro durante teste: {e}")
    import traceback
    traceback.print_exc()
