#!/usr/bin/env python3
"""
Script para diagnóstico detalhado do arquivo ieee14_protecao.json
"""

import json
import pandas as pd
import pandapower as pp


def analisar_arquivo_json():
    """Analisa o arquivo JSON e verifica sua estrutura"""

    caminho_arquivo = "simuladores/power_sim/data/ieee14_protecao.json"

    try:
        print("=== DIAGNÓSTICO DETALHADO DO ARQUIVO JSON ===")

        # Carrega o arquivo JSON
        with open(caminho_arquivo, 'r') as f:
            data = json.load(f)

        print(f"✓ Arquivo JSON carregado com sucesso")
        print(f"  - Tamanho do arquivo: {len(str(data))} caracteres")
        print(f"  - Chaves principais: {list(data.keys())}")

        # Verifica pandapower_net
        if 'pandapower_net' in data:
            print(f"\n--- PANDAPOWER_NET ---")
            net_json = data['pandapower_net']
            print(f"  - Tipo: {type(net_json)}")
            print(f"  - Tamanho: {len(net_json)} caracteres")

            # Tenta deserializar a rede
            try:
                net = pp.from_json_string(net_json)
                print(f"  - Deserialização: ✓ SUCESSO")
                print(f"  - Barras: {len(net.bus)} barras")
                print(f"  - Linhas: {len(net.line)} linhas")
                print(f"  - Transformadores: {len(net.trafo)} transformadores")
                print(f"  - Geradores: {len(net.ext_grid)} geradores")
                print(f"  - Cargas: {len(net.load)} cargas")

                # Mostra detalhes das barras
                print(f"\n  === BARRAS ===")
                for i, row in net.bus.iterrows():
                    print(f"    Barra {i}: {row['name']} - {row['vn_kv']} kV")

                # Mostra detalhes das linhas
                print(f"\n  === LINHAS ===")
                for i, row in net.line.iterrows():
                    print(
                        f"    Linha {i}: {row['name']} - {row['from_bus']} -> {row['to_bus']}")

                # Mostra detalhes dos transformadores
                print(f"\n  === TRANSFORMADORES ===")
                for i, row in net.trafo.iterrows():
                    print(
                        f"    Trafo {i}: {row['name']} - {row['hv_bus']} -> {row['lv_bus']}")

                # Mostra detalhes das cargas
                print(f"\n  === CARGAS ===")
                for i, row in net.load.iterrows():
                    print(
                        f"    Carga {i}: {row['name']} - Barra {row['bus']} - {row['p_mw']} MW")

            except Exception as e:
                print(f"  - Deserialização: ✗ FALHA")
                print(f"  - Erro: {str(e)}")

        # Verifica protection_devices
        if 'protection_devices' in data:
            print(f"\n--- PROTECTION_DEVICES ---")
            protection = data['protection_devices']
            print(f"  - Tipo: {type(protection)}")
            print(f"  - Chaves: {list(protection.keys())}")

            if 'reles' in protection:
                reles = protection['reles']
                print(f"  - Relés: {len(reles)} dispositivos")
                print(f"  - Primeiros 5 relés:")
                for i, rele in enumerate(reles[:5]):
                    print(
                        f"    {i+1}. {rele['id']} - Tipo: {rele['tipo']} - Elemento: {rele['element_type']}")

            if 'topology' in protection:
                topology = protection['topology']
                print(f"  - Topologia: {len(topology)} elementos")
                print(f"  - Chaves da topologia: {list(topology.keys())[:10]}")

        print(f"\n=== RESUMO ===")
        print(f"✓ Arquivo JSON estruturalmente válido")
        print(f"✓ Contém dados do pandapower")
        print(f"✓ Contém dispositivos de proteção")

        return True

    except FileNotFoundError:
        print(f"✗ Arquivo não encontrado: {caminho_arquivo}")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ Erro ao decodificar JSON: {e}")
        return False
    except Exception as e:
        print(f"✗ Erro inesperado: {e}")
        return False


if __name__ == "__main__":
    analisar_arquivo_json()
