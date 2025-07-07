#!/usr/bin/env python3
"""
Script para testar a API ProtecAI Mini.
Executa uma série de testes para validar todos os endpoints.
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path

# Configuração
BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_api():
    """Executa testes completos da API."""
    print("🔋 Teste da API ProtecAI Mini")
    print("=" * 50)
    
    # 1. Teste de health check
    print("\n1️⃣ Teste de Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 2. Teste de informações
    print("\n2️⃣ Teste de Informações")
    try:
        response = requests.get(f"{BASE_URL}/info", timeout=TIMEOUT)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Versão: {data.get('version')}")
        print(f"   Endpoints: {len(data.get('endpoints', []))}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Teste da rede elétrica
    print("\n3️⃣ Teste da Rede Elétrica")
    try:
        response = requests.get(f"{BASE_URL}/network/topology", timeout=TIMEOUT)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Barras: {data.get('total_buses', 0)}")
        print(f"   Linhas: {data.get('total_lines', 0)}")
        print(f"   Geradores: {data.get('total_generators', 0)}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 4. Teste dos dispositivos de proteção
    print("\n4️⃣ Teste dos Dispositivos de Proteção")
    try:
        response = requests.get(f"{BASE_URL}/protection/devices", timeout=TIMEOUT)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Total de dispositivos: {data.get('total_devices', 0)}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 5. Teste das zonas de proteção
    print("\n5️⃣ Teste das Zonas de Proteção")
    try:
        response = requests.get(f"{BASE_URL}/protection/zones", timeout=TIMEOUT)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Total de zonas: {data.get('total_zones', 0)}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 6. Teste de simulação rápida
    print("\n6️⃣ Teste de Simulação Rápida")
    try:
        simulation_config = {
            "fault_type": "short_circuit",
            "element_type": "bus",
            "element_id": 4,
            "fault_impedance": 0.01,
            "severity": "medium"
        }
        
        response = requests.post(
            f"{BASE_URL}/simulation/quick-analysis",
            json=simulation_config,
            timeout=TIMEOUT
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            fault_current = data.get('fault_analysis', {}).get('fault_current', {})
            print(f"   Corrente de falta: {fault_current.get('magnitude', 0):.2f} A")
            print(f"   Barras afetadas: {len(data.get('fault_analysis', {}).get('affected_buses', []))}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 7. Teste de templates de simulação
    print("\n7️⃣ Teste de Templates de Simulação")
    try:
        response = requests.get(f"{BASE_URL}/simulation/templates", timeout=TIMEOUT)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Templates disponíveis: {len(data.get('templates', []))}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 8. Teste de configuração RL
    print("\n8️⃣ Teste de Configuração RL")
    try:
        response = requests.get(f"{BASE_URL}/rl/config/default", timeout=TIMEOUT)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Episódios padrão: {data.get('episodes', 0)}")
        print(f"   Taxa de aprendizado: {data.get('learning_rate', 0)}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 9. Teste de modelos RL
    print("\n9️⃣ Teste de Modelos RL")
    try:
        response = requests.get(f"{BASE_URL}/rl/models", timeout=TIMEOUT)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Modelos disponíveis: {data.get('total', 0)}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 10. Teste de templates de visualização
    print("\n🔟 Teste de Templates de Visualização")
    try:
        response = requests.get(f"{BASE_URL}/visualization/templates", timeout=TIMEOUT)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Templates disponíveis: {len(data.get('templates', []))}")
        for template in data.get('templates', []):
            print(f"   - {template.get('name')}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 11. Teste de formatos suportados
    print("\n1️⃣1️⃣ Teste de Formatos Suportados")
    try:
        response = requests.get(f"{BASE_URL}/visualization/formats", timeout=TIMEOUT)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Formatos de imagem: {data.get('image_formats', [])}")
        print(f"   Formatos de relatório: {data.get('report_formats', [])}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 12. Teste de estatísticas
    print("\n1️⃣2️⃣ Teste de Estatísticas")
    try:
        response = requests.get(f"{BASE_URL}/simulation/statistics", timeout=TIMEOUT)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Total de simulações: {data.get('total_simulations', 0)}")
        print(f"   Taxa de sucesso: {data.get('success_rate', 0):.1f}%")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Teste da API concluído!")
    print(f"🕒 Executado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

def test_simulation_workflow():
    """Testa fluxo completo de simulação."""
    print("\n🔬 Teste de Fluxo de Simulação Completo")
    print("=" * 50)
    
    # 1. Criar configuração de simulação
    simulation_config = {
        "name": "Teste API - Curto-circuito",
        "description": "Simulação de teste via API",
        "faults": [
            {
                "fault_type": "short_circuit",
                "element_type": "bus",
                "element_id": 4,
                "fault_impedance": 0.01,
                "severity": "high"
            }
        ],
        "analysis_options": {
            "include_protection_analysis": True,
            "include_stability_analysis": True
        }
    }
    
    try:
        # 2. Iniciar simulação
        print("\n1️⃣ Iniciando simulação...")
        response = requests.post(
            f"{BASE_URL}/simulation/run",
            json=simulation_config,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            simulation_id = data.get('simulation_id')
            print(f"   ✅ Simulação iniciada: {simulation_id}")
            
            # 3. Monitorar progresso
            print("\n2️⃣ Monitorando progresso...")
            for i in range(10):  # Máximo 10 tentativas
                time.sleep(1)
                
                response = requests.get(f"{BASE_URL}/simulation/status/{simulation_id}")
                if response.status_code == 200:
                    status_data = response.json()
                    status = status_data.get('status')
                    print(f"   Status: {status}")
                    
                    if status == "completed":
                        print("   ✅ Simulação concluída!")
                        
                        # 4. Obter resultados
                        print("\n3️⃣ Obtendo resultados...")
                        response = requests.get(f"{BASE_URL}/simulation/results/{simulation_id}")
                        if response.status_code == 200:
                            results = response.json()
                            print(f"   Análise de faltas: {len(results.get('results', {}).get('fault_analysis', []))}")
                            print(f"   Ações de proteção: {len(results.get('results', {}).get('protection_response', []))}")
                            print(f"   Recomendações: {len(results.get('results', {}).get('recommendations', []))}")
                        break
                    
                    elif status == "failed":
                        print("   ❌ Simulação falhou!")
                        break
                else:
                    print(f"   ❌ Erro ao verificar status: {response.status_code}")
                    break
            
        else:
            print(f"   ❌ Erro ao iniciar simulação: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro no fluxo de simulação: {e}")

def test_rl_workflow():
    """Testa fluxo completo de RL."""
    print("\n🧠 Teste de Fluxo de RL Completo")
    print("=" * 50)
    
    # Configuração de treinamento reduzida para teste
    training_config = {
        "episodes": 50,  # Reduzido para teste
        "learning_rate": 0.01,
        "discount_factor": 0.95,
        "epsilon_start": 1.0,
        "epsilon_end": 0.1,
        "epsilon_decay": 0.99,
        "reward_weights": {
            "coordination": 0.4,
            "response_time": 0.3,
            "selectivity": 0.3
        }
    }
    
    try:
        # 1. Iniciar treinamento
        print("\n1️⃣ Iniciando treinamento RL...")
        response = requests.post(
            f"{BASE_URL}/rl/train",
            json=training_config,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            training_id = data.get('training_id')
            print(f"   ✅ Treinamento iniciado: {training_id}")
            
            # 2. Monitorar progresso
            print("\n2️⃣ Monitorando progresso...")
            for i in range(15):  # Máximo 15 tentativas
                time.sleep(2)
                
                response = requests.get(f"{BASE_URL}/rl/training/status/{training_id}")
                if response.status_code == 200:
                    status_data = response.json()
                    status = status_data.get('status')
                    progress = status_data.get('progress', 0)
                    current_reward = status_data.get('current_reward', 0)
                    
                    print(f"   Status: {status} | Progresso: {progress:.1f}% | Recompensa: {current_reward:.2f}")
                    
                    if status == "completed":
                        print("   ✅ Treinamento concluído!")
                        
                        # 3. Testar predição
                        print("\n3️⃣ Testando predição...")
                        test_state = {
                            "fault_current": 3000.0,
                            "fault_location": 4,
                            "system_loading": 0.7,
                            "protection_settings": {},
                            "network_topology": {}
                        }
                        
                        response = requests.post(
                            f"{BASE_URL}/rl/models/{training_id}/predict",
                            json=test_state,
                            timeout=TIMEOUT
                        )
                        
                        if response.status_code == 200:
                            prediction = response.json()
                            actions = prediction.get('prediction', {}).get('recommended_actions', [])
                            confidence = prediction.get('prediction', {}).get('confidence', 0)
                            print(f"   Ações recomendadas: {len(actions)}")
                            print(f"   Confiança: {confidence:.2f}")
                        break
                    
                    elif status == "failed":
                        print("   ❌ Treinamento falhou!")
                        break
                else:
                    print(f"   ❌ Erro ao verificar status: {response.status_code}")
                    break
            
        else:
            print(f"   ❌ Erro ao iniciar treinamento: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro no fluxo de RL: {e}")

def main():
    """Função principal."""
    print("🚀 Iniciando testes da API ProtecAI Mini")
    print("Certifique-se de que a API está rodando em http://localhost:8000")
    print()
    
    # Verificar se a API está rodando
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API está rodando!")
        else:
            print("❌ API não está respondendo corretamente")
            return
    except Exception as e:
        print(f"❌ Erro ao conectar com a API: {e}")
        print("Certifique-se de que a API está rodando com:")
        print("   python -m uvicorn src.backend.api.main:app --reload")
        return
    
    # Executar testes
    test_api()
    test_simulation_workflow()
    test_rl_workflow()
    
    print("\n🎉 Todos os testes concluídos!")

if __name__ == "__main__":
    main()
