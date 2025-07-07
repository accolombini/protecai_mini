#!/usr/bin/env python3
"""
Teste Abrangente da API ProtecAI Mini
Valida todos os endpoints com cenários críticos para plataformas petrolíferas
"""

import requests
import json
import time
import sys
from typing import Dict, List, Any

# Configuração da API
API_BASE = "http://localhost:8000"
API_V1 = f"{API_BASE}/api/v1"

class ProtecAITester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Registrar resultado do teste."""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        print(f"{status} | {test_name}")
        if details:
            print(f"      {details}")
            
        self.results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
    
    def check_api_health(self) -> bool:
        """Verificar se a API está respondendo."""
        try:
            response = requests.get(f"{API_BASE}/", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def test_protection_devices(self):
        """Testar endpoints de dispositivos de proteção."""
        print("\n🔧 TESTANDO DISPOSITIVOS DE PROTEÇÃO...")
        
        # 1. Listar todos os dispositivos
        try:
            response = requests.get(f"{API_V1}/protection/devices")
            success = response.status_code == 200
            data = response.json() if success else {}
            details = f"Status: {response.status_code}, Dispositivos: {data.get('total_devices', 0)}"
            self.log_test("GET /protection/devices", success, details)
        except Exception as e:
            self.log_test("GET /protection/devices", False, f"Erro: {str(e)}")
        
        # 2. Listar dispositivos por tipo
        for device_type in ["reles", "disjuntores", "fuseis"]:
            try:
                response = requests.get(f"{API_V1}/protection/devices/{device_type}")
                success = response.status_code in [200, 404]  # 404 é aceitável se não há dispositivos
                data = response.json() if response.status_code == 200 else {}
                count = data.get('count', 0) if response.status_code == 200 else 0
                details = f"Status: {response.status_code}, Count: {count}"
                self.log_test(f"GET /protection/devices/{device_type}", success, details)
            except Exception as e:
                self.log_test(f"GET /protection/devices/{device_type}", False, f"Erro: {str(e)}")
    
    def test_protection_zones(self):
        """Testar endpoints de zonas de proteção."""
        print("\n🗺️  TESTANDO ZONAS DE PROTEÇÃO...")
        
        # 1. Listar zonas
        try:
            response = requests.get(f"{API_V1}/protection/zones")
            success = response.status_code == 200
            data = response.json() if success else {}
            details = f"Status: {response.status_code}, Zonas: {data.get('total_zones', 0)}"
            self.log_test("GET /protection/zones", success, details)
        except Exception as e:
            self.log_test("GET /protection/zones", False, f"Erro: {str(e)}")
    
    def test_protection_status(self):
        """Testar status geral do sistema."""
        print("\n📊 TESTANDO STATUS DO SISTEMA...")
        
        try:
            response = requests.get(f"{API_V1}/protection/status")
            success = response.status_code == 200
            data = response.json() if success else {}
            status = data.get('system_status', 'UNKNOWN')
            coverage = data.get('coverage', '0%')
            details = f"Status: {response.status_code}, Sistema: {status}, Cobertura: {coverage}"
            self.log_test("GET /protection/status", success, details)
        except Exception as e:
            self.log_test("GET /protection/status", False, f"Erro: {str(e)}")
    
    def test_compliance_check(self):
        """Testar verificação de conformidade."""
        print("\n📋 TESTANDO CONFORMIDADE NORMATIVA...")
        
        # Standards críticos para petróleo
        standards = ["NBR_5410", "API_RP_14C", "IEC_61850", "IEEE_C37_112"]
        
        payload = {
            "standards": standards,
            "detailed_report": True
        }
        
        try:
            response = requests.post(f"{API_V1}/protection/compliance/check", json=payload)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                overall = data.get('overall_compliance', {})
                compliant = overall.get('compliant', False)
                score = overall.get('score', 0.0)
                compliant_count = data.get('summary', {}).get('compliant_standards', 0)
                
                details = f"Status: {response.status_code}, Conformes: {compliant_count}/{len(standards)}, Score: {score:.2f}, Aprovado: {compliant}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("POST /protection/compliance/check", success, details)
            
            # Validar conformidade crítica
            if success and data:
                nbr_compliant = data.get('standards', {}).get('NBR_5410', {}).get('compliant', False)
                api_compliant = data.get('standards', {}).get('API_RP_14C', {}).get('compliant', False)
                
                critical_compliance = nbr_compliant and api_compliant
                self.log_test("Conformidade Crítica (NBR+API)", critical_compliance, 
                            f"NBR_5410: {nbr_compliant}, API_RP_14C: {api_compliant}")
                            
        except Exception as e:
            self.log_test("POST /protection/compliance/check", False, f"Erro: {str(e)}")
    
    def test_protection_scenarios(self):
        """Testar cenários de proteção com diferentes configurações."""
        print("\n⚡ TESTANDO CENÁRIOS DE PROTEÇÃO...")
        
        scenarios = [
            {
                "name": "Falta Severa com RL",
                "data": {
                    "scenario_type": "fault",
                    "location": "bus_1",
                    "severity": 0.8,
                    "use_rl": True,
                    "training_episodes": 100
                }
            },
            {
                "name": "Falta Severa sem RL",
                "data": {
                    "scenario_type": "fault",
                    "location": "bus_1", 
                    "severity": 0.8,
                    "use_rl": False,
                    "training_episodes": 0
                }
            },
            {
                "name": "Mudança de Carga com RL",
                "data": {
                    "scenario_type": "load_change",
                    "location": "line_2",
                    "severity": 0.6,
                    "use_rl": True,
                    "training_episodes": 50
                }
            },
            {
                "name": "Falha de Equipamento",
                "data": {
                    "scenario_type": "equipment_failure",
                    "location": "relay_3",
                    "severity": 0.7,
                    "use_rl": True,
                    "training_episodes": 75
                }
            }
        ]
        
        for scenario in scenarios:
            try:
                response = requests.post(f"{API_V1}/protection/scenarios", json=scenario["data"])
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    compliance = data.get('compliance_assessment', {})
                    safety_level = compliance.get('safety_level', 'UNKNOWN')
                    overall_score = compliance.get('overall_score', 0.0)
                    rl_enabled = scenario["data"]["use_rl"]
                    
                    details = f"Status: {response.status_code}, Safety: {safety_level}, Score: {overall_score:.2f}, RL: {rl_enabled}"
                    
                    # Teste adicional: RL deve melhorar performance em cenários críticos
                    if rl_enabled and scenario["data"]["severity"] > 0.7:
                        rl_effective = overall_score > 0.8 and safety_level in ["EXCELLENT", "ACCEPTABLE"]
                        details += f", RL Efetivo: {rl_effective}"
                else:
                    details = f"Status: {response.status_code}"
                    
                self.log_test(f"Cenário: {scenario['name']}", success, details)
                
            except Exception as e:
                self.log_test(f"Cenário: {scenario['name']}", False, f"Erro: {str(e)}")
    
    def test_edge_cases(self):
        """Testar casos extremos e validações."""
        print("\n🔥 TESTANDO CASOS EXTREMOS...")
        
        # 1. Cenário com parâmetros inválidos
        try:
            invalid_scenario = {
                "scenario_type": "invalid_type",
                "location": "nowhere",
                "severity": 2.0,  # > 1.0
                "use_rl": True
            }
            response = requests.post(f"{API_V1}/protection/scenarios", json=invalid_scenario)
            success = response.status_code == 400  # Deve rejeitar
            details = f"Status: {response.status_code} (esperado 400)"
            self.log_test("Cenário Inválido", success, details)
        except Exception as e:
            self.log_test("Cenário Inválido", False, f"Erro: {str(e)}")
        
        # 2. Standards não reconhecidos
        try:
            invalid_compliance = {
                "standards": ["INVALID_STANDARD", "ANOTHER_FAKE"],
                "detailed_report": True
            }
            response = requests.post(f"{API_V1}/protection/compliance/check", json=invalid_compliance)
            success = response.status_code == 200  # API deve lidar graciosamente
            
            if success:
                data = response.json()
                # Verificar se standards inválidos são identificados
                invalid_std_data = data.get('standards', {}).get('INVALID_STANDARD', {})
                properly_handled = not invalid_std_data.get('compliant', True)
                details = f"Status: {response.status_code}, Tratamento: {properly_handled}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Standards Inválidos", success, details)
        except Exception as e:
            self.log_test("Standards Inválidos", False, f"Erro: {str(e)}")
    
    def test_petroleum_readiness(self):
        """Teste específico para aprovação em ambiente petrolífero."""
        print("\n🛢️  TESTANDO PRONTIDÃO PARA PETRÓLEO...")
        
        # Cenário crítico que deve ser aprovado para petróleo
        petroleum_scenario = {
            "scenario_type": "fault",
            "location": "critical_bus",
            "severity": 0.9,  # Severidade máxima
            "use_rl": True,   # RL deve estar habilitado
            "training_episodes": 200  # Treinamento extenso
        }
        
        try:
            response = requests.post(f"{API_V1}/protection/scenarios", json=petroleum_scenario)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                compliance = data.get('compliance_assessment', {})
                safety_level = compliance.get('safety_level', 'CRITICAL_FAILURE')
                overall_score = compliance.get('overall_score', 0.0)
                standards_met = compliance.get('standards_met', [])
                
                # Critérios rigorosos para petróleo
                petroleum_ready = (
                    safety_level == "EXCELLENT" and
                    overall_score > 0.90 and
                    "NBR_5410" in standards_met and
                    "API_RP_14C" in standards_met
                )
                
                # Verificar se RL está sendo efetivo
                rl_impact = compliance.get('rl_impact', {})
                rl_effective = rl_impact.get('effectiveness') == "EXCELENTE"
                
                details = f"Safety: {safety_level}, Score: {overall_score:.2f}, Standards: {len(standards_met)}/4, RL: {rl_effective}, Aprovado: {petroleum_ready}"
                
                self.log_test("Prontidão Petrolífera", petroleum_ready, details)
                
                # Teste adicional: tempo de resposta
                fault_analysis = data.get('results', {}).get('fault_analysis', {})
                clearance_time = fault_analysis.get('clearance_time', 1.0)
                fast_response = clearance_time < 0.1  # < 100ms
                
                self.log_test("Tempo de Resposta Crítico", fast_response, 
                            f"Clearance: {clearance_time*1000:.0f}ms (req: <100ms)")
                
            else:
                details = f"Status: {response.status_code}"
                self.log_test("Prontidão Petrolífera", False, details)
                
        except Exception as e:
            self.log_test("Prontidão Petrolífera", False, f"Erro: {str(e)}")
    
    def run_all_tests(self):
        """Executar todos os testes."""
        print("🚀 INICIANDO TESTE ABRANGENTE DA API PROTECAI MINI")
        print("=" * 60)
        
        # Verificar se API está online
        if not self.check_api_health():
            print("❌ ERRO: API não está respondendo em http://localhost:8000")
            print("   Certifique-se de que o servidor está executando:")
            print("   python start_api.py")
            return False
        
        print("✅ API está online e respondendo")
        
        # Executar todos os grupos de testes
        self.test_protection_devices()
        self.test_protection_zones()
        self.test_protection_status()
        self.test_compliance_check()
        self.test_protection_scenarios()
        self.test_edge_cases()
        self.test_petroleum_readiness()
        
        # Relatório final
        self.print_final_report()
        
        return self.failed_tests == 0
    
    def print_final_report(self):
        """Imprimir relatório final."""
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL DO TESTE")
        print("=" * 60)
        
        print(f"Total de Testes: {self.total_tests}")
        print(f"✅ Aprovados: {self.passed_tests}")
        print(f"❌ Falharam: {self.failed_tests}")
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"📈 Taxa de Sucesso: {success_rate:.1f}%")
        
        if self.failed_tests == 0:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("✅ Sistema aprovado para operação em ambiente petrolífero")
        else:
            print(f"\n⚠️  {self.failed_tests} TESTES FALHARAM")
            print("❌ Sistema necessita correções antes da operação")
            
            # Listar testes que falharam
            print("\nTestes que falharam:")
            for result in self.results:
                if not result["passed"]:
                    print(f"  • {result['test']}: {result['details']}")
        
        print("\n" + "=" * 60)


def main():
    """Função principal."""
    tester = ProtecAITester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
