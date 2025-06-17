from simuladores.power_sim.ieee14 import IEEE14System


def test_ieee14_carga_total():
    net = IEEE14System().net
    total_load = net.load.p_mw.sum()
    assert total_load > 0, "Carga total deveria ser maior que zero"


def test_ieee14_barras():
    net = IEEE14System().net
    assert len(net.bus) == 14, "Deveria haver 14 barras no sistema IEEE 14"
