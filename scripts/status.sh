#!/usr/bin/env bash
# status.sh – Systemstatus am Eventtag prüfen (offline, kein Internet nötig)
set -euo pipefail

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_NAME="vorbestellungs-kasse"
PORT=8000

echo "=== Vorbestellungs-Kasse – Systemstatus ==="
echo ""

# Kassensystem
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "  Kassensystem:  läuft"
else
    echo "  Kassensystem:  GESTOPPT – starten mit: sudo systemctl start $SERVICE_NAME"
fi

# WLAN-Hotspot
HOTSPOT_SSID=$(nmcli -g 802-11-wireless.ssid connection show Hotspot 2>/dev/null || echo "nicht konfiguriert")
HOTSPOT_STATE=$(nmcli -g GENERAL.STATE connection show --active Hotspot 2>/dev/null || true)
if [ -n "$HOTSPOT_STATE" ]; then
    echo "  WLAN-Hotspot:  aktiv  (SSID: $HOTSPOT_SSID)"
else
    echo "  WLAN-Hotspot:  INAKTIV – starten mit: sudo nmcli connection up Hotspot"
fi

# Drucker
PRINTER_DEVICE=$(grep -E '^PRINTER_DEVICE=' "$INSTALL_DIR/.env" 2>/dev/null \
    | cut -d'=' -f2 | tr -d '"' | tr -d "'" || echo "/dev/usb/lp0")
PRINTER_DEVICE="${PRINTER_DEVICE:-/dev/usb/lp0}"
if [ -e "$PRINTER_DEVICE" ]; then
    echo "  Drucker:       gefunden ($PRINTER_DEVICE)"
else
    echo "  Drucker:       nicht gefunden – Kabel prüfen, dann Seite neu laden"
fi

# URL – Hotspot-IP bevorzugen, Fallback auf primäre Netzwerkadresse
HOTSPOT_IP=$(nmcli -g IP4.ADDRESS connection show --active Hotspot 2>/dev/null | cut -d'/' -f1 || true)
IP="${HOTSPOT_IP:-$(hostname -I 2>/dev/null | awk '{print $1}')}"
echo ""
echo "  Kassenoberfläche: http://${IP}:${PORT}"
echo ""
