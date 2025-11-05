# 🚀 Guia Rápido - Activity Tracker

## Instalação em 3 Passos

### 1. Instalar o Sistema

```bash
git clone <seu-repositorio>
cd logbook-tool
chmod +x scripts/install.sh
./scripts/install.sh
```

### 2. Iniciar os Serviços

```bash
~/activity-tracker/start.sh
```

### 3. Acessar o Dashboard

Abra no navegador: **http://localhost:5001**

---

## 📊 Funcionalidades Principais

### Monitoramento Automático
- ✅ Janelas e aplicações ativas
- ✅ Sites visitados (com extensão)
- ✅ Comandos do terminal
- ✅ Tempo ocioso

### Monitoramento Avançado (Opcional)
- 📝 Texto digitado em aplicações
- 📝 Inputs em WhatsApp Web, Telegram, Discord
- 🔍 Buscas realizadas no Google

### Análise com IA
- 🤖 Resumo diário automático
- 📈 Score de produtividade
- 💡 Sugestões personalizadas
- 📊 Categorização inteligente

---

## 🎯 Uso Diário

### Ver Atividades do Dia
```bash
# No navegador
http://localhost:5001
```

### Gerar Resumo Diário
```bash
# Opção 1: Via web
http://localhost:5001/summary.html

# Opção 2: Via terminal
~/activity-tracker/generate-summary.sh
```

### Verificar Status
```bash
~/activity-tracker/status.sh
```

### Ver Logs
```bash
~/activity-tracker/logs.sh
```

---

## 🔌 Instalar Extensão do Navegador

### Firefox
1. Abra: `about:debugging#/runtime/this-firefox`
2. Clique em "Carregar extensão temporária"
3. Selecione: `~/activity-tracker/browser-extension/manifest.json`

### Chrome
1. Abra: `chrome://extensions`
2. Ative "Modo desenvolvedor"
3. Clique em "Carregar sem compactação"
4. Selecione: `~/activity-tracker/browser-extension`

---

## 🤖 Configurar IA (Ollama - Recomendado)

```bash
# Instalar Ollama
curl https://ollama.ai/install.sh | sh

# Baixar modelo
ollama pull llama3.2

# Testar
curl http://localhost:11434

# Gerar resumo
http://localhost:5001/summary.html
```

---

## ⚙️ Comandos Úteis

### Iniciar
```bash
~/activity-tracker/start.sh
```

### Parar
```bash
~/activity-tracker/stop.sh
```

### Status
```bash
~/activity-tracker/status.sh
```

### Habilitar no Boot
```bash
systemctl --user enable activity-tracker-agent.service
systemctl --user enable activity-tracker-api.service
systemctl --user enable activity-tracker-keyboard.service  # Opcional
```

### Desabilitar Monitoramento de Teclado
```bash
systemctl --user stop activity-tracker-keyboard.service
systemctl --user disable activity-tracker-keyboard.service
```

---

## 📁 Onde Estão os Dados?

```
~/.activity_tracker/
├── activity.db          # Banco de dados SQLite
├── agent.log           # Logs do sistema
├── term_history.log    # Histórico do terminal
└── summary_*.md        # Resumos salvos
```

---

## 🆘 Resolução de Problemas

### Serviços não iniciam
```bash
# Ver erros
journalctl --user -u activity-tracker-agent.service -n 50

# Reiniciar
~/activity-tracker/stop.sh
~/activity-tracker/start.sh
```

### Dashboard não abre
```bash
# Verificar se API está rodando
curl http://localhost:5001/api/stats

# Ver logs da API
~/activity-tracker/logs.sh api
```

### Extensão não funciona
1. Verifique se a API está rodando
2. Abra console do navegador (F12)
3. Recarregue a extensão

### Ollama não gera resumo
```bash
# Verificar se está rodando
curl http://localhost:11434

# Iniciar manualmente
ollama serve

# Verificar modelo instalado
ollama list
```

---

## 🔒 Privacidade

### ⚠️ IMPORTANTE
Este sistema captura dados sensíveis. Use apenas em seu computador pessoal e com seu consentimento.

### Limpar Dados
```bash
# Backup
cp ~/.activity_tracker/activity.db ~/.activity_tracker/backup.db

# Limpar tudo
rm ~/.activity_tracker/activity.db

# Serviços criarão novo banco automaticamente
```

---

## 📊 Estatísticas Coletadas

| Tipo | Descrição | Sensibilidade |
|------|-----------|---------------|
| `window` | Janelas ativas | 🟡 Média |
| `website` | Sites visitados | 🟡 Média |
| `terminal` | Comandos shell | 🔴 Alta |
| `whatsapp` | Atividade WhatsApp | 🔴 Alta |
| `telegram` | Atividade Telegram | 🔴 Alta |
| `text_input` | Texto digitado | 🔴 Muito Alta |
| `idle` | Tempo ocioso | 🟢 Baixa |

---

## 💡 Dicas

1. **Produtividade**: Revise seu resumo diário para identificar padrões
2. **Foco**: Use as estatísticas para minimizar distrações
3. **Tempo**: Compare dias da semana para otimizar rotina
4. **Metas**: Defina tempo máximo em categorias específicas
5. **Pausas**: Use tempo idle para identificar necessidade de descanso

---

## 📚 Recursos Adicionais

- **README Completo**: `/workspaces/logbook-tool/README.md`
- **Documentação da API**: http://localhost:5001/api/stats
- **Dashboard**: http://localhost:5001
- **Resumo IA**: http://localhost:5001/summary.html

---

**Desenvolvido com ❤️ para gestão de tempo e produtividade**
