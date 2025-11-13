#!/bin/bash
# test-installation.sh - Testa se a instalação está funcionando corretamente

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SUCCESS=0
FAILED=0

echo -e "${BLUE}╔════════════════════════════════════════╗"
echo -e "║  Activity Tracker - Teste de Sistema  ║"
echo -e "╚════════════════════════════════════════╝${NC}\n"

# Função para testar
test_check() {
    local name="$1"
    local command="$2"
    
    echo -n "  Testando $name... "
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ OK${NC}"
        ((SUCCESS++))
        return 0
    else
        echo -e "${RED}✗ FALHOU${NC}"
        ((FAILED++))
        return 1
    fi
}

echo -e "${YELLOW}[1/4] Verificando instalação de arquivos${NC}"
test_check "Diretório principal" "[ -d ~/activity-tracker ]"
test_check "Scripts do agente" "[ -f ~/activity-tracker/agent/agent.py ]"
test_check "API" "[ -f ~/activity-tracker/agent/api.py ]"
test_check "Extensão navegador" "[ -d ~/activity-tracker/browser-extension ]"
test_check "Ambiente Python" "[ -d ~/activity-tracker/venv ]"
echo ""

echo -e "${YELLOW}[2/4] Verificando dependências do sistema${NC}"
test_check "xdotool" "which xdotool"
test_check "xprintidle" "which xprintidle"
test_check "wmctrl" "which wmctrl"
test_check "Python 3" "which python3"
test_check "curl" "which curl"
echo ""

echo -e "${YELLOW}[3/4] Verificando serviços systemd${NC}"
test_check "Serviço agent (habilitado)" "systemctl --user is-enabled activity-tracker-agent"
test_check "Serviço API (habilitado)" "systemctl --user is-enabled activity-tracker-api"
test_check "Serviço agent (ativo)" "systemctl --user is-active activity-tracker-agent"
test_check "Serviço API (ativo)" "systemctl --user is-active activity-tracker-api"
echo ""

echo -e "${YELLOW}[4/4] Verificando funcionalidade${NC}"
test_check "API respondendo" "curl -s http://localhost:5001/api/health | grep -q ok"
test_check "Banco de dados existe" "[ -f ~/.config/activity-tracker/tracker.db ]"
test_check "Banco com eventos" "sqlite3 ~/.config/activity-tracker/tracker.db 'SELECT COUNT(*) FROM events' | grep -q '[0-9]'"
test_check "Hook do bash configurado" "grep -q 'activity-tracker' ~/.bashrc"
echo ""

# Resumo
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "  Testes executados: $((SUCCESS + FAILED))"
echo -e "  ${GREEN}Sucessos: $SUCCESS${NC}"
echo -e "  ${RED}Falhas: $FAILED${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ Sistema funcionando perfeitamente!${NC}"
    echo ""
    echo -e "${BLUE}Próximos passos:${NC}"
    echo -e "  1. Acesse: ${YELLOW}http://localhost:5001${NC}"
    echo -e "  2. Instale a extensão do navegador (veja BROWSER-EXTENSION-GUIDE.md)"
    echo -e "  3. Monitore os logs: ${YELLOW}journalctl --user -u activity-tracker-* -f${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Alguns testes falharam. Veja os erros acima.${NC}"
    echo ""
    echo -e "${BLUE}Comandos úteis para debug:${NC}"
    echo -e "  • Ver status: ${YELLOW}systemctl --user status activity-tracker-*${NC}"
    echo -e "  • Ver logs: ${YELLOW}journalctl --user -u activity-tracker-agent -n 50${NC}"
    echo -e "  • Reiniciar: ${YELLOW}systemctl --user restart activity-tracker-*${NC}"
    echo ""
    exit 1
fi
