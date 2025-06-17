# simuladores/power_sim/gerar_ieee14_json.py

import pandapower.networks as pn
import pandapower as pp
import os


def export_ieee14(path: str) -> None:
    """
    Exporta a rede IEEE 14 barras para um arquivo JSON.

    Args:
        path (str): Caminho completo onde o arquivo será salvo.
    """
    net = pn.case14()
    pp.to_json(net, path)
    print(f"✅ Arquivo JSON salvo em: {path}")


if __name__ == "__main__":
    # Caminho absoluto com base na raiz do projeto
    DIR = os.path.dirname(__file__)
    json_path = os.path.abspath(os.path.join(DIR, "data", "ieee14.json"))

    export_ieee14(json_path)
