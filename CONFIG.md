# Configuração do Activity Tracker

# Este arquivo contém opções de configuração avançadas
# Copie e edite conforme necessário

# ======================
# Monitoramento de Janelas
# ======================

# Intervalo de polling (segundos)
POLL_SEC=5

# Tempo para considerar ocioso (segundos)
IDLE_THRESHOLD=60

# ======================
# Monitoramento de Teclado
# ======================

# Tamanho do buffer de texto
BUFFER_SIZE=1000

# Intervalo para salvar texto (segundos)
SAVE_INTERVAL=30

# Tamanho mínimo de texto para salvar
MIN_TEXT_LENGTH=5

# Desabilitar monitoramento de teclado
# Para desabilitar:
# systemctl --user disable activity-tracker-keyboard.service

# ======================
# API
# ======================

# Porta da API
API_PORT=5001

# Host da API
API_HOST=0.0.0.0

# ======================
# IA e Resumos
# ======================

# Usar Ollama (true) ou OpenAI (false)
USE_OLLAMA=true

# Modelo do Ollama
OLLAMA_MODEL=llama3.2

# URL do Ollama
OLLAMA_URL=http://localhost:11434

# OpenAI API Key (se USE_OLLAMA=false)
# export OPENAI_API_KEY="sk-..."

# ======================
# Banco de Dados
# ======================

# Caminho do banco de dados
DB_PATH=~/.activity_tracker/activity.db

# Limite de eventos por query
MAX_EVENTS=10000

# ======================
# Extensão do Navegador
# ======================

# Sites para monitorar inputs
MONITORED_SITES=(
    "web.whatsapp.com"
    "web.telegram.org"
    "discord.com"
    "slack.com"
    "facebook.com"
    "twitter.com"
    "instagram.com"
    "linkedin.com"
)

# ======================
# Categorização
# ======================

# Palavras-chave por categoria
# Edite em: agent/ai_summarizer.py -> categorize_activities()

# ======================
# Logs
# ======================

# Diretório de logs
LOG_DIR=~/.activity_tracker

# Nível de log (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# ======================
# Privacidade
# ======================

# Lista de aplicações/sites para IGNORAR
IGNORE_APPS=(
    # Exemplo: "Private Browser"
    # Exemplo: "banking.com"
)

# Desabilitar captura de texto em apps específicos
IGNORE_TEXT_APPS=(
    # Exemplo: "password-manager"
)

# ======================
# Backup Automático
# ======================

# Criar backup diário do banco de dados
# Adicione ao crontab:
# 0 2 * * * cp ~/.activity_tracker/activity.db ~/.activity_tracker/backup/activity_$(date +\%Y\%m\%d).db

# Limpar backups antigos (manter últimos 30 dias)
# 0 3 * * * find ~/.activity_tracker/backup -name "activity_*.db" -mtime +30 -delete

# ======================
# Notificações
# ======================

# Enviar resumo diário por email (configurar sendmail)
# DAILY_SUMMARY_EMAIL=seu@email.com

# Hora do resumo diário
# SUMMARY_HOUR=20

# ======================
# Performance
# ======================

# Limitar tamanho do banco de dados
# Apagar eventos mais antigos que N dias
# Para configurar:
# sqlite3 ~/.activity_tracker/activity.db "DELETE FROM events WHERE ts < strftime('%s', 'now', '-90 days')"

# ======================
# Integração
# ======================

# Webhook para enviar eventos (opcional)
# WEBHOOK_URL=http://localhost:8080/activity

# Token de autenticação para webhook
# WEBHOOK_TOKEN=seu-token-secreto

# ======================
# Desenvolvimento
# ======================

# Modo debug (verbose logs)
# export DEBUG=1

# Não salvar no banco (apenas logs)
# export DRY_RUN=1

# ======================
# Exemplo de Uso
# ======================

# 1. Copie este arquivo:
#    cp CONFIG.md ~/.activity_tracker/config.sh

# 2. Edite as variáveis:
#    nano ~/.activity_tracker/config.sh

# 3. Carregue antes de iniciar:
#    source ~/.activity_tracker/config.sh
#    ~/activity-tracker/start.sh

# ======================
# Variáveis de Ambiente
# ======================

# As seguintes variáveis podem ser definidas no shell:

# export ACTIVITY_TRACKER_DB=~/.activity_tracker/activity.db
# export ACTIVITY_TRACKER_LOG_LEVEL=INFO
# export ACTIVITY_TRACKER_API_PORT=5001
# export ACTIVITY_TRACKER_OLLAMA_URL=http://localhost:11434
# export OPENAI_API_KEY=sk-...

# Adicione ao ~/.bashrc para tornar permanente
