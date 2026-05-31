# Troubleshooting

---

## App antwortet nicht

Browser zeigt keine Seite oder „Verbindung abgelehnt".

```bash
# Status prüfen
sudo systemctl status vorbestellungs-kasse

# Service starten falls gestoppt
sudo systemctl start vorbestellungs-kasse

# Logs live lesen
sudo journalctl -u vorbestellungs-kasse -f
```

Danach Browser-Seite neu laden.

---

## WLAN-Hotspot nicht sichtbar

Das Netz erscheint nicht auf den Tablets.

```bash
# Gesamtstatus inkl. Hotspot prüfen
bash scripts/status.sh

# Hotspot manuell starten
sudo nmcli connection up Hotspot
```

---

## Drucker nicht erkannt

Die App zeigt **«Drucker nicht verbunden»**.

1. Ist der Wert PRINTER_ENABLED in der .env Datei auf "true" gesetzt?
2. USB-Kabel prüfen (sicher eingesteckt, Drucker eingeschaltet?)
3. Drucker kurz aus- und wieder einschalten
4. Gerät prüfen:
   ```bash
   ls /dev/usb/
   ```
   Wenn `/dev/usb/lp0` fehlt: Pi neu starten, dann Seite neu laden.

Der Druckerfehler blockiert die Zahlung nicht — die App zeigt den Fehler an
und markiert die Bestellung trotzdem als bezahlt.

---

## Tablet findet `kasse.local` nicht

WLAN verbunden, aber `http://kasse.local:8000` lädt nicht.

`*.local`-Adressen funktionieren auf manchen Android-Geräten nicht. Lösung hierfür ist:
die IP-Adresse zu verwenden:

```bash
bash scripts/status.sh
# Zeigt am Ende: Kassenoberfläche: http://192.168.x.x:8000
```

Diese IP in den Tablets im Browser eingeben.
