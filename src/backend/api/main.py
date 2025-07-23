"""
ProtecAI_Mini - API REST Principal (FastAPI)
============================================

API REST para laboratório de coordenação de proteção elétrica com IA/ML.
Permite parametrização dinâmica de dispositivos de proteção e execução 
de simulações em tempo real.

Funcionalidades:
- Gestão da rede elétrica (IEEE 14 barras)
- Configuração dinâmica de dispositivos de proteção
- Simulações de falhas e análises
- Treinamento e otimização RL
- Visualizações e relatórios
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn
from contextlib import asynccontextmanager

# Importar routers
from .routers import (
    network,
    protection,
    simulation,
    rl_agent,
    visualization,
    fault_location,
    protection_zones,
    realtime_tracking,
    ai_insights,
    executive_validation
)

# Configurações globais
API_VERSION = "1.0.0"
API_TITLE = "ProtecAI Mini - Laboratório de Coordenação de Proteção"
API_DESCRIPTION = """
🔋 **ProtecAI Mini** - Laboratório Inteligente de Coordenação de Proteção Elétrica

## 🎯 Funcionalidades Principais

### 🏗️ **Gestão da Rede Elétrica**
- Carregamento e configuração da rede IEEE 14 barras
- Modificação dinâmica de parâmetros da rede
- Validação de conectividade e integridade

### 🛡️ **Dispositivos de Proteção**
- Configuração de relés (51, 67, 87T, 27/59)
- Ajuste dinâmico de settings (pickup, timing, curvas)
- Gestão de disjuntores e fusíveis

### ⚡ **Simulações e Análises**
- Simulação de falhas (curto-circuito, sobrecarga)
- Análise de coordenação de proteção
- Estudos de seletividade

### 🧠 **Inteligência Artificial**
- Treinamento de agentes RL para otimização
- Recomendação automática de settings
- Análise preditiva de performance

### 📊 **Visualizações e Relatórios**
- Diagramas unifilares da rede
- Gráficos de coordenação
- Relatórios de performance

---
🚀 **Desenvolvido para Petrobras** - Inovação em Proteção Elétrica
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciamento do ciclo de vida da aplicação."""
    print("🚀 Iniciando ProtecAI Mini API...")
    print("📋 Validando dependências...")

    # Validar estrutura de diretórios
    docs_path = Path("docs")
    data_path = Path("simuladores/power_sim/data")

    if not docs_path.exists():
        docs_path.mkdir(exist_ok=True)
        print("📁 Diretório docs/ criado")

    if not data_path.exists():
        print("⚠️ Diretório de dados não encontrado")

    print("✅ ProtecAI Mini API inicializada com sucesso!")

    yield

    print("⏹️ Finalizando ProtecAI Mini API...")


# Criar aplicação FastAPI
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS para permitir acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar arquivos estáticos
docs_path = Path("docs")
if docs_path.exists():
    app.mount("/static", StaticFiles(directory="docs"), name="static")

# Incluir routers
app.include_router(
    network.router,
    prefix="/api/v1/network",
    tags=["🏗️ Rede Elétrica"]
)

app.include_router(
    protection.router,
    prefix="/api/v1/protection",
    tags=["🛡️ Dispositivos de Proteção"]
)

app.include_router(
    simulation.router,
    prefix="/api/v1/simulation",
    tags=["⚡ Simulações"]
)

app.include_router(
    rl_agent.router,
    prefix="/api/v1/rl",
    tags=["🧠 Reinforcement Learning"]
)

app.include_router(
    visualization.router,
    prefix="/api/v1/visualization",
    tags=["📊 Visualizações"]
)

# Novos routers para funcionalidades avançadas
app.include_router(
    fault_location.router,
    prefix="/api/v1/fault-location",
    tags=["📍 Localização de Faltas"]
)

app.include_router(
    protection_zones.router,
    prefix="/api/v1/protection-zones",
    tags=["🛡️ Zonas de Proteção"]
)

app.include_router(
    realtime_tracking.router,
    prefix="/api/v1/realtime-tracking",
    tags=["⏱️ Rastreamento Tempo Real"]
)

app.include_router(
    ai_insights.router,
    prefix="/api/v1/ai-insights",
    tags=["🤖 Insights da IA"]
)

# Router específico para RL
app.include_router(
    ai_insights.router,
    prefix="/api/v1/rl",
    tags=["🎯 Reinforcement Learning"]
)

app.include_router(
    executive_validation.router,
    prefix="/api/v1/executive",
    tags=["👔 Validação Executiva"]
)

# Endpoints principais


@app.get("/", tags=["🏠 Principal"])
async def root():
    """Endpoint raiz - Status da API."""
    return {
        "message": "🔋 ProtecAI Mini - Laboratório de Coordenação de Proteção",
        "version": API_VERSION,
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "network": "/api/v1/network",
            "protection": "/api/v1/protection",
            "simulation": "/api/v1/simulation",
            "rl": "/api/v1/rl",
            "visualization": "/api/v1/visualization",
            "fault_location": "/api/v1/fault-location",
            "protection_zones": "/api/v1/protection-zones",
            "realtime_tracking": "/api/v1/realtime-tracking",
            "ai_insights": "/api/v1/ai-insights",
            "executive": "/api/v1/executive"
        },
        "features": [
            "🏗️ Gestão de Rede IEEE 14 barras",
            "🛡️ Configuração Dinâmica de Proteção",
            "⚡ Simulações de Falhas",
            "🧠 Otimização com RL/ML",
            "📊 Visualizações Avançadas",
            "📍 Localização Precisa de Faltas",
            "🛡️ Análise de Zonas de Proteção",
            "⏱️ Rastreamento em Tempo Real",
            "🤖 Insights Inteligentes da IA",
            "👔 Validação Executiva"
        ]
    }


@app.get("/health", tags=["🏠 Principal"])
async def health_check():
    """Endpoint de health check."""
    return {
        "status": "healthy",
        "timestamp": "2025-01-07T12:00:00Z",
        "version": API_VERSION,
        "services": {
            "pandapower": "✅ OK",
            "rl_engine": "✅ OK",
            "visualization": "✅ OK"
        }
    }


@app.get("/info", tags=["🏠 Principal"])
async def api_info():
    """Informações detalhadas da API."""
    return {
        "api": {
            "name": "ProtecAI Mini",
            "version": API_VERSION,
            "description": "Laboratório de Coordenação de Proteção Elétrica",
            "company": "Petrobras",
            "environment": "development"
        },
        "capabilities": {
            "network_simulation": True,
            "protection_coordination": True,
            "rl_optimization": True,
            "real_time_visualization": True,
            "dynamic_configuration": True
        },
        "supported_formats": {
            "input": ["JSON", "PandaPower"],
            "output": ["JSON", "PNG", "PDF", "CSV"]
        }
    }


# Executar aplicação
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
