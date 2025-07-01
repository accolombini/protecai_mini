'''
Script: visualizar_topologia_protecao.py
Descricao: Carrega e plota a topologia da rede IEEE 14 modificada para o ProtecAI_MINI, incluindo dispositivos de proteção
Autor: Projeto ProtecAI_MINI
'''

import json
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
import matplotlib.patches as mpatches
from matplotlib.patches import Ellipse, Rectangle


def carregar_dados_json(path):
    with open(path, "r") as f:
        net_data = json.load(f)

    if set(net_data.keys()) == {"_module", "_class", "_object"}:
        net_data = net_data["_object"]

    net_data = {
        k: v for k, v in net_data.items()
        if k not in ["_module", "_class", "_object"]
    }

    if "bus_geodata" not in net_data or not isinstance(net_data["bus_geodata"], dict):
        raise ValueError(
            "bus_geodata ausente ou inválido no arquivo JSON. Não é possível plotar a rede.")

    return net_data


def montar_grafo(net_data):
    G = nx.Graph()
    bus_geodata = net_data["bus_geodata"]

    for bus_id, coords in bus_geodata.items():
        try:
            bid = int(bus_id)
            G.add_node(bid, pos=(coords["x"], coords["y"]))
        except Exception as e:
            print(f"[!] Erro ao adicionar coordenadas do bus {bus_id}: {e}")

    for tipo, chave_from, chave_to in [("line", "from_bus", "to_bus")]:
        elementos = net_data.get(tipo, {})
        if isinstance(elementos, dict):
            for elem_id, elem in elementos.items():
                try:
                    if isinstance(elem, dict) and all(k in elem for k in [chave_from, chave_to]):
                        u = int(elem[chave_from])
                        v = int(elem[chave_to])
                        G.add_edge(u, v, tipo=tipo, id=elem_id)
                except Exception as e:
                    print(f"[!] Erro em {tipo} {elem_id}: {e}")

    for tid, trafo in net_data.get("trafo", {}).items():
        try:
            u = int(trafo["hv_bus"])
            v = int(trafo["lv_bus"])
            G.add_edge(u, v, tipo="trafo", id=tid)
        except Exception as e:
            print(
                f"[!] Erro ao adicionar transformador {tid} como aresta: {e}")

    return G


def plotar_grafo(G, net_data):
    pos = nx.get_node_attributes(G, "pos")
    if not pos:
        raise ValueError(
            "Coordenadas de posição não encontradas nos nós do grafo.")

    fig, ax = plt.subplots(figsize=(18, 14))

    nx.draw_networkx_nodes(
        G, pos, node_color="lightblue", node_size=700, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=11, font_weight="bold", ax=ax)

    arestas = [(u, v) for u, v, d in G.edges(data=True)
               if d.get("tipo") in ["line", "trafo"]]
    nx.draw_networkx_edges(G, pos, edgelist=arestas,
                           edge_color="black", style="solid", width=1.8, ax=ax)

    prot = net_data.get("protection_devices", {})
    zona_id = 1
    trafos_ja_representados = set()
    zonas_por_barra = set()
    desloc_por_barra = {}

    offset_relays = {
        "87T": 6,
        "zona": 4,
        "comum": 2
    }

    for rele in prot.get("reles", []):
        try:
            tipo = rele.get("tipo", "?")
            is_87t = tipo.startswith("87")
            cor = "purple" if is_87t else "blue"

            if rele.get("element_type") == "trafo":
                trafo_id = str(rele["element_id"])
                if trafo_id not in trafos_ja_representados:
                    trafo = net_data.get("trafo", {}).get(trafo_id)
                    if trafo:
                        u = int(trafo["hv_bus"])
                        v = int(trafo["lv_bus"])
                        mx, my = (pos[u][0] + pos[v][0]) / \
                            2, (pos[u][1] + pos[v][1]) / 2
                        ax.add_patch(Ellipse(
                            (mx, my + 1.2), width=2.2, height=2.2, edgecolor="red", facecolor="none", lw=2))
                        ax.add_patch(Ellipse(
                            (mx, my - 1.2), width=2.2, height=2.2, edgecolor="red", facecolor="none", lw=2))
                        ax.text(
                            mx, my + offset_relays["zona"], f"Z{zona_id}", color="red", fontsize=9, ha="center")
                        ax.add_patch(
                            Rectangle((mx - 0.6, my - 0.6), 1.2, 1.2, color="purple"))
                        ax.text(
                            mx, my + offset_relays["87T"], tipo, color=cor, fontsize=9, ha="center")
                        zona_id += 1
                        trafos_ja_representados.add(trafo_id)
            else:
                for b in rele.get("barras", []):
                    if b in pos:
                        deslocamento = desloc_por_barra.get(b, 0)
                        x, y = pos[b]
                        ax.text(
                            x, y + deslocamento + offset_relays["comum"], tipo, color=cor, fontsize=9, ha="center")

                        if b not in zonas_por_barra:
                            ax.text(
                                x, y + deslocamento + offset_relays["comum"] + 1.5, f"Z{zona_id}", color="red", fontsize=9, ha="center")
                            zonas_por_barra.add(b)
                            zona_id += 1

                        desloc_por_barra[b] = deslocamento + 3.5
        except Exception as e:
            print(f"[!] Erro ao plotar relé {rele}: {e}")

    for tipo, letra, cor, desloc_base in [("disjuntores", "D", "darkgreen", -2), ("fusiveis", "F", "orange", -4)]:
        for item in prot.get(tipo, []):
            try:
                if item.get("element_type") == "bus":
                    bid = int(item["element_id"])
                    if bid in pos:
                        x, y = pos[bid]
                        ax.text(x, y + desloc_base, letra,
                                color=cor, fontsize=10, ha="center")
                elif item.get("element_type") == "gen":
                    gid = int(item["element_id"])
                    gen = net_data.get("gen", {}).get(str(gid))
                    if gen:
                        bid = int(gen["bus"])
                        if bid in pos:
                            x, y = pos[bid]
                            ax.text(x, y + desloc_base, letra,
                                    color=cor, fontsize=10, ha="center")
            except Exception as e:
                print(f"[!] Erro ao plotar {tipo[:-1]} {item}: {e}")

    for gid, gen in net_data.get("gen", {}).items():
        try:
            bid = int(gen["bus"])
            if bid in pos:
                x, y = pos[bid]
                ax.text(x, y + 8, "G", color="black", fontsize=10, ha="center")
        except Exception as e:
            print(f"[!] Erro ao plotar gerador {gid}: {e}")

    ax.set_title(
        "Topologia IEEE 14 Barras com Dispositivos de Proteção", fontsize=15)
    ax.axis("off")

    legenda = [
        mpatches.Patch(color="blue", label="Relés 51 / 67 / 27-59"),
        mpatches.Patch(
            color="purple", label="Relés 87T (diferencial)", linewidth=2),
        mpatches.Patch(color="darkgreen", label="Disjuntores (D)"),
        mpatches.Patch(color="orange", label="Fusíveis (F)"),
        mpatches.Patch(color="black", label="Linhas"),
        mpatches.Patch(edgecolor="red", facecolor="none",
                       label="Transformadores", linewidth=2)
    ]
    ax.legend(handles=legenda, loc="lower center",
              fontsize=10, bbox_to_anchor=(0.5, -0.1), ncol=3)

    out_path = Path(__file__).resolve(
    ).parents[2] / "docs" / "ieee14_topologia_protecao.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"✅ Figura salva em: {out_path}")
    plt.show()


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    json_candidates = [
        base_dir / "data" / "ieee14_protecao.json",
        base_dir.parent / "data" / "ieee14_protecao.json",
        base_dir.parent.parent / "data" / "ieee14_protecao.json"
    ]
    json_path = next((p for p in json_candidates if p.exists()), None)

    if not json_path:
        raise FileNotFoundError(
            "Nenhum arquivo ieee14_protecao.json encontrado nos caminhos esperados.")

    net_data = carregar_dados_json(json_path)
    grafo = montar_grafo(net_data)
    plotar_grafo(grafo, net_data)
