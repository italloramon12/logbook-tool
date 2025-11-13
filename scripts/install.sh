#!/bin/bash
# install.sh - Activity Tracker Installation Script
set -e

echo "=================================="
echo "Activity Tracker - Instalação"
echo "=================================="
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verifica se está no Ubuntu
if [ ! -f /etc/os-release ]; then
    echo -e "${RED}❌ Este script foi desenvolvido para Ubuntu/Debian${NC}"
    exit 1
fi

# Diretório de instalação
INSTALL_DIR="$HOME/activity-tracker"
CONFIG_DIR="$HOME/.activity_tracker"

echo -e "${GREEN}📁 Diretório de instalação: $INSTALL_DIR${NC}"
echo ""

# 1. Instalar dependências do sistema
echo -e "${YELLOW}[1/7]${NC} Instalando dependências do sistema..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip xdotool xprintidle wmctrl curl

# 2. Criar diretórios
echo -e "${YELLOW}[2/7]${NC} Criando diretórios..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"

# 3. Copiar arquivos
echo -e "${YELLOW}[3/7]${NC} Copiando arquivos..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cp -r "$PROJECT_DIR/agent" "$INSTALL_DIR/"
cp -r "$PROJECT_DIR/browser-extension" "$INSTALL_DIR/"
cp -r "$PROJECT_DIR/scripts" "$INSTALL_DIR/"
cp "$PROJECT_DIR/requirements.txt" "$INSTALL_DIR/"

# 4. Criar ambiente virtual Python
echo -e "${YELLOW}[4/7]${NC} Configurando ambiente Python..."
cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. Configurar serviço systemd
echo -e "${YELLOW}[5/7]${NC} Configurando serviço systemd..."

# Cria o arquivo de serviço do agente
cat > "$INSTALL_DIR/activity-tracker-agent.service" << EOF
[Unit]
Description=Activity Tracker Agent
After=graphical.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR/agent
Environment=DISPLAY=:0
Environment=XAUTHORITY=$HOME/.Xauthority
ExecStart=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/agent/agent.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
EOF

# Cria o arquivo de serviço da API
cat > "$INSTALL_DIR/activity-tracker-api.service" << EOF
[Unit]
Description=Activity Tracker API
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR/agent
ExecStart=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/agent/api.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
EOF

# Copia para systemd user
mkdir -p "$HOME/.config/systemd/user"
cp "$INSTALL_DIR/activity-tracker-agent.service" "$HOME/.config/systemd/user/"
cp "$INSTALL_DIR/activity-tracker-api.service" "$HOME/.config/systemd/user/"

# Recarrega systemd
systemctl --user daemon-reload

# 6. Configurar shell hook
echo -e "${YELLOW}[6/7]${NC} Configurando hook do shell..."

# Detecta shell
SHELL_RC=""
if [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
else
    SHELL_RC="$HOME/.bashrc"
fi

# Adiciona source ao shell config se ainda não existir
if ! grep -q "activity-tracker/scripts/log_command.sh" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# Activity Tracker shell hook" >> "$SHELL_RC"
    echo "source $INSTALL_DIR/scripts/log_command.sh" >> "$SHELL_RC"
    echo -e "${GREEN}✓ Hook adicionado ao $SHELL_RC${NC}"
else
    echo -e "${GREEN}✓ Hook já existe em $SHELL_RC${NC}"
fi

# 7. Criar scripts de controle
echo -e "${YELLOW}[7/7]${NC} Criando scripts de controle..."

# Script de start
cat > "$INSTALL_DIR/start.sh" << 'EOF'
#!/bin/bash
echo "🚀 Iniciando Activity Tracker..."
systemctl --user start activity-tracker-agent.service
systemctl --user start activity-tracker-api.service
echo "✓ Serviços iniciados"
echo "📊 Dashboard: http://localhost:5001"
EOF
chmod +x "$INSTALL_DIR/start.sh"

# Script de stop
cat > "$INSTALL_DIR/stop.sh" << 'EOF'
#!/bin/bash
echo "🛑 Parando Activity Tracker..."
systemctl --user stop activity-tracker-agent.service
systemctl --user stop activity-tracker-api.service
echo "✓ Serviços parados"
EOF
chmod +x "$INSTALL_DIR/stop.sh"

# Script de status
cat > "$INSTALL_DIR/status.sh" << 'EOF'
#!/bin/bash
echo "📊 Status do Activity Tracker:"
echo ""
echo "Agent:"
systemctl --user status activity-tracker-agent.service --no-pager | head -n 3
echo ""
echo "API:"
systemctl --user status activity-tracker-api.service --no-pager | head -n 3
EOF
chmod +x "$INSTALL_DIR/status.sh"

# Script de logs
cat > "$INSTALL_DIR/logs.sh" << 'EOF'
#!/bin/bash
if [ "$1" == "agent" ]; then
    journalctl --user -u activity-tracker-agent.service -f
elif [ "$1" == "api" ]; then
    journalctl --user -u activity-tracker-api.service -f
else
    echo "Logs disponíveis em:"
    echo "  - Agent: $HOME/.activity_tracker/agent.log"
    echo "  - Systemd Agent: journalctl --user -u activity-tracker-agent.service -f"
    echo "  - Systemd API: journalctl --user -u activity-tracker-api.service -f"
fi
EOF
chmod +x "$INSTALL_DIR/logs.sh"

echo ""
echo -e "${GREEN}=================================="
echo "✅ Instalação Concluída!"
echo -e "==================================${NC}"
echo ""
echo "📝 Próximos passos:"
echo ""
echo "1. Ativar serviços no login:"
echo "   systemctl --user enable activity-tracker-agent.service"
echo "   systemctl --user enable activity-tracker-api.service"
echo ""
echo "2. Iniciar agora:"
echo "   $INSTALL_DIR/start.sh"
echo ""
echo "3. Ver status:"
echo "   $INSTALL_DIR/status.sh"
echo ""
echo "4. Acessar dashboard:"
echo "   http://localhost:5001"
echo ""
echo "5. Instalar extensão do navegador:"
echo "   - Firefox: about:debugging > This Firefox > Load Temporary Add-on"
echo "   - Chrome: chrome://extensions > Developer mode > Load unpacked"
echo "   - Pasta: $INSTALL_DIR/browser-extension"
echo ""
echo "6. Reiniciar terminal para ativar hook de comandos"
echo ""
echo -e "${YELLOW}📁 Arquivos de configuração: $CONFIG_DIR${NC}"
echo -e "${YELLOW}📊 Banco de dados: $CONFIG_DIR/activity.db${NC}"
echo ""
