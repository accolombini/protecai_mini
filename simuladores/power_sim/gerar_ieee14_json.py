"""
    
ProtecAI_MINI - Gerador de Topologia e Dados de Proteção (.json)

Gera um arquivo .json LIMPO e padronizado para uso nos scripts de visualização e simulação ProtecAI.

    ||>Padrão de exportação:
        - "pandapower_net": string serializada (via pp.to_json)
        - "protection_devices": dicionário (relés, disjuntores, fusíveis)
        - "bus_geodata": dicionário {índice: {x, y}}
        - "line_geodata": dicionário {índice: {"coords": [...]}}
        |> NÃO exporta curvas, resultados, nem artefatos IEEE.

    ||>Compatível com Pandapower 3.1.2+, Pandas 1.x+, Python 3.8+

"""

import pandapower as pp
import numpy as np
import pandas as pd
import json
from pathlib import Path
from typing import Dict, Tuple

# ====== PARÂMETROS E CONSTANTES ======
# Conforme especificação do projeto PETRO_PROTECAI_MINI
TRAFO_SN_MVA = 25.0  # 25 MVA (conforme especificação)
TRAFO_VN_HV = 13.8   # 13.8 kV (média tensão offshore)
TRAFO_VN_LV = 13.8   # 13.8 kV (mesmo nível - simplificado)

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
    (2, 3),   # Trafo 1 - Conforme especificação (25 MVA)
    (6, 9),   # Trafo 2 - Conforme especificação (25 MVA)
]

EXPORT_PATH = Path("simuladores") / "power_sim" / \
    "data" / "ieee14_protecao.json"


def criar_rede_limpa() -> pp.pandapowerNet:
    """
    Cria uma rede mínima conforme o escopo ProtecAI (barras, linhas e trafos do projeto).
    Baseado nas especificações do PETRO_PROTECAI_MINI para ambiente offshore.

    Returns:
        pp.pandapowerNet: Rede criada
    """
    net = pp.create_empty_network(
        sn_mva=100, f_hz=60, name="ProtecAI_Mini_Offshore")

    # Barras - todas em 13.8 kV (média tensão offshore conforme especificação)
    for idx, barra_ieee in enumerate(BARRAS):
        pp.create_bus(net, name=f"B{barra_ieee}", vn_kv=TRAFO_VN_HV, type="b")

    # Linhas (conectam barras do mesmo nível - 13.8 kV)
    # Parâmetros ajustados para ambiente offshore
    for from_ieee, to_ieee in LINHAS:
        from_bus = BARRA_MAP[from_ieee]
        to_bus = BARRA_MAP[to_ieee]

        pp.create_line_from_parameters(
            net,
            from_bus=from_bus,
            to_bus=to_bus,
            length_km=2.0,   # Distâncias curtas em plataforma
            r_ohm_per_km=0.08,
            x_ohm_per_km=0.35,
            c_nf_per_km=15.0,
            max_i_ka=1.5,
            name=f"L_{from_ieee}_{to_ieee}"
        )

    # Transformadores (25 MVA cada, conforme especificação)
    for idx, (hv_ieee, lv_ieee) in enumerate(TRAFOS):
        pp.create_transformer_from_parameters(
            net,
            hv_bus=BARRA_MAP[hv_ieee],
            lv_bus=BARRA_MAP[lv_ieee],
            sn_mva=TRAFO_SN_MVA,  # 25 MVA
            vn_hv_kv=TRAFO_VN_HV,  # 13.8 kV
            vn_lv_kv=TRAFO_VN_LV,  # 13.8 kV
            vk_percent=6.5,
            vkr_percent=0.8,
            pfe_kw=25.0,
            i0_percent=0.3,
            name=f"TR{idx+1}_25MVA"
        )

    # Cargas offshore - conforme especificação do projeto
    # Distribuição típica de plataforma de petróleo
    cargas_mw = {
        2: 0.0,   # Geração principal - sem carga
        3: 8.0,   # Carga industrial (equipamentos de processo)
        6: 0.0,   # Subestação intermediária - sem carga
        7: 5.0,   # Carga auxiliar (sistemas de segurança)
        9: 0.0,   # Distribuição - sem carga
        10: 6.0,  # Carga de utilidades (HVAC, iluminação)
        14: 4.0   # Carga de telecomunicações e controle
    }

    for idx, barra_ieee in enumerate(BARRAS):
        p_mw = cargas_mw[barra_ieee]
        if p_mw > 0:
            # Fator de potência típico offshore: 0.85
            q_mvar = p_mw * 0.62  # tan(arccos(0.85))
            pp.create_load(net, bus=idx, p_mw=p_mw, q_mvar=q_mvar,
                           name=f"Carga_B{barra_ieee}")

    # Fonte principal (ext_grid) - gerador da plataforma
    pp.create_ext_grid(net, bus=0, vm_pu=1.05, name="Gerador_Principal_B2")
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
    protection_zones: list,
    bus_geodata: pd.DataFrame,
    line_geodata: pd.DataFrame,
    caminho: Path
) -> None:
    """
    Exporta o net e os componentes extras no formato ProtecAI.
    Salva um arquivo JSON com os campos: pandapower_net, protection_devices, protection_zones, bus_geodata, line_geodata.
    """
    import json

    # Executar power flow para garantir que a rede está válida
    try:
        pp.runpp(net, verbose=False)
        print("✅ Power flow executado com sucesso")
    except Exception as e:
        print(f"⚠️ Aviso: Power flow falhou: {e}")

    # Serializar a rede PandaPower para JSON
    try:
        pandapower_json = pp.to_json(net)
        print(f"✅ Rede serializada: {len(pandapower_json)} caracteres")
    except Exception as e:
        print(f"❌ Erro na serialização: {e}")
        # Fallback: serializar manualmente os elementos principais
        pandapower_json = json.dumps({
            "version": "3.1.2",
            "name": net.name,
            "f_hz": net.f_hz,
            "sn_mva": net.sn_mva,
            "bus": net.bus.to_dict('records'),
            "line": net.line.to_dict('records'),
            "trafo": net.trafo.to_dict('records'),
            "load": net.load.to_dict('records'),
            "ext_grid": net.ext_grid.to_dict('records'),
        })

    saida = {
        "pandapower_net": pandapower_json,  # net serializado como string!
        "protection_devices": protection_devices,  # Dicionário dos dispositivos!
        "protection_zones": protection_zones,  # Lista das zonas de proteção!
        # DataFrame para dict!
        "bus_geodata": bus_geodata.to_dict(orient="index"),
        # DataFrame para dict!
        "line_geodata": line_geodata.to_dict(orient="index"),
    }

    caminho.parent.mkdir(parents=True, exist_ok=True)

    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)

    print(f"✅ Arquivo ProtecAI salvo em: {caminho}")

    # Verificação imediata
    print(f"📊 Resumo dos dados exportados:")
    print(f"   - Barras: {len(net.bus)}")
    print(f"   - Linhas: {len(net.line)}")
    print(f"   - Transformadores: {len(net.trafo)}")
    print(f"   - Cargas: {len(net.load)}")
    print(f"   - Geradores: {len(net.ext_grid)}")
    print(f"   - Relés: {len(protection_devices['reles'])}")
    print(f"   - Disjuntores: {len(protection_devices['disjuntores'])}")
    print(f"   - Fusíveis: {len(protection_devices['fusiveis'])}")
    print(f"   - Zonas de proteção: {len(protection_zones)}")


def gerar_zonas_protecao(net: pp.pandapowerNet) -> list:
    """
    Gera zonas de proteção para transformadores conforme especificação offshore.
    Cada transformador define uma zona de proteção primária.

    Args:
        net: Rede PandaPower

    Returns:
        list: Lista de zonas de proteção
    """
    zonas = []

    # Zona 1: Transformador TR1 (Barras 2-3)
    # Proteção diferencial do primeiro transformador de 25 MVA
    zonas.append({
        "nome": "ZONA_TR1_25MVA",
        "tipo": "diferencial_transformador",
        "transformador_id": 0,  # Primeiro transformador
        "barras": [0, 1],  # Índices das barras conectadas (B2, B3)
        "barras_ieee": [2, 3],  # Numeração IEEE original
        "tensao_kv": 13.8,
        "potencia_mva": 25.0,
        "protecao_primaria": "87T",
        "protecao_backup": ["50/51", "67"],
        "tempo_atuacao_ms": 50,
        "descricao": "Zona de proteção diferencial do transformador principal TR1"
    })

    # Zona 2: Transformador TR2 (Barras 6-9)
    # Proteção diferencial do segundo transformador de 25 MVA
    zonas.append({
        "nome": "ZONA_TR2_25MVA",
        "tipo": "diferencial_transformador",
        "transformador_id": 1,  # Segundo transformador
        "barras": [2, 4],  # Índices das barras conectadas (B6, B9)
        "barras_ieee": [6, 9],  # Numeração IEEE original
        "tensao_kv": 13.8,
        "potencia_mva": 25.0,
        "protecao_primaria": "87T",
        "protecao_backup": ["50/51", "67"],
        "tempo_atuacao_ms": 50,
        "descricao": "Zona de proteção diferencial do transformador auxiliar TR2"
    })

    print(f"✅ Geradas {len(zonas)} zonas de proteção para transformadores")
    return zonas


def main() -> None:
    """
    Pipeline completo: cria rede, gera dados, exporta para JSON ProtecAI.
    """
    net = criar_rede_limpa()
    bus_geodata, line_geodata = gerar_geodata(net)
    protection_devices = gerar_protection_devices(net)
    protection_zones = gerar_zonas_protecao(net)
    exportar_json_customizado(net, protection_devices, protection_zones,
                              bus_geodata, line_geodata, EXPORT_PATH)


if __name__ == "__main__":
    main()
