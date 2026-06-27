# config.py — leitura da configuração do agente a partir do agent.conf

import configparser
import os

# Caminho do arquivo de configuração
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "agent.conf")


class AgentConfig:
    def __init__(self):
        self._config = configparser.ConfigParser()
        self._config.read(CONFIG_PATH)

    # --- Central ---
    @property
    def central_url(self) -> str:
        return self._config.get("central", "url", fallback="http://localhost:8000")

    @property
    def token(self) -> str:
        return self._config.get("central", "token", fallback="")

    # --- Backup ---
    @property
    def watch_folder(self) -> str:
        return self._config.get("backup", "watch_folder", fallback="")

    @property
    def schedule(self) -> list:
        raw = self._config.get("backup", "schedule", fallback="06:00")
        return [s.strip() for s in raw.split(",")]

    @property
    def retention_days(self) -> int:
        return self._config.getint("backup", "retention_days", fallback=7)

    # --- Agente ---
    @property
    def name(self) -> str:
        return self._config.get("agent", "name", fallback="syncore-agent")

    @property
    def platform(self) -> str:
        return self._config.get("agent", "platform", fallback="linux")

    @property
    def version(self) -> str:
        return self._config.get("agent", "version", fallback="1.0.0")

    def validar(self) -> list:
        """Valida as configurações obrigatórias. Retorna lista de erros."""
        erros = []
        if not self.central_url:
            erros.append("central.url não configurado.")
        if not self.token or self.token == "COLE_O_TOKEN_AQUI":
            erros.append("central.token não configurado.")
        if not self.watch_folder:
            erros.append("backup.watch_folder não configurado.")
        if not self.name:
            erros.append("agent.name não configurado.")
        return erros


# Instância global
config = AgentConfig()