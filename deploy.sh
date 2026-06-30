#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0;3m' # No Color
BOLD='\033[1m'

echo -e "${GREEN}${BOLD}=== Telegram PostBot Server Installer ===${NC}"

# Check if run as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Error: This script must be run as root (sudo).${NC}"
  echo "Please run: sudo bash deploy.sh"
  exit 1
fi

# Detect absolute path of directory
APP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
echo -e "Application directory detected as: ${YELLOW}${APP_DIR}${NC}"

# Check if .env exists
if [ ! -f "${APP_DIR}/.env" ]; then
  echo -e "${YELLOW}Warning: .env file not found in ${APP_DIR}.${NC}"
  echo "Please create a .env file with your tokens before launching the service."
  echo "Creating a template .env file..."
  cat <<EOT > "${APP_DIR}/.env"
MAIN_BOT_TOKEN="YOUR_BOT_TOKEN"
DATABASE_PATH="db.db"
PASSWORD="ChooseYourPassword2026!"
EOT
  echo -e "${GREEN}Template .env created at ${APP_DIR}/.env. Please edit it later!${NC}"
fi

# Install system dependencies
echo -e "\n${YELLOW}1. Installing system dependencies (Python3, pip, venv)...${NC}"
apt update
apt install -y python3 python3-pip python3-venv

# Create virtual environment
echo -e "\n${YELLOW}2. Creating Python virtual environment...${NC}"
if [ -d "${APP_DIR}/venv" ]; then
  echo "Virtual environment already exists, skipping creation..."
else
  python3 -m venv "${APP_DIR}/venv"
fi

# Upgrade pip and install requirements
echo -e "\n${YELLOW}3. Installing project requirements...${NC}"
"${APP_DIR}/venv/bin/pip" install --upgrade pip
"${APP_DIR}/venv/bin/pip" install -r "${APP_DIR}/requirements.txt"

# Creating systemd service file
echo -e "\n${YELLOW}4. Configuring systemd service...${NC}"
SERVICE_FILE="/etc/systemd/system/postbot.service"

cat <<EOT > "$SERVICE_FILE"
[Unit]
Description=Telegram PostBot Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${APP_DIR}
ExecStart=${APP_DIR}/venv/bin/python ${APP_DIR}/bot.py
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=postbot

[Install]
WantedBy=multi-user.target
EOT

echo -e "Created systemd service at: ${YELLOW}${SERVICE_FILE}${NC}"

# Reload systemd, enable and start service
echo -e "\n${YELLOW}5. Starting the postbot service...${NC}"
systemctl daemon-reload
systemctl enable postbot.service

# If .env is still default template, warn the user and do not start yet
if grep -q "YOUR_BOT_TOKEN" "${APP_DIR}/.env"; then
  echo -e "${YELLOW}Notice: Default template token detected in .env.${NC}"
  echo -e "${YELLOW}Service enabled, but NOT started. Please edit ${APP_DIR}/.env first, then run:${NC}"
  echo -e "${BOLD}sudo systemctl start postbot.service${NC}"
else
  systemctl restart postbot.service
  echo -e "${GREEN}Service successfully started!${NC}"
fi

echo -e "\n${GREEN}${BOLD}=== Setup Completed Successfully! ===${NC}"
echo -e "How to manage the bot service:"
echo -e "  • Start:          ${BOLD}sudo systemctl start postbot.service${NC}"
echo -e "  • Stop:           ${BOLD}sudo systemctl stop postbot.service${NC}"
echo -e "  • Restart:        ${BOLD}sudo systemctl restart postbot.service${NC}"
echo -e "  • Check status:   ${BOLD}sudo systemctl status postbot.service${NC}"
echo -e "  • View live logs: ${BOLD}sudo journalctl -u postbot.service -f${NC}"
echo -e "\nRemember to upload your production database file ${YELLOW}db.db${NC} and edit your ${YELLOW}.env${NC} file if needed."
