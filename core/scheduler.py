# scheduler.py — agendamento de tarefas periódicas do agente

import logging
import schedule
import time
import threading
from config import config

logger = logging.getLogger(__name__)

_rodando = False
_thread: threading.Thread = None


def _executar_backup_agendado():
    """Callback executado nos horários configurados no agent.conf."""
    from core.watcher import listar_arquivos_novos, marcar_processado
    from core.uploader import enviar_com_retry
    from core.reporter import reportar_status

    logger.info("Iniciando ciclo de backup agendado.")
    arquivos = listar_arquivos_novos()

    if not arquivos:
        logger.info("Nenhum arquivo novo encontrado.")
        return

    for caminho in arquivos:
        logger.info(f"Processando: {caminho}")
        sucesso = enviar_com_retry(caminho)
        marcar_processado(caminho)

        if not sucesso:
            import os
            reportar_status(
                nome_arquivo=os.path.basename(caminho),
                status="failed",
                mensagem_erro="Todas as tentativas de envio falharam.",
            )


def _executar_heartbeat():
    """Envia heartbeat para a central a cada 5 minutos."""
    from core.reporter import enviar_heartbeat
    enviar_heartbeat()


def _executar_verificacao_update():
    """Verifica se há update disponível a cada hora."""
    from updater.checker import verificar_update
    verificar_update()


def _loop():
    """Loop principal do agendador."""
    while _rodando:
        schedule.run_pending()
        time.sleep(10)


def iniciar():
    """Configura e inicia o agendador em uma thread separada."""
    global _rodando, _thread

    # Agenda backups nos horários configurados
    for horario in config.schedule:
        schedule.every().day.at(horario).do(_executar_backup_agendado)
        logger.info(f"Backup agendado para: {horario}")

    # Heartbeat a cada 5 minutos
    schedule.every(5).minutes.do(_executar_heartbeat)

    # Verificação de update a cada hora
    schedule.every().hour.do(_executar_verificacao_update)

    _rodando = True
    _thread = threading.Thread(target=_loop, daemon=True)
    _thread.start()
    logger.info("Agendador iniciado.")


def parar():
    """Para o agendador."""
    global _rodando
    _rodando = False
    schedule.clear()
    logger.info("Agendador parado.")