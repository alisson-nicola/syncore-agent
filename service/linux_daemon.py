# linux_daemon.py — integração com systemd no Linux

import logging
import subprocess
import os

logger = logging.getLogger(__name__)

SERVICE_NAME = "syncore-agent"
SERVICE_PATH = f"/etc/systemd/system/{SERVICE_NAME}.service"
BINARY_PATH = "/opt/syncore-agent/syncore-agent"
CONFIG_PATH = "/etc/syncore-agent/agent.conf"


def gerar_unit_file() -> str:
    """Gera o conteúdo do arquivo de unit do systemd."""
    return f"""[Unit]
Description=Syncore Backup Agent
After=network.target

[Service]
Type=simple
ExecStart={BINARY_PATH}
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""


def instalar_servico():
    """Instala e habilita o serviço no systemd."""
    try:
        with open(SERVICE_PATH, "w") as f:
            f.write(gerar_unit_file())

        subprocess.run(["systemctl", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "enable", SERVICE_NAME], check=True)
        subprocess.run(["systemctl", "start", SERVICE_NAME], check=True)
        logger.info("Serviço instalado e iniciado com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao instalar serviço: {e}")


def status_servico() -> str:
    """Retorna o status atual do serviço."""
    try:
        resultado = subprocess.run(
            ["systemctl", "is-active", SERVICE_NAME],
            capture_output=True, text=True,
        )
        return resultado.stdout.strip()
    except Exception:
        return "unknown"