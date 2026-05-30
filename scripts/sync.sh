#!/usr/bin/env bash
# sync.sh – Lokale Änderungen auf den Raspberry Pi übertragen (Entwicklung)
# Verwendung:  bash scripts/sync.sh [pi@fischerfest.local]
set -euo pipefail

REMOTE="${1:-fischerfest}"
REMOTE_DIR="~/asg-ettlingen-cashier"

echo "→ Sync nach $REMOTE:$REMOTE_DIR ..."

rsync -az --delete \
    --exclude='.venv/' \
    --exclude='data/' \
    --exclude='.git/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.env' \
    "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/" \
    "$REMOTE:$REMOTE_DIR"

echo "→ Service neu starten..."
ssh "$REMOTE" 'sudo systemctl restart fischverkauf && sleep 1 && systemctl is-active fischverkauf'

echo "OK"
