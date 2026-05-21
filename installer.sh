#!/bin/bash
# installer.sh - Alpha Setup

echo "[*] Initializing Alpha Agent Environment..."

# 1. System Dependencies
echo "[*] Installing system packages..."
sudo apt-update -y && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git nodejs npm sqlite3 curl

# 2. Setup Python Backend (Agent Brain & Tools)
echo "[*] Setting up Python environment..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install --with-deps chromium  # For headless browsing
cd ..

# 3. Setup Next.js Frontend (Command Center)
echo "[*] Building secure frontend..."
cd frontend
npm install
npm run build
cd ..

# 4. Install Cloudflare Tunnel (cloudflared)
echo "[*] Installing Cloudflare daemon..."
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb

# 5. Launch Subsystems using PM2 (Node Process Manager) for stability
echo "[*] Booting subsystems..."
sudo npm install -g pm2
pm2 start "cd frontend && npm run start" --name "alpha-ui"
pm2 start "cd backend && source venv/bin/activate && python agent.py" --name "alpha-agent"
pm2 start "./auto_backup.sh" --name "alpha-sync"

# 6. Launch Tunnel (Replace with your specific tunnel token later)
# pm2 start "cloudflared tunnel run <YOUR_TUNNEL_TOKEN>" --name "alpha-tunnel"

pm2 save
echo "[+] Alpha Setup Complete. System is live and syncing."