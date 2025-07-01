"""
Script: gerar_ieee14_protecao_json.py
Descricao: Gera a rede IEEE 14 modificada para incluir transformadores, dispositivos de protecao e ajustar a tensao nominal
Autor: Projeto ProtecAI_MINI
"""

import pandapower.networks as nw
import pandapower as pp
import pandas as pd
import numpy as np
import json
from pathlib import Path


def criar_geodata(net):
    """Gera coordenadas circulares mínimas para visualização gráfica da rede elétrica."""
    n = len(net.bus)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    net.bus_geodata = pd.DataFrame({
        "x": 100 * np.cos(angles),
        "y": 100 * np.sin(angles)
    })
    net.line_geodata = pd.DataFrame({"coords": [
        [(net.bus_geodata.iloc[row.from_bus].x, net.bus_geodata.iloc[row.from_bus].y),
         (net.bus_geodata.iloc[row.to_bus].x, net.bus_geodata.iloc[row.to_bus].y)]
        for _, row in net.line.iterrows()
    ]})


def inserir_trafos(net):
    """Substitui pares de linhas por transformadores de 25 MVA com parâmetros definidos e nomes explícitos."""
    linhas_para_substituir = [(0, 4), (1, 5)]
    for from_bus, to_bus in linhas_para_substituir:
        linha_idx = net.line[(net.line.from_bus == from_bus)
                             & (net.line.to_bus == to_bus)].index
        net.line.drop(index=linha_idx, inplace=True)
        pp.create_transformer_from_parameters(
            net,
            hv_bus=from_bus,
            lv_bus=to_bus,
            sn_mva=25.0,
            vn_hv_kv=13.8,
            vn_lv_kv=13.8,
            vk_percent=12.2,
            vkr_percent=0.25,
            pfe_kw=60.0,
            i0_percent=0.06,
            shift_degree=0.0,
            tap_side="hv",
            tap_neutral=0,
            tap_min=-9,
            tap_max=9,
            tap_step_percent=1.5,
            name=f"TR_25MVA_B{from_bus}_B{to_bus}"
        )


def adicionar_dispositivos_protecao(net):
    """Adiciona relés, disjuntores e fusíveis simulados à estrutura do sistema."""
    trafos = net.trafo.index.tolist()
    geradores = net.gen.index.tolist()

    net.protection_devices = {
        "reles": [
            {"tipo": "51", "nome": "RELE_51_B3_B4", "barras": [3, 4]},
            {"tipo": "51", "nome": "RELE_51_B4_B5", "barras": [4, 5]},
            {"tipo": "51", "nome": "RELE_51_B5_B6", "barras": [5, 6]},
            {"tipo": "51", "nome": "RELE_51_B6_B13", "barras": [6, 13]},
            {"tipo": "67", "nome": "RELE_67_B2", "barras": [2]},
            {"tipo": "67", "nome": "RELE_67_B3", "barras": [3]},
            {"tipo": "67", "nome": "RELE_67_B6", "barras": [6]},
            {"tipo": "87T", "nome": "RELE_87T_B2_B4", "barras": [
                2, 4], "element_type": "trafo", "element_id": trafos[0]},
            {"tipo": "87T", "nome": "RELE_87T_B4_B5", "barras": [
                4, 5], "element_type": "trafo", "element_id": trafos[1]},
            {"tipo": "27_59", "nome": "RELE_27_59_B7", "barras": [7]},
            {"tipo": "27_59", "nome": "RELE_27_59_B9", "barras": [9]},
            {"tipo": "27_59", "nome": "RELE_27_59_B10", "barras": [10]},
            {"tipo": "27_59", "nome": "RELE_27_59_B14", "barras": [14]}
        ],
        "disjuntores": [
            {"nome": "DISJ_B4", "barra": 4, "element_type": "bus", "element_id": 4},
            {"nome": "DISJ_B5", "barra": 5, "element_type": "bus", "element_id": 5},
            {"nome": "DISJ_B6", "barra": 6, "element_type": "bus", "element_id": 6},
            {"nome": "DISJ_G1", "gerador": 1,
                "element_type": "gen", "element_id": geradores[0]},
            {"nome": "DISJ_G2", "gerador": 2,
                "element_type": "gen", "element_id": geradores[1]}
        ],
        "fusiveis": [
            {"nome": "FUSIVEL_B7", "barra": 7,
                "element_type": "bus", "element_id": 7},
            {"nome": "FUSIVEL_B9", "barra": 9,
                "element_type": "bus", "element_id": 9},
            {"nome": "FUSIVEL_B10", "barra": 10,
                "element_type": "bus", "element_id": 10},
            {"nome": "FUSIVEL_B14", "barra": 14,
                "element_type": "bus", "element_id": 14}
        ]
    }


def exportar_ieee14_com_protecao(path_saida):
    net = nw.case14()
    criar_geodata(net)
    inserir_trafos(net)
    adicionar_dispositivos_protecao(net)

    net_dict = {}
    for chave, valor in net.items():
        if hasattr(valor, "to_dict"):
            dicionario = valor.to_dict(orient="index")
            if isinstance(dicionario, dict):
                dicionario_limpo = {}
                for k, v in dicionario.items():
                    if isinstance(v, dict):
                        v_limpo = {ik: iv for ik, iv in v.items() if ik not in [
                            "dtype", "orient", "is_multiindex", "is_multicolumn"]}
                        dicionario_limpo[str(k)] = v_limpo
                net_dict[chave] = dicionario_limpo
        elif isinstance(valor, dict):
            net_dict[chave] = valor

    net_dict["bus_geodata"] = net.bus_geodata.to_dict(orient="index")
    net_dict["line_geodata"] = net.line_geodata.to_dict(orient="index")
    net_dict["protection_devices"] = net.protection_devices

    with open(path_saida, "w") as f:
        json.dump(net_dict, f, indent=2)

    print(f"✅ Arquivo JSON gerado com sucesso: {path_saida}")


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    json_path = base_dir / "data" / "ieee14_protecao.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    exportar_ieee14_com_protecao(json_path)
