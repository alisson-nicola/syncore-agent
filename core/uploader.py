# uploader.py — compressão, criptografia e envio do backup para a central

import hashlib
import logging
import os
import time
import requests
from crypto.encryptor import criptografar
from config import config

logger = logging.getLogger(__name__)


def calcular_hash(conteudo: bytes) -> str:
    """Calcula o hash SHA-256 do conteúdo."""
    return hashlib.sha256(conteudo).hexdigest()


def enviar_backup(caminho_arquivo: str) -> bool:
    """
    Lê, criptografa e envia um arquivo de backup para a central.
    Retorna True se enviado com sucesso, False caso contrário.
    """
    if not os.path.exists(caminho_arquivo):
        logger.error(f"Arquivo não encontrado: {caminho_arquivo}")
        return False

    nome_arquivo = os.path.basename(caminho_arquivo)

    try:
        # Lê o conteúdo original
        with open(caminho_arquivo, "rb") as f:
            conteudo = f.read()

        # Calcula hash antes de criptografar
        hash_original = calcular_hash(conteudo)

        # Criptografa com o token
        conteudo_enc = criptografar(conteudo, config.token)

        logger.info(f"Enviando backup: {nome_arquivo} ({len(conteudo)} bytes)")

        # Envia para a central
        resposta = requests.post(
            f"{config.central_url}/api/v1/backup/upload",
            headers={"Authorization": f"Bearer {config.token}"},
            files={"arquivo": (nome_arquivo, conteudo_enc, "application/octet-stream")},
            data={
                "hash_original": hash_original,
                "nome_arquivo": nome_arquivo,
                "token_plain": config.token,
            },
            timeout=120,
        )

        if resposta.status_code == 200:
            logger.info(f"Backup enviado com sucesso: {nome_arquivo}")
            return True
        else:
            logger.error(f"Erro ao enviar backup: {resposta.status_code} — {resposta.text}")
            return False

    except requests.exceptions.ConnectionError:
        logger.error(f"Sem conexão com a central. Backup será reenviado depois: {nome_arquivo}")
        return False

    except requests.exceptions.Timeout:
        logger.error(f"Timeout ao enviar backup: {nome_arquivo}")
        return False

    except Exception as e:
        logger.error(f"Erro inesperado ao enviar backup: {e}")
        return False


def enviar_com_retry(caminho_arquivo: str, tentativas: int = 5) -> bool:
    """
    Tenta enviar o backup com backoff exponencial.
    Útil quando a central está temporariamente indisponível.
    """
    for tentativa in range(1, tentativas + 1):
        logger.info(f"Tentativa {tentativa}/{tentativas}: {os.path.basename(caminho_arquivo)}")
        if enviar_backup(caminho_arquivo):
            return True

        if tentativa < tentativas:
            espera = 2 ** tentativa  # 2, 4, 8, 16 segundos
            logger.info(f"Aguardando {espera}s antes da próxima tentativa...")
            time.sleep(espera)

    logger.error(f"Todas as tentativas falharam: {os.path.basename(caminho_arquivo)}")
    return False