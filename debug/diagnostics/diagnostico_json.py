#!/usr/bin/env python3
"""
Script para analisar e diagnosticar o arquivo ieee14_protecao.json
"""

import json
import pandas as pd
from pathlib import Path

def analyze_json_file():
    """Analisa o arquivo JSON e reporta problemas."""
    
    json_path = Path("simuladores/power_sim/data/ieee14_protecao.json")
    
    print("🔍 DIAGNÓSTICO DO ARQUIVO JSON")
    print("=" * 50)
    
    # Verificar se arquivo existe
    if not json_path.exists():
        print(f"❌ Arquivo não encontrado: {json_path}")
        return False
    
    # Verificar tamanho do arquivo
    file_size = json_path.stat().st_size
    print(f"📁 Tamanho do arquivo: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    
    try:
        # Carregar JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ JSON carregado com sucesso")
        print(f"📊 Estrutura principal: {len(data)} seções")
        
        # Mostrar chaves principais
        print("\n🗂️ Chaves principais:")
        for key in data.keys():
            print(f"   - {key}: {type(data[key])}")
        
        # Analisar cada seção
        print("\n📋 ANÁLISE DETALHADA:")
        print("-" * 30)
        
        # 1. Verificar seção pandapower_net
        if "pandapower_net" in data:
            net_data = data["pandapower_net"]
            if isinstance(net_data, str):
                # É string JSON, precisa deserializar
                try:
                    import pandas as pd
                    import pandapower as pp
                    net = pp.from_json_string(net_data)
                    print(f"🏗️ Rede PandaPower (deserializada):")
                    print(f"   - Barras: {len(net.bus)}")
                    print(f"   - Linhas: {len(net.line)}")
                    print(f"   - Transformadores: {len(net.trafo)}")
                    print(f"   - Geradores: {len(net.gen)}")
                    print(f"   - Cargas: {len(net.load)}")
                except Exception as e:
                    print(f"❌ Erro ao deserializar rede: {e}")
            else:
                print(f"❌ pandapower_net não é string JSON: {type(net_data)}")
        else:
            print("❌ Seção 'pandapower_net' não encontrada")
        
        # 2. Verificar bus, line, etc. (formato antigo)
        sections = ["bus", "line", "trafo", "gen", "load"]
        for section in sections:
            if section in data:
                count = len(data[section]) if isinstance(data[section], list) else "não é lista"
                print(f"🔌 {section}: {count}")
        
        # 3. Verificar dispositivos de proteção
        if "protection_devices" in data:
            prot_devices = data["protection_devices"]
            print(f"🛡️ Dispositivos de proteção:")
            if isinstance(prot_devices, dict):
                for device_type, devices in prot_devices.items():
                    count = len(devices) if isinstance(devices, list) else "não é lista"
                    print(f"   - {device_type}: {count}")
            else:
                print(f"   ❌ Não é dicionário: {type(prot_devices)}")
        else:
            print("❌ Seção 'protection_devices' não encontrada")
        
        # 4. Verificar zonas de proteção
        if "protection_zones" in data:
            zones = data["protection_zones"]
            count = len(zones) if isinstance(zones, list) else "não é lista"
            print(f"🏷️ Zonas de proteção: {count}")
        else:
            print("❌ Seção 'protection_zones' não encontrada")
        
        # 5. Verificar metadados
        if "metadata" in data:
            metadata = data["metadata"]
            print(f"📝 Metadados: {type(metadata)}")
            if isinstance(metadata, dict):
                for key, value in metadata.items():
                    print(f"   - {key}: {value}")
        
        print("\n" + "=" * 50)
        
        # Diagnóstico final
        print("🏥 DIAGNÓSTICO:")
        
        # Verificar se há dados da rede
        has_network_data = False
        if "pandapower_net" in data:
            has_network_data = True
            print("✅ Dados da rede encontrados (formato PandaPower)")
        elif any(section in data for section in ["bus", "line", "trafo"]):
            has_network_data = True
            print("⚠️ Dados da rede encontrados (formato legado)")
        else:
            print("❌ Dados da rede NÃO encontrados")
        
        # Verificar dispositivos de proteção
        if "protection_devices" in data:
            print("✅ Dispositivos de proteção encontrados")
        else:
            print("❌ Dispositivos de proteção NÃO encontrados")
        
        # Verificar zonas
        if "protection_zones" in data:
            print("✅ Zonas de proteção encontradas")
        else:
            print("❌ Zonas de proteção NÃO encontradas")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Erro JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def suggest_fix():
    """Sugere como corrigir o problema."""
    print("\n🛠️ SUGESTÕES DE CORREÇÃO:")
    print("=" * 30)
    print("1. Regenerar o arquivo JSON:")
    print("   python simuladores/power_sim/gerar_ieee14_json.py")
    print()
    print("2. Verificar a estrutura esperada:")
    print("   - pandapower_net: string JSON da rede")
    print("   - protection_devices: dict com reles, disjuntores, etc.")
    print("   - protection_zones: lista de zonas")
    print("   - metadata: informações do arquivo")

if __name__ == "__main__":
    success = analyze_json_file()
    if not success:
        suggest_fix()
