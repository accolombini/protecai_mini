#!/usr/bin/env python3
"""
Script de teste para diagnosticar os cenários de carga e falha de equipamento.
"""
import json
import sys
import os
from pathlib import Path
import importlib.util

# Importação direta usando importlib para evitar problemas do Pylance
def load_protection_module():
    """Carrega o módulo protection dinamicamente."""
    current_dir = Path(__file__).parent
    protection_file = current_dir / "src" / "backend" / "api" / "routers" / "protection.py"
    
    spec = importlib.util.spec_from_file_location("protection", protection_file)
    protection_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(protection_module)
    
    return protection_module

try:
    # Carregar módulo dinamicamente
    protection = load_protection_module()
    simulate_load_change_scenario = protection.simulate_load_change_scenario
    simulate_equipment_failure_scenario = protection.simulate_equipment_failure_scenario  
    assess_scenario_compliance = protection.assess_scenario_compliance
    
    print("=== TESTE DE CENÁRIO DE MUDANÇA DE CARGA ===")
    
    # Teste cenário de mudança de carga
    load_result = simulate_load_change_scenario("Bus_07", 0.5, True, 1000)
    print("\nEstrutura retornada por simulate_load_change_scenario:")
    print(json.dumps(load_result, indent=2, default=str))
    
    # Teste compliance
    load_compliance = assess_scenario_compliance(load_result, True)
    print(f"\nCompliance Score: {load_compliance['overall_score']:.3f}")
    print(f"Standards Met: {load_compliance['standards_met']}")
    print(f"NBR 5410: {load_compliance['standards_evaluation'].get('NBR_5410', {}).get('score', 'N/A')}")
    
    print("\n" + "="*50)
    print("=== TESTE DE CENÁRIO DE FALHA DE EQUIPAMENTO ===")
    
    # Teste cenário de falha de equipamento
    failure_result = simulate_equipment_failure_scenario("Bus_07", 0.5, True, 1000)
    print("\nEstrutura retornada por simulate_equipment_failure_scenario:")
    print(json.dumps(failure_result, indent=2, default=str))
    
    # Teste compliance
    failure_compliance = assess_scenario_compliance(failure_result, True)
    print(f"\nCompliance Score: {failure_compliance['overall_score']:.3f}")
    print(f"Standards Met: {failure_compliance['standards_met']}")
    print(f"NBR 5410: {failure_compliance['standards_evaluation'].get('NBR_5410', {}).get('score', 'N/A')}")
    
    print("\n" + "="*50)
    print("=== VERIFICAÇÃO DE ESTRUTURAS NECESSÁRIAS ===")
    
    required_keys = ['device_actions', 'system_impact', 'fault_analysis', 'coordination']
    
    print("\nCenário de Mudança de Carga:")
    for key in required_keys:
        status = "✓" if key in load_result else "✗"
        print(f"  {status} {key}")
        if key in load_result:
            print(f"    Tipo: {type(load_result[key])}")
            if isinstance(load_result[key], dict):
                print(f"    Chaves: {list(load_result[key].keys())}")
    
    print("\nCenário de Falha de Equipamento:")
    for key in required_keys:
        status = "✓" if key in failure_result else "✗"
        print(f"  {status} {key}")
        if key in failure_result:
            print(f"    Tipo: {type(failure_result[key])}")
            if isinstance(failure_result[key], dict):
                print(f"    Chaves: {list(failure_result[key].keys())}")
                
except Exception as e:
    print(f"Erro durante teste: {e}")
    import traceback
    traceback.print_exc()
