#!/usr/bin/env python3
"""
Script para corrigir problemas de compatibilidade entre versões do PandaPower

Problemas identificados:
1. Arquivos JSON com formato incorreto (falta version e format_version)
2. Incompatibilidade entre PandaPower 2.14.1 e 3.1.2
3. Métodos de importação/exportação mudaram

Este script resolve estes problemas.
"""

import os
import json
import pandas as pd
import pandapower as pp
import pandapower.networks as nw
from pathlib import Path


def fix_json_format_compatibility():
    """
    Corrige problemas de compatibilidade com arquivos JSON do PandaPower.
    
    O principal problema é que o arquivo ieee14_protecao.json foi gerado
    com uma versão mais antiga e não tem os campos necessários para a v3.1.2
    """
    print("🔧 Corrigindo compatibilidade do PandaPower...")
    
    # Caminho para os arquivos JSON
    data_dir = Path("simuladores/power_sim/data")
    json_files = [
        data_dir / "ieee14.json",
        data_dir / "ieee14_protecao.json"
    ]
    
    for json_file in json_files:
        if json_file.exists():
            print(f"🔍 Verificando: {json_file}")
            
            try:
                # Tentar carregar com pandapower primeiro
                net = pp.from_json(str(json_file))
                print(f"✅ {json_file.name} está OK")
                
            except Exception as e:
                print(f"❌ Erro em {json_file.name}: {e}")
                
                # Tentar corrigir o arquivo
                print(f"🔧 Tentando corrigir {json_file.name}...")
                
                # Fazer backup
                backup_file = json_file.with_suffix('.json.backup')
                if not backup_file.exists():
                    json_file.rename(backup_file)
                    print(f"💾 Backup criado: {backup_file}")
                
                # Recriar o arquivo usando a rede case14 padrão
                if "ieee14" in json_file.name:
                    regenerate_ieee14_json(json_file)
                elif "protecao" in json_file.name:
                    regenerate_protecao_json(json_file)


def regenerate_ieee14_json(output_path):
    """Regenera o arquivo IEEE14 com a versão atual do PandaPower"""
    print("🔄 Regenerando IEEE14 base...")
    
    # Usar a rede IEEE14 padrão do pandapower
    net = nw.case14()
    
    # Adicionar informações de versão
    net.version = pp.__version__
    net.format_version = "3.0.0"
    
    # Salvar
    pp.to_json(net, str(output_path))
    print(f"✅ {output_path.name} regenerado com sucesso!")


def regenerate_protecao_json(output_path):
    """Regenera o arquivo IEEE14 com dispositivos de proteção"""
    print("🔄 Regenerando IEEE14 com proteção...")
    
    # Usar a rede IEEE14 padrão do pandapower
    net = nw.case14()
    
    # Adicionar geodata básico
    add_basic_geodata(net)
    
    # Adicionar dispositivos de proteção customizados
    add_protection_devices(net)
    
    # Adicionar informações de versão
    net.version = pp.__version__
    net.format_version = "3.0.0"
    
    # Salvar
    pp.to_json(net, str(output_path))
    print(f"✅ {output_path.name} regenerado com sucesso!")


def add_basic_geodata(net):
    """Adiciona coordenadas básicas para visualização"""
    import numpy as np
    
    n_buses = len(net.bus)
    angles = np.linspace(0, 2 * np.pi, n_buses, endpoint=False)
    
    # Geodata para barras
    net.bus_geodata = pd.DataFrame({
        "x": 100 * np.cos(angles),
        "y": 100 * np.sin(angles)
    })
    
    # Geodata para linhas
    line_coords = []
    for _, line in net.line.iterrows():
        from_bus = line.from_bus
        to_bus = line.to_bus
        from_coords = (net.bus_geodata.iloc[from_bus].x, net.bus_geodata.iloc[from_bus].y)
        to_coords = (net.bus_geodata.iloc[to_bus].x, net.bus_geodata.iloc[to_bus].y)
        line_coords.append([from_coords, to_coords])
    
    net.line_geodata = pd.DataFrame({"coords": line_coords})


def add_protection_devices(net):
    """Adiciona dispositivos de proteção à rede"""
    
    # Adicionar atributo customizado para dispositivos de proteção
    protection_devices = {
        "reles": [
            {
                "tipo": "51",
                "id": f"RELE_51_L{i}",
                "element_type": "line",
                "element_id": i,
                "curva": "IEC",
                "pickup": 1.2,
                "tempo_atuacao": 0.2
            }
            for i in range(min(5, len(net.line)))  # Primeiras 5 linhas
        ],
        "disjuntores": [
            {
                "nome": f"DISJ_B{i+1}",
                "barra": i,
                "element_type": "bus",
                "element_id": i
            }
            for i in range(min(6, len(net.bus)))  # Primeiras 6 barras
        ],
        "fusiveis": [
            {
                "nome": f"FUSIVEL_B{i+7}",
                "barra": i+6,
                "element_type": "bus",
                "element_id": i+6
            }
            for i in range(min(4, len(net.bus)-6))  # Próximas 4 barras
        ]
    }
    
    # Adicionar como atributo customizado
    net.protection_devices = protection_devices


def check_pandapower_version():
    """Verifica a versão do PandaPower e mostra informações de compatibilidade"""
    print(f"📦 PandaPower versão: {pp.__version__}")
    
    # Verificar se é a versão esperada
    expected_version = "3.1.2"
    if pp.__version__ == expected_version:
        print(f"✅ Versão correta: {expected_version}")
    else:
        print(f"⚠️ Versão diferente da esperada: {expected_version}")
        print("💡 Execute: pip install pandapower==3.1.2")


def test_basic_functionality():
    """Testa funcionalidades básicas do PandaPower"""
    print("\n🧪 Testando funcionalidades básicas...")
    
    try:
        # Teste 1: Criar rede simples
        net = pp.create_empty_network()
        bus1 = pp.create_bus(net, vn_kv=20.)
        bus2 = pp.create_bus(net, vn_kv=0.4)
        trafo = pp.create_transformer(net, bus1, bus2, std_type="0.4 MVA 20/0.4 kV")
        load = pp.create_load(net, bus2, p_mw=0.1)
        ext_grid = pp.create_ext_grid(net, bus1)
        
        print("✅ Criação de rede: OK")
        
        # Teste 2: Executar fluxo de carga
        pp.runpp(net)
        print("✅ Fluxo de carga: OK")
        
        # Teste 3: Salvar/carregar JSON
        temp_path = "temp_test.json"
        pp.to_json(net, temp_path)
        net_loaded = pp.from_json(temp_path)
        os.remove(temp_path)
        print("✅ Salvar/carregar JSON: OK")
        
        print("🎉 Todos os testes passaram!")
        
    except Exception as e:
        print(f"❌ Erro nos testes: {e}")
        return False
    
    return True


def main():
    print("🚀 Iniciando correção de compatibilidade do PandaPower")
    print("=" * 60)
    
    # Verificar versão
    check_pandapower_version()
    
    # Testar funcionalidades básicas
    if not test_basic_functionality():
        print("❌ Testes básicos falharam. Verifique a instalação do PandaPower.")
        return
    
    # Corrigir arquivos JSON
    fix_json_format_compatibility()
    
    print("\n" + "=" * 60)
    print("✅ Correção concluída!")
    print("\n📝 Próximos passos:")
    print("1. Execute: python -m pytest tests/ -v")
    print("2. Execute: python main.py")
    print("3. Se houver erros, revise os arquivos de proteção elétrica")


if __name__ == "__main__":
    main()
