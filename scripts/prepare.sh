#!/usr/bin/env bash
# prepare.sh – Einmaliges Setup mit Internetzugang (zuhause / vor dem Event)
# Läuft auf dem Raspberry Pi nach dem ersten `git clone`.
# Erfordert Internet für pip. Kann gefahrlos mehrfach ausgeführt werden.
# Voraussetzung: apt-Pakete wurden laut docs/einrichtung.md manuell installiert.
set -euo pipefail

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_NAME="vorbestellungs-kasse"
VENV_DIR="$INSTALL_DIR/.venv"
PI_USER="${SUDO_USER:-pi}"

# Helper: einzelnen Wert aus .env lesen
_env_val() {
    grep -E "^$1=" "$INSTALL_DIR/.env" 2>/dev/null | cut -d'=' -f2- | tr -d '"' | tr -d "'"
}

echo "=== Vorbestellungs-Kasse – Vorbereitung ==="
echo "Verzeichnis: $INSTALL_DIR"
echo ""

cd "$INSTALL_DIR"

# .env anlegen bevor andere Schritte daraus lesen
echo "[0/7] Konfigurationsdatei prüfen..."
if [ ! -f "$INSTALL_DIR/.env" ]; then
    cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
    echo "      .env aus Vorlage erstellt."
    echo ""
    echo "  WICHTIG: $INSTALL_DIR/.env öffnen und mindestens diese Werte anpassen:"
    echo "    PI_HOSTNAME   – Netzwerkname des Raspberry Pi (z.B. 'meinverein-kasse')"
    echo "    HOTSPOT_SSID  – WLAN-Name des Hotspots"
    echo "    HOTSPOT_PASSWORD – WLAN-Passwort"
    echo "    VEREINSNAME, EVENT_NAME, EVENT_JAHR"
    echo ""
    echo "  Danach prepare.sh erneut ausführen."
    echo ""
else
    echo "      .env vorhanden."
fi

# Infra-Einstellungen aus .env lesen (mit Fallbacks)
PI_HOSTNAME="$(_env_val PI_HOSTNAME)"; PI_HOSTNAME="${PI_HOSTNAME:-kasse}"
HOTSPOT_SSID="$(_env_val HOTSPOT_SSID)"; HOTSPOT_SSID="${HOTSPOT_SSID:-MeinVerein}"
HOTSPOT_PASSWORD="$(_env_val HOTSPOT_PASSWORD)"; HOTSPOT_PASSWORD="${HOTSPOT_PASSWORD:-MeinPasswort}"

# Hostname setzen (ermöglicht z.B. ssh pi@kasse.local)
echo "[1/7] Hostname setzen..."
CURRENT_HOSTNAME=$(hostname)
if [ "$CURRENT_HOSTNAME" != "$PI_HOSTNAME" ]; then
    sudo hostnamectl set-hostname "$PI_HOSTNAME"
    sudo sed -i "s/\b$CURRENT_HOSTNAME\b/$PI_HOSTNAME/g" /etc/hosts
    echo "      Hostname geändert: $CURRENT_HOSTNAME → $PI_HOSTNAME"
    echo "      Erreichbar nach Neustart als: ssh pi@${PI_HOSTNAME}.local"
else
    echo "      Hostname bereits '$PI_HOSTNAME' – keine Änderung."
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

# Aktuelle Konfiguration anzeigen
echo "[5/7] Konfiguration..."
echo "      PI_HOSTNAME   = $PI_HOSTNAME"
echo "      HOTSPOT_SSID  = $HOTSPOT_SSID"
echo "      EVENT_NAME    = $(_env_val EVENT_NAME)"
echo "      VEREINSNAME   = $(_env_val VEREINSNAME)"
echo "      Zum Ändern: $INSTALL_DIR/.env bearbeiten, dann prepare.sh erneut ausführen."

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
sudo sed "s|/home/pi/vorbestellungs-kasse|$INSTALL_DIR|g" \
    "$INSTALL_DIR/systemd/$SERVICE_NAME.service" \
    | sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
echo "      Service aktiviert (startet beim nächsten Booten automatisch)."
echo "      Installationsverzeichnis: $INSTALL_DIR"

echo ""
echo "=== Vorbereitung abgeschlossen ==="
echo ""
echo "Nächste Schritte:"
echo "  1. .env prüfen und ggf. anpassen"
echo "  2. Pi einmal neu starten (Hostname + Drucker-Gruppe wirksam)"
echo "  3. CSV-Datei mit Bestellungen bereitstellen"
echo "  4. Am Eventtag: scripts/event.sh ausführen"
