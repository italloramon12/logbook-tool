# Activity Tracker — Protótipo (Ubuntu)

> Protótipo de uma solução local para monitorar atividades em máquinas Ubuntu: janelas ativas, tempo ocioso, comandos do terminal e navegação web (via extensão). **Uso somente com consentimento do usuário.**

## Componentes
- `agent/agent.py` — daemon que detecta janelas ativas e idle (usa `xdotool`, `xprintidle`).
- `agent/db.py` — SQLite persistence.
- `agent/api.py` — Flask API para visualizar e exportar logbook (porta 5001).
- `agent/static/index.html` — front-end simples.
- `browser-extension/` — extensão para capturar abas/URLs e tempo em abas.
- `shell-hook/log_command.sh` — snippet para registrar comandos do shell (~/.bashrc ou ~/.zshrc).
- `agent/systemd/activity-tracker.service` — unit systemd para rodar o agente.

## Pré-requisitos (Ubuntu)
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip xdotool xprintidle wmctrl
