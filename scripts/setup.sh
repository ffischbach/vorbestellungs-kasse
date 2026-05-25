#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_NAME="fischverkauf"
VENV_DIR="$INSTALL_DIR/.venv"

echo "=== Fischerfest Kassensystem – Setup ==="
echo "Verzeichnis: $INSTALL_DIR"

cd "$INSTALL_DIR"

# Virtuelle Umgebung anlegen und Abhängigkeiten installieren
echo "Erstelle virtuelle Umgebung..."
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet .

# Datenverzeichnis anlegen
mkdir -p "$INSTALL_DIR/data"

# .env anlegen falls nicht vorhanden
if [ ! -f "$INSTALL_DIR/.env" ]; then
    cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
    echo "Hinweis: .env aus Vorlage erstellt – bitte vor dem Event prüfen."
fi

# systemd-Service installieren und aktivieren
echo "Installiere systemd-Service..."
sudo cp "$INSTALL_DIR/systemd/$SERVICE_NAME.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo ""
echo "=== Setup abgeschlossen ==="
echo "Kassensystem erreichbar unter: http://$(hostname -I | awk '{print $1}'):8000"
