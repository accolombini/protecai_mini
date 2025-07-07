#!/usr/bin/env python3
"""
Verificação da integridade dos dados do PandaPower no arquivo ieee14_protecao.json
"""
import json
import pandas as pd
import sys
from pathlib import Path


def verify_pandapower_data(file_path):
    """Verifica a integridade dos dados do PandaPower"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print("=" * 60)
        print("VERIFICAÇÃO DA INTEGRIDADE - PANDAPOWER DATA")
        print("=" * 60)

        # Extrair dados do PandaPower
        if 'pandapower_net' not in data:
            print("ERRO: pandapower_net não encontrado!")
            return False

        pandapower_str = data['pandapower_net']
        print(f"   - Tamanho da string JSON: {len(pandapower_str)} caracteres")

        try:
            net_data = json.loads(pandapower_str)
            print("   - Parsing JSON bem-sucedido")
        except json.JSONDecodeError as e:
            print(f"   - ERRO no parsing JSON: {e}")
            return False

        # Verificar estrutura básica
        print("\n1. ESTRUTURA BÁSICA:")
        print(f"   - Módulo: {net_data.get('_module', 'N/A')}")
        print(f"   - Classe: {net_data.get('_class', 'N/A')}")
        print(f"   - Versão: {net_data.get('version', 'N/A')}")
        print(f"   - Nome da rede: {net_data.get('name', 'N/A')}")
        print(f"   - Frequência: {net_data.get('f_hz', 'N/A')} Hz")
        print(f"   - Potência base: {net_data.get('sn_mva', 'N/A')} MVA")

        # Verificar elementos principais
        elements = ['bus', 'line', 'trafo', 'load', 'ext_grid', 'gen', 'sgen']

        print("\n2. ELEMENTOS DO SISTEMA:")
        for element in elements:
            if element in net_data:
                try:
                    element_data = json.loads(net_data[element]['_object'])
                    rows = len(element_data['data'])
                    cols = len(element_data['columns'])
                    print(
                        f"   - {element.upper()}: {rows} elementos, {cols} colunas")

                    if rows > 0:
                        print(f"     * Colunas: {element_data['columns']}")
                        print(
                            f"     * Primeira linha: {element_data['data'][0]}")

                        # Verificações específicas
                        if element == 'bus':
                            bus_names = [row[0]
                                         for row in element_data['data']]
                            print(f"     * Nomes das barras: {bus_names}")

                        elif element == 'line':
                            line_names = [row[0]
                                          for row in element_data['data']]
                            print(f"     * Nomes das linhas: {line_names}")

                        elif element == 'trafo':
                            trafo_names = [row[0]
                                           for row in element_data['data']]
                            print(
                                f"     * Nomes dos transformadores: {trafo_names}")

                        elif element == 'load':
                            load_names = [row[0]
                                          for row in element_data['data']]
                            print(f"     * Nomes das cargas: {load_names}")

                        elif element == 'ext_grid':
                            gen_names = [row[0]
                                         for row in element_data['data']]
                            print(f"     * Nomes dos geradores: {gen_names}")

                except Exception as e:
                    print(f"   - {element.upper()}: ERRO ao processar - {e}")
            else:
                print(f"   - {element.upper()}: Não encontrado")

        # Verificar conectividade
        print("\n3. VERIFICAÇÃO DE CONECTIVIDADE:")

        # Extrair dados de barras e linhas
        try:
            bus_data = json.loads(net_data['bus']['_object'])
            line_data = json.loads(net_data['line']['_object'])

            # Verificar se todas as barras referenciadas nas linhas existem
            bus_count = len(bus_data['data'])
            line_count = len(line_data['data'])

            print(f"   - Total de barras: {bus_count}")
            print(f"   - Total de linhas: {line_count}")

            # Verificar índices das barras nas linhas
            from_bus_col = line_data['columns'].index('from_bus')
            to_bus_col = line_data['columns'].index('to_bus')

            valid_connections = 0
            for line in line_data['data']:
                from_bus = line[from_bus_col]
                to_bus = line[to_bus_col]

                if 0 <= from_bus < bus_count and 0 <= to_bus < bus_count:
                    valid_connections += 1
                else:
                    print(
                        f"     * ERRO: Linha {line[0]} conecta barras inválidas: {from_bus} -> {to_bus}")

            print(f"   - Conexões válidas: {valid_connections}/{line_count}")

        except Exception as e:
            print(f"   - ERRO na verificação de conectividade: {e}")

        # Verificar transformadores
        print("\n4. VERIFICAÇÃO DE TRANSFORMADORES:")
        try:
            trafo_data = json.loads(net_data['trafo']['_object'])
            trafo_count = len(trafo_data['data'])

            if trafo_count > 0:
                hv_bus_col = trafo_data['columns'].index('hv_bus')
                lv_bus_col = trafo_data['columns'].index('lv_bus')

                print(f"   - Total de transformadores: {trafo_count}")

                for trafo in trafo_data['data']:
                    hv_bus = trafo[hv_bus_col]
                    lv_bus = trafo[lv_bus_col]
                    trafo_name = trafo[0]

                    if 0 <= hv_bus < bus_count and 0 <= lv_bus < bus_count:
                        print(
                            f"     * {trafo_name}: {hv_bus} -> {lv_bus} (OK)")
                    else:
                        print(
                            f"     * {trafo_name}: {hv_bus} -> {lv_bus} (ERRO)")
            else:
                print("   - Nenhum transformador encontrado")

        except Exception as e:
            print(f"   - ERRO na verificação de transformadores: {e}")

        # Verificar cargas
        print("\n5. VERIFICAÇÃO DE CARGAS:")
        try:
            load_data = json.loads(net_data['load']['_object'])
            load_count = len(load_data['data'])

            if load_count > 0:
                bus_col = load_data['columns'].index('bus')
                p_col = load_data['columns'].index('p_mw')
                q_col = load_data['columns'].index('q_mvar')

                print(f"   - Total de cargas: {load_count}")

                total_p = 0
                total_q = 0

                for load in load_data['data']:
                    bus = load[bus_col]
                    p_mw = load[p_col]
                    q_mvar = load[q_col]
                    load_name = load[0]

                    total_p += p_mw
                    total_q += q_mvar

                    if 0 <= bus < bus_count:
                        print(
                            f"     * {load_name}: Bus {bus}, P={p_mw} MW, Q={q_mvar} MVar (OK)")
                    else:
                        print(
                            f"     * {load_name}: Bus {bus} (ERRO - barra inválida)")

                print(
                    f"   - Potência total: P={total_p:.1f} MW, Q={total_q:.1f} MVar")
            else:
                print("   - Nenhuma carga encontrada")

        except Exception as e:
            print(f"   - ERRO na verificação de cargas: {e}")

        print("\n" + "=" * 60)
        print("VERIFICAÇÃO CONCLUÍDA!")
        print("=" * 60)

        return True

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

    # Executar verificação
    success = verify_pandapower_data(json_file)

    if not success:
        sys.exit(1)
