"""
Executa simulações elétricas com pandapower para uma rede fornecida.
"""

import pandapower as pp
import time


def run_power_flow(net, imprimir_resultado=False):
    """
    Executa o fluxo de carga e retorna resultados e tempo de execução.

    Args:
        net (pandapowerNet): rede elétrica carregada.
        imprimir_resultado (bool): se True, imprime os resultados ao final.

    Returns:
        dict: resultados da simulação contendo:
            - tempo de execução
            - carga total
            - perdas
            - tensão mínima e máxima
    """
    inicio = time.time()
    pp.runpp(net)
    fim = time.time()

    perdas = net.res_line.pl_mw.sum()
    tensoes = net.res_bus.vm_pu
    resultado = {
        "tempo_execucao_s": round(fim - inicio, 4),
        "carga_total_mw": round(net.res_load.p_mw.sum(), 4),
        "perdas_mw": round(perdas, 4),
        "tensao_min_pu": round(tensoes.min(), 4),
        "tensao_max_pu": round(tensoes.max(), 4)
    }

    if imprimir_resultado:
        print("\n[Resultados da Simulação]")
        for k, v in resultado.items():
            print(f"{k.replace('_', ' ').capitalize()}: {v}")

    return resultado
