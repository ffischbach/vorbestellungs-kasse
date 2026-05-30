# vorbestellungs-kasse

Offline-Kassensystem für Vorbestellungen an Vereins- oder Gemeinde-Events.
Kunden bestellen vorab online, holen am Eventtag ab und zahlen bar.

Läuft auf einem Raspberry Pi mit eigenem WLAN-Hotspot. Es ist kein Internet vor Ort nötig! 
Mitarbeiter suchen Bestellungen per Handy oder Tablet, bestätigen die Abholung mit einem klick, und der Bon wird gedruckt.

---

## Features

- Echtzeit-Suche nach Name, E-Mail oder Bestellnummer (Teilstrings)
- Automatischer Bondruck per ESC/POS (Epson TM-T20III)
- Live-Sync aller Tablets über Server-Sent Events – kein Reload nötig
- CSV-Import aus WooCommerce, Shopify, Pretix, Eventbrite und mehr
- Kassenzettel mit Wechselgeldberechnung und Schnellbetragsauswahl
- Vollständig offline – eigener WLAN-Hotspot

---

## Hardware

| Gerät | Rolle |
|---|---|
| Raspberry Pi 4 Model B | Server, Hotspot, Druckserver |
| Epson TM-T20III (USB, 80 mm) | Bondrucker |
| Tablets / Smartphones | Kassenoberfläche im Browser |

---

## Schnellstart (Entwicklung)

```bash
uv sync --group dev
cp .env.example .env
uv run uvicorn app.main:app --reload
```

```bash
uv run pytest          # Tests
uv run ruff check .    # Linting
uv run mypy app        # Typchecks
```

---

## Deployment auf den Raspberry Pi

Ersteinrichtung (einmalig, mit Internet): → [docs/einrichtung.md](docs/einrichtung.md)

---

## Konfiguration

Vollständige Referenz aller `.env`-Variablen: → [docs/konfiguration.md](docs/konfiguration.md)

Die wichtigsten Werte für euren Event:

| Variable | Beispiel |
|---|---|
| `VEREINSNAME` | `ASG Ettlingen` |
| `EVENT_NAME` | `Fischerfest` |
| `EVENT_JAHR` | `2026` |

---

## Dokumentation

| Dokument | Inhalt |
|---|---|
| [Einrichtung (Raspberry Pi)](docs/einrichtung.md) | SD-Karte, SSH, Hotspot, systemd |
| [Für euren Verein anpassen](docs/neuer-verein.md) | Andere Shops, CSV-Formate, Fork |
| [Konfigurationsreferenz](docs/konfiguration.md) | Alle `.env`-Variablen |
