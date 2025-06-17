from simuladores.power_sim.ieee14 import IEEE14System
from simuladores.power_sim.scripts_simulacao import run_power_flow


def test_simulacao_fluxo():
    net = IEEE14System().net
    result = run_power_flow(net)

    assert result["carga_total_mw"] > 0
    assert 0 < result["tensao_min_pu"] <= 1.1
    assert 0 < result["tensao_max_pu"] <= 1.1
    assert result["tempo_execucao_s"] < 5.0, "Simulação demorou demais"
