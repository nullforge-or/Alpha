#!/bin/bash
# auto_backup.sh - 5 Minute Git Sync

while true; do
    echo "[*] Syncing state to Git at $(date)"
    git add .
    git commit -m "Auto-backup: Alpha state at $(date)"
    
    # Using a PAT (Personal Access Token) cached in the system
    git push origin main
    
    sleep 300
done