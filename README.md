# Activity Tracker — Monitoramento Completo de Atividades (Ubuntu)

> Sistema completo de monitoramento de atividades para Ubuntu. Captura janelas ativas, navegação web, comandos do terminal, texto digitado (com consentimento) e gera resumos inteligentes usando IA. **⚠️ Uso apenas com consentimento explícito do usuário.**

## 🎯 Objetivo

Fornecer um sistema de monitoramento **local e privado** que permite ao usuário:

1. **Rastrear** todas as suas atividades diárias no computador
2. **Entender** como está usando seu tempo
3. **Analisar** padrões de produtividade e comportamento
4. **Receber** resumos inteligentes e insights sobre suas atividades
5. **Melhorar** gestão de tempo e foco

## ✨ Funcionalidades

### 🖥️ Monitoramento do Sistema
- ✅ Janelas ativas (títulos e duração)
- ✅ Tempo ocioso (idle detection)
- ✅ Comandos executados no terminal
- ✅ Detecção automática de ambiente (X11/Wayland)

### 🌐 Monitoramento Web (Extensão do Navegador)
- ✅ URLs visitadas e tempo em cada site
- ✅ Categorização automática (WhatsApp, YouTube, GitHub, etc)
- ✅ Captação de buscas realizadas (Google, Bing, DuckDuckGo)
- ✅ Formulários enviados
- ✅ Tempo específico em redes sociais

### ⌨️ Monitoramento de Texto (Opcional)
- ✅ Captura texto digitado em aplicações desktop
- ✅ Captura texto digitado em sites específicos (WhatsApp Web, Telegram, Discord, etc)
- ✅ Contexto da aplicação onde o texto foi digitado
- ⚠️ **Requer consentimento explícito e configuração manual**

### 🤖 Análise Inteligente com IA
- ✅ Categorização automática de atividades
- ✅ Geração de resumos diários com insights
- ✅ Avaliação de produtividade (score 0-10)
- ✅ Sugestões personalizadas de melhoria
- ✅ Suporte a Ollama (IA local) ou OpenAI API

### 📊 Dashboard e Relatórios
- ✅ Interface web moderna e responsiva
- ✅ Visualização em tempo real
- ✅ Estatísticas por categoria
- ✅ Top atividades do dia
- ✅ Exportação para Markdown
- ✅ Página dedicada de resumo diário

## 📦 Componentes

- **`agent/agent.py`** — Daemon que detecta janelas ativas e idle
- **`agent/keyboard_monitor.py`** — Monitor de texto digitado (opcional)
- **`agent/db.py`** — Persistência SQLite
- **`agent/api.py`** — API Flask para dashboard (porta 5001)
- **`agent/ai_summarizer.py`** — Geração de resumos com IA
- **`agent/static/index.html`** — Dashboard principal
- **`agent/static/summary.html`** — Página de resumo diário
- **`browser-extension/`** — Extensão para Firefox/Chrome
- **`scripts/log_command.sh`** — Hook para bash/zsh
- **`scripts/install.sh`** — Script de instalação automática

## 🔧 Pré-requisitos (Ubuntu)

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip xdotool xprintidle wmctrl curl
```

### Opcional: Ollama (para resumos com IA local)

```bash
# Instalar Ollama
curl https://ollama.ai/install.sh | sh

# Baixar modelo LLaMA 3.2
ollama pull llama3.2
```

## 🚀 Instalação Rápida

```bash
# Clone o repositório
git clone <seu-repositorio>
cd logbook-tool

# Execute o instalador
chmod +x scripts/install.sh
./scripts/install.sh
```

O script de instalação irá:
1. Instalar dependências do sistema
2. Criar ambiente virtual Python
3. Instalar pacotes Python necessários
4. Configurar serviços systemd
5. Configurar hook do shell
6. Criar scripts de controle

## 🎮 Como Usar

### Iniciar Serviços

```bash
# Iniciar todos os serviços
~/activity-tracker/start.sh

# Ou iniciar manualmente
systemctl --user start activity-tracker-agent.service
systemctl --user start activity-tracker-keyboard.service  # Opcional
systemctl --user start activity-tracker-api.service
```

### Habilitar Inicialização Automática

```bash
systemctl --user enable activity-tracker-agent.service
systemctl --user enable activity-tracker-keyboard.service  # Opcional
systemctl --user enable activity-tracker-api.service
```

### Verificar Status

```bash
~/activity-tracker/status.sh
```

### Ver Logs

```bash
# Logs gerais
~/activity-tracker/logs.sh

# Logs específicos
~/activity-tracker/logs.sh agent
~/activity-tracker/logs.sh keyboard
~/activity-tracker/logs.sh api
```

### Parar Serviços

```bash
~/activity-tracker/stop.sh
```

## 🌐 Acessar Dashboard

Após iniciar os serviços:

- **Dashboard Principal**: http://localhost:5001
- **Resumo Diário**: http://localhost:5001/summary.html

## 🔌 Instalar Extensão do Navegador

### Firefox

1. Abra `about:debugging`
2. Clique em "This Firefox"
3. Clique em "Load Temporary Add-on"
4. Selecione `~/activity-tracker/browser-extension/manifest.json`

### Chrome/Chromium

1. Abra `chrome://extensions`
2. Ative "Developer mode"
3. Clique em "Load unpacked"
4. Selecione a pasta `~/activity-tracker/browser-extension`

## 📊 Gerar Resumo Diário

### Via Interface Web

Acesse http://localhost:5001/summary.html e clique em "Gerar Resumo com IA"

### Via Terminal

```bash
~/activity-tracker/generate-summary.sh
```

O resumo será salvo em `~/.activity_tracker/summary_YYYY-MM-DD.md`

## 📁 Estrutura de Arquivos

```
~/activity-tracker/          # Instalação
  ├── agent/
  │   ├── agent.py           # Monitor de janelas
  │   ├── keyboard_monitor.py # Monitor de teclado
  │   ├── api.py             # API Flask
  │   ├── db.py              # Banco de dados
  │   ├── ai_summarizer.py   # Resumos com IA
  │   └── static/
  │       ├── index.html     # Dashboard
  │       └── summary.html   # Resumo diário
  ├── browser-extension/
  │   ├── manifest.json
  │   ├── background.js
  │   └── content.js
  ├── scripts/
  │   ├── install.sh
  │   └── log_command.sh
  └── venv/                  # Ambiente Python

~/.activity_tracker/         # Dados e logs
  ├── activity.db           # Banco SQLite
  ├── agent.log             # Logs do agente
  ├── term_history.log      # Histórico terminal
  └── summary_*.md          # Resumos salvos
```

## 🔒 Privacidade e Segurança

### ⚠️ IMPORTANTE

Este sistema captura informações sensíveis:
- Janelas ativas e aplicações utilizadas
- URLs visitadas
- Comandos executados no terminal
- **Texto digitado** (se habilitado)

### Recomendações de Segurança

1. ✅ **Use apenas em computadores pessoais**
2. ✅ **Obtenha consentimento explícito** se monitorar outras pessoas
3. ✅ **Proteja o banco de dados** (`~/.activity_tracker/activity.db`)
4. ✅ **Desabilite monitoramento de teclado** se não precisar
5. ✅ **Revise dados coletados** regularmente
6. ✅ **Exclua dados antigos** quando não forem mais necessários

### Desabilitar Monitoramento de Teclado

```bash
# Parar serviço
systemctl --user stop activity-tracker-keyboard.service

# Desabilitar permanentemente
systemctl --user disable activity-tracker-keyboard.service
```

### Limpar Dados

```bash
# Backup antes de limpar
cp ~/.activity_tracker/activity.db ~/.activity_tracker/activity.db.backup

# Limpar banco (cuidado!)
rm ~/.activity_tracker/activity.db

# Recriar estrutura
sqlite3 ~/.activity_tracker/activity.db < schema.sql
```

## 🤖 Configurar IA

### Opção 1: Ollama (Recomendado - Local e Gratuito)

```bash
# Instalar
curl https://ollama.ai/install.sh | sh

# Baixar modelo
ollama pull llama3.2

# Testar
curl http://localhost:11434
```

### Opção 2: OpenAI API

```bash
# Definir API key
export OPENAI_API_KEY="sk-..."

# Adicionar ao ~/.bashrc
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.bashrc
```

Edite `agent/ai_summarizer.py` e configure `use_ollama=False` se quiser usar OpenAI.

## 📈 Categorias Automáticas

O sistema categoriza automaticamente atividades em:

- **Work** (Trabalho): Office, Excel, Word, Docs, Email
- **Communication** (Comunicação): WhatsApp, Telegram, Discord, Slack, Zoom
- **Entertainment** (Entretenimento): YouTube, Netflix, Spotify, Games
- **Productivity** (Produtividade): Notion, Trello, Asana, Todoist
- **Social Media** (Redes Sociais): Facebook, Twitter, Instagram, LinkedIn
- **Development** (Desenvolvimento): VSCode, GitHub, Terminal, StackOverflow
- **Idle** (Ocioso): Tempo sem atividade
- **Other** (Outros): Atividades não categorizadas

## 🛠️ Desenvolvimento

### Estrutura do Código

```python
# Adicionar novo tipo de evento
from db import insert_event

insert_event(
    ts=int(time.time()),
    typ="custom_type",
    title="Minha Atividade",
    detail="Detalhes adicionais",
    duration=120  # segundos
)
```

### API Endpoints

- `GET /api/events` - Lista todos os eventos
- `GET /api/stats` - Estatísticas do dia
- `GET /api/categories` - Atividades categorizadas
- `GET /api/summary` - Resumo diário com IA
- `GET /api/export_markdown` - Exporta em Markdown
- `POST /api/log_event` - Registra novo evento

### Banco de Dados

```sql
-- Estrutura da tabela events
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER NOT NULL,
    type TEXT NOT NULL,
    title TEXT,
    detail TEXT,
    duration INTEGER DEFAULT 0
);
```

## 🐛 Troubleshooting

### Serviços não iniciam

```bash
# Ver logs
journalctl --user -u activity-tracker-agent.service -n 50

# Verificar Python
which python3
python3 --version
```

### Extensão não funciona

- Verifique se a API está rodando: `curl http://localhost:5001/api/stats`
- Veja console do navegador (F12)
- Recarregue a extensão

### Ollama não responde

```bash
# Verificar se está rodando
systemctl status ollama

# Iniciar manualmente
ollama serve

# Testar
curl http://localhost:11434
```

### Permissões negadas

```bash
# Dar permissões
chmod +x ~/activity-tracker/*.sh
chmod +x ~/activity-tracker/agent/*.py
```

## 📝 TODO / Melhorias Futuras

- [ ] Suporte nativo para Wayland
- [ ] Detecção de aplicações por categoria (ML)
- [ ] Gráficos interativos no dashboard
- [ ] Notificações de padrões incomuns
- [ ] Exportação para outros formatos (JSON, CSV)
- [ ] Sincronização entre dispositivos (opcional)
- [ ] Modo "foco" com bloqueio de sites
- [ ] Integração com calendários

## 📄 Licença

Este projeto é fornecido "como está" para fins educacionais e pessoais.

**⚠️ AVISO LEGAL**: O uso inadequado desta ferramenta para monitorar outras pessoas sem consentimento pode violar leis de privacidade. Use com responsabilidade.

## 🤝 Contribuindo

Contribuições são bem-vindas! Abra issues ou pull requests.

## 📧 Suporte

Para problemas, abra uma issue no repositório.

---

**Desenvolvido com ❤️ para ajudar na gestão de tempo e produtividade**

