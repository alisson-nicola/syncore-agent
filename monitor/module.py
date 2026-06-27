# module.py — interface MonitorModule reservada para a Fase 2
# Esta estrutura está preparada mas sem implementação ativa.

import logging

logger = logging.getLogger(__name__)


class MonitorModule:
    """
    Interface de monitoramento — Fase 2.
    Quando ativado, coletará métricas (CPU, memória, disco, processos)
    e enviará para a central via POST /api/v1/metrics.
    """

    def __init__(self):
        self.ativo = False

    def iniciar(self):
        """Inicia a coleta de métricas. Não implementado nesta versão."""
        logger.info("MonitorModule: não implementado nesta versão (Fase 2).")

    def parar(self):
        """Para a coleta de métricas."""
        pass

    def coletar(self) -> dict:
        """Coleta métricas do sistema. Não implementado nesta versão."""
        return {}

    def enviar(self) -> bool:
        """Envia métricas para a central. Não implementado nesta versão."""
        return False