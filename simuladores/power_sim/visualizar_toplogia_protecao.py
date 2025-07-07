'''
    ||> Visualização da rede de teste ProtecAI_Mini com Pandapower e Matplotlib.
        - Carrega dados de um arquivo JSON contendo a rede e dispositivos de proteção.
        - Plota a rede com barras, linhas, transformadores, cargas, geração e dispositivos de proteção.
        - Salva a visualização em um arquivo PNG.        
'''

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import json
import pandapower as pp
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use backend sem interface gráfica

# Paleta e símbolos
COLOR_BARRA = "blue"
COLOR_LINHA = "black"
COLOR_TRAFO = "purple"
COLOR_CARGA = "green"
COLOR_GEN = "orange"
COLOR_RELE = "red"
COLOR_DISJ = "gold"
COLOR_FUSIVEL = "deeppink"
COLOR_ZONA_PROTECAO = "lightblue"
COLOR_ZONA_BORDA = "darkblue"

MARKER_BARRA = "o"
MARKER_CARGA = "s"
MARKER_GEN = "P"
MARKER_RELE = "^"
MARKER_DISJ = "s"
MARKER_FUSIVEL = "*"

FONT_LABEL = 10
FONT_TITULO = 16


def carregar_json(path_json):
    print(f"🔄 Carregando JSON: {path_json}")
    try:
        with open(path_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("✅ JSON carregado com sucesso")

        print("🔄 Convertendo rede PandaPower...")
        # O pandapower_net já é uma string JSON, usar diretamente
        net_json_str = data["pandapower_net"]
        print(
            f"🔍 Tipo: {type(net_json_str)}, Tamanho: {len(net_json_str)} chars")
        net = pp.from_json_string(net_json_str)
        print(
            f"✅ Rede carregada: {len(net.bus)} barras, {len(net.line)} linhas")

        protection_devices = data["protection_devices"]
        print(
            f"✅ Dispositivos de proteção: {len(protection_devices['reles'])} relés")

        # Carregando zonas de proteção
        protection_zones = data.get("protection_zones", [])
        print(f"✅ Zonas de proteção: {len(protection_zones)} zonas")

        bus_geodata = pd.DataFrame.from_dict(
            data["bus_geodata"], orient="index")
        line_geodata = pd.DataFrame.from_dict(
            data["line_geodata"], orient="index")
        bus_geodata.index = bus_geodata.index.astype(int)
        line_geodata.index = line_geodata.index.astype(int)
        print("✅ Geodados processados")

        return net, protection_devices, protection_zones, bus_geodata, line_geodata
    except Exception as e:
        print(f"❌ Erro ao carregar JSON: {e}")
        sys.exit(1)


def plotar_zonas_protecao(ax, net, bus_geodata, protection_zones):
    """Plota as zonas de proteção como áreas sombreadas na rede."""
    print("🛡️ Plotando zonas de proteção...")

    from matplotlib.patches import Polygon
    import numpy as np

    # Processar cada zona de proteção
    for zona in protection_zones:
        nome = zona.get("nome", "ZONA")
        tipo = zona.get("tipo", "")
        barras = zona.get("barras", [])

        if len(barras) < 2:
            continue

        print(f"  📍 Plotando zona: {nome} - Barras: {barras}")

        try:
            # Obter coordenadas das barras da zona
            coords_zona = []
            for barra_id in barras:
                if barra_id in bus_geodata.index:
                    x = bus_geodata.loc[barra_id, "x"]
                    y = bus_geodata.loc[barra_id, "y"]
                    coords_zona.append([x, y])

            if len(coords_zona) >= 2:
                # Calcular centro da zona
                coords_array = np.array(coords_zona)
                center_x = np.mean(coords_array[:, 0])
                center_y = np.mean(coords_array[:, 1])

                # Para transformadores (2 barras), criar um retângulo
                if len(coords_zona) == 2:
                    x1, y1 = coords_zona[0]
                    x2, y2 = coords_zona[1]

                    # Calcular vetor perpendicular para criar largura
                    dx = x2 - x1
                    dy = y2 - y1
                    length = np.sqrt(dx**2 + dy**2)

                    if length > 0:
                        # Normalizar e criar perpendicular
                        perp_x = -dy / length * 0.08  # Largura da zona
                        perp_y = dx / length * 0.08

                        # Expandir um pouco ao longo da linha
                        extend_x = dx / length * 0.05
                        extend_y = dy / length * 0.05

                        # Criar retângulo ao redor do transformador
                        poly_coords = [
                            [x1 - extend_x + perp_x, y1 - extend_y + perp_y],
                            [x1 - extend_x - perp_x, y1 - extend_y - perp_y],
                            [x2 + extend_x - perp_x, y2 + extend_y - perp_y],
                            [x2 + extend_x + perp_x, y2 + extend_y + perp_y]
                        ]

                        # Criar e plotar o polígono
                        polygon = Polygon(poly_coords, alpha=0.3,
                                          facecolor=COLOR_ZONA_PROTECAO,
                                          edgecolor=COLOR_ZONA_BORDA,
                                          linewidth=2, zorder=0.5)
                        ax.add_patch(polygon)

                        # Adicionar label da zona
                        label_text = nome.replace(
                            "ZONA_", "").replace("_25MVA", "")
                        ax.text(center_x, center_y - 0.1, label_text, fontsize=8,
                                color=COLOR_ZONA_BORDA, ha="center", va="center",
                                fontweight="bold", backgroundcolor="white",
                                bbox=dict(boxstyle="round,pad=0.2",
                                          facecolor="white", alpha=0.8), zorder=15)

                else:
                    # Para múltiplas barras, criar um círculo expandido
                    # Calcular raio baseado na distância máxima do centro
                    max_dist = 0
                    for coord in coords_zona:
                        dist = np.sqrt(
                            (coord[0] - center_x)**2 + (coord[1] - center_y)**2)
                        max_dist = max(max_dist, dist)

                    radius = max_dist + 0.05  # Adicionar margem

                    # Criar círculo aproximado com polígono
                    angles = np.linspace(0, 2*np.pi, 20)
                    circle_coords = []
                    for angle in angles:
                        x = center_x + radius * np.cos(angle)
                        y = center_y + radius * np.sin(angle)
                        circle_coords.append([x, y])

                    polygon = Polygon(circle_coords, alpha=0.3,
                                      facecolor=COLOR_ZONA_PROTECAO,
                                      edgecolor=COLOR_ZONA_BORDA,
                                      linewidth=2, zorder=0.5)
                    ax.add_patch(polygon)

                    label_text = nome.replace(
                        "ZONA_", "").replace("_25MVA", "")
                    ax.text(center_x, center_y, label_text, fontsize=8,
                            color=COLOR_ZONA_BORDA, ha="center", va="center",
                            fontweight="bold", backgroundcolor="white",
                            bbox=dict(boxstyle="round,pad=0.2",
                                      facecolor="white", alpha=0.8), zorder=15)

        except Exception as e:
            print(f"⚠️ Erro ao plotar zona {nome}: {e}")
            continue


def plotar_rede(net, bus_geodata, line_geodata, protection_devices, protection_zones, path_out):
    print("🎨 Iniciando plotagem da rede...")

    # Conjunto de índices válidos
    barras_validas = set(net.bus.index)
    linhas_validas = set(net.line.index)
    trafos_validos = set(net.trafo.index)
    cargas_validas = set(net.load.index)

    print(
        f"📊 Elementos válidos - Barras: {len(barras_validas)}, Linhas: {len(linhas_validas)}, Trafos: {len(trafos_validos)}")

    fig, ax = plt.subplots(figsize=(12, 8))
    plt.title("ProtecAI_Mini Rede de Teste",
              fontsize=FONT_TITULO, fontweight="bold", pad=24)

    # Plotar zonas de proteção primeiro (no fundo)
    plotar_zonas_protecao(ax, net, bus_geodata, protection_zones)

    # Linhas
    print("🔗 Plotando linhas...")
    for idx, line in net.line.iterrows():
        try:
            coords = line_geodata.loc[idx, "coords"]
            xs, ys = zip(*coords)
            ax.plot(xs, ys, color=COLOR_LINHA, linewidth=2, zorder=1)
            xm, ym = np.mean(xs), np.mean(ys)
            ax.text(xm, ym, f"L{idx}", fontsize=FONT_LABEL, color=COLOR_LINHA,
                    ha="center", va="center", backgroundcolor="white", zorder=10)
        except Exception as e:
            print(f"⚠️ Erro ao plotar linha {idx}: {e}")
            continue

    # Trafos
    print("🔌 Plotando transformadores...")
    for idx, trafo in net.trafo.iterrows():
        try:
            hv = int(trafo["hv_bus"])
            lv = int(trafo["lv_bus"])
            if hv in barras_validas and lv in barras_validas:
                x0, y0 = bus_geodata.loc[hv, "x"], bus_geodata.loc[hv, "y"]
                x1, y1 = bus_geodata.loc[lv, "x"], bus_geodata.loc[lv, "y"]
                ax.plot([x0, x1], [y0, y1], color=COLOR_TRAFO,
                        linewidth=3, linestyle="--", zorder=2)
                xm, ym = (x0+x1)/2, (y0+y1)/2
                ax.text(xm, ym, f"TR{idx+1}", fontsize=FONT_LABEL, color=COLOR_TRAFO,
                        ha="center", va="center", fontweight="bold", backgroundcolor="white", zorder=10)
        except Exception as e:
            print(f"⚠️ Erro ao plotar trafo {idx}: {e}")
            continue

    # Barras
    print("⚡ Plotando barras...")
    for idx, bus in net.bus.iterrows():
        try:
            x, y = bus_geodata.loc[idx, "x"], bus_geodata.loc[idx, "y"]
            ax.scatter(x, y, color=COLOR_BARRA, marker=MARKER_BARRA,
                       s=250, zorder=3, edgecolors="black", linewidths=1.5)
            ax.text(x, y+0.05, bus["name"], fontsize=FONT_LABEL, color=COLOR_BARRA,
                    ha="center", va="bottom", fontweight="bold", backgroundcolor="white", zorder=20)
        except Exception as e:
            print(f"⚠️ Erro ao plotar barra {idx}: {e}")
            continue

    # Cargas
    for idx, carga in net.load.iterrows():
        bus_idx = int(carga["bus"])
        if bus_idx in barras_validas:
            x, y = bus_geodata.loc[bus_idx, "x"], bus_geodata.loc[bus_idx, "y"]
            ax.scatter(x-0.04, y-0.04, color=COLOR_CARGA,
                       marker=MARKER_CARGA, s=130, zorder=4, edgecolors="black")
            ax.text(x-0.06, y-0.07, "Carga", fontsize=FONT_LABEL, color=COLOR_CARGA,
                    ha="center", va="center", fontstyle="italic", backgroundcolor="white", zorder=20)

    # Geração (Fonte)
    for idx, gen in net.ext_grid.iterrows():
        bus_idx = int(gen["bus"])
        if bus_idx in barras_validas:
            x, y = bus_geodata.loc[bus_idx, "x"], bus_geodata.loc[bus_idx, "y"]
            ax.scatter(x+0.06, y+0.06, color=COLOR_GEN,
                       marker=MARKER_GEN, s=180, zorder=4, edgecolors="black")
            ax.text(x+0.08, y+0.08, "Fonte", fontsize=FONT_LABEL, color=COLOR_GEN,
                    ha="center", va="center", backgroundcolor="white", fontstyle="italic", zorder=20)

    # Relés
    for rele in protection_devices["reles"]:
        tipo = rele.get("tipo", "RELE")
        if rele["element_type"] == "line":
            idx = int(rele["element_id"])
            if idx in linhas_validas:
                coords = line_geodata.loc[idx, "coords"]
                x, y = np.mean([coords[0][0], coords[1][0]]), np.mean(
                    [coords[0][1], coords[1][1]])
                dx, dy = 0, -0.08
            else:
                continue
        elif rele["element_type"] == "bus":
            idx = int(rele["element_id"])
            if idx in barras_validas:
                x, y = bus_geodata.loc[idx, "x"], bus_geodata.loc[idx, "y"]
                dx, dy = -0.08, 0.08
            else:
                continue
        elif rele["element_type"] == "trafo":
            idx = int(rele["element_id"])
            if idx in trafos_validos:
                hv = int(net.trafo.iloc[idx]["hv_bus"])
                lv = int(net.trafo.iloc[idx]["lv_bus"])
                x, y = (bus_geodata.loc[hv, "x"] + bus_geodata.loc[lv, "x"]) / \
                    2, (bus_geodata.loc[hv, "y"] + bus_geodata.loc[lv, "y"])/2
                dx, dy = 0.07, -0.07
            else:
                continue
        else:
            continue
        ax.scatter(x+dx, y+dy, color=COLOR_RELE, marker=MARKER_RELE,
                   s=130, zorder=5, edgecolors="black")
        ax.text(x+dx, y+dy-0.04, f"{tipo}", fontsize=FONT_LABEL, color=COLOR_RELE,
                ha="center", va="center", backgroundcolor="white", zorder=25)

    # Disjuntores
    for disj in protection_devices["disjuntores"]:
        if disj["element_type"] == "line":
            idx = int(disj["element_id"])
            if idx in linhas_validas:
                coords = line_geodata.loc[idx, "coords"]
                x, y = np.mean([coords[0][0], coords[1][0]]), np.mean(
                    [coords[0][1], coords[1][1]])
                dx, dy = 0.06, 0.06
            else:
                continue
        elif disj["element_type"] == "trafo":
            idx = int(disj["element_id"])
            if idx in trafos_validos:
                hv = int(net.trafo.iloc[idx]["hv_bus"])
                lv = int(net.trafo.iloc[idx]["lv_bus"])
                x, y = (bus_geodata.loc[hv, "x"] + bus_geodata.loc[lv, "x"]) / \
                    2, (bus_geodata.loc[hv, "y"] + bus_geodata.loc[lv, "y"])/2
                dx, dy = 0.08, 0.08
            else:
                continue
        elif disj["element_type"] in ["gen", "ext_grid"]:
            idx = 0
            if idx in barras_validas:
                x, y = bus_geodata.loc[idx, "x"], bus_geodata.loc[idx, "y"]
                dx, dy = 0.11, 0
            else:
                continue
        else:
            continue
        ax.scatter(x+dx, y+dy, color=COLOR_DISJ, marker=MARKER_DISJ,
                   s=110, zorder=5, edgecolors="black")
        ax.text(x+dx, y+dy-0.04, "DJ", fontsize=FONT_LABEL, color=COLOR_DISJ,
                ha="center", va="center", backgroundcolor="white", zorder=25)

    # Fusíveis
    for fusivel in protection_devices["fusiveis"]:
        idx = int(fusivel["element_id"])
        if idx in barras_validas:
            x, y = bus_geodata.loc[idx, "x"], bus_geodata.loc[idx, "y"]
            ax.scatter(x, y-0.09, color=COLOR_FUSIVEL,
                       marker=MARKER_FUSIVEL, s=180, zorder=6, edgecolors="black")
            ax.text(x, y-0.12, "FUS", fontsize=FONT_LABEL, color=COLOR_FUSIVEL,
                    ha="center", va="center", backgroundcolor="white", zorder=26)

    # Zonas de Proteção
    for zona in protection_devices.get("zonas", []):
        if zona["element_type"] == "bus":
            idx = int(zona["element_id"])
            if idx in barras_validas:
                x, y = bus_geodata.loc[idx, "x"], bus_geodata.loc[idx, "y"]
                raio = 0.15
                circulo = plt.Circle(
                    (x, y), raio, color=COLOR_ZONA_PROTECAO, alpha=0.3, zorder=0)
                ax.add_artist(circulo)
                ax.text(x, y+0.1, "Zona", fontsize=FONT_LABEL, color=COLOR_ZONA_BORDA,
                        ha="center", va="center", fontweight="bold", zorder=10)
        elif zona["element_type"] == "trafo":
            idx = int(zona["element_id"])
            if idx in trafos_validos:
                hv = int(net.trafo.iloc[idx]["hv_bus"])
                lv = int(net.trafo.iloc[idx]["lv_bus"])
                x, y = (bus_geodata.loc[hv, "x"] + bus_geodata.loc[lv, "x"]) / \
                    2, (bus_geodata.loc[hv, "y"] + bus_geodata.loc[lv, "y"])/2
                raio = 0.2
                circulo = plt.Circle(
                    (x, y), raio, color=COLOR_ZONA_PROTECAO, alpha=0.3, zorder=0)
                ax.add_artist(circulo)
                ax.text(x, y+0.1, "Zona", fontsize=FONT_LABEL, color=COLOR_ZONA_BORDA,
                        ha="center", va="center", fontweight="bold", zorder=10)

    # Legenda
    legendas = [
        (COLOR_BARRA, MARKER_BARRA, "Barra"),
        (COLOR_LINHA, "_", "Linha"),
        (COLOR_TRAFO, "_", "Trafo"),
        (COLOR_CARGA, MARKER_CARGA, "Carga"),
        (COLOR_GEN, MARKER_GEN, "Geração"),
        (COLOR_RELE, MARKER_RELE, "Relé"),
        (COLOR_DISJ, MARKER_DISJ, "Disjuntor"),
        (COLOR_FUSIVEL, MARKER_FUSIVEL, "Fusível"),
        (COLOR_ZONA_PROTECAO, "_", "Zona de Proteção"),
    ]
    for cor, mark, nome in legendas:
        if mark == "_":
            ax.plot([], [], color=cor, label=nome, linewidth=3)
        else:
            ax.scatter([], [], color=cor, marker=mark,
                       label=nome, s=120, edgecolors="black")

    ax.legend(loc="lower left", fontsize=FONT_LABEL, frameon=True)
    ax.axis("off")
    plt.tight_layout()
    path_out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path_out, dpi=300)
    plt.close()
    print(f"Imagem salva em: {path_out}")


def main():
    path_json = Path("simuladores") / "power_sim" / \
        "data" / "ieee14_protecao.json"
    # Garantir que o arquivo seja salvo na pasta docs da raiz do projeto
    path_out = Path(__file__).resolve(
    ).parents[2] / "docs" / "rede_protecai.png"
    try:
        net, protection_devices, protection_zones, bus_geodata, line_geodata = carregar_json(
            path_json)
        plotar_rede(net, bus_geodata, line_geodata,
                    protection_devices, protection_zones, path_out)
    except Exception as e:
        print(f"[ERRO] Falha na visualização: {e}")


if __name__ == "__main__":
    main()
