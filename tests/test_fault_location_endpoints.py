"""
Testes para endpoints de localização de faltas.
Cobertura completa dos endpoints /api/v1/fault-location/*
"""

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import json


class TestFaultLocationAnalyze:
    """Testes para o endpoint /api/v1/fault-location/analyze"""

    @pytest.mark.asyncio
    async def test_analyze_fault_success(
        self,
        async_client: AsyncClient,
        sample_fault_location_request,
        expected_fault_location_response_structure
    ):
        """Teste de análise de falta com dados válidos."""
        response = await async_client.post(
            "/api/v1/fault-location/analyze",
            json=sample_fault_location_request
        )

        assert response.status_code == 200
        data = response.json()

        # Verificar estrutura da resposta
        for field, field_type in expected_fault_location_response_structure.items():
            assert field in data
            if isinstance(field_type, tuple):
                assert isinstance(data[field], field_type)
            else:
                assert isinstance(data[field], field_type)

        # Verificar valores específicos
        assert data["accuracy_confidence"] >= 0.0
        assert data["accuracy_confidence"] <= 1.0
        assert "fault_location" in data
        assert len(data["impact_zones"]) > 0
        assert "fault_id" in data["fault_location"]

    @pytest.mark.asyncio
    async def test_analyze_fault_missing_voltage_measurements(
        self,
        async_client: AsyncClient,
        sample_fault_location_request
    ):
        """Teste com medições de tensão ausentes."""
        request_data = sample_fault_location_request.copy()
        del request_data["voltage_measurements"]

        response = await async_client.post(
            "/api/v1/fault-location/analyze",
            json=request_data
        )

        assert response.status_code == 422
        error_data = response.json()
        assert "voltage_measurements" in str(error_data["detail"])

    @pytest.mark.asyncio
    async def test_analyze_fault_missing_current_measurements(
        self,
        async_client: AsyncClient,
        sample_fault_location_request
    ):
        """Teste com medições de corrente ausentes."""
        request_data = sample_fault_location_request.copy()
        del request_data["current_measurements"]

        response = await async_client.post(
            "/api/v1/fault-location/analyze",
            json=request_data
        )

        assert response.status_code == 422
        error_data = response.json()
        assert "current_measurements" in str(error_data["detail"])

    @pytest.mark.asyncio
    async def test_analyze_fault_invalid_fault_type(
        self,
        async_client: AsyncClient,
        sample_fault_location_request
    ):
        """Teste com tipo de falta inválido."""
        request_data = sample_fault_location_request.copy()
        request_data["fault_type"] = "invalid_fault_type"

        response = await async_client.post(
            "/api/v1/fault-location/analyze",
            json=request_data
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_analyze_fault_empty_sequence_of_events(
        self,
        async_client: AsyncClient,
        sample_fault_location_request
    ):
        """Teste com sequência de eventos vazia."""
        request_data = sample_fault_location_request.copy()
        request_data["sequence_of_events"] = []

        response = await async_client.post(
            "/api/v1/fault-location/analyze",
            json=request_data
        )

        assert response.status_code == 422


class TestFaultLocationZones:
    """Testes para o endpoint /api/v1/fault-location/zones/{fault_id}"""

    @pytest.mark.asyncio
    async def test_get_fault_zones_success(self, async_client: AsyncClient):
        """Teste de obtenção de zonas afetadas por falta."""
        fault_id = "fault_test_001"

        response = await async_client.get(f"/api/v1/fault-location/zones/{fault_id}")

        assert response.status_code == 200
        data = response.json()

        # Verificar estrutura da resposta
        assert "fault_id" in data
        assert "affected_zones" in data
        assert "zone_analysis" in data
        assert "protection_coordination" in data
        assert "recommendations" in data

        # Verificar tipos
        assert isinstance(data["affected_zones"], list)
        assert isinstance(data["zone_analysis"], dict)
        assert isinstance(data["protection_coordination"], dict)
        assert isinstance(data["recommendations"], list)

    @pytest.mark.asyncio
    async def test_get_fault_zones_not_found(self, async_client: AsyncClient):
        """Teste com fault_id não encontrado."""
        fault_id = "nonexistent_fault_999"

        response = await async_client.get(f"/api/v1/fault-location/zones/{fault_id}")

        assert response.status_code == 404
        error_data = response.json()
        assert "not found" in error_data["detail"].lower()


class TestFaultLocationVisualization:
    """Testes para o endpoint /api/v1/fault-location/visualization/{fault_id}"""

    @pytest.mark.asyncio
    async def test_get_fault_visualization_success(self, async_client: AsyncClient):
        """Teste de obtenção de visualização de falta."""
        fault_id = "fault_test_001"

        response = await async_client.get(f"/api/v1/fault-location/visualization/{fault_id}")

        assert response.status_code == 200
        data = response.json()

        # Verificar estrutura da resposta
        assert "fault_id" in data
        assert "network_diagram" in data
        assert "fault_location_marker" in data
        assert "affected_equipment" in data
        assert "visualization_config" in data

        # Verificar dados de visualização
        assert isinstance(data["network_diagram"], dict)
        assert isinstance(data["fault_location_marker"], dict)
        assert isinstance(data["affected_equipment"], list)
        assert "coordinates" in data["fault_location_marker"]

    @pytest.mark.asyncio
    async def test_get_fault_visualization_with_format(self, async_client: AsyncClient):
        """Teste de visualização com formato específico."""
        fault_id = "fault_test_001"

        response = await async_client.get(
            f"/api/v1/fault-location/visualization/{fault_id}",
            params={"format": "svg", "include_measurements": True}
        )

        assert response.status_code == 200
        data = response.json()

        assert "format" in data
        assert data["format"] == "svg"
        assert "measurements_overlay" in data


class TestFaultLocationRealtime:
    """Testes para endpoints de tempo real de localização de faltas"""

    @pytest.mark.asyncio
    async def test_start_realtime_location(self, async_client: AsyncClient):
        """Teste de início de localização em tempo real."""
        config = {
            "monitoring_interval": 1.0,
            "location_algorithm": "impedance_based",
            "confidence_threshold": 0.8,
            "auto_analyze": True
        }

        response = await async_client.post(
            "/api/v1/fault-location/realtime-tracking/session/start",
            json=config
        )

        assert response.status_code == 200
        data = response.json()

        assert "session_id" in data
        assert "status" in data
        assert data["status"] == "started"
        assert "monitoring_config" in data

    @pytest.mark.asyncio
    async def test_get_realtime_status(self, async_client: AsyncClient):
        """Teste de obtenção de status em tempo real."""
        session_id = "test_session_001"

        response = await async_client.get(
            f"/api/v1/fault-location/realtime-tracking/session/{session_id}/status"
        )

        assert response.status_code == 200
        data = response.json()

        assert "session_id" in data
        assert "status" in data
        assert "active_monitoring" in data
        assert "recent_detections" in data
        assert isinstance(data["recent_detections"], list)

    @pytest.mark.asyncio
    async def test_stop_realtime_location(self, async_client: AsyncClient):
        """Teste de parada de localização em tempo real."""
        session_id = "test_session_001"

        response = await async_client.post(
            f"/api/v1/fault-location/realtime-tracking/session/{session_id}/stop"
        )

        assert response.status_code == 200
        data = response.json()

        assert "session_id" in data
        assert "status" in data
        assert data["status"] == "stopped"
        assert "session_summary" in data


class TestFaultLocationHistory:
    """Testes para histórico de localização de faltas"""

    @pytest.mark.asyncio
    async def test_get_fault_history(self, async_client: AsyncClient):
        """Teste de obtenção do histórico de faltas."""
        response = await async_client.get("/api/v1/fault-location/history")

        assert response.status_code == 200
        data = response.json()

        assert "total_faults" in data
        assert "faults" in data
        assert "summary_statistics" in data
        assert isinstance(data["faults"], list)

    @pytest.mark.asyncio
    async def test_get_fault_history_with_filters(self, async_client: AsyncClient):
        """Teste de histórico com filtros."""
        params = {
            "start_date": "2025-07-01",
            "end_date": "2025-07-15",
            "fault_type": "phase_to_ground",
            "min_confidence": 0.8
        }

        response = await async_client.get(
            "/api/v1/fault-location/history",
            params=params
        )

        assert response.status_code == 200
        data = response.json()

        # Verificar que os filtros foram aplicados
        for fault in data["faults"]:
            assert fault["fault_type"] == "phase_to_ground"
            assert fault["confidence_score"] >= 0.8

    @pytest.mark.asyncio
    async def test_get_fault_details(self, async_client: AsyncClient):
        """Teste de obtenção de detalhes de falta específica."""
        fault_id = "fault_test_001"

        response = await async_client.get(f"/api/v1/fault-location/history/{fault_id}")

        assert response.status_code == 200
        data = response.json()

        assert "fault_id" in data
        assert "analysis_details" in data
        assert "location_results" in data
        assert "sequence_of_events" in data
        assert "lessons_learned" in data


class TestFaultLocationPerformance:
    """Testes de performance dos endpoints de localização"""

    @pytest.mark.asyncio
    async def test_analyze_fault_performance(
        self,
        async_client: AsyncClient,
        sample_fault_location_request
    ):
        """Teste de performance da análise de falta."""
        import time

        start_time = time.time()

        response = await async_client.post(
            "/api/v1/fault-location/analyze",
            json=sample_fault_location_request
        )

        end_time = time.time()
        response_time = end_time - start_time

        assert response.status_code == 200
        assert response_time < 5.0  # Deve responder em menos de 5 segundos

    @pytest.mark.asyncio
    async def test_concurrent_fault_analysis(
        self,
        async_client: AsyncClient,
        sample_fault_location_request
    ):
        """Teste de análises concorrentes."""
        import asyncio

        # Criar múltiplas requisições concorrentes
        tasks = []
        for i in range(5):
            request_data = sample_fault_location_request.copy()
            request_data["sequence_of_events"][0]["location"] = f"line_test_{i}"

            task = async_client.post(
                "/api/v1/fault-location/analyze",
                json=request_data
            )
            tasks.append(task)

        # Executar todas as requisições concorrentemente
        responses = await asyncio.gather(*tasks)

        # Verificar que todas as requisições foram bem-sucedidas
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert "fault_id" in data
            assert "confidence_score" in data


class TestFaultLocationIntegration:
    """Testes de integração entre diferentes endpoints"""

    @pytest.mark.asyncio
    async def test_full_fault_analysis_workflow(
        self,
        async_client: AsyncClient,
        sample_fault_location_request
    ):
        """Teste do fluxo completo de análise de falta."""

        # 1. Analisar falta
        response = await async_client.post(
            "/api/v1/fault-location/analyze",
            json=sample_fault_location_request
        )
        assert response.status_code == 200
        analysis_data = response.json()
        fault_id = analysis_data["fault_id"]

        # 2. Obter zonas afetadas
        response = await async_client.get(f"/api/v1/fault-location/zones/{fault_id}")
        assert response.status_code == 200
        zones_data = response.json()

        # 3. Obter visualização
        response = await async_client.get(f"/api/v1/fault-location/visualization/{fault_id}")
        assert response.status_code == 200
        viz_data = response.json()

        # 4. Verificar consistência dos dados
        assert zones_data["fault_id"] == fault_id
        assert viz_data["fault_id"] == fault_id

        # 5. Verificar no histórico
        response = await async_client.get(f"/api/v1/fault-location/history/{fault_id}")
        assert response.status_code == 200
        history_data = response.json()
        assert history_data["fault_id"] == fault_id


# Testes de edge cases e robustez
class TestFaultLocationEdgeCases:
    """Testes para casos extremos e robustez"""

    @pytest.mark.asyncio
    async def test_malformed_json_request(self, async_client: AsyncClient):
        """Teste com JSON malformado."""
        malformed_data = '{"voltage_measurements": {"bus_1": {"magnitude": }}'

        response = await async_client.post(
            "/api/v1/fault-location/analyze",
            content=malformed_data,
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_extremely_large_request(
        self,
        async_client: AsyncClient,
        sample_fault_location_request
    ):
        """Teste com requisição muito grande."""
        large_request = sample_fault_location_request.copy()

        # Adicionar muitos eventos para testar limites
        large_events = []
        base_time = datetime.now()
        for i in range(1000):
            event = {
                "timestamp": (base_time + timedelta(milliseconds=i)).isoformat(),
                "event": f"test_event_{i}",
                "location": f"test_location_{i}",
                "data": f"test_data_{i}" * 100  # String longa
            }
            large_events.append(event)

        large_request["sequence_of_events"] = large_events

        response = await async_client.post(
            "/api/v1/fault-location/analyze",
            json=large_request,
            timeout=30.0
        )

        # Deve processar ou retornar erro apropriado
        # OK, Too Large, ou Unprocessable
        assert response.status_code in [200, 413, 422]

    @pytest.mark.asyncio
    async def test_special_characters_in_location(
        self,
        async_client: AsyncClient,
        sample_fault_location_request
    ):
        """Teste com caracteres especiais em localização."""
        request_data = sample_fault_location_request.copy()
        request_data["sequence_of_events"][0]["location"] = "line_测试_🔥_location"

        response = await async_client.post(
            "/api/v1/fault-location/analyze",
            json=request_data
        )

        assert response.status_code == 200
        data = response.json()
        assert "fault_id" in data
