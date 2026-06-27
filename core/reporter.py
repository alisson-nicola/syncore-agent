# reporter.py — reporta status de backup para a central

import logging
import requests
from config import config

logger = logging.getLogger(__name__)


def reportar_status(nome_arquivo: str, status: str, mensagem_erro: str = None) -> bool:
    """
    Reporta o status de um backup para a central sem enviar arquivo.
    Usado quando o backup falhou antes de gerar o arquivo.
    """
    try:
        dados = {
            "nome_arquivo": nome_arquivo,
            "status": status,
        }
        if mensagem_erro:
            dados["mensagem_erro"] = mensagem_erro

        resposta = requests.post(
            f"{config.central_url}/api/v1/backup/status",
            headers={"Authorization": f"Bearer {config.token}"},
            data=dados,
            timeout=30,
        )

        if resposta.status_code == 200:
            logger.info(f"Status reportado: {nome_arquivo} — {status}")
            return True
        else:
            logger.error(f"Erro ao reportar status: {resposta.status_code}")
            return False

    except Exception as e:
        logger.error(f"Falha ao reportar status para a central: {e}")
        return False


def enviar_heartbeat() -> bool:
    """
    Envia heartbeat para a central informando que o agente está online.
    Atualiza o campo ultimo_contato no banco da central.
    """
    try:
        resposta = requests.get(
            f"{config.central_url}/api/v1/agent/ping",
            headers={"Authorization": f"Bearer {config.token}"},
            timeout=10,
        )

        if resposta.status_code == 200:
            logger.debug("Heartbeat enviado com sucesso.")
            return True
        else:
            logger.warning(f"Heartbeat retornou status inesperado: {resposta.status_code}")
            return False

    except Exception as e:
        logger.warning(f"Falha ao enviar heartbeat: {e}")
        return False