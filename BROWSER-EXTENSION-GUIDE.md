# 🔧 Como Instalar a Extensão do Navegador

## Google Chrome / Microsoft Edge / Brave

### Passo 1: Abrir página de extensões
Digite na barra de endereços:
```
chrome://extensions/
```

### Passo 2: Ativar modo desenvolvedor
No canto superior direito, ative a chave **"Modo do desenvolvedor"**

### Passo 3: Carregar extensão
1. Clique no botão **"Carregar sem compactação"** (ou "Load unpacked")
2. Navegue até a pasta: `~/activity-tracker/browser-extension`
3. Selecione a pasta e clique em "Selecionar"

### Passo 4: Verificar instalação
Você verá a extensão **"ActivityTracker Web Companion"** na lista.
Um ícone verde com a letra "A" aparecerá na barra de ferramentas.

---

## Mozilla Firefox

### Passo 1: Abrir página de debug
Digite na barra de endereços:
```
about:debugging#/runtime/this-firefox
```

### Passo 2: Carregar extensão temporária
1. Clique em **"Carregar extensão temporária..."**
2. Navegue até: `~/activity-tracker/browser-extension`
3. Selecione o arquivo **`manifest.json`**
4. Clique em "Abrir"

### Nota importante para Firefox
A extensão precisa ser recarregada toda vez que você reiniciar o navegador.
Para instalação permanente no Firefox, a extensão precisa ser assinada.

---

## Verificar se está funcionando

### 1. Ver console da extensão

**Chrome/Edge:**
1. Vá em `chrome://extensions/`
2. Encontre "ActivityTracker Web Companion"
3. Clique em "service worker" ou "background page"
4. Veja os logs no console

**Firefox:**
1. Vá em `about:debugging#/runtime/this-firefox`
2. Clique em "Inspecionar" na extensão
3. Veja os logs no console

### 2. Verificar API

Abra o terminal e execute:
```bash
# Ver logs da API
journalctl --user -u activity-tracker-api -f
```

Navegue entre sites e você verá logs como:
```
Event logged: {ts: 1699920000, type: "website", title: "GitHub", ...}
```

### 3. Ver no banco de dados

```bash
sqlite3 ~/.config/activity-tracker/tracker.db \
  "SELECT datetime(ts, 'unixepoch', 'localtime') as time, type, title, detail 
   FROM events WHERE type='website' ORDER BY ts DESC LIMIT 10;"
```

---

## Troubleshooting

### ❌ Extensão não aparece
- Verifique se está na pasta correta: `~/activity-tracker/browser-extension`
- Certifique-se que os arquivos `manifest.json`, `background.js` e `content.js` existem

### ❌ Não registra sites visitados
1. Verifique se a API está rodando:
   ```bash
   systemctl --user status activity-tracker-api
   ```

2. Teste a API manualmente:
   ```bash
   curl http://localhost:5001/api/health
   ```

3. Verifique permissões da extensão:
   - Chrome: A extensão deve ter acesso a `http://localhost:5001/*`
   - Veja em Detalhes da extensão > Permissões

### ❌ Console mostra erro de CORS
Isso é normal se a API não estiver rodando. Inicie com:
```bash
systemctl --user start activity-tracker-api
```

### ❌ "Failed to fetch" no console
A API não está acessível. Verifique:
```bash
# API está rodando?
curl http://localhost:5001/api/health

# Porta está aberta?
netstat -tlnp | grep 5001
```

---

## Desinstalar Extensão

**Chrome/Edge:**
1. `chrome://extensions/`
2. Clique em "Remover" na extensão ActivityTracker

**Firefox:**
1. `about:addons`
2. Clique em "Remover" na extensão ActivityTracker

---

## Notas de Privacidade

✅ A extensão **NÃO** envia dados para internet  
✅ Tudo fica armazenado localmente em `~/.config/activity-tracker/tracker.db`  
✅ Você pode desativar o monitoramento de sites a qualquer momento  
✅ O código é open source - você pode auditar o que ele faz  

---

**💡 Dica:** Para monitoramento mais detalhado, mantenha a extensão sempre ativa!
