#!/usr/bin/env python3
"""
Script para testar especificamente o endpoint de compliance do dashboard.
"""
import requests
import json

def test_dashboard_compliance():
    """Testa o endpoint de compliance que o dashboard usa."""
    
    # URL correta do endpoint de compliance
    url = "http://localhost:8000/api/v1/protection/compliance/check"
    
    # Payload padrão (mesma estrutura que o frontend usa)
    payload = {
        "standards": ["IEC_61850", "IEEE_C37_112", "NBR_5410", "API_RP_14C"],
        "check_all": True
    }
    
    try:
        print("🔍 Testando endpoint de compliance do dashboard...")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload)
        
        print(f"\n📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Resposta recebida:")
            print(json.dumps(data, indent=2, default=str))
            
            # Analisar especificamente NBR 5410
            if "standards" in data:
                nbr_data = data["standards"].get("NBR_5410", {})
                print(f"\n🎯 NBR 5410 Detalhes:")
                print(f"  - Compliant: {nbr_data.get('compliant', 'N/A')}")
                print(f"  - Score: {nbr_data.get('score', 'N/A')}")
                print(f"  - Issues: {nbr_data.get('issues', [])}")
                print(f"  - Details: {nbr_data.get('details', 'N/A')}")
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_dashboard_compliance()
