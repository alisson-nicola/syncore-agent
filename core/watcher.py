# watcher.py — monitora pasta de backup aguardando novos arquivos

import os
import time
import logging
from config import config

logger = logging.getLogger(__name__)

# Arquivos já processados nesta sessão (evita reenvio)
_processados: set = set()


def listar_arquivos_novos() -> list:
    """
    Lista arquivos ZIP na pasta monitorada que ainda não foram processados.
    Aguarda o arquivo estar estável (tamanho não muda por 2s) antes de retornar.
    """
    pasta = config.watch_folder

    if not os.path.exists(pasta):
        logger.warning(f"Pasta monitorada não existe: {pasta}")
        return []

    novos = []
    for nome in os.listdir(pasta):
        if not nome.lower().endswith(".zip"):
            continue

        caminho = os.path.join(pasta, nome)

        if caminho in _processados:
            continue

        # Verifica se o arquivo está estável (não está sendo gravado)
        if _arquivo_estavel(caminho):
            novos.append(caminho)

    return novos


def marcar_processado(caminho: str):
    """Marca um arquivo como já processado para evitar reenvio."""
    _processados.add(caminho)
    logger.debug(f"Arquivo marcado como processado: {caminho}")


def _arquivo_estavel(caminho: str, espera: float = 2.0) -> bool:
    """
    Verifica se o arquivo está estável verificando se o tamanho
    não mudou após um intervalo de espera.
    """
    try:
        tamanho_antes = os.path.getsize(caminho)
        time.sleep(espera)
        tamanho_depois = os.path.getsize(caminho)
        return tamanho_antes == tamanho_depois
    except Exception:
        return False