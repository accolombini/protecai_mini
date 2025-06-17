"""
Script principal para orquestrar a geração da rede IEEE14 e executar simulações.
Executado a partir da raiz do projeto.
"""

import os
import sys
from simuladores.power_sim.ieee14 import IEEE14System
from simuladores.power_sim.scripts_simulacao import run_power_flow

# ==================================
# 🔍 Verificar se o arquivo JSON da rede IEEE 14 existe
# ==================================

json_path = "simuladores/power_sim/data/ieee14.json"

if not os.path.exists(json_path):
    print(f"⚠️ Arquivo JSON não encontrado: {json_path}")
    print("🔀 Você deve gerar este arquivo antes de executar o main")
    print("Por favor, gere a rede IEEE 14 antes de executar as simulações.")
    print("🔄 Executando o script de geração... python scripts/gerar_ieee14_json.py\n")
    sys.exit(1)

def main():
    print("🔌 Iniciando simulação IEEE 14 BARRAS")

    # Criar rede IEEE 14
    sistema = IEEE14System()
    net = sistema.get_network()

    # Executar fluxo de carga
    resultado = run_power_flow(net)

    # Exibir resultados
    print("✅ Simulação concluída com sucesso!")
    print("📊 Resultados:")
    for chave, valor in resultado.items():
        print(f"  - {chave}: {valor}")


if __name__ == "__main__":
    main()
