# windows_service.py — integração com Windows Service via pywin32

import logging
import sys
import os

logger = logging.getLogger(__name__)

SERVICE_NAME = "SyncoreAgent"
SERVICE_DISPLAY_NAME = "Syncore Backup Agent"
SERVICE_DESCRIPTION = "Agente de backup centralizado Syncore."


def iniciar_windows_service():
    """
    Registra e inicia o agente como Windows Service.
    Requer pywin32 instalado e execução como administrador.
    """
    try:
        import win32serviceutil
        import win32service
        import win32event
        import servicemanager

        class SyncoreAgentService(win32serviceutil.ServiceFramework):
            _svc_name_ = SERVICE_NAME
            _svc_display_name_ = SERVICE_DISPLAY_NAME
            _svc_description_ = SERVICE_DESCRIPTION

            def __init__(self, args):
                win32serviceutil.ServiceFramework.__init__(self, args)
                self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
                self._running = True

            def SvcStop(self):
                self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
                win32event.SetEvent(self.hWaitStop)
                self._running = False

                from core.scheduler import parar
                parar()

            def SvcDoRun(self):
                servicemanager.LogMsg(
                    servicemanager.EVENTLOG_INFORMATION_TYPE,
                    servicemanager.PYS_SERVICE_STARTED,
                    (self._svc_name_, ""),
                )
                self._main()

            def _main(self):
                import time
                from core.scheduler import iniciar
                from core.reporter import enviar_heartbeat
                from monitor.module import MonitorModule

                enviar_heartbeat()
                monitor = MonitorModule()
                monitor.iniciar()
                iniciar()

                while self._running:
                    time.sleep(60)

        if len(sys.argv) == 1:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(SyncoreAgentService)
            servicemanager.StartServiceCtrlDispatcher()
        else:
            win32serviceutil.HandleCommandLine(SyncoreAgentService)

    except ImportError:
        logger.error("pywin32 não instalado. Windows Service não disponível.")
    except Exception as e:
        logger.error(f"Erro ao iniciar Windows Service: {e}")