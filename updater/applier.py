# applier.py — aplica o update do agente com rollback automático

import os
import sys
import time
import shutil
import logging
import subprocess
from updater.downloader import validar_assinatura
from config import config

logger = logging.getLogger(__name__)

# Caminho do binário atual em execução
BINARIO_ATUAL = os.path.abspath(sys.argv[0])
BINARIO_BACKUP = BINARIO_ATUAL + ".backup"


def aplicar_update(conteudo: bytes, assinatura_b64: str, versao: str) -> bool:
    """
    Valida a assinatura, substitui o binário e reinicia o serviço.
    Em caso de falha, restaura o binário anterior automaticamente.
    """
    logger.info(f"Iniciando aplicação do update versão {versao}...")

    # Valida assinatura RSA antes de qualquer coisa
    if not validar_assinatura(conteudo, assinatura_b64):
        logger.error("Update rejeitado — assinatura inválida.")
        return False

    try:
        # Faz backup do binário atual
        if os.path.exists(BINARIO_ATUAL):
            shutil.copy2(BINARIO_ATUAL, BINARIO_BACKUP)
            logger.info(f"Backup do binário atual salvo em: {BINARIO_BACKUP}")

        # Escreve o novo binário
        with open(BINARIO_ATUAL, "wb") as f:
            f.write(conteudo)

        # Torna executável em Linux
        if config.platform == "linux":
            os.chmod(BINARIO_ATUAL, 0o755)

        logger.info("Novo binário gravado. Reiniciando serviço...")

        # Reinicia o serviço
        _reiniciar_servico()

        # Aguarda 30 segundos e verifica se o serviço subiu
        time.sleep(30)

        if _servico_rodando():
            logger.info(f"Update versão {versao} aplicado com sucesso.")
            # Remove backup após sucesso
            if os.path.exists(BINARIO_BACKUP):
                os.remove(BINARIO_BACKUP)
            return True
        else:
            logger.error("Serviço não subiu após update. Iniciando rollback...")
            _rollback()
            return False

    except Exception as e:
        logger.error(f"Erro ao aplicar update: {e}. Iniciando rollback...")
        _rollback()
        return False


def _rollback():
    """Restaura o binário anterior e reinicia o serviço."""
    try:
        if os.path.exists(BINARIO_BACKUP):
            shutil.copy2(BINARIO_BACKUP, BINARIO_ATUAL)
            if config.platform == "linux":
                os.chmod(BINARIO_ATUAL, 0o755)
            os.remove(BINARIO_BACKUP)
            logger.info("Rollback concluído — binário anterior restaurado.")
            _reiniciar_servico()
        else:
            logger.error("Arquivo de backup não encontrado — rollback impossível.")
    except Exception as e:
        logger.error(f"Erro durante rollback: {e}")


def _reiniciar_servico():
    """Reinicia o serviço do agente conforme a plataforma."""
    try:
        if config.platform == "windows":
            subprocess.Popen(
                ["sc", "stop", "SyncoreAgent"],
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            time.sleep(3)
            subprocess.Popen(
                ["sc", "start", "SyncoreAgent"],
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        else:
            subprocess.Popen(["systemctl", "restart", "syncore-agent"])
    except Exception as e:
        logger.error(f"Erro ao reiniciar serviço: {e}")


def _servico_rodando() -> bool:
    """Verifica se o serviço está rodando após o update."""
    try:
        if config.platform == "windows":
            resultado = subprocess.run(
                ["sc", "query", "SyncoreAgent"],
                capture_output=True, text=True, shell=True,
            )
            return "RUNNING" in resultado.stdout
        else:
            resultado = subprocess.run(
                ["systemctl", "is-active", "syncore-agent"],
                capture_output=True, text=True,
            )
            return resultado.stdout.strip() == "active"
    except Exception:
        return False