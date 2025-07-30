#!/usr/bin/env python3
"""
Teste Completo do ProtecAI Mini
Sistema de Coordenação de Proteção com RL - IEEE 14-Bus
"""

import sys
import time
import requests
import json
from rl_protection_coordinator import ProtectionCoordinator

def test_rl_system():
    """Testa o sistema RL completo"""
    print("🔋 TESTE COMPLETO DO PROTECAI MINI")
    print("=" * 60)
    
    # 1. Teste do Core RL
    print("\n1️⃣ Testando Sistema RL Core...")
    coordinator = ProtectionCoordinator()
    
    print(f"   ✅ Sistema inicializado: {len(coordinator.protection_devices)} dispositivos")
    print(f"   ✅ Zonas configuradas: {len(coordinator.protection_zones)}")
    
    # 2. Teste de Simulação de Falta
    print("\n2️⃣ Testando Simulação de Faltas...")
    scenarios = [
        {'bus': 4, 'fault_type': '3ph', 'severity': 0.8, 'name': 'Falta Trifásica Bus 4'},
        {'bus': 7, 'fault_type': '2ph', 'severity': 0.6, 'name': 'Falta Bifásica Bus 7'},
        {'bus': 14, 'fault_type': '1ph', 'severity': 0.5, 'name': 'Falta Monofásica Bus 14'}
    ]
    
    for scenario in scenarios:
        result = coordinator.simulate_fault(
            scenario['bus'], 
            scenario['fault_type'], 
            scenario['severity']
        )
        
        operating_devices = len([d for d in result.device_responses if d['should_operate']])
        coordination_status = "✅ OK" if result.coordination_ok else "⚠️  AJUSTE NECESSÁRIO"
        
        print(f"   🔍 {scenario['name']}:")
        print(f"      Zona: {result.affected_zone} | Corrente: {result.fault_current_a:.0f}A")
        print(f"      Dispositivos Operando: {operating_devices} | Coordenação: {coordination_status}")
    
    # 3. Teste de Treinamento RL
    print("\n3️⃣ Testando Treinamento RL...")
    train_result = coordinator.train_rl_agent(episodes=5)
    
    print(f"   ✅ Episódios treinados: {train_result['episodes_completed']}")
    print(f"   ✅ Total de episódios: {train_result['total_episodes']}")
    print(f"   ✅ Epsilon final: {train_result['final_epsilon']:.3f}")
    
    # 4. Teste de Status do Sistema
    print("\n4️⃣ Testando Status do Sistema...")
    system_status = coordinator.get_system_status()
    rl_status = coordinator.get_rl_status()
    
    print(f"   ✅ Saúde do Sistema: {system_status['system_health']}")
    print(f"   ✅ Status RL: {rl_status['status']}")
    print(f"   ✅ Episódios RL: {rl_status['episodes']}")
    
    print("\n✅ SISTEMA RL CORE: FUNCIONAL!")
    return True

def test_api_connection():
    """Testa conexão com a API"""
    print("\n5️⃣ Testando Conexão com API...")
    
    try:
        # Health check
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ API Status: {health_data['status']}")
            print(f"   ✅ Versão: {health_data['version']}")
            
            # Verificar serviços
            services = health_data.get('services', {})
            for service, status in services.items():
                print(f"   ✅ {service}: {status}")
            
            return True
        else:
            print(f"   ❌ API retornou código: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ⚠️  API não está rodando. Execute: python start_api.py")
        return False
    except Exception as e:
        print(f"   ❌ Erro na API: {e}")
        return False

def test_optimization_demo():
    """Demonstra otimização RL em tempo real"""
    print("\n6️⃣ Demonstração de Otimização RL...")
    
    coordinator = ProtectionCoordinator()
    
    # Cenário inicial
    print("   📊 Avaliação Inicial:")
    initial_score = coordinator._evaluate_coordination_quality()
    print(f"      Score Inicial: {initial_score:.1f}")
    
    # Otimização rápida
    print("   🤖 Executando Otimização (10 episódios)...")
    optimization_result = coordinator.optimize_protection_with_rl(episodes=10)
    
    print(f"   ✅ Score Final: {optimization_result['best_coordination_score']:.1f}")
    print(f"   ✅ Melhoria: {optimization_result['improvement']:.1f}")
    print(f"   ✅ Ajustes Realizados: {optimization_result['total_adjustments']}")
    
    return True

def main():
    """Função principal de teste"""
    start_time = time.time()
    
    # Testes sequenciais
    tests_passed = 0
    total_tests = 4
    
    # Core RL System
    if test_rl_system():
        tests_passed += 1
    
    # API Connection
    if test_api_connection():
        tests_passed += 1
    
    # Optimization Demo
    if test_optimization_demo():
        tests_passed += 1
    
    # Frontend Check
    print("\n7️⃣ Verificando Frontend...")
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        if response.status_code == 200:
            print("   ✅ Frontend React: Operacional")
            tests_passed += 1
        else:
            print("   ⚠️  Frontend: Executar 'npm run dev' no diretório frontend")
    except:
        print("   ⚠️  Frontend: Não acessível em localhost:5173")
    
    # Relatório Final
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 60)
    print("📋 RELATÓRIO FINAL DO TESTE")
    print("=" * 60)
    print(f"✅ Testes Aprovados: {tests_passed}/{total_tests}")
    print(f"⏱️  Tempo Total: {duration:.2f} segundos")
    
    if tests_passed == total_tests:
        print("🎉 PROTECAI MINI: 100% FUNCIONAL!")
        print("\n🌐 Acesse:")
        print("   • Backend API: http://localhost:8000/docs")
        print("   • Frontend: http://localhost:5173")
        return 0
    else:
        print("⚠️  Alguns testes falharam. Verifique os logs acima.")
        return 1

if __name__ == "__main__":
    exit(main())
