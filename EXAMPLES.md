# 📖 Exemplos de Uso - Activity Tracker

## 🎯 Casos de Uso Comuns

### 1. Analisar Produtividade da Semana

```bash
# Gerar resumos de cada dia
for i in {0..6}; do
    date=$(date -d "$i days ago" +%Y-%m-%d)
    echo "Gerando resumo de $date..."
    # Adicionar parâmetro de data na API futuramente
done

# Por enquanto, use o dashboard para ver dias anteriores
```

### 2. Encontrar Tempo Perdido em Redes Sociais

```bash
# Via SQLite
sqlite3 ~/.activity_tracker/activity.db << EOF
SELECT 
    type,
    SUM(duration) as total_seconds,
    SUM(duration)/3600.0 as total_hours
FROM events 
WHERE type IN ('facebook', 'twitter', 'instagram', 'youtube')
  AND ts >= strftime('%s', 'now', '-7 days')
GROUP BY type
ORDER BY total_seconds DESC;
EOF
```

### 3. Top 10 Atividades do Mês

```bash
sqlite3 ~/.activity_tracker/activity.db << EOF
SELECT 
    title,
    COUNT(*) as times,
    SUM(duration) as total_seconds,
    SUM(duration)/3600.0 as hours
FROM events
WHERE ts >= strftime('%s', 'now', '-30 days')
  AND type NOT IN ('idle')
GROUP BY title
ORDER BY total_seconds DESC
LIMIT 10;
EOF
```

### 4. Tempo Total Trabalhando vs Entretenimento

```bash
# Via API
curl -s http://localhost:5001/api/categories | jq '{
  work: .work.time,
  development: .development.time,
  entertainment: .entertainment.time,
  social_media: .social_media.time
}'
```

### 5. Detectar Horas Mais Produtivas

```bash
sqlite3 ~/.activity_tracker/activity.db << EOF
SELECT 
    strftime('%H', datetime(ts, 'unixepoch', 'localtime')) as hour,
    COUNT(*) as activities,
    SUM(duration)/3600.0 as hours
FROM events
WHERE type IN ('work', 'development', 'productivity')
  AND ts >= strftime('%s', 'now', '-7 days')
GROUP BY hour
ORDER BY hours DESC;
EOF
```

## 🔧 Scripts Úteis

### Backup Automático

```bash
#!/bin/bash
# backup_activity.sh - Adicionar ao crontab

BACKUP_DIR=~/.activity_tracker/backups
mkdir -p $BACKUP_DIR

DATE=$(date +%Y%m%d_%H%M%S)
cp ~/.activity_tracker/activity.db $BACKUP_DIR/activity_$DATE.db

# Manter apenas últimos 30 dias
find $BACKUP_DIR -name "activity_*.db" -mtime +30 -delete

echo "Backup criado: activity_$DATE.db"
```

Adicionar ao crontab:
```bash
crontab -e
# Adicionar:
0 2 * * * /path/to/backup_activity.sh
```

### Limpeza de Dados Antigos

```bash
#!/bin/bash
# cleanup_old_data.sh

echo "Limpando eventos com mais de 90 dias..."

sqlite3 ~/.activity_tracker/activity.db << EOF
DELETE FROM events 
WHERE ts < strftime('%s', 'now', '-90 days');

VACUUM;
EOF

echo "Limpeza concluída!"
```

### Exportar Dados para CSV

```bash
#!/bin/bash
# export_to_csv.sh

OUTPUT=~/activity_tracker_export_$(date +%Y%m%d).csv

sqlite3 -header -csv ~/.activity_tracker/activity.db << EOF > $OUTPUT
SELECT 
    datetime(ts, 'unixepoch', 'localtime') as timestamp,
    type,
    title,
    detail,
    duration
FROM events
WHERE ts >= strftime('%s', 'now', '-30 days')
ORDER BY ts DESC;
EOF

echo "Exportado para: $OUTPUT"
```

### Resumo Semanal Automático

```bash
#!/bin/bash
# weekly_summary.sh - Executar toda segunda-feira

~/activity-tracker/generate-summary.sh

# Enviar por email (se configurado sendmail)
# cat ~/.activity_tracker/summary_$(date +%Y-%m-%d).md | mail -s "Resumo Semanal" seu@email.com
```

## 🎨 Personalização

### Adicionar Nova Categoria

Edite `agent/ai_summarizer.py`:

```python
def categorize_activities(self, activities: List[Dict]) -> Dict:
    categories = {
        "work": {"time": 0, "apps": []},
        # ... outras categorias
        "education": {"time": 0, "apps": []},  # NOVA
    }
    
    keywords = {
        # ... outras keywords
        "education": ["coursera", "udemy", "khan", "edx", "duolingo"],  # NOVA
    }
```

### Criar Relatório Personalizado

```python
#!/usr/bin/env python3
# custom_report.py

import sys
sys.path.insert(0, '/home/seu-usuario/activity-tracker/agent')

from db import fetch_events
import time

# Pegar últimos 7 dias
now = int(time.time())
week_ago = now - (7 * 86400)

events = fetch_events(week_ago, now, limit=100000)

# Análise personalizada
apps = {}
for event in events:
    title = event[3]
    duration = event[5]
    if title not in apps:
        apps[title] = 0
    apps[title] += duration

# Top 20
top = sorted(apps.items(), key=lambda x: x[1], reverse=True)[:20]

print("Top 20 Apps da Semana:")
print("=" * 50)
for i, (app, seconds) in enumerate(top, 1):
    hours = seconds / 3600
    print(f"{i:2d}. {app[:40]:40s} {hours:6.2f}h")
```

### Integrar com Webhook

```python
#!/usr/bin/env python3
# webhook_notifier.py

import requests
import time
from db import fetch_events

# Configuração
WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

def send_daily_summary():
    now = int(time.time())
    day_start = now - (now % 86400)
    
    events = fetch_events(day_start, now)
    total_time = sum(e[5] for e in events)
    
    message = {
        "text": f"📊 Resumo do Dia",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Tempo total monitorado:* {total_time/3600:.1f}h"
                }
            }
        ]
    }
    
    requests.post(WEBHOOK_URL, json=message)

if __name__ == "__main__":
    send_daily_summary()
```

## 📊 Queries SQL Úteis

### Tempo por Aplicação Hoje

```sql
SELECT 
    title,
    SUM(duration) as seconds,
    SUM(duration)/3600.0 as hours,
    COUNT(*) as sessions
FROM events
WHERE ts >= strftime('%s', 'now', 'start of day')
  AND type = 'window'
GROUP BY title
ORDER BY seconds DESC
LIMIT 10;
```

### Distribuição de Tempo por Hora do Dia

```sql
SELECT 
    strftime('%H', datetime(ts, 'unixepoch', 'localtime')) as hour,
    SUM(duration)/3600.0 as hours
FROM events
WHERE ts >= strftime('%s', 'now', '-7 days')
GROUP BY hour
ORDER BY hour;
```

### Sites Mais Visitados

```sql
SELECT 
    title,
    COUNT(*) as visits,
    SUM(duration)/60.0 as minutes
FROM events
WHERE type IN ('website', 'whatsapp', 'youtube', 'github')
  AND ts >= strftime('%s', 'now', '-7 days')
GROUP BY title
ORDER BY minutes DESC
LIMIT 15;
```

### Tempo Ocioso vs Ativo

```sql
SELECT 
    CASE WHEN type = 'idle' THEN 'Ocioso' ELSE 'Ativo' END as status,
    SUM(duration)/3600.0 as hours,
    (SUM(duration)*100.0 / (SELECT SUM(duration) FROM events)) as percentage
FROM events
WHERE ts >= strftime('%s', 'now', '-7 days')
GROUP BY status;
```

### Texto Digitado por Aplicação

```sql
SELECT 
    type as app,
    COUNT(*) as times,
    SUM(LENGTH(detail)) as total_chars
FROM events
WHERE type IN ('whatsapp', 'telegram', 'discord', 'slack', 'text_input')
  AND ts >= strftime('%s', 'now', 'start of day')
GROUP BY type
ORDER BY total_chars DESC;
```

## 🔔 Automações com Cron

### Crontab Completo

```bash
crontab -e
```

Adicione:

```bash
# Backup diário às 2:00 AM
0 2 * * * /home/usuario/activity-tracker/scripts/backup.sh

# Limpeza de dados antigos toda segunda às 3:00 AM
0 3 * * 1 /home/usuario/activity-tracker/scripts/cleanup.sh

# Resumo diário às 20:00
0 20 * * * /home/usuario/activity-tracker/generate-summary.sh

# Resumo semanal toda segunda às 9:00
0 9 * * 1 /home/usuario/activity-tracker/scripts/weekly_summary.sh

# Verificar se serviços estão rodando a cada hora
0 * * * * systemctl --user is-active activity-tracker-agent.service || systemctl --user start activity-tracker-agent.service
```

## 📱 Integração com Notificações Desktop

```bash
#!/bin/bash
# notify_summary.sh

SUMMARY=$(curl -s http://localhost:5001/api/stats | jq -r '.total_seconds')
HOURS=$(echo "$SUMMARY / 3600" | bc)

notify-send "Activity Tracker" "Você trabalhou ${HOURS}h hoje! 🎉"
```

## 🎯 Metas e Objetivos

### Definir Meta Diária

```python
#!/usr/bin/env python3
# check_daily_goal.py

from db import fetch_events
import time

GOAL_HOURS = 6  # Meta: 6h de trabalho produtivo

now = int(time.time())
day_start = now - (now % 86400)

events = fetch_events(day_start, now)

# Tempo produtivo
productive_time = sum(
    e[5] for e in events 
    if e[2] in ['work', 'development', 'productivity']
)

hours = productive_time / 3600
percentage = (hours / GOAL_HOURS) * 100

print(f"Meta do dia: {GOAL_HOURS}h")
print(f"Trabalhado: {hours:.1f}h ({percentage:.1f}%)")

if hours >= GOAL_HOURS:
    print("✅ Meta atingida!")
else:
    remaining = GOAL_HOURS - hours
    print(f"⏰ Faltam {remaining:.1f}h")
```

## 🔍 Análises Avançadas

### Correlação entre Sono e Produtividade

```bash
# Requer dados de sono de outra fonte
# Exemplo: integração com smartwatch/Fitbit
```

### Padrões de Distração

```sql
-- Quantas vezes você se distraiu (mudou de app produtivo para entretenimento)
SELECT 
    date(datetime(e1.ts, 'unixepoch', 'localtime')) as day,
    COUNT(*) as distractions
FROM events e1
JOIN events e2 ON e2.id = e1.id + 1
WHERE e1.type IN ('work', 'development')
  AND e2.type IN ('entertainment', 'social_media')
GROUP BY day
ORDER BY day DESC;
```

---

**Mais exemplos e scripts disponíveis na comunidade!**
