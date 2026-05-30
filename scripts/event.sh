#!/usr/bin/env bash
# event.sh – Start am Eventtag (offline, kein Internet nötig)
# Prüft den System-Zustand und startet den Service.
# Läuft in unter 1 Minute durch.
set -euo pipefail

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_NAME="fischverkauf"
VENV_DIR="$INSTALL_DIR/.venv"
PORT=8000

echo "=== Fischerfest Kassensystem – Eventstart ==="
echo ""

cd "$INSTALL_DIR"

# Voraussetzungen prüfen
ERRORS=0

echo "[1/5] Voraussetzungen prüfen..."

if [ ! -d "$VENV_DIR" ]; then
    echo "  FEHLER: Virtuelle Umgebung fehlt – bitte zuerst scripts/prepare.sh ausführen."
    ERRORS=$((ERRORS + 1))
fi

if [ ! -f "$INSTALL_DIR/.env" ]; then
    echo "  FEHLER: .env fehlt – bitte zuerst scripts/prepare.sh ausführen."
    ERRORS=$((ERRORS + 1))
fi

if [ ! -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
    echo "  FEHLER: systemd-Service nicht installiert – bitte zuerst scripts/prepare.sh ausführen."
    ERRORS=$((ERRORS + 1))
fi

if [ "$ERRORS" -gt 0 ]; then
    echo ""
    echo "Abbruch: Bitte zuerst scripts/prepare.sh ausführen (mit Internetzugang)."
    exit 1
fi

echo "      OK"

# Datenverzeichnis sicherstellen
echo "[2/5] Datenverzeichnis prüfen..."
mkdir -p "$INSTALL_DIR/data"
echo "      OK"

# WLAN-Hotspot prüfen und ggf. aktivieren
echo "[3/5] WLAN-Hotspot prüfen..."
if ! nmcli connection show Hotspot &>/dev/null; then
    echo "  FEHLER: Hotspot nicht konfiguriert – bitte zuerst scripts/prepare.sh ausführen."
    exit 1
fi

HOTSPOT_STATE=$(nmcli -g GENERAL.STATE connection show --active Hotspot 2>/dev/null || true)
if [ -z "$HOTSPOT_STATE" ]; then
    echo "      Hotspot nicht aktiv – wird gestartet..."
    sudo nmcli connection up Hotspot
    sleep 2
fi

HOTSPOT_SSID=$(nmcli -g 802-11-wireless.ssid connection show Hotspot 2>/dev/null || echo "unbekannt")
echo "      Aktiv. SSID: $HOTSPOT_SSID"

# Service starten / neu starten
echo "[4/5] Kassensystem starten..."
sudo systemctl restart "$SERVICE_NAME"

# Kurz warten und Status prüfen
sleep 2
if ! systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "  FEHLER: Service konnte nicht gestartet werden."
    echo "  Logs: sudo journalctl -u $SERVICE_NAME -n 30"
    exit 1
fi
echo "      Läuft."

# Drucker prüfen (nicht-blockierend – Warnung, kein Abbruch)
echo "[5/5] Drucker prüfen..."
PRINTER_DEVICE=$(grep -E '^PRINTER_DEVICE=' "$INSTALL_DIR/.env" 2>/dev/null \
    | cut -d'=' -f2 | tr -d '"' | tr -d "'" || echo "/dev/usb/lp0")
PRINTER_DEVICE="${PRINTER_DEVICE:-/dev/usb/lp0}"

if [ -e "$PRINTER_DEVICE" ]; then
    echo "      Drucker gefunden: $PRINTER_DEVICE"
else
    echo "      WARNUNG: Drucker nicht gefunden unter $PRINTER_DEVICE"
    echo "      Drucker jetzt einstecken und einschalten, dann Seite neu laden."
fi

# Ergebnis
IP=$(hostname -I 2>/dev/null | awk '{print $1}')
echo ""
echo "=== System bereit ==="
echo ""
echo "  WLAN:         $HOTSPOT_SSID  (Passwort: im Vorbereitungs-Protokoll)"
echo "  Kassensystem: http://${IP}:${PORT}"
echo "  Tablets mit dem WLAN verbinden und diese Adresse im Browser öffnen."
echo ""
echo "  Logs live:    sudo journalctl -u $SERVICE_NAME -f"
echo "  Stoppen:      sudo systemctl stop $SERVICE_NAME"
