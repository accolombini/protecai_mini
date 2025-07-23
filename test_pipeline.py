#!/usr/bin/env python3
"""
🔧 Pipeline de Testes ProtecAI Mini
===================================

Script completo para validar toda a pipeline do sistema antes da demonstração.
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any

class ProtecAIPipelineTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        self.passed = 0
        self.failed = 0
        
    def log_result(self, test_name: str, passed: bool, message: str = ""):
        """Registra resultado do teste"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
            
        print(f"{status} | {test_name}: {message}")
        
    def test_health_endpoint(self):
        """Testa endpoint de saúde"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_result("Health Endpoint", True, "API está saudável")
                    return True
                else:
                    self.log_result("Health Endpoint", False, f"Status não saudável: {data.get('status')}")
            else:
                self.log_result("Health Endpoint", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Health Endpoint", False, f"Erro: {str(e)}")
        return False
        
    def test_zones_configuration(self):
        """Testa configuração das zonas"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/protection-zones/zones/detailed-configuration", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Verificar estrutura básica
                if "zone_configuration" in data:
                    zones = data["zone_configuration"]
                    
                    # Verificar zona primária
                    if "zona_1_primaria" in zones:
                        z1 = zones["zona_1_primaria"]
                        if z1.get("selectivity_index", 0) > 90:
                            self.log_result("Zones Configuration", True, f"Zona 1 seletividade: {z1.get('selectivity_index')}%")
                            return True
                        else:
                            self.log_result("Zones Configuration", False, f"Seletividade baixa: {z1.get('selectivity_index')}%")
                    else:
                        self.log_result("Zones Configuration", False, "Zona 1 não encontrada")
                else:
                    self.log_result("Zones Configuration", False, "Estrutura de dados inválida")
            else:
                self.log_result("Zones Configuration", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Zones Configuration", False, f"Erro: {str(e)}")
        return False
        
    def test_realtime_status(self):
        """Testa status em tempo real"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/protection-zones/zones/real-time-status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if "zones_status" in data and "summary" in data:
                    summary = data["summary"]
                    total_zones = summary.get("total_zones", 0)
                    
                    if total_zones > 0:
                        self.log_result("Real-time Status", True, f"{total_zones} zonas monitoradas")
                        return True
                    else:
                        self.log_result("Real-time Status", False, "Nenhuma zona monitorada")
                else:
                    self.log_result("Real-time Status", False, "Estrutura de resposta inválida")
            else:
                self.log_result("Real-time Status", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Real-time Status", False, f"Erro: {str(e)}")
        return False
        
    def test_fault_simulation(self):
        """Testa simulação de falta"""
        try:
            payload = {
                "location": {
                    "line": "line_2_5",
                    "position_km": 3.2
                },
                "type": "phase_to_ground",
                "magnitude": 2.5
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/protection-zones/fault-simulation/detailed-analysis",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "fault_simulation" in data and "simulation_id" in data:
                    fault_sim = data["fault_simulation"]
                    
                    # Verificar se dispositivos primários operaram
                    devices_op = fault_sim.get("devices_operation", {})
                    primary_ops = devices_op.get("primary_operation", [])
                    
                    if primary_ops:
                        device_name = primary_ops[0].get("device", "unknown")
                        op_time = primary_ops[0].get("operation_time", 0)
                        self.log_result("Fault Simulation", True, f"{device_name} operou em {op_time*1000:.1f}ms")
                        return True
                    else:
                        self.log_result("Fault Simulation", False, "Nenhum dispositivo primário operou")
                else:
                    self.log_result("Fault Simulation", False, "Estrutura de resposta inválida")
            else:
                self.log_result("Fault Simulation", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Fault Simulation", False, f"Erro: {str(e)}")
        return False
        
    def test_network_visualization(self):
        """Testa dados de visualização da rede"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/protection-zones/visualization/complete", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if "network_topology" in data:
                    topology = data["network_topology"]
                    buses = topology.get("buses", {})
                    lines = topology.get("lines", {})
                    
                    if len(buses) >= 14 and len(lines) >= 10:
                        self.log_result("Network Visualization", True, f"{len(buses)} barras, {len(lines)} linhas")
                        return True
                    else:
                        self.log_result("Network Visualization", False, f"Dados incompletos: {len(buses)} barras, {len(lines)} linhas")
                else:
                    self.log_result("Network Visualization", False, "Estrutura de dados inválida")
            else:
                self.log_result("Network Visualization", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Network Visualization", False, f"Erro: {str(e)}")
        return False
        
    def test_device_management(self):
        """Testa gerenciamento de dispositivos"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/protection-zones/zones", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    total_zones = len(data)
                    
                    if total_zones > 0:
                        self.log_result("Device Management", True, f"{total_zones} zonas de proteção encontradas")
                        return True
                    else:
                        self.log_result("Device Management", False, "Nenhuma zona encontrada")
                else:
                    self.log_result("Device Management", False, "Estrutura de dados inválida")
            else:
                self.log_result("Device Management", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Device Management", False, f"Erro: {str(e)}")
        return False
        
    def test_standards_compliance(self):
        """Testa conformidade com normas"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/protection-zones/standards/compliance-monitoring", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if "compliance_summary" in data:
                    compliance = data["compliance_summary"]
                    overall_score = compliance.get("overall_score", 0)
                    
                    if overall_score > 80:
                        self.log_result("Standards Compliance", True, f"Score de conformidade: {overall_score}%")
                        return True
                    else:
                        self.log_result("Standards Compliance", False, f"Score baixo: {overall_score}%")
                else:
                    self.log_result("Standards Compliance", False, "Dados de conformidade não encontrados")
            else:
                self.log_result("Standards Compliance", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Standards Compliance", False, f"Erro: {str(e)}")
        return False
        
    def run_all_tests(self):
        """Executa todos os testes"""
        print("🔧 ProtecAI Mini - Pipeline de Testes")
        print("=" * 50)
        print(f"🌐 Base URL: {self.base_url}")
        print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Lista de testes
        tests = [
            ("Saúde da API", self.test_health_endpoint),
            ("Configuração de Zonas", self.test_zones_configuration),
            ("Status Tempo Real", self.test_realtime_status),
            ("Simulação de Falta", self.test_fault_simulation),
            ("Visualização da Rede", self.test_network_visualization),
            ("Gerenciamento de Dispositivos", self.test_device_management),
            ("Conformidade com Normas", self.test_standards_compliance),
        ]
        
        # Executar testes
        for test_name, test_func in tests:
            print(f"🧪 Executando: {test_name}...")
            test_func()
            time.sleep(0.5)  # Pequena pausa entre testes
            
        print()
        print("=" * 50)
        print("📊 RESUMO DOS TESTES")
        print("=" * 50)
        print(f"✅ Passou: {self.passed}")
        print(f"❌ Falhou: {self.failed}")
        print(f"📊 Total: {len(self.results)}")
        
        if self.failed == 0:
            print("🎉 TODOS OS TESTES PASSARAM! Sistema pronto para demonstração.")
            return True
        else:
            print(f"⚠️  {self.failed} teste(s) falharam. Revisar antes da demonstração.")
            return False
            
    def generate_report(self, filename: str = None):
        """Gera relatório detalhado"""
        if filename is None:
            filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        report = {
            "test_run": {
                "timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
                "total_tests": len(self.results),
                "passed": self.passed,
                "failed": self.failed,
                "success_rate": (self.passed / len(self.results)) * 100 if self.results else 0
            },
            "results": self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"📄 Relatório salvo: {filename}")
        return filename

def main():
    """Função principal"""
    print("🚀 Iniciando testes da pipeline ProtecAI Mini...")
    
    # Verificar se API está rodando
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code != 200:
            print("❌ API não está respondendo. Inicie com: python start_api.py")
            sys.exit(1)
    except:
        print("❌ API não está rodando. Inicie com: python start_api.py")
        sys.exit(1)
        
    # Executar testes
    tester = ProtecAIPipelineTester()
    success = tester.run_all_tests()
    
    # Gerar relatório
    report_file = tester.generate_report()
    
    # Exit code para CI/CD
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
