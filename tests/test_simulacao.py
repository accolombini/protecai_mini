import pytest
from simuladores.power_sim.ieee14 import IEEE14System
from simuladores.power_sim.scripts_simulacao import run_power_flow


def test_simulacao_fluxo():
    """
    Executa o fluxo de carga e valida os resultados principais:
    - Carga total deve ser positiva
    - Tensões devem estar dentro dos limites operacionais
    - Simulação deve terminar em tempo razoável (< 5s)
    """
    net = IEEE14System().get_network()
    resultado = run_power_flow(net, imprimir_resultado=True)

    assert resultado["carga_total_mw"] > 0, "Carga total não pode ser zero"
    assert 0.9 <= resultado["tensao_min_pu"] <= 1.1, "Tensão mínima fora dos limites esperados"
    assert 0.9 <= resultado["tensao_max_pu"] <= 1.1, "Tensão máxima fora dos limites esperados"
    assert resultado["tempo_execucao_s"] < 5.0, "Simulação demorou mais que o esperado"
