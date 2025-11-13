# ⚡ Guia Rápido - Activity Tracker

## 🚀 Instalação (1 comando)

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/italloramon12/logbook-tool/main/install-simple.sh)
```

## ✅ Verificar se está funcionando

```bash
# Checar serviços
systemctl --user status activity-tracker-*

# Ou usar o script de teste
./test-installation.sh
```

## 🌐 Acessar Dashboard

Abra no navegador:
```
http://localhost:5001
```

## 🔌 Instalar Extensão (Chrome/Edge)

1. Abra: `chrome://extensions/`
2. Ative "Modo desenvolvedor"
3. Clique "Carregar sem compactação"
4. Selecione: `~/activity-tracker/browser-extension`

[Ver guia completo](BROWSER-EXTENSION-GUIDE.md)

## 📊 Ver Seus Dados

### Via Interface Web
```
http://localhost:5001
```

### Via Banco de Dados
```bash
# Ver últimos 10 eventos
sqlite3 ~/.config/activity-tracker/tracker.db \
  "SELECT datetime(ts, 'unixepoch', 'localtime'), type, title 
   FROM events ORDER BY ts DESC LIMIT 10;"
```

### Via API
```bash
# Testar API
curl http://localhost:5001/api/health

# Ver eventos recentes (JSON)
curl http://localhost:5001/api/events?limit=10
```

## 🎛️ Controlar Serviços

```bash
# Status
systemctl --user status activity-tracker-*

# Parar
systemctl --user stop activity-tracker-*

# Iniciar
systemctl --user start activity-tracker-*

# Reiniciar
systemctl --user restart activity-tracker-*

# Ver logs em tempo real
journalctl --user -u activity-tracker-agent -f
journalctl --user -u activity-tracker-api -f
```

## 🗑️ Desinstalar

```bash
# Parar e desabilitar
systemctl --user stop activity-tracker-*
systemctl --user disable activity-tracker-*

# Remover arquivos
rm -rf ~/activity-tracker
rm -rf ~/.config/activity-tracker
rm ~/.config/systemd/user/activity-tracker-*

# Remover hook do bash
sed -i '/activity-tracker/d' ~/.bashrc
```

## 🆘 Problemas Comuns

### API não responde
```bash
# Verificar se está rodando
systemctl --user status activity-tracker-api

# Ver logs de erro
journalctl --user -u activity-tracker-api -n 50

# Reiniciar
systemctl --user restart activity-tracker-api
```

### Agente não monitora janelas
```bash
# Verificar dependências
which xdotool xprintidle wmctrl

# Ver logs
journalctl --user -u activity-tracker-agent -n 50

# Testar manualmente
~/activity-tracker/venv/bin/python3 ~/activity-tracker/agent/agent.py
```

### Extensão não funciona
1. Verificar se API está rodando (curl http://localhost:5001/api/health)
2. Abrir console da extensão (chrome://extensions/ > Detalhes > service worker)
3. Ver se há erros no console
4. Recarregar a extensão

### Terminal não registra comandos
```bash
# Verificar se hook foi adicionado
grep "activity-tracker" ~/.bashrc

# Recarregar bash
source ~/.bashrc

# Testar manualmente
echo "test command" | bash ~/activity-tracker/log_command.sh
```

## 📖 Documentação Completa

- [README.md](README-NEW.md) - Documentação completa
- [BROWSER-EXTENSION-GUIDE.md](BROWSER-EXTENSION-GUIDE.md) - Guia da extensão
- [INSTALL.md](INSTALL.md) - Instalação one-line

## 💡 Dicas

1. **Primeira vez?** Execute `./test-installation.sh` para validar
2. **Logs em tempo real:** Use `journalctl --user -u activity-tracker-* -f`
3. **Ver banco direto:** Use `sqlite3 ~/.config/activity-tracker/tracker.db`
4. **Privacidade:** Tudo fica no seu PC, nada vai pra internet
5. **Performance:** O agente usa <1% de CPU e <50MB de RAM

---

**🎉 Pronto! Seu sistema já está monitorando tudo automaticamente.**

Qualquer dúvida, veja a [documentação completa](README-NEW.md) ou abra uma issue no GitHub.
