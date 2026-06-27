# checker.py — verifica se há nova versão do agente disponível na central

import logging
import requests
from config import config

logger = logging.getLogger(__name__)


def verificar_update() -> dict | None:
    """
    Consulta a central se há uma versão mais recente disponível.
    Retorna dict com informações do update ou None se não houver.
    """
    try:
        resposta = requests.get(
            f"{config.central_url}/api/v1/update/check",
            headers={"Authorization": f"Bearer {config.token}"},
            timeout=10,
        )

        if resposta.status_code != 200:
            logger.warning(f"Erro ao verificar update: {resposta.status_code}")
            return None

        dados = resposta.json()

        if dados.get("update_available"):
            versao = dados.get("versao")
            logger.info(f"Update disponível: versão {versao}")

            # Inicia o processo de download e aplicação
            from updater.downloader import baixar_update
            from updater.applier import aplicar_update

            binario, assinatura = baixar_update(versao)
            if binario and assinatura:
                aplicar_update(binario, assinatura, versao)
            return dados

        else:
            logger.debug("Nenhum update disponível.")
            return None

    except Exception as e:
        logger.error(f"Erro ao verificar update: {e}")
        return None