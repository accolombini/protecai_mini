#!/usr/bin/env python3
"""
Script de teste para diagnosticar os cenários de carga e falha de equipamento.
Versão corrigida com importações adequadas.
"""
import json
import sys
import os
from pathlib import Path

def main():
    """Função principal para testar os cenários."""
    
    # Configurar caminhos
    base_dir = Path(__file__).parent.parent
    src_dir = base_dir / "src"
    
    # Adicionar caminhos ao sys.path
    sys.path.insert(0, str(src_dir))
    sys.path.insert(0, str(src_dir / "backend"))
    sys.path.insert(0, str(src_dir / "backend" / "api"))
    sys.path.insert(0, str(src_dir / "backend" / "api" / "routers"))
    
    try:
        # Tentar importar diretamente
        from src.backend.api.routers.protection import (
            simulate_load_change_scenario, 
            simulate_equipment_failure_scenario, 
            assess_scenario_compliance
        )
        
        print("✅ Importações bem-sucedidas!")
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        
        # Tentar abordagem alternativa
        try:
            import importlib.util
            protection_path = src_dir / "backend" / "api" / "routers" / "protection.py"
            
            spec = importlib.util.spec_from_file_location("protection", protection_path)
            protection_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(protection_module)
            
            simulate_load_change_scenario = protection_module.simulate_load_change_scenario
            simulate_equipment_failure_scenario = protection_module.simulate_equipment_failure_scenario
            assess_scenario_compliance = protection_module.assess_scenario_compliance
            
            print("✅ Importação alternativa bem-sucedida!")
            
        except Exception as e2:
            print(f"❌ Erro na importação alternativa: {e2}")
            return
    
    # Executar testes
    print("\n" + "="*60)
    print("=== TESTE DE CENÁRIO DE MUDANÇA DE CARGA ===")
    
    try:
        # Teste cenário de mudança de carga
        load_result = simulate_load_change_scenario("Bus_07", 0.5, True, 1000)
        print("\n📊 Estrutura retornada por simulate_load_change_scenario:")
        print(json.dumps(load_result, indent=2, default=str))
        
        # Teste compliance
        load_compliance = assess_scenario_compliance(load_result, True)
        print(f"\n🎯 Compliance Score: {load_compliance['overall_score']:.3f}")
        print(f"📋 Standards Met: {load_compliance['standards_met']}")
        
        # Verificar NBR 5410
        nbr_score = load_compliance['standards_evaluation'].get('NBR_5410', {}).get('score', 'N/A')
        print(f"🛡️ NBR 5410: {nbr_score}")
        
    except Exception as e:
        print(f"❌ Erro no teste de mudança de carga: {e}")
    
    print("\n" + "="*60)
    print("=== TESTE DE CENÁRIO DE FALHA DE EQUIPAMENTO ===")
    
    try:
        # Teste cenário de falha de equipamento
        failure_result = simulate_equipment_failure_scenario("Bus_07", 0.5, True, 1000)
        print("\n📊 Estrutura retornada por simulate_equipment_failure_scenario:")
        print(json.dumps(failure_result, indent=2, default=str))
        
        # Teste compliance
        failure_compliance = assess_scenario_compliance(failure_result, True)
        print(f"\n🎯 Compliance Score: {failure_compliance['overall_score']:.3f}")
        print(f"📋 Standards Met: {failure_compliance['standards_met']}")
        
        # Verificar NBR 5410
        nbr_score = failure_compliance['standards_evaluation'].get('NBR_5410', {}).get('score', 'N/A')
        print(f"🛡️ NBR 5410: {nbr_score}")
        
    except Exception as e:
        print(f"❌ Erro no teste de falha de equipamento: {e}")
    
    print("\n" + "="*60)
    print("=== VERIFICAÇÃO DE ESTRUTURAS NECESSÁRIAS ===")
    
    try:
        required_keys = ['device_actions', 'system_impact', 'fault_analysis', 'coordination']
        
        print("\n🔧 Cenário de Mudança de Carga:")
        for key in required_keys:
            status = "✅" if key in load_result else "❌"
            print(f"  {status} {key}")
            if key in load_result:
                print(f"    📋 Tipo: {type(load_result[key])}")
                if isinstance(load_result[key], dict):
                    print(f"    🔑 Chaves: {list(load_result[key].keys())}")
        
        print("\n⚠️ Cenário de Falha de Equipamento:")
        for key in required_keys:
            status = "✅" if key in failure_result else "❌"
            print(f"  {status} {key}")
            if key in failure_result:
                print(f"    📋 Tipo: {type(failure_result[key])}")
                if isinstance(failure_result[key], dict):
                    print(f"    🔑 Chaves: {list(failure_result[key].keys())}")
                    
    except Exception as e:
        print(f"❌ Erro na verificação de estruturas: {e}")
    
    print("\n" + "="*60)
    print("🎉 TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main()
