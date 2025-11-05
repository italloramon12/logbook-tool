#!/bin/bash
# test_system.sh - Testa se o sistema está funcionando corretamente

set -e

echo "🧪 Testando Activity Tracker..."
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função de teste
test_component() {
    local name=$1
    local command=$2
    
    echo -n "Testing $name... "
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
}

# Testa dependências do sistema
echo "1. Verificando dependências do sistema:"
test_component "python3" "which python3"
test_component "xdotool" "which xdotool"
test_component "xprintidle" "which xprintidle"
test_component "wmctrl" "which wmctrl"
echo ""

# Testa instalação
echo "2. Verificando instalação:"
test_component "Diretório de instalação" "test -d ~/activity-tracker"
test_component "Ambiente virtual Python" "test -d ~/activity-tracker/venv"
test_component "Arquivo de banco de dados" "test -f ~/.activity_tracker/activity.db || true"
echo ""

# Testa módulos Python
echo "3. Verificando módulos Python:"
cd ~/activity-tracker/agent
source ../venv/bin/activate

test_component "Flask" "python3 -c 'import flask'"
test_component "pynput" "python3 -c 'import pynput'"
test_component "requests" "python3 -c 'import requests'"
echo ""

# Testa sintaxe dos scripts
echo "4. Verificando sintaxe dos scripts:"
test_component "agent.py" "python3 -m py_compile agent.py"
test_component "api.py" "python3 -m py_compile api.py"
test_component "db.py" "python3 -m py_compile db.py"
test_component "keyboard_monitor.py" "python3 -m py_compile keyboard_monitor.py"
test_component "ai_summarizer.py" "python3 -m py_compile ai_summarizer.py"
echo ""

# Testa serviços systemd
echo "5. Verificando serviços systemd:"
test_component "activity-tracker-agent.service" "test -f ~/.config/systemd/user/activity-tracker-agent.service"
test_component "activity-tracker-keyboard.service" "test -f ~/.config/systemd/user/activity-tracker-keyboard.service"
test_component "activity-tracker-api.service" "test -f ~/.config/systemd/user/activity-tracker-api.service"
echo ""

# Testa API (se estiver rodando)
echo "6. Verificando API (se estiver rodando):"
if curl -s http://localhost:5001/api/stats > /dev/null 2>&1; then
    echo -e "API está rodando: ${GREEN}✓${NC}"
    
    # Testa endpoints
    test_component "GET /api/events" "curl -s http://localhost:5001/api/events > /dev/null"
    test_component "GET /api/stats" "curl -s http://localhost:5001/api/stats > /dev/null"
    test_component "GET /api/categories" "curl -s http://localhost:5001/api/categories > /dev/null"
else
    echo -e "API não está rodando: ${YELLOW}⚠${NC}"
    echo "  Execute: ~/activity-tracker/start.sh"
fi
echo ""

# Testa Ollama (opcional)
echo "7. Verificando Ollama (opcional):"
if curl -s http://localhost:11434 > /dev/null 2>&1; then
    echo -e "Ollama está rodando: ${GREEN}✓${NC}"
    
    # Lista modelos
    if command -v ollama > /dev/null 2>&1; then
        echo "  Modelos instalados:"
        ollama list | head -n 5
    fi
else
    echo -e "Ollama não está instalado/rodando: ${YELLOW}⚠${NC}"
    echo "  Opcional - para resumos com IA local"
    echo "  Instalar: curl https://ollama.ai/install.sh | sh"
fi
echo ""

# Testa extensão do navegador
echo "8. Verificando extensão do navegador:"
test_component "manifest.json" "test -f ~/activity-tracker/browser-extension/manifest.json"
test_component "background.js" "test -f ~/activity-tracker/browser-extension/background.js"
test_component "content.js" "test -f ~/activity-tracker/browser-extension/content.js"
test_component "icon.png" "test -f ~/activity-tracker/browser-extension/icon.png"
echo ""

# Resumo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Resumo do Teste"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if systemctl --user is-active --quiet activity-tracker-agent.service; then
    echo -e "Agent: ${GREEN}Rodando${NC}"
else
    echo -e "Agent: ${RED}Parado${NC}"
fi

if systemctl --user is-active --quiet activity-tracker-api.service; then
    echo -e "API: ${GREEN}Rodando${NC}"
else
    echo -e "API: ${RED}Parada${NC}"
fi

if systemctl --user is-active --quiet activity-tracker-keyboard.service; then
    echo -e "Keyboard Monitor: ${GREEN}Rodando${NC}"
else
    echo -e "Keyboard Monitor: ${YELLOW}Parado (opcional)${NC}"
fi

echo ""
echo "URLs:"
echo "  Dashboard: http://localhost:5001"
echo "  Resumo IA: http://localhost:5001/summary.html"
echo ""

if ! systemctl --user is-active --quiet activity-tracker-agent.service; then
    echo -e "${YELLOW}💡 Para iniciar os serviços:${NC}"
    echo "   ~/activity-tracker/start.sh"
    echo ""
fi

echo "✅ Teste concluído!"
