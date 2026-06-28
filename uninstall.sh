#!/bin/bash
# uninstall.sh — desinstalação do agente Syncore no Linux

set -e

INSTALL_DIR="/opt/syncore-agent"
CONFIG_DIR="/etc/syncore-agent"
SERVICE_NAME="syncore-agent"

echo "==================================================="
echo " Syncore Agent — Desinstalador Linux"
echo "==================================================="

if [ "$EUID" -ne 0 ]; then
    echo "Execute como root: sudo ./uninstall.sh"
    exit 1
fi

echo "[1/4] Parando serviço..."
systemctl stop "$SERVICE_NAME" 2>/dev/null || true

echo "[2/4] Desabilitando serviço..."
systemctl disable "$SERVICE_NAME" 2>/dev/null || true

echo "[3/4] Removendo arquivos do serviço..."
rm -f "/etc/systemd/system/$SERVICE_NAME.service"
systemctl daemon-reload

echo "[4/4] Removendo binário..."
rm -rf "$INSTALL_DIR"

echo ""
read -p "Remover configurações em $CONFIG_DIR? (s/N): " resposta
if [ "$resposta" = "s" ] || [ "$resposta" = "S" ]; then
    rm -rf "$CONFIG_DIR"
    echo "Configurações removidas."
else
    echo "Configurações mantidas em $CONFIG_DIR."
fi

echo ""
echo "Syncore Agent desinstalado com sucesso."
