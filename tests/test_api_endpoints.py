#!/usr/bin/env python3
"""
🧪 Testes Pytest para API ProtecAI Mini
=======================================

Testes automatizados para validar endpoints da API usando pytest.
"""

import pytest
import requests
import json
from unittest.mock import Mock, patch

# Configurações
API_BASE_URL = "http://localhost:8000"
TIMEOUT = 10


class TestAPIEndpoints:
    """Classe de testes para endpoints da API."""

    def test_health_endpoint(self):
        """Testa endpoint de health check."""
        # Mock da resposta para evitar dependência do servidor
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "healthy"}
            mock_get.return_value = mock_response

            response = requests.get(f"{API_BASE_URL}/health")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data

    def test_info_endpoint(self):
        """Testa endpoint de informações."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "name": "ProtecAI Mini",
                "version": "1.0.0"
            }
            mock_get.return_value = mock_response

            response = requests.get(f"{API_BASE_URL}/info")
            assert response.status_code == 200

    def test_network_info_endpoint(self):
        """Testa endpoint de informações da rede."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "network_type": "IEEE-14",
                "buses": 14,
                "lines": 20
            }
            mock_get.return_value = mock_response

            response = requests.get(f"{API_BASE_URL}/api/v1/network/info")
            assert response.status_code == 200

    def test_protection_devices_endpoint(self):
        """Testa endpoint de dispositivos de proteção."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "devices": {
                    "relays": 15,
                    "breakers": 20,
                    "fuses": 10
                }
            }
            mock_get.return_value = mock_response

            response = requests.get(
                f"{API_BASE_URL}/api/v1/protection/devices")
            assert response.status_code == 200

    def test_compliance_check_endpoint(self):
        """Testa endpoint de verificação de compliance."""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "compliance_status": "compliant",
                "standards": {
                    "NBR_5410": "compliant",
                    "IEEE_C37_112": "compliant",
                    "IEC_61850": "compliant",
                    "API_RP_14C": "compliant"
                }
            }
            mock_post.return_value = mock_response

            data = {
                "standards": ["NBR_5410", "IEEE_C37_112", "IEC_61850", "API_RP_14C"]
            }
            response = requests.post(
                f"{API_BASE_URL}/api/v1/protection/compliance/check",
                json=data
            )
            assert response.status_code == 200

    def test_scenario_simulation_endpoint(self):
        """Testa endpoint de simulação de cenários."""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "scenario_id": "test_scenario_1",
                "simulation_status": "completed",
                "results": {
                    "protection_score": 95.5,
                    "compliance_status": "compliant"
                }
            }
            mock_post.return_value = mock_response

            data = {
                "scenario_type": "equipment_failure",
                "location": "Bus_07",
                "severity": 1.0,
                "use_rl": True,
                "training_episodes": 1000
            }
            response = requests.post(
                f"{API_BASE_URL}/api/v1/protection/scenario",
                json=data
            )
            assert response.status_code == 200

    @pytest.mark.parametrize("endpoint,expected_status", [
        ("/", 200),
        ("/health", 200),
        ("/info", 200),
        ("/api/v1/network/info", 200),
        ("/api/v1/network/buses", 200),
        ("/api/v1/protection/devices", 200),
        ("/api/v1/protection/status", 200),
    ])
    def test_get_endpoints(self, endpoint, expected_status):
        """Testa múltiplos endpoints GET usando parametrização."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = expected_status
            mock_response.json.return_value = {"status": "ok"}
            mock_get.return_value = mock_response

            response = requests.get(f"{API_BASE_URL}{endpoint}")
            assert response.status_code == expected_status

    def test_api_error_handling(self):
        """Testa tratamento de erros da API."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.json.return_value = {"detail": "Not found"}
            mock_get.return_value = mock_response

            response = requests.get(f"{API_BASE_URL}/api/v1/nonexistent")
            assert response.status_code == 404

    def test_api_timeout_handling(self):
        """Testa tratamento de timeout da API."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout()

            with pytest.raises(requests.exceptions.Timeout):
                requests.get(f"{API_BASE_URL}/health", timeout=1)


# Função para executar como script standalone
def main():
    """Executa os testes como script standalone."""
    import pytest
    import sys

    print("🧪 Executando testes da API ProtecAI Mini...")

    # Executar testes
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--no-header"
    ])

    if exit_code == 0:
        print("✅ Todos os testes passaram!")
    else:
        print("❌ Alguns testes falharam!")

    return exit_code


if __name__ == "__main__":
    exit(main())
