"""
Script principal para orquestrar a simulação do sistema IEEE 14 Barras com proteção.
Executado a partir da raiz do projeto.
"""

import os
import sys
from pathlib import Path
from simuladores.power_sim.ieee14 import IEEE14System
from simuladores.power_sim.scripts_simulacao import run_power_flow

# Caminho esperado do JSON com dispositivos de proteção
json_path = Path("simuladores/power_sim/data/ieee14_protecao.json")

if not json_path.exists():
    print(f"\n⚠️ Arquivo JSON não encontrado: {json_path}")
    print("🔄 Você deve gerar este arquivo com o script correto:")
    print("   ➜  python simuladores/power_sim/gerar_ieee14_protecao_json.py\n")
    sys.exit(1)


def main():
    print("\n🔌 Iniciando simulação do sistema IEEE 14 BARRAS com proteção...")

    # Carregar rede modificada com dispositivos de proteção
    sistema = IEEE14System()
    net = sistema.get_network()

    # Executar simulação elétrica
    resultado = run_power_flow(net, imprimir_resultado=True)

    print("\n✅ Simulação concluída com sucesso!")


if __name__ == "__main__":
    main()
