"""
ProtecAI - Gerador de Topologia e Dados de Proteção (.json)
-----------------------------------------------------------
Gera um arquivo .json LIMPO e padronizado para uso nos scripts de visualização e simulação ProtecAI.

Padrão de exportação:
- "pandapower_net": string serializada (via pp.to_json)
- "protection_devices": dicionário (relés, disjuntores, fusíveis)
- "bus_geodata": dicionário {índice: {x, y}}
- "line_geodata": dicionário {índice: {"coords": [...]}}
NÃO exporta curvas, resultados, nem artefatos IEEE.

Compatível com Pandapower 3.1.2+, Pandas 1.x+, Python 3.8+

Autor: Code GPT / Petrobras-UFF-ProtecAI
"""

import pandapower as pp
import numpy as np
import pandas as pd
import json
from pathlib import Path
from typing import Dict, Tuple

# ====== PARÂMETROS E CONSTANTES ======
TRAFO_SN_MVA = 13.8
TRAFO_VN_KV = 0.22  # 220V == 0.22kV

BARRAS = [2, 3, 6, 7, 9, 10, 14]
BARRA_MAP = {i: idx for idx, i in enumerate(BARRAS)}

LINHAS = [
    # Conexões primárias (espinha dorsal da malha)
    (2, 3),
    (3, 6),
    (6, 7),
    (7, 9),
    (9, 10),
    (10, 14),

    # Conexões de malha (criam redundância e múltiplos caminhos)
    (2, 6),    # Bypass direto B2 → B6
    (3, 7),    # Bypass B3 → B7
    (6, 9),    # Bypass B6 → B9
    (7, 10),   # Bypass B7 → B10
    (9, 14),   # Bypass B9 → B14
    (2, 7),    # Conexão longa B2 → B7 (redundância extra)
]

TRAFOS = [
    (2, 3),   # Trafo 1 - Entrada principal
    (6, 7),   # Trafo 2 - Seção intermediária
    (9, 10)   # Trafo 3 - Seção final (adicional para maior redundância)
]

EXPORT_PATH = Path("simuladores") / "power_sim" / \
    "data" / "ieee14_protecao.json"


def criar_rede_limpa() -> pp.pandapowerNet:
    """
    Cria uma rede mínima conforme o escopo ProtecAI (barras, linhas e trafos do projeto).

    Returns:
        pp.pandapowerNet: Rede criada
    """
    net = pp.create_empty_network(sn_mva=15, f_hz=60, name="ProtecAI_Mini")
    # Barras
    for idx in range(len(BARRAS)):
        pp.create_bus(net, name=f"B{BARRAS[idx]}", vn_kv=TRAFO_VN_KV, type="b")
    # Linhas
    for from_ieee, to_ieee in LINHAS:
        pp.create_line_from_parameters(
            net,
            from_bus=BARRA_MAP[from_ieee],
            to_bus=BARRA_MAP[to_ieee],
            length_km=1.0,
            r_ohm_per_km=0.05,
            x_ohm_per_km=0.10,
            c_nf_per_km=0.0,
            max_i_ka=1.0,
            name=f"L_{from_ieee}_{to_ieee}"
        )
    # Trafos
    for idx, (hv_ieee, lv_ieee) in enumerate(TRAFOS):
        pp.create_transformer_from_parameters(
            net,
            hv_bus=BARRA_MAP[hv_ieee],
            lv_bus=BARRA_MAP[lv_ieee],
            sn_mva=TRAFO_SN_MVA,
            vn_hv_kv=TRAFO_VN_KV,
            vn_lv_kv=TRAFO_VN_KV,
            vk_percent=10.5,
            vkr_percent=0.5,
            pfe_kw=0.0,
            i0_percent=0.01,
            name=f"TR{idx+1}"
        )
    # Cargas (ajuste se desejar)
    for idx in range(len(BARRAS)):
        pp.create_load(net, bus=idx, p_mw=1.0, q_mvar=0.5,
                       name=f"Carga_B{BARRAS[idx]}")
    # Fonte (ext_grid)
    pp.create_ext_grid(net, bus=0, vm_pu=1.0, name="Fonte_B2")
    return net


def gerar_geodata(net: pp.pandapowerNet) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Gera geodados das barras e linhas para visualização.

    Args:
        net (pp.pandapowerNet): Rede

    Returns:
        bus_geodata (pd.DataFrame)
        line_geodata (pd.DataFrame)
    """
    n_bus = len(net.bus)
    angs = np.linspace(0, 2 * np.pi, n_bus, endpoint=False)
    x = np.cos(angs)
    y = np.sin(angs)
    bus_geodata = pd.DataFrame({"x": x, "y": y}, index=net.bus.index)
    line_coords = []
    for idx, row in net.line.iterrows():
        from_bus = row['from_bus']
        to_bus = row['to_bus']
        coords = [
            [float(bus_geodata.loc[from_bus, "x"]),
             float(bus_geodata.loc[from_bus, "y"])],
            [float(bus_geodata.loc[to_bus, "x"]),
             float(bus_geodata.loc[to_bus, "y"])]
        ]
        line_coords.append(coords)
    line_geodata = pd.DataFrame({"coords": line_coords}, index=net.line.index)
    return bus_geodata, line_geodata


def gerar_protection_devices(net: pp.pandapowerNet) -> Dict:
    """
    Gera dicionário de dispositivos de proteção para toda a rede.

    Args:
        net (pp.pandapowerNet): Rede

    Returns:
        dict: {"reles": [...], "disjuntores": [...], "fusiveis": [...]}
    """
    protection = {
        "reles": [],
        "disjuntores": [],
        "fusiveis": []
    }
    # Relés 51 nas linhas
    for idx in net.line.index:
        protection["reles"].append({
            "tipo": "51",
            "id": f"RELE_51_L{idx}",
            "element_type": "line",
            "element_id": int(idx),
            "curva": "IEC",
            "pickup": 1.20,
            "tempo_atuacao": 0.20,
        })
    # Relés 67 em todas barras
    for idx in net.bus.index:
        protection["reles"].append({
            "tipo": "67",
            "id": f"RELE_67_B{idx+1}",
            "element_type": "bus",
            "element_id": int(idx),
            "direcao": "bidirecional",
            "pickup": 1.10,
            "curva": "IEC",
            "tempo_atuacao": 0.15,
        })
    # Relés 87T nos trafos
    for idx in net.trafo.index:
        protection["reles"].append({
            "tipo": "87T",
            "id": f"RELE_87T_TR{idx}",
            "element_type": "trafo",
            "element_id": int(idx),
            "pickup": 0.60,
            "curva": "RMS",
            "tempo_atuacao": 0.08,
        })
    # Relés 27/59 nas barras finais (B7, B9, B10, B14)
    for idx in [3, 4, 5, 6]:
        protection["reles"].append({
            "tipo": "27/59",
            "id": f"RELE_27_59_B{BARRAS[idx]}",
            "element_type": "bus",
            "element_id": int(idx),
            "pickup_sub": 0.85,
            "pickup_sobre": 1.15,
            "tempo_atuacao": 0.05
        })
    # Disjuntores em linhas, trafos e barra de geração
    for idx in net.line.index:
        protection["disjuntores"].append({
            "id": f"DISJ_L{idx}",
            "element_type": "line",
            "element_id": int(idx),
            "delay": 0.02,
            "status": "fechado"
        })
    for idx in net.trafo.index:
        protection["disjuntores"].append({
            "id": f"DISJ_TR{idx}",
            "element_type": "trafo",
            "element_id": int(idx),
            "delay": 0.02,
            "status": "fechado"
        })
    protection["disjuntores"].append({
        "id": f"DISJ_GEN",
        "element_type": "ext_grid",
        "element_id": 0,
        "delay": 0.02,
        "status": "fechado"
    })
    # Fusíveis em barras finais
    for idx in [3, 4, 5, 6]:
        protection["fusiveis"].append({
            "id": f"FUSIVEL_B{BARRAS[idx]}",
            "element_type": "bus",
            "element_id": int(idx),
            "corrente_fusao": 2.50,
            "delay": 0.01
        })
    return protection


def exportar_json_customizado(
    net: pp.pandapowerNet,
    protection_devices: Dict,
    bus_geodata: pd.DataFrame,
    line_geodata: pd.DataFrame,
    caminho: Path
) -> None:
    """
    Exporta o net e os componentes extras no formato ProtecAI.
    Salva um arquivo JSON com os campos: pandapower_net, protection_devices, bus_geodata, line_geodata.
    """
    import json
    saida = {
        "pandapower_net": pp.to_json(net),  # net serializado como string!
        "protection_devices": protection_devices,  # Dicionário dos dispositivos!
        # DataFrame para dict!
        "bus_geodata": bus_geodata.to_dict(orient="index"),
        # DataFrame para dict!
        "line_geodata": line_geodata.to_dict(orient="index"),
    }
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)
    print(f"Arquivo ProtecAI salvo em: {caminho}")


def main() -> None:
    """
    Pipeline completo: cria rede, gera dados, exporta para JSON ProtecAI.
    """
    net = criar_rede_limpa()
    bus_geodata, line_geodata = gerar_geodata(net)
    protection_devices = gerar_protection_devices(net)
    exportar_json_customizado(net, protection_devices,
                              bus_geodata, line_geodata, EXPORT_PATH)


if __name__ == "__main__":
    main()
