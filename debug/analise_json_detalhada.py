#!/usr/bin/env python3
"""
Análise detalhada da estrutura do arquivo ieee14_protecao.json
"""
import json
import pandas as pd
import sys
from pathlib import Path


def analyze_json_structure(file_path):
    """Analisa a estrutura do arquivo JSON de proteção"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print("=" * 60)
        print("ANÁLISE DETALHADA - ieee14_protecao.json")
        print("=" * 60)

        # Verificar estrutura principal
        print("\n1. ESTRUTURA PRINCIPAL:")
        print(f"   - Chaves principais: {list(data.keys())}")

        # Analisar pandapower_net
        print("\n2. PANDAPOWER NETWORK:")
        if 'pandapower_net' in data:
            print("   - Pandapower_net encontrado (é uma string JSON)")
            try:
                # Tentar deserializar a string JSON
                net_data = json.loads(data['pandapower_net'])
                print(f"   - Tipo: {type(net_data)}")
                print(f"   - Chaves do objeto: {list(net_data.keys())}")

                # Verificar elementos principais
                if 'bus' in net_data:
                    bus_data = json.loads(net_data['bus']['_object'])
                    print(f"   - Número de barras: {len(bus_data['data'])}")
                    print(
                        f"   - Nomes das barras: {[row[0] for row in bus_data['data']]}")

                if 'line' in net_data:
                    line_data = json.loads(net_data['line']['_object'])
                    print(f"   - Número de linhas: {len(line_data['data'])}")
                    print(
                        f"   - Nomes das linhas: {[row[0] for row in line_data['data']]}")

                if 'trafo' in net_data:
                    trafo_data = json.loads(net_data['trafo']['_object'])
                    print(
                        f"   - Número de transformadores: {len(trafo_data['data'])}")
                    print(
                        f"   - Nomes dos transformadores: {[row[0] for row in trafo_data['data']]}")

                if 'load' in net_data:
                    load_data = json.loads(net_data['load']['_object'])
                    print(f"   - Número de cargas: {len(load_data['data'])}")
                    print(
                        f"   - Nomes das cargas: {[row[0] for row in load_data['data']]}")

                if 'ext_grid' in net_data:
                    ext_grid_data = json.loads(net_data['ext_grid']['_object'])
                    print(
                        f"   - Número de geradores: {len(ext_grid_data['data'])}")
                    if ext_grid_data['data']:
                        print(
                            f"   - Nome do gerador: {ext_grid_data['data'][0][0]}")

            except Exception as e:
                print(f"   - ERRO ao deserializar pandapower_net: {e}")
        else:
            print("   - ERRO: pandapower_net não encontrado!")

        # Analisar dispositivos de proteção
        print("\n3. DISPOSITIVOS DE PROTEÇÃO:")
        if 'protection_devices' in data:
            prot_devices = data['protection_devices']

            if 'reles' in prot_devices:
                reles = prot_devices['reles']
                print(f"   - Número de relés: {len(reles)}")

                # Contar por tipo
                tipos_reles = {}
                for rele in reles:
                    tipo = rele.get('tipo', 'N/A')
                    tipos_reles[tipo] = tipos_reles.get(tipo, 0) + 1

                print("   - Tipos de relés:")
                for tipo, count in tipos_reles.items():
                    print(f"     * {tipo}: {count} unidades")

                # Mostrar alguns exemplos
                print("\n   - Exemplos de relés:")
                for i, rele in enumerate(reles[:5]):  # Primeiros 5
                    print(
                        f"     * {rele['id']}: {rele['tipo']} - {rele['element_type']} {rele['element_id']}")

            if 'disjuntores' in prot_devices:
                disjuntores = prot_devices['disjuntores']
                print(f"   - Número de disjuntores: {len(disjuntores)}")

                # Contar por status
                status_count = {}
                for disj in disjuntores:
                    status = disj.get('status', 'N/A')
                    status_count[status] = status_count.get(status, 0) + 1

                print("   - Status dos disjuntores:")
                for status, count in status_count.items():
                    print(f"     * {status}: {count} unidades")

            if 'fusíveis' in prot_devices:
                fusiveis = prot_devices['fusíveis']
                print(f"   - Número de fusíveis: {len(fusiveis)}")
        else:
            print("   - ERRO: protection_devices não encontrado!")

        # Analisar zonas de proteção
        print("\n4. ZONAS DE PROTEÇÃO:")
        if 'protection_zones' in data:
            zones = data['protection_zones']
            print(f"   - Número de zonas: {len(zones)}")

            for zone in zones:
                print(f"   - {zone['nome']}: {zone['tipo']}")
                print(f"     * Transformador ID: {zone['transformador_id']}")
                print(
                    f"     * Barras: {zone['barras']} (IEEE: {zone['barras_ieee']})")
                print(f"     * Proteção primária: {zone['protecao_primaria']}")
                print(f"     * Proteção backup: {zone['protecao_backup']}")
        else:
            print("   - ERRO: protection_zones não encontrado!")

        # Analisar geodata
        print("\n5. DADOS GEOGRÁFICOS:")
        if 'bus_geodata' in data:
            geodata = data['bus_geodata']
            print(f"   - Número de barras com coordenadas: {len(geodata)}")
            print(f"   - IDs das barras: {list(geodata.keys())}")

        if 'line_geodata' in data:
            line_geodata = data['line_geodata']
            print(
                f"   - Número de linhas com coordenadas: {len(line_geodata)}")
            print(f"   - IDs das linhas: {list(line_geodata.keys())}")

        print("\n" + "=" * 60)
        print("ANÁLISE CONCLUÍDA COM SUCESSO!")
        print("=" * 60)

        return True

    except FileNotFoundError:
        print(f"ERRO: Arquivo não encontrado: {file_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"ERRO: Arquivo JSON inválido: {e}")
        return False
    except Exception as e:
        print(f"ERRO: {e}")
        return False


if __name__ == "__main__":
    # Caminho para o arquivo
    json_file = Path(__file__).parent / "simuladores" / \
        "power_sim" / "data" / "ieee14_protecao.json"

    if not json_file.exists():
        print(f"ERRO: Arquivo não encontrado: {json_file}")
        sys.exit(1)

    # Executar análise
    success = analyze_json_structure(json_file)

    if not success:
        sys.exit(1)
