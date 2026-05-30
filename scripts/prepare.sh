#!/usr/bin/env bash
# prepare.sh – Einmaliges Setup mit Internetzugang (zuhause / vor dem Event)
# Läuft auf dem Raspberry Pi nach dem ersten `git clone`.
# Erfordert Internet für pip. Kann gefahrlos mehrfach ausgeführt werden.
# Voraussetzung: apt-Pakete wurden laut docs/einrichtung.md manuell installiert.
set -euo pipefail

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_NAME="fischverkauf"
VENV_DIR="$INSTALL_DIR/.venv"
PI_USER="${SUDO_USER:-pi}"

# WLAN-Hotspot-Einstellungen – hier anpassen falls gewünscht
HOTSPOT_SSID="Anglerverein"
HOTSPOT_PASSWORD="Fischerfest2025"

echo "=== Fischerfest Kassensystem – Vorbereitung ==="
echo "Verzeichnis: $INSTALL_DIR"
echo ""

cd "$INSTALL_DIR"

# Hostname setzen (ermöglicht ssh pi@fischerfest.local)
echo "[1/7] Hostname setzen..."
CURRENT_HOSTNAME=$(hostname)
if [ "$CURRENT_HOSTNAME" != "fischerfest" ]; then
    sudo hostnamectl set-hostname fischerfest
    # /etc/hosts aktualisieren damit localhost-Auflösung nicht bricht
    sudo sed -i "s/\b$CURRENT_HOSTNAME\b/fischerfest/g" /etc/hosts
    echo "      Hostname geändert: $CURRENT_HOSTNAME → fischerfest"
    echo "      Erreichbar nach Neustart als: ssh pi@fischerfest.local"
else
    echo "      Hostname bereits 'fischerfest' – keine Änderung."
fi

# Drucker-Berechtigung setzen (Gruppe lp)
echo "[2/7] Drucker-Berechtigung prüfen..."
if id -nG "$PI_USER" | grep -qw lp; then
    echo "      $PI_USER ist bereits in Gruppe 'lp'."
else
    sudo usermod -a -G lp "$PI_USER"
    echo "      $PI_USER zur Gruppe 'lp' hinzugefügt."
    echo "      HINWEIS: Einmal aus- und wieder einloggen (oder neu starten),"
    echo "      damit die Drucker-Berechtigung wirksam wird."
fi

# Virtuelle Umgebung anlegen und Abhängigkeiten installieren (braucht Internet)
echo "[3/7] Virtuelle Umgebung und Abhängigkeiten..."
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet .
echo "      OK"

# Datenverzeichnis anlegen
echo "[4/7] Datenverzeichnis anlegen..."
mkdir -p "$INSTALL_DIR/data"
echo "      OK"

# .env anlegen falls nicht vorhanden
echo "[5/7] Konfiguration prüfen..."
if [ ! -f "$INSTALL_DIR/.env" ]; then
    cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
    echo "      .env aus Vorlage erstellt."
    echo ""
    echo "  WICHTIG: Bitte jetzt $INSTALL_DIR/.env öffnen und"
    echo "  VEREINSNAME, EVENT_JAHR und PRINTER_DEVICE prüfen."
    echo ""
else
    echo "      .env bereits vorhanden – keine Änderung."
fi

# WLAN-Hotspot einrichten (wird beim Booten automatisch aktiviert)
echo "[6/7] WLAN-Hotspot einrichten..."
if nmcli connection show Hotspot &>/dev/null; then
    echo "      Hotspot bereits konfiguriert – übersprungen."
    echo "      SSID: $(nmcli -g 802-11-wireless.ssid connection show Hotspot)"
else
    sudo nmcli device wifi hotspot \
        ifname wlan0 \
        ssid "$HOTSPOT_SSID" \
        password "$HOTSPOT_PASSWORD" \
        band bg
    sudo nmcli connection modify Hotspot \
        connection.autoconnect yes \
        connection.autoconnect-priority 100
    echo "      Hotspot erstellt: SSID=$HOTSPOT_SSID"
fi

# systemd-Service installieren und für Auto-Start aktivieren
echo "[7/7] systemd-Service installieren..."
sudo cp "$INSTALL_DIR/systemd/$SERVICE_NAME.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
echo "      Service aktiviert (startet beim nächsten Booten automatisch)."

echo ""
echo "=== Vorbereitung abgeschlossen ==="
echo ""
echo "Nächste Schritte:"
echo "  1. .env prüfen und ggf. anpassen"
echo "  2. Pi einmal neu starten (Hostname + Drucker-Gruppe wirksam)"
echo "  3. CSV-Datei mit Bestellungen bereitstellen"
echo "  4. Am Eventtag: scripts/event.sh ausführen"
