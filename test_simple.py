#!/usr/bin/env python3
"""
Teste simples para verificar se a estrutura básica funciona
"""

import asyncio
import json
from httpx import AsyncClient
from src.backend.api.main import app


async def test_basic():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Teste simples de análise de falta
        sample_request = {
            "voltage_measurements": {"bus_6": {"magnitude": 0.85, "angle": -15.2}},
            "current_measurements": {"line_6_13": {"magnitude": 2.35, "angle": 45.2}},
            "sequence_of_events": [{
                "timestamp": "2024-01-15T10:30:00",
                "event": "fault_detected",
                "location": "line_6_13"
            }],
            "protection_settings": {"relay_6": {"pickup": 1.2, "time_dial": 0.5, "curve": "very_inverse"}},
            "fault_type": "phase_to_ground",
            "network_configuration": "normal"
        }

        print("🔍 Testando análise de falta...")
        response = await client.post("/api/v1/fault-location/analyze", json=sample_request)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            fault_analysis = response.json()
            print(f"✅ Fault ID: {fault_analysis['fault_id']}")
            print(f"✅ Confidence: {fault_analysis['confidence_score']}")
            print(
                f"✅ Affected zones: {len(fault_analysis.get('affected_zones', []))}")
            return True
        else:
            print(f"❌ Erro: {response.text}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_basic())
    if success:
        print("🎉 Teste básico passou!")
    else:
        print("💥 Teste básico falhou!")
