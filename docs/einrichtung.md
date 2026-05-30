# Einrichtungsanleitung – Raspberry Pi

Einmalige Schritte zur Ersteinrichtung des Kassensystems auf dem Raspberry Pi.
Danach reicht jedes Jahr `git pull && bash scripts/prepare.sh` + Neustart.

---

## Voraussetzungen

- Raspberry Pi 4 Model B mit Netzteil
- Micro-SD-Karte (mind. 16 GB)
- Laptop mit SD-Kartenleser und Internetzugang
- Raspberry Pi Imager ([raspberrypi.com/software](https://www.raspberrypi.com/software/))

---

## Schritt 1 – SD-Karte flashen

1. Raspberry Pi Imager öffnen
2. **Gerät:** Raspberry Pi 4
3. **Betriebssystem:** Raspberry Pi OS Lite (64-bit) – kein Desktop nötig
4. **Speichermedium:** deine SD-Karte
5. Vor dem Schreiben das **Zahnrad-Icon** (erweiterte Einstellungen) öffnen und
   folgendes konfigurieren:

   | Einstellung | Wert |
   |---|---|
   | Hostname | `fischerfest` |
   | SSH aktivieren | Ja (Passwort-Authentifizierung) |
   | Benutzername | `pi` |
   | Passwort | _(sicheres Passwort wählen und notieren)_ |
   | WLAN konfigurieren | Heimnetz eintragen (für die Ersteinrichtung) |
   | Zeitzone | `Europe/Berlin` |

6. Karte schreiben, in den Pi einlegen, Pi einschalten

---

## Schritt 2 – Per SSH verbinden

Pi ca. 60 Sekunden booten lassen, dann:

```bash
ssh pi@fischerfest.local
```

Falls `fischerfest.local` nicht auflöst (kommt vor bei manchen Routern):

```bash
# IP-Adresse im Router-Interface nachschauen, dann:
ssh pi@<IP-Adresse>
```

---

## Schritt 3 – System aktualisieren

```bash
sudo apt update && sudo apt upgrade -y
```

Dauert beim ersten Mal 5–15 Minuten. Nur einmalig nötig.

---

## Schritt 4 – Repository klonen

```bash
git clone https://github.com/ASG-Ettlingen/fischverkauf.git ~/fischverkauf
cd ~/fischverkauf
```

---

## Schritt 5 – Vorbereitung ausführen

```bash
bash scripts/prepare.sh
```

Das Script erledigt automatisch:
- Systempakete installieren (`python3-venv`, `git`, `libusb-1.0-0-dev`)
- Hostname auf `fischerfest` setzen
- Benutzer `pi` zur Drucker-Gruppe `lp` hinzufügen
- Virtuelle Python-Umgebung anlegen und App-Abhängigkeiten installieren
- `.env` aus Vorlage erstellen
- WLAN-Hotspot einrichten (`Anglerverein` / `Fischerfest2025`)
- systemd-Service installieren und für Auto-Start aktivieren

---

## Schritt 6 – Konfiguration anpassen

```bash
nano ~/fischverkauf/.env
```

Mindestens prüfen:

| Variable | Bedeutung |
|---|---|
| `VEREINSNAME` | Erscheint auf dem Bon |
| `EVENT_JAHR` | Erscheint auf dem Bon |
| `PRINTER_DEVICE` | USB-Pfad des Druckers (Standard `/dev/usb/lp0`) |

---

## Schritt 7 – Neustart

```bash
sudo reboot
```

Nach dem Neustart:
- Hostname und Drucker-Gruppe sind aktiv
- WLAN-Hotspot startet automatisch
- Kassensystem startet automatisch

Verbindung wiederherstellen:

```bash
ssh pi@fischerfest.local
```

---

## Schritt 8 – Funktion prüfen

```bash
# Service läuft?
systemctl status fischverkauf

# Hotspot aktiv?
nmcli connection show Hotspot

# Logs (live)
sudo journalctl -u fischverkauf -f
```

Im Browser: `http://fischerfest.local:8000` – die Kassenoberfläche sollte
erscheinen (noch ohne Bestellungen).

---

## Jährliche Aktualisierung

```bash
cd ~/fischverkauf
git pull
bash scripts/prepare.sh
sudo reboot
```

---

## CSV importieren (vor jedem Event)

Bestellungen aus WooCommerce exportieren und auf den Pi übertragen:

```bash
# Von deinem Laptop aus:
scp bestellungen.csv pi@fischerfest.local:~/fischverkauf/data/

# Auf dem Pi importieren:
curl -X POST http://localhost:8000/admin/import \
  -F "file=@data/bestellungen.csv"
```

Oder über die Admin-Oberfläche im Browser unter `/admin`.
