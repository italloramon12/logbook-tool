#!/bin/bash
# install-simple.sh - Instalação Simplificada do Activity Tracker
set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

clear
echo -e "${GREEN}"
echo "╔════════════════════════════════════════╗"
echo "║   Activity Tracker - Instalação       ║"
echo "║   Sistema de Monitoramento Ubuntu     ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# Diretórios
INSTALL_DIR="$HOME/activity-tracker"
CONFIG_DIR="$HOME/.config/activity-tracker"

echo -e "${BLUE}📁 Instalando em: ${INSTALL_DIR}${NC}\n"

# 1. Verificar dependências
echo -e "${YELLOW}[1/6]${NC} Verificando sistema..."
if [ ! -f /etc/os-release ]; then
    echo -e "${RED}❌ Sistema não suportado. Requer Ubuntu/Debian${NC}"
    exit 1
fi

# 2. Instalar dependências
echo -e "${YELLOW}[2/6]${NC} Instalando dependências..."
sudo apt update -qq
sudo apt install -y python3 python3-venv python3-pip xdotool xprintidle wmctrl curl > /dev/null 2>&1
echo -e "${GREEN}   ✓ Dependências instaladas${NC}"

# 3. Criar estrutura de diretórios
echo -e "${YELLOW}[3/6]${NC} Criando estrutura..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"

# Copiar arquivos do projeto atual
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cp -r "$PROJECT_DIR/agent" "$INSTALL_DIR/" 2>/dev/null || true
cp -r "$PROJECT_DIR/browser-extension" "$INSTALL_DIR/" 2>/dev/null || true
cp "$PROJECT_DIR/requirements.txt" "$INSTALL_DIR/" 2>/dev/null || true

echo -e "${GREEN}   ✓ Estrutura criada${NC}"

# 4. Configurar ambiente Python
echo -e "${YELLOW}[4/6]${NC} Configurando Python..."
cd "$INSTALL_DIR"
python3 -m venv venv > /dev/null 2>&1
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}   ✓ Ambiente Python configurado${NC}"

# 5. Configurar hook do terminal
echo -e "${YELLOW}[5/6]${NC} Configurando monitoramento de terminal..."

# Script de log de comandos
cat > "$INSTALL_DIR/log_command.sh" << 'LOGEOF'
#!/bin/bash
if [ -n "$BASH_COMMAND" ] && [ "$BASH_COMMAND" != "$PROMPT_COMMAND" ]; then
    curl -s -X POST http://localhost:5001/api/log_event \
         -H "Content-Type: application/json" \
         -d "{\"ts\":$(date +%s),\"type\":\"terminal\",\"title\":\"bash\",\"detail\":\"$BASH_COMMAND\",\"duration\":0}" \
         > /dev/null 2>&1 || true
fi
LOGEOF

chmod +x "$INSTALL_DIR/log_command.sh"

# Adicionar ao bashrc se não existir
if ! grep -q "activity-tracker/log_command.sh" "$HOME/.bashrc"; then
    cat >> "$HOME/.bashrc" << 'BASHEOF'

# Activity Tracker - Monitoramento de comandos
if [ -f "$HOME/activity-tracker/log_command.sh" ]; then
    trap 'bash "$HOME/activity-tracker/log_command.sh"' DEBUG
fi
BASHEOF
    echo -e "${GREEN}   ✓ Hook do terminal configurado${NC}"
else
    echo -e "${GREEN}   ✓ Hook do terminal já configurado${NC}"
fi

# 6. Configurar serviços systemd
echo -e "${YELLOW}[6/6]${NC} Configurando serviços..."

mkdir -p "$HOME/.config/systemd/user"

# Serviço do Agente
cat > "$HOME/.config/systemd/user/activity-tracker-agent.service" << EOF
[Unit]
Description=Activity Tracker Agent
After=graphical.target

[Service]
Type=simple
WorkingDirectory=$INSTALL_DIR/agent
Environment=DISPLAY=:0
Environment=XAUTHORITY=$HOME/.Xauthority
ExecStart=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/agent/agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

# Serviço da API
cat > "$HOME/.config/systemd/user/activity-tracker-api.service" << EOF
[Unit]
Description=Activity Tracker API
After=network.target

[Service]
Type=simple
WorkingDirectory=$INSTALL_DIR/agent
ExecStart=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/agent/api.py
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

# Recarregar systemd e iniciar serviços
systemctl --user daemon-reload
systemctl --user enable activity-tracker-agent.service activity-tracker-api.service
systemctl --user start activity-tracker-agent.service activity-tracker-api.service

echo -e "${GREEN}   ✓ Serviços configurados e iniciados${NC}"

# Resumo final
echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗"
echo -e "║  ✓ Instalação Concluída com Sucesso!  ║"
echo -e "╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📊 Próximos passos:${NC}"
echo ""
echo -e "  1. ${YELLOW}Verificar serviços:${NC}"
echo -e "     systemctl --user status activity-tracker-*"
echo ""
echo -e "  2. ${YELLOW}Acessar interface web:${NC}"
echo -e "     http://localhost:5001"
echo ""
echo -e "  3. ${YELLOW}Instalar extensão do navegador:${NC}"
echo -e "     Chrome/Edge: chrome://extensions (Ativar modo desenvolvedor)"
echo -e "     Firefox: about:debugging#/runtime/this-firefox"
echo -e "     Carregar: ${INSTALL_DIR}/browser-extension"
echo ""
echo -e "  4. ${YELLOW}Logs do sistema:${NC}"
echo -e "     journalctl --user -u activity-tracker-agent -f"
echo -e "     journalctl --user -u activity-tracker-api -f"
echo ""
echo -e "${GREEN}💡 O monitoramento já está ativo!${NC}"
echo -e "${BLUE}   Banco de dados: ~/.config/activity-tracker/tracker.db${NC}"
echo ""
