#!/usr/bin/env python3
"""
🧪 Script de Teste Automatizado para Validação Completa da API ProtecAI Mini
=============================================================================

Testa todos os endpoints disponíveis da API para garantir funcionalidade completa.
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path

# Configurações
API_BASE_URL = "http://localhost:8000"
TIMEOUT = 10

def print_header(title):
    """Imprime cabeçalho formatado."""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_test_result(endpoint, status_code, response_time, success=True):
    """Imprime resultado do teste."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {endpoint:<40} [{status_code}] ({response_time:.2f}s)")

def test_endpoint(method, endpoint, data=None, expected_status=200):
    """Testa um endpoint específico."""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        start_time = time.time()
        
        if method.upper() == "GET":
            response = requests.get(url, timeout=TIMEOUT)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=TIMEOUT)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, timeout=TIMEOUT)
        elif method.upper() == "DELETE":
            response = requests.delete(url, timeout=TIMEOUT)
        
        response_time = time.time() - start_time
        
        success = response.status_code == expected_status
        print_test_result(f"{method} {endpoint}", response.status_code, response_time, success)
        
        if success and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict):
                    # Mostrar apenas as chaves principais para resumo
                    keys = list(data.keys())[:5]  # Primeiras 5 chaves
                    print(f"     📋 Keys: {keys}")
                    if len(data.keys()) > 5:
                        print(f"     ... and {len(data.keys()) - 5} more")
            except:
                pass
        
        return response, success
        
    except requests.exceptions.RequestException as e:
        print_test_result(f"{method} {endpoint}", "ERROR", 0, False)
        print(f"     ❌ Error: {e}")
        return None, False

def main():
    """Função principal - executa todos os testes."""
    print_header("VALIDAÇÃO COMPLETA DA API PROTECAI MINI")
    print(f"🚀 Iniciando testes em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {API_BASE_URL}")
    
    # Contadores
    total_tests = 0
    passed_tests = 0
    
    # 1. Testes Básicos
    print_header("1. ENDPOINTS BÁSICOS")
    
    basic_endpoints = [
        ("GET", "/", 200),
        ("GET", "/health", 200),
        ("GET", "/info", 200),
        ("GET", "/docs", 200),
    ]
    
    for method, endpoint, expected_status in basic_endpoints:
        response, success = test_endpoint(method, endpoint, expected_status=expected_status)
        total_tests += 1
        if success:
            passed_tests += 1
    
    # 2. Testes de Rede
    print_header("2. ENDPOINTS DE REDE")
    
    network_endpoints = [
        ("GET", "/api/v1/network/info", 200),
        ("GET", "/api/v1/network/buses", 200),
        ("GET", "/api/v1/network/lines", 200),
        ("GET", "/api/v1/network/transformers", 200),
        ("GET", "/api/v1/network/loads", 200),
    ]
    
    for method, endpoint, expected_status in network_endpoints:
        response, success = test_endpoint(method, endpoint, expected_status=expected_status)
        total_tests += 1
        if success:
            passed_tests += 1
    
    # 3. Testes de Proteção
    print_header("3. ENDPOINTS DE PROTEÇÃO")
    
    protection_endpoints = [
        ("GET", "/api/v1/protection/devices", 200),
        ("GET", "/api/v1/protection/devices/reles", 200),
        ("GET", "/api/v1/protection/devices/disjuntores", 200),
        ("GET", "/api/v1/protection/devices/fusiveis", 200),
        ("GET", "/api/v1/protection/zones", 200),
        ("GET", "/api/v1/protection/status", 200),
        ("POST", "/api/v1/protection/coordination/analyze", 200),
    ]
    
    for method, endpoint, expected_status in protection_endpoints:
        response, success = test_endpoint(method, endpoint, expected_status=expected_status)
        total_tests += 1
        if success:
            passed_tests += 1
    
    # 4. Testes de Simulação
    print_header("4. ENDPOINTS DE SIMULAÇÃO")
    
    simulation_endpoints = [
        ("GET", "/api/v1/simulation/status", 200),
        ("GET", "/api/v1/simulation/scenarios", 200),
        ("GET", "/api/v1/simulation/results", 200),
    ]
    
    for method, endpoint, expected_status in simulation_endpoints:
        response, success = test_endpoint(method, endpoint, expected_status=expected_status)
        total_tests += 1
        if success:
            passed_tests += 1
    
    # 5. Testes de RL
    print_header("5. ENDPOINTS DE REINFORCEMENT LEARNING")
    
    rl_endpoints = [
        ("GET", "/api/v1/rl/status", 200),
        ("GET", "/api/v1/rl/models", 200),
        ("GET", "/api/v1/rl/training/status", 200),
    ]
    
    for method, endpoint, expected_status in rl_endpoints:
        response, success = test_endpoint(method, endpoint, expected_status=expected_status)
        total_tests += 1
        if success:
            passed_tests += 1
    
    # 6. Testes de Visualização
    print_header("6. ENDPOINTS DE VISUALIZAÇÃO")
    
    visualization_endpoints = [
        ("GET", "/api/v1/visualization/network", 200),
        ("GET", "/api/v1/visualization/protection", 200),
        ("GET", "/api/v1/visualization/reports", 200),
    ]
    
    for method, endpoint, expected_status in visualization_endpoints:
        response, success = test_endpoint(method, endpoint, expected_status=expected_status)
        total_tests += 1
        if success:
            passed_tests += 1
    
    # Teste específico - Obter detalhes de um relé
    print_header("7. TESTES ESPECÍFICOS DE FUNCIONALIDADE")
    
    # Teste de relé específico
    response, success = test_endpoint("GET", "/api/v1/protection/devices/reles/RELE_51_L0", 200)
    total_tests += 1
    if success:
        passed_tests += 1
    
    # Teste de análise de coordenação
    response, success = test_endpoint("POST", "/api/v1/protection/coordination/analyze", 200)
    total_tests += 1
    if success:
        passed_tests += 1
    
    # Resumo Final
    print_header("RESUMO DOS TESTES")
    print(f"📊 Total de Testes: {total_tests}")
    print(f"✅ Testes Aprovados: {passed_tests}")
    print(f"❌ Testes Falharam: {total_tests - passed_tests}")
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"🎯 Taxa de Sucesso: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 API ESTÁ FUNCIONANDO CORRETAMENTE!")
    elif success_rate >= 60:
        print("⚠️ API PARCIALMENTE FUNCIONAL - Alguns endpoints precisam de atenção")
    else:
        print("❌ API COM PROBLEMAS - Requer investigação")
    
    # Salvar relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"api_test_report_{timestamp}.json"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "success_rate": success_rate,
        "base_url": API_BASE_URL
    }
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📁 Relatório salvo em: {report_file}")

if __name__ == "__main__":
    main()
