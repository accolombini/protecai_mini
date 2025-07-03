'''
    Esse script realiza as seguintes verificações no arquivo ieee14_protecao.json:

    ✅ Existência do arquivo
    ✅ Presença de barras e conexões (linhas ou transformadores)
    ✅ Estrutura esperada dos dispositivos de proteção (relés, disjuntores e fusíveis)
    ✅ Zonas de proteção corretamente definidas (com exatamente duas barras)
    ✅ Ausência de barras isoladas na rede
    ✅ Estrutura válida da rede (pandapowerNet)
        ||> Execute com pytest para verificar as condições acima.
              |> Exemplo de execução: pytest tests/test_ieee14_json.py   

'''

# test_ieee14_json.py

"""
Testes automatizados para verificar a consistência do arquivo ieee14_protecao.json
"""

import pytest
import pandapower as pp
from pathlib import Path


def carregar_rede():
    json_path = Path(__file__).resolve(
    ).parents[1] / "simuladores" / "power_sim" / "data" / "ieee14_protecao.json"
    if not json_path.exists():
        raise FileNotFoundError(f"❌ Arquivo não encontrado: {json_path}")
    
    # Carrega o JSON customizado
    import json
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extrai a rede PandaPower da string JSON
    rede = pp.from_json_string(data["pandapower_net"])
    
    # Adiciona os dados de proteção à rede para compatibilidade com os testes
    rede.protection_devices = data["protection_devices"]
    if "protection_zones" in data:
        rede.protection_zones = data["protection_zones"]
    
    return rede


@pytest.fixture(scope="module")
def rede():
    return carregar_rede()


def test_estrutura_geral(rede):
    assert hasattr(rede, "bus"), "Tabela 'bus' ausente."
    assert hasattr(rede, "line"), "Tabela 'line' ausente."
    assert hasattr(rede, "trafo"), "Tabela 'trafo' ausente."
    assert hasattr(
        rede, "protection_devices"), "Campo 'protection_devices' ausente."


def test_dispositivos_de_protecao(rede):
    dispositivos = rede.protection_devices
    assert isinstance(dispositivos, dict), "Dispositivos de proteção devem ser um dicionário."
    
    # Verifica se as categorias principais existem
    assert "reles" in dispositivos, "Relés ausentes."
    assert "disjuntores" in dispositivos, "Disjuntores ausentes."
    assert "fusiveis" in dispositivos, "Fusíveis ausentes."
    
    # Verifica relés
    for i, rele in enumerate(dispositivos["reles"]):
        assert "id" in rele, f"Relé {i} sem campo 'id'."
        assert "element_type" in rele, f"Relé {i} sem campo 'element_type'."
        assert "element_id" in rele, f"Relé {i} sem campo 'element_id'."
    
    # Verifica disjuntores
    for i, disj in enumerate(dispositivos["disjuntores"]):
        assert "id" in disj, f"Disjuntor {i} sem campo 'id'."
        assert "element_type" in disj, f"Disjuntor {i} sem campo 'element_type'."
        assert "element_id" in disj, f"Disjuntor {i} sem campo 'element_id'."
    
    # Verifica fusíveis
    for i, fus in enumerate(dispositivos["fusiveis"]):
        assert "id" in fus, f"Fusível {i} sem campo 'id'."
        assert "element_type" in fus, f"Fusível {i} sem campo 'element_type'."
        assert "element_id" in fus, f"Fusível {i} sem campo 'element_id'."


def test_zonas_de_protecao(rede):
    # Se não há zonas de proteção definidas, pula o teste
    if not hasattr(rede, "protection_zones") or rede.protection_zones is None:
        pytest.skip("Zonas de proteção não implementadas ainda")
    
    zonas = rede.protection_zones
    for zona in zonas:
        assert "nome" in zona and zona["nome"], "Zona sem nome."
        assert "barras" in zona and isinstance(
            zona["barras"], list), "Zona sem lista de barras."
        if len(zona["barras"]) != 2:
            print(
                f"⚠️ Zona '{zona.get('nome')}' possui {len(zona['barras'])} barra(s): {zona['barras']}")
        assert len(
            zona["barras"]) == 2, f"Zona '{zona.get('nome')}' não conecta exatamente 2 barras."


def test_barras_conectadas(rede):
    # Barras conectadas por linhas e transformadores
    conectadas = set(rede.line.from_bus).union(set(rede.line.to_bus))
    conectadas |= set(rede.trafo.hv_bus).union(set(rede.trafo.lv_bus))
    
    # Verifica se há barras isoladas
    for idx in rede.bus.index:
        if idx not in conectadas:
            print(f"⚠️ Barra {idx} está isolada.")
        assert idx in conectadas, f"Barra {idx} está isolada na topologia."


def test_rede_valida(rede):
    assert isinstance(
        rede, pp.pandapowerNet), "Rede não é um objeto pandapowerNet."
    assert len(rede.bus) > 0, "Rede sem barras."
    assert len(rede.line) + len(rede.trafo) > 0, "Rede sem conexões."


def test_arquivo_existe():
    json_path = Path(__file__).resolve(
    ).parents[1] / "simuladores" / "power_sim" / "data" / "ieee14_protecao.json"
    assert json_path.exists(), f"Arquivo {json_path} não encontrado."
