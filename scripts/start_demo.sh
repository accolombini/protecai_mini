#!/bin/bash

# 🛢️ ProtecAI Mini - Script de Inicialização Rápida
# Para demonstração ao cliente

echo "🛢️  ProtecAI Mini - Sistema de Coordenação de Proteção"
echo "============================================="
echo ""

# Verificar se está no diretório correto
if [ ! -f "start_api.py" ]; then
    echo "❌ Erro: Execute este script no diretório raiz do projeto"
    echo "   Navegue até: protecai_mini/"
    exit 1
fi

echo "📋 Verificando pré-requisitos..."

# Verificar Python
if ! command -v python &> /dev/null; then
    echo "❌ Python não encontrado. Instale Python 3.8+"
    exit 1
fi

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Instale Node.js 16+"
    exit 1
fi

echo "✅ Pré-requisitos OK"
echo ""

# Instalar dependências Python (se necessário)
echo "📦 Verificando dependências Python..."
if [ ! -d "venv" ]; then
    echo "⚙️  Criando ambiente virtual..."
    python -m venv venv
fi

source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Dependências Python OK"
echo ""

# Iniciar Backend
echo "🚀 Iniciando Backend API..."
echo "   URL: http://localhost:8000"
python start_api.py &
BACKEND_PID=$!

# Aguardar backend inicializar
sleep 5

# Verificar se backend está rodando
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend API iniciado com sucesso"
else
    echo "❌ Erro ao iniciar Backend API"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""

# Iniciar Frontend
echo "🚀 Iniciando Frontend React..."
echo "   URL: http://localhost:5173"
cd src/frontend/petro-protecai-frontend

# Instalar dependências Node (se necessário)
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências Node.js..."
    npm install > /dev/null 2>&1
fi

# Iniciar servidor de desenvolvimento
npm run dev &
FRONTEND_PID=$!

echo ""
echo "🎉 Sistema iniciado com sucesso!"
echo ""
echo "📊 URLs de Acesso:"
echo "   🖥️  Frontend: http://localhost:5173"
echo "   🔧 Backend:  http://localhost:8000"
echo "   📋 Health:   http://localhost:8000/health"
echo ""
echo "🎯 Para demonstração ao cliente:"
echo "   1. Abrir: http://localhost:5173"
echo "   2. Seguir: TUTORIAL.md"
echo ""
echo "⏹️  Para parar o sistema: Ctrl+C"
echo ""

# Aguardar interrupção
trap 'echo ""; echo "⏹️ Parando sistema..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT

# Aguardar indefinidamente
wait
