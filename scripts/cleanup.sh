#!/bin/bash
# ProtecAI Mini - Script de Limpeza e Organização
# Mantém a estrutura do projeto limpa e organizada

echo "🧹 Iniciando limpeza do ambiente ProtecAI Mini..."

# Remover arquivos temporários desnecessários
echo "🗑️ Removendo arquivos temporários..."
find . -name "*.pyc" -delete 2>/dev/null
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.tmp" -delete 2>/dev/null
find . -name ".DS_Store" -delete 2>/dev/null

# Limpar logs antigos (manter apenas os últimos 5)
if [ -d "logs" ]; then
    echo "📋 Limpando logs antigos..."
    cd logs && ls -t *.log 2>/dev/null | tail -n +6 | xargs rm -f
    cd ..
fi

# Limpar relatórios de coverage antigos
if [ -d "htmlcov" ] && [ -z "$(ls -A htmlcov)" ]; then
    echo "📊 Removendo diretório htmlcov vazio..."
    rm -rf htmlcov
fi

# Verificar estrutura de diretórios essenciais
echo "📁 Verificando estrutura de diretórios..."
mkdir -p src/backend/core
mkdir -p src/frontend
mkdir -p tests
mkdir -p docs
mkdir -p scripts
mkdir -p reports
mkdir -p temp

echo "✅ Limpeza concluída!"
echo "📊 Estrutura do projeto organizada e limpa"
