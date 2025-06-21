# simuladores/power_sim/gerar_ieee14_json.py


import pandapower as pp
import os


def export_ieee14(path: str) -> None:
    """
    Gera e exporta a rede IEEE 14 barras utilizando a API moderna do pandapower.

    A estrutura segue o modelo clássico IEEE 14 com:
    - 14 barras
    - 20 linhas (ramais e conexões)
    - 11 cargas
    - 5 geradores (incluindo a barra slack)

    Args:
        path (str): Caminho completo onde o arquivo será salvo.
    """
    net = pp.create_empty_network()

    # Barras
    for i in range(14):
        pp.create_bus(net, vn_kv=132.0, name=f"Bus {i+1}")

    # Conexões (Linhas simplificadas entre as barras, valores técnicos genéricos)
    conexoes = [
        (0, 1), (0, 3), (1, 2), (1, 4), (2, 3), (2, 5), (3, 6),
        (4, 5), (5, 6), (6, 7), (6, 11), (7, 8), (8, 9), (9, 10),
        (9, 13), (10, 11), (11, 12), (12, 13)
    ]

    for from_bus, to_bus in conexoes:
        pp.create_line_from_parameters(
            net,
            from_bus=from_bus,
            to_bus=to_bus,
            length_km=1.0,
            r_ohm_per_km=0.1,
            x_ohm_per_km=0.2,
            c_nf_per_km=10.0,
            max_i_ka=0.5,
            name=f"Line {from_bus+1}-{to_bus+1}"
        )

    # Geração
    pp.create_ext_grid(net, bus=0, vm_pu=1.06, name="Slack Bus")

    geradores = [(1, 1.045), (2, 1.01), (3, 1.07), (5, 1.02)]
    for bus, vm_pu in geradores:
        pp.create_gen(net, bus=bus, p_mw=40.0,
                      vm_pu=vm_pu, name=f"Gen Bus {bus+1}")

    # Cargas (simplificadas)
    cargas = [
        (3, 100, 30), (4, 90, 20), (5, 120, 35), (6, 60, 10),
        (8, 100, 35), (9, 125, 50), (10, 90, 30), (11, 60, 10),
        (12, 45, 15), (13, 60, 20), (1, 20, 5)
    ]
    for bus, p, q in cargas:
        pp.create_load(net, bus=bus, p_mw=p, q_mvar=q,
                       name=f"Load Bus {bus+1}")

    # Exporta para JSON
    pp.to_json(net, path)
    print(f"✅ Arquivo JSON salvo em: {path}")


if __name__ == "__main__":
    DIR = os.path.dirname(__file__)
    json_path = os.path.abspath(os.path.join(DIR, "data", "ieee14.json"))
    export_ieee14(json_path)
