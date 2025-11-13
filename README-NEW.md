# 📊 Activity Tracker - Logbook Automático para Ubuntu

Sistema completo de monitoramento de atividades que registra **tudo** que você faz no computador e gera um logbook detalhado do seu dia.

## 🎯 O que ele monitora?

✅ **Sites acessados** - URLs, títulos, tempo em cada página  
✅ **Comandos do terminal** - Tudo que você executa no bash  
✅ **Aplicativos usados** - Qual janela estava ativa e por quanto tempo  
✅ **Tempo ocioso** - Detecta quando você está ausente  
✅ **Inputs em sites** - Opcional: texto digitado em redes sociais  

## 🚀 Instalação Rápida (Uma linha!)

```bash
curl -fsSL https://raw.githubusercontent.com/italloramon12/logbook-tool/main/install-simple.sh | bash
```

### Ou instalação manual:

```bash
# Clonar repositório
git clone https://github.com/italloramon12/logbook-tool.git
cd logbook-tool

# Executar instalação
chmod +x install-simple.sh
./install-simple.sh
```

## 📦 O que é instalado?

- **Agente de monitoramento** - Monitora janelas ativas e tempo ocioso
- **API REST** - Recebe eventos e armazena no banco de dados
- **Interface Web** - Visualiza seus dados em http://localhost:5001
- **Hook do terminal** - Captura comandos bash automaticamente
- **Extensão do navegador** - Monitora sites e tempo de navegação

## 🔧 Configuração da Extensão do Navegador

### Google Chrome / Microsoft Edge

1. Abra `chrome://extensions/` (ou `edge://extensions/`)
2. Ative o **Modo do desenvolvedor** (canto superior direito)
3. Clique em **Carregar sem compactação**
4. Selecione a pasta: `~/activity-tracker/browser-extension`

### Mozilla Firefox

1. Abra `about:debugging#/runtime/this-firefox`
2. Clique em **Carregar extensão temporária**
3. Navegue até `~/activity-tracker/browser-extension`
4. Selecione o arquivo `manifest.json`

## 📊 Como Usar

### Verificar se está funcionando

```bash
# Status dos serviços
systemctl --user status activity-tracker-*

# Ver logs em tempo real
journalctl --user -u activity-tracker-agent -f
```

### Acessar a interface web

Abra seu navegador e acesse:
```
http://localhost:5001
```

Você verá:
- Timeline de atividades do dia
- Gráficos de tempo por aplicativo/site
- Resumo de comandos executados
- Estatísticas de produtividade

### Ver banco de dados diretamente

```bash
sqlite3 ~/.config/activity-tracker/tracker.db "SELECT * FROM events ORDER BY ts DESC LIMIT 10;"
```

## 🎮 Comandos Úteis

```bash
# Parar monitoramento
systemctl --user stop activity-tracker-*

# Iniciar monitoramento
systemctl --user start activity-tracker-*

# Reiniciar serviços
systemctl --user restart activity-tracker-*

# Desabilitar início automático
systemctl --user disable activity-tracker-*

# Ver eventos em tempo real
tail -f ~/.config/activity-tracker/tracker.db
```

## 📁 Estrutura de Arquivos

```
~/activity-tracker/
├── agent/
│   ├── agent.py              # Agente principal de monitoramento
│   ├── api.py                # API REST
│   ├── db.py                 # Gerenciamento do banco de dados
│   ├── keyboard_monitor.py   # Monitor de teclado (futuro)
│   └── static/
│       ├── index.html        # Interface web
│       └── summary.html      # Página de resumo
├── browser-extension/
│   ├── manifest.json
│   ├── background.js
│   ├── content.js
│   └── icon.svg
├── venv/                     # Ambiente Python
└── log_command.sh            # Hook do terminal

~/.config/activity-tracker/
└── tracker.db                # Banco de dados SQLite
```

## 🔍 API REST

A API local aceita eventos de qualquer fonte:

### Endpoint: POST /api/log_event

```bash
curl -X POST http://localhost:5001/api/log_event \
  -H "Content-Type: application/json" \
  -d '{
    "ts": 1699920000,
    "type": "terminal",
    "title": "bash",
    "detail": "git commit -m \"feat: nova funcionalidade\"",
    "duration": 0
  }'
```

**Tipos de eventos:**
- `window` - Janela ativa
- `terminal` - Comando no terminal
- `website` - Site/URL visitado
- `idle` - Tempo ocioso
- `text_input` - Texto digitado

## 🛠️ Desenvolvimento

### Estrutura do código

```python
# agent.py - Loop principal de monitoramento
- Detecta janela ativa a cada 2 segundos
- Monitora tempo ocioso
- Envia eventos para a API

# api.py - Servidor Flask
- Endpoint /api/log_event
- Armazena eventos no SQLite
- Serve interface web

# db.py - Camada de dados
- Gerencia conexão SQLite
- Schema do banco
```

### Adicionar novo tipo de monitoramento

1. Criar função de coleta em `agent.py`
2. Enviar evento via `log_event()`
3. API já processa automaticamente
4. Visualizar na interface web

## 🔐 Privacidade

**⚠️ IMPORTANTE: Seus dados ficam 100% no seu computador!**

- Nenhum dado é enviado para internet
- Banco de dados local: `~/.config/activity-tracker/tracker.db`
- Você tem controle total dos seus dados
- Pode deletar o banco a qualquer momento

### Desinstalar completamente

```bash
# Parar serviços
systemctl --user stop activity-tracker-*
systemctl --user disable activity-tracker-*

# Remover arquivos
rm -rf ~/activity-tracker
rm -rf ~/.config/activity-tracker
rm ~/.config/systemd/user/activity-tracker-*

# Remover hook do bash
sed -i '/activity-tracker/d' ~/.bashrc
```

## 🐛 Troubleshooting

### Serviços não iniciam

```bash
# Ver logs detalhados
journalctl --user -u activity-tracker-agent -n 50
journalctl --user -u activity-tracker-api -n 50

# Verificar dependências
which xdotool xprintidle wmctrl python3
```

### Interface web não abre

```bash
# Verificar se API está rodando
curl http://localhost:5001/api/health

# Verificar porta em uso
netstat -tlnp | grep 5001
```

### Extensão não funciona

1. Verificar se API está rodando (porta 5001)
2. Ver console do navegador (F12) para erros
3. Verificar permissões da extensão
4. Recarregar a extensão

### Terminal não está sendo monitorado

```bash
# Verificar se hook foi adicionado
grep "activity-tracker" ~/.bashrc

# Recarregar bash
source ~/.bashrc

# Testar manualmente
bash ~/activity-tracker/log_command.sh
```

## 📈 Roadmap

- [ ] Suporte para Wayland
- [ ] Monitoramento de aplicativos Electron
- [ ] Exportar relatórios em PDF
- [ ] Dashboard com métricas de produtividade
- [ ] Categorização automática de atividades
- [ ] Suporte para múltiplos monitores
- [ ] App mobile para visualização

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se livre para:
- Reportar bugs
- Sugerir novas funcionalidades
- Enviar pull requests
- Melhorar a documentação

## 📄 Licença

MIT License - Veja arquivo LICENSE para detalhes

## 👨‍💻 Autor

**Itallo Ramon**
- GitHub: [@italloramon12](https://github.com/italloramon12)

---

⭐ Se este projeto foi útil, deixe uma estrela no repositório!
