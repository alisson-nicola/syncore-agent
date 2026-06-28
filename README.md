# Syncore Agent

Agente de backup do sistema Syncore. Roda como serviço de sistema (Windows Service / systemd Linux), monitora uma pasta configurada e envia backups criptografados para a central.

---

## Requisitos

- Python 3.11+ (apenas para desenvolvimento)
- Linux ou Windows
- Acesso à central Syncore

---

## Instalação em produção

### Linux

1. Baixe o binário gerado pelo PyInstaller
2. Execute o instalador:

```bash
sudo ./install.sh
```

3. Edite a configuração:

```bash
sudo nano /etc/syncore-agent/agent.conf
```

4. Inicie o serviço:

```bash
sudo systemctl start syncore-agent
sudo systemctl status syncore-agent
```

---

## Configuração (agent.conf)

```ini
[central]
url = https://central.suaempresa.com
token = TOKEN_GERADO_NO_DASHBOARD

[backup]
watch_folder = /var/backups/erp
schedule = 06:00, 18:00
retention_days = 7

[agent]
name = ERP-Filial-01
platform = linux
version = 1.0.0
```

| Campo | Descrição |
|---|---|
| `url` | URL da central Syncore |
| `token` | Token gerado no dashboard ao cadastrar o agente |
| `watch_folder` | Pasta monitorada para arquivos de backup (.zip) |
| `schedule` | Horários de envio (HH:MM, separados por vírgula) |
| `retention_days` | Dias de retenção local |
| `name` | Nome do agente (deve coincidir com o cadastro na central) |
| `platform` | `windows` ou `linux` |
| `version` | Versão atual do agente |

---

## Build

### Linux

```bash
./build.sh
```

O binário será gerado em `dist/syncore-agent`.

---

## Logs

**Linux:**
```bash
journalctl -u syncore-agent -f
```

**Direto:**
```bash
tail -f syncore-agent.log
```

---

## Desinstalação

```bash
sudo ./uninstall.sh
```

---

## Segurança

- O token é armazenado localmente no `agent.conf` — proteja o acesso ao arquivo
- O payload é criptografado com Fernet antes do envio
- Updates são validados com assinatura RSA antes de serem aplicados
- Rollback automático em caso de falha no update
