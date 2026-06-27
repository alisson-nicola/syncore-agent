# downloader.py — baixa e valida o binário de update da central

import logging
import requests
from config import config

logger = logging.getLogger(__name__)


def baixar_update(versao: str) -> tuple[bytes, str] | tuple[None, None]:
    """
    Baixa o binário de update da central.
    Retorna tupla (conteudo_bytes, assinatura_base64) ou (None, None) em caso de falha.
    """
    try:
        logger.info(f"Baixando update versão {versao}...")

        resposta = requests.get(
            f"{config.central_url}/api/v1/update/download",
            headers={"Authorization": f"Bearer {config.token}"},
            timeout=120,
            stream=True,
        )

        if resposta.status_code != 200:
            logger.error(f"Erro ao baixar update: {resposta.status_code}")
            return None, None

        # Lê a assinatura RSA do header
        assinatura = resposta.headers.get("X-Assinatura-RSA")
        if not assinatura:
            logger.error("Assinatura RSA ausente no header da resposta.")
            return None, None

        # Lê o conteúdo do binário
        conteudo = b""
        for chunk in resposta.iter_content(chunk_size=8192):
            conteudo += chunk

        if not conteudo:
            logger.error("Binário baixado está vazio.")
            return None, None

        logger.info(f"Binário baixado: {len(conteudo)} bytes.")
        return conteudo, assinatura

    except requests.exceptions.ConnectionError:
        logger.error("Sem conexão com a central ao tentar baixar update.")
        return None, None

    except requests.exceptions.Timeout:
        logger.error("Timeout ao baixar update.")
        return None, None

    except Exception as e:
        logger.error(f"Erro inesperado ao baixar update: {e}")
        return None, None


def validar_assinatura(conteudo: bytes, assinatura_b64: str) -> bool:
    """
    Valida a assinatura RSA do binário usando a chave pública embutida.
    Retorna True se válida, False caso contrário.
    """
    import base64
    import os
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.exceptions import InvalidSignature

    try:
        # Carrega a chave pública do repositório do agente
        chave_path = os.path.join(os.path.dirname(__file__), "..", "keys", "public.pem")
        with open(chave_path, "rb") as f:
            chave_publica = serialization.load_pem_public_key(f.read())

        assinatura = base64.b64decode(assinatura_b64)

        chave_publica.verify(
            assinatura,
            conteudo,
            padding.PKCS1v15(),
            hashes.SHA256(),
        )

        logger.info("Assinatura RSA válida.")
        return True

    except InvalidSignature:
        logger.error("Assinatura RSA inválida — update rejeitado.")
        return False

    except Exception as e:
        logger.error(f"Erro ao validar assinatura: {e}")
        return False