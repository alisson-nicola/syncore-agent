#!/bin/bash
# build.sh — gera o binário do agente Syncore para Linux

set -e

echo "==================================================="
echo " Syncore Agent — Build Linux"
echo "==================================================="

# Verifica dependências
if ! command -v pyinstaller &> /dev/null; then
    echo "Instalando PyInstaller..."
    pip install pyinstaller --break-system-packages
fi

echo "[1/3] Limpando build anterior..."
rm -rf build/ dist/

echo "[2/3] Gerando binário..."
pyinstaller build.spec

echo "[3/3] Binário gerado em: dist/syncore-agent"
echo ""
echo "Para instalar:"
echo "  cp dist/syncore-agent ."
echo "  sudo ./install.sh"
