#!/usr/bin/env python3
"""
Script unificado para demonstração completa da API ProtecAI Mini.
Inclui inicialização, testes e demonstração de funcionalidades.
"""

import subprocess
import sys
import time
import requests
from pathlib import Path
from datetime import datetime
import json


def check_dependencies():
    """Verifica se todas as dependências estão instaladas."""
    print("🔍 Verificando dependências...")

    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "requests",
        "pandas",
        "numpy",
        "matplotlib",
        "pandapower"
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package}")

    if missing_packages:
        print(f"\n⚠️  Pacotes faltando: {', '.join(missing_packages)}")
        print("Execute: pip install -r requirements.txt")
        return False

    print("✅ Todas as dependências estão instaladas!")
    return True


def check_data_files():
    """Verifica se os arquivos de dados estão presentes."""
    print("\n📁 Verificando arquivos de dados...")

    required_files = [
        "simuladores/power_sim/data/ieee14_protecao.json",
        "simuladores/power_sim/gerar_ieee14_json.py",
        "simuladores/power_sim/visualizar_toplogia_protecao.py",
        "simuladores/power_sim/rl_protection_agent.py"
    ]

    missing_files = []

    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"   ❌ {file_path}")

    if missing_files:
        print(f"\n⚠️  Arquivos faltando: {', '.join(missing_files)}")
        print("Execute os scripts de geração primeiro!")
        return False

    print("✅ Todos os arquivos de dados estão presentes!")
    return True


def start_api_server():
    """Inicia o servidor da API."""
    print("\n🚀 Iniciando servidor da API...")

    try:
        # Comando para iniciar a API
        cmd = [
            sys.executable, "-m", "uvicorn",
            "src.backend.api.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ]

        print("📡 Servidor iniciando em: http://localhost:8000")
        print("📚 Documentação: http://localhost:8000/docs")
        print("🔄 Documentação alternativa: http://localhost:8000/redoc")

        # Iniciar processo em background
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Aguardar um pouco para o servidor iniciar
        print("⏳ Aguardando servidor inicializar...")
        time.sleep(5)

        # Verificar se o servidor está rodando
        try:
            response = requests.get("http://localhost:8000/health", timeout=10)
            if response.status_code == 200:
                print("✅ Servidor iniciado com sucesso!")
                return process
            else:
                print(
                    f"❌ Servidor não está respondendo: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao conectar com o servidor: {e}")
            return None

    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return None


def run_api_tests():
    """Executa testes da API."""
    print("\n🧪 Executando testes da API...")

    try:
        # Executar script de teste
        result = subprocess.run([sys.executable, "test_api.py"],
                                capture_output=True, text=True, timeout=60)

        print("📊 Resultado dos testes:")
        print(result.stdout)

        if result.stderr:
            print("⚠️  Avisos/Erros:")
            print(result.stderr)

        if result.returncode == 0:
            print("✅ Todos os testes foram executados!")
        else:
            print(f"❌ Alguns testes falharam (código: {result.returncode})")

    except subprocess.TimeoutExpired:
        print("⏰ Timeout nos testes da API")
    except Exception as e:
        print(f"❌ Erro ao executar testes: {e}")


def demonstrate_features():
    """Demonstra as funcionalidades principais da API."""
    print("\n🎯 Demonstração das Funcionalidades")
    print("=" * 50)

    base_url = "http://localhost:8000"

    # 1. Informações da API
    print("\n1️⃣ Informações da API")
    try:
        response = requests.get(f"{base_url}/info")
        if response.status_code == 200:
            info = response.json()
            print(f"   📊 Versão: {info.get('version')}")
            print(f"   📅 Iniciado em: {info.get('startup_time')}")
            print(f"   🔗 Endpoints: {len(info.get('endpoints', []))}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    # 2. Status da rede
    print("\n2️⃣ Status da Rede Elétrica")
    try:
        response = requests.get(f"{base_url}/network/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   🏗️  Status: {status.get('status')}")
            print(f"   ⚡ Barras: {status.get('total_buses')}")
            print(f"   🔌 Linhas: {status.get('total_lines')}")
            print(f"   🔋 Geradores: {status.get('total_generators')}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    # 3. Dispositivos de proteção
    print("\n3️⃣ Dispositivos de Proteção")
    try:
        response = requests.get(f"{base_url}/protection/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   🛡️  Status: {status.get('system_status')}")
            print(f"   📱 Dispositivos: {status.get('total_devices')}")
            print(f"   ✅ Habilitados: {status.get('enabled_devices')}")
            print(f"   📊 Cobertura: {status.get('coverage')}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    # 4. Simulação rápida
    print("\n4️⃣ Simulação Rápida")
    try:
        fault_config = {
            "fault_type": "short_circuit",
            "element_type": "bus",
            "element_id": 4,
            "severity": "medium"
        }

        response = requests.post(
            f"{base_url}/simulation/quick-analysis", json=fault_config)
        if response.status_code == 200:
            analysis = response.json()
            fault_data = analysis.get('fault_analysis', {})
            print(f"   ⚡ Tipo de falta: {fault_data.get('fault_type')}")
            print(
                f"   🔢 Corrente: {fault_data.get('fault_current', {}).get('magnitude', 0):.0f} A")
            print(
                f"   📍 Barras afetadas: {len(fault_data.get('affected_buses', []))}")
            print(
                f"   ⏱️  Tempo de recuperação: {fault_data.get('recovery_time', {}).get('total_recovery_time', 0):.2f} s")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    # 5. Configuração RL
    print("\n5️⃣ Configuração de RL")
    try:
        response = requests.get(f"{base_url}/rl/performance/metrics")
        if response.status_code == 200:
            metrics = response.json()
            print(f"   🧠 Modelos: {metrics.get('total_models')}")
            print(f"   🎯 Treinamentos: {metrics.get('total_trainings')}")
            print(f"   ✅ Sucessos: {metrics.get('successful_trainings')}")
            print(
                f"   🏆 Melhor recompensa: {metrics.get('best_overall_reward', 0):.2f}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")


def interactive_demo():
    """Demonstração interativa."""
    print("\n🎮 Demonstração Interativa")
    print("=" * 50)

    while True:
        print("\n🎯 Escolha uma opção:")
        print("1. 📊 Visualizar status da rede")
        print("2. 🛡️  Analisar proteção")
        print("3. ⚡ Simular falta")
        print("4. 🧠 Configurar RL")
        print("5. 📈 Gerar visualização")
        print("6. 📝 Gerar relatório")
        print("0. 🚪 Sair")

        choice = input("\n➤ Opção: ").strip()

        if choice == "0":
            print("👋 Até logo!")
            break
        elif choice == "1":
            show_network_status()
        elif choice == "2":
            analyze_protection()
        elif choice == "3":
            simulate_fault()
        elif choice == "4":
            configure_rl()
        elif choice == "5":
            generate_visualization()
        elif choice == "6":
            generate_report()
        else:
            print("❌ Opção inválida!")


def show_network_status():
    """Mostra status da rede."""
    print("\n📊 Status da Rede")
    try:
        response = requests.get("http://localhost:8000/network/topology")
        if response.status_code == 200:
            data = response.json()
            print(f"   Barras: {data.get('total_buses')}")
            print(f"   Linhas: {data.get('total_lines')}")
            print(f"   Transformadores: {data.get('total_transformers')}")
            print(f"   Geradores: {data.get('total_generators')}")
            print(f"   Cargas: {data.get('total_loads')}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")


def analyze_protection():
    """Analisa coordenação de proteção."""
    print("\n🛡️  Análise de Proteção")
    try:
        response = requests.post(
            "http://localhost:8000/protection/coordination/analyze")
        if response.status_code == 200:
            data = response.json()
            print(f"   Dispositivos: {data.get('total_devices')}")
            print(f"   Problemas: {len(data.get('coordination_issues', []))}")
            print(f"   Recomendações: {len(data.get('recommendations', []))}")
            print(f"   Qualidade: {data.get('coordination_quality')}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")


def simulate_fault():
    """Simula uma falta."""
    print("\n⚡ Simulação de Falta")
    fault_config = {
        "fault_type": "short_circuit",
        "element_type": "bus",
        "element_id": 4,
        "severity": "high"
    }

    try:
        response = requests.post(
            "http://localhost:8000/simulation/quick-analysis", json=fault_config)
        if response.status_code == 200:
            data = response.json()
            fault_data = data.get('fault_analysis', {})
            print(
                f"   Corrente: {fault_data.get('fault_current', {}).get('magnitude', 0):.0f} A")
            print(
                f"   Impacto: {fault_data.get('system_impact', {}).get('stability')}")
            print(f"   Ações: {len(fault_data.get('protection_actions', []))}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")


def configure_rl():
    """Configura RL."""
    print("\n🧠 Configuração de RL")
    try:
        config = {
            "episodes": 100,
            "learning_rate": 0.01,
            "discount_factor": 0.95
        }

        response = requests.post("http://localhost:8000/rl/train", json=config)
        if response.status_code == 200:
            data = response.json()
            print(f"   Treinamento iniciado: {data.get('training_id')}")
            print(f"   Status: {data.get('status')}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")


def generate_visualization():
    """Gera visualização."""
    print("\n📈 Geração de Visualização")
    try:
        config = {
            "visualization_type": "network_topology",
            "parameters": {"show_protection_devices": True},
            "title": "Rede IEEE 14 Barras"
        }

        response = requests.post(
            "http://localhost:8000/visualization/generate", json=config)
        if response.status_code == 200:
            data = response.json()
            print(f"   Visualização: {data.get('filename')}")
            print(f"   Tipo: {data.get('type')}")
            print(f"   Status: {data.get('status')}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")


def generate_report():
    """Gera relatório."""
    print("\n📝 Geração de Relatório")
    try:
        config = {
            "report_type": "system_overview",
            "include_sections": ["summary", "analysis", "recommendations"],
            "output_format": "html"
        }

        response = requests.post(
            "http://localhost:8000/visualization/report/generate", json=config)
        if response.status_code == 200:
            data = response.json()
            print(f"   Relatório: {data.get('filename')}")
            print(f"   Tipo: {data.get('type')}")
            print(f"   Status: {data.get('status')}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")


def main():
    """Função principal."""
    print("🔋 ProtecAI Mini - Demonstração Completa da API")
    print("=" * 60)
    print(f"📅 Executado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()

    # Verificações iniciais
    if not check_dependencies():
        return 1

    if not check_data_files():
        return 1

    # Menu principal
    while True:
        print("\n🎯 Menu Principal")
        print("=" * 30)
        print("1. 🚀 Iniciar servidor da API")
        print("2. 🧪 Executar testes da API")
        print("3. 🎯 Demonstrar funcionalidades")
        print("4. 🎮 Demonstração interativa")
        print("5. 📚 Abrir documentação")
        print("0. 🚪 Sair")

        choice = input("\n➤ Escolha uma opção: ").strip()

        if choice == "0":
            print("👋 Até logo!")
            break
        elif choice == "1":
            server_process = start_api_server()
            if server_process:
                try:
                    print("🔄 Servidor rodando... Pressione Ctrl+C para parar")
                    server_process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Parando servidor...")
                    server_process.terminate()
                    server_process.wait()
        elif choice == "2":
            run_api_tests()
        elif choice == "3":
            demonstrate_features()
        elif choice == "4":
            interactive_demo()
        elif choice == "5":
            print("📚 Documentação disponível em:")
            print("   http://localhost:8000/docs")
            print("   http://localhost:8000/redoc")
        else:
            print("❌ Opção inválida!")

    return 0


if __name__ == "__main__":
    exit(main())
