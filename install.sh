#!/bin/bash
# install.sh — instalação do agente Syncore no Linux

set -e

INSTALL_DIR="/opt/syncore-agent"
CONFIG_DIR="/etc/syncore-agent"
SERVICE_NAME="syncore-agent"
BINARY_NAME="syncore-agent"

echo "==================================================="
echo " Syncore Agent — Instalador Linux"
echo "==================================================="

# Verifica se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "Execute como root: sudo ./install.sh"
    exit 1
fi

# Verifica se o binário existe no diretório atual
if [ ! -f "./$BINARY_NAME" ]; then
    echo "Erro: binário '$BINARY_NAME' não encontrado no diretório atual."
    echo "Gere o binário com PyInstaller antes de instalar."
    exit 1
fi

echo "[1/5] Criando diretórios..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"

echo "[2/5] Copiando binário..."
cp "./$BINARY_NAME" "$INSTALL_DIR/$BINARY_NAME"
chmod 755 "$INSTALL_DIR/$BINARY_NAME"

echo "[3/5] Criando configuração padrão..."
if [ ! -f "$CONFIG_DIR/agent.conf" ]; then
    cat > "$CONFIG_DIR/agent.conf" << 'CONF'
[central]
url = https://central.suaempresa.com
token = COLE_O_TOKEN_AQUI

[backup]
watch_folder = /var/backups/erp
schedule = 06:00, 18:00
retention_days = 7

[agent]
name = NOME_DO_SERVIDOR
platform = linux
version = 1.0.0
CONF
    echo "Configuração criada em: $CONFIG_DIR/agent.conf"
    echo "IMPORTANTE: edite o arquivo antes de iniciar o serviço."
else
    echo "Configuração já existe em $CONFIG_DIR/agent.conf — mantida."
fi

echo "[4/5] Criando serviço systemd..."
cat > "/etc/systemd/system/$SERVICE_NAME.service" << UNIT
[Unit]
Description=Syncore Backup Agent
After=network.target

[Service]
Type=simple
ExecStart=$INSTALL_DIR/$BINARY_NAME
WorkingDirectory=$INSTALL_DIR
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
UNIT

echo "[5/5] Habilitando serviço..."
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"

echo ""
echo "==================================================="
echo " Instalação concluída!"
echo "==================================================="
echo ""
echo "Próximos passos:"
echo "  1. Edite a configuração: nano $CONFIG_DIR/agent.conf"
echo "  2. Inicie o serviço:     systemctl start $SERVICE_NAME"
echo "  3. Verifique o status:   systemctl status $SERVICE_NAME"
echo "  4. Veja os logs:         journalctl -u $SERVICE_NAME -f"
echo ""
