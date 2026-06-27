# main.py — entrypoint do agente Syncore

import logging
import signal
import sys
import time
from logging.handlers import RotatingFileHandler

from config import config
from core.scheduler import iniciar, parar
from core.reporter import enviar_heartbeat
from monitor.module import MonitorModule


# --- Configuração de logging ---
def configurar_logging():
    """Configura logging com rotação de arquivo."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Handler de arquivo com rotação
    handler_arquivo = RotatingFileHandler(
        "syncore-agent.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding="utf-8",
    )
    handler_arquivo.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    ))

    # Handler de console
    handler_console = logging.StreamHandler()
    handler_console.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    ))

    logger.addHandler(handler_arquivo)
    logger.addHandler(handler_console)


logger = logging.getLogger(__name__)


# --- Encerramento gracioso ---
def sinal_encerramento(sig, frame):
    logger.info("Sinal de encerramento recebido. Parando agente...")
    parar()
    sys.exit(0)


def main():
    configurar_logging()

    logger.info("=" * 50)
    logger.info(f"Syncore Agent v{config.version} iniciando...")
    logger.info(f"Agente: {config.name}")
    logger.info(f"Plataforma: {config.platform}")
    logger.info(f"Central: {config.central_url}")
    logger.info("=" * 50)

    # Valida configurações obrigatórias
    erros = config.validar()
    if erros:
        for erro in erros:
            logger.error(f"Configuração inválida: {erro}")
        logger.error("Corrija o arquivo agent.conf e reinicie o agente.")
        sys.exit(1)

    # Registra sinais de encerramento
    signal.signal(signal.SIGINT, sinal_encerramento)
    signal.signal(signal.SIGTERM, sinal_encerramento)

    # Envia heartbeat inicial
    logger.info("Enviando heartbeat inicial...")
    enviar_heartbeat()

    # Inicia monitor (Fase 2 — sem implementação ativa)
    monitor = MonitorModule()
    monitor.iniciar()

    # Inicia agendador
    iniciar()

    logger.info("Agente em execução. Aguardando eventos...")

    # Loop principal
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        sinal_encerramento(None, None)


if __name__ == "__main__":
    main()