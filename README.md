# fischverkauf

Abholsystem für das jährliche Fischerfest der ASG Ettlingen. Kunden bestellen
Fisch vorab online, holen ihn am Eventtag ab und zahlen bar. Die App läuft auf
einem Raspberry Pi mit eigenem WLAN-Hotspot – kein Internet, kein IT-Personal
vor Ort nötig.

Mitarbeiter suchen Bestellungen per Tablet (Name, E-Mail oder Bestellnummer),
bestätigen die Abholung, und der Bon kommt aus dem Drucker. Fertig.

## Setup (Entwicklung)

```bash
uv sync --group dev
cp .env.example .env
uv run uvicorn app.main:app --reload
```

## Deployment (Raspberry Pi)

Ersteinrichtung: siehe [docs/einrichtung.md](docs/einrichtung.md)

```bash
bash scripts/prepare.sh        # einmalig zuhause (braucht Internet)
git pull && bash scripts/prepare.sh  # nach Updates

bash scripts/event.sh          # am Eventtag vor Ort (offline)

# CSV aus WooCommerce importieren
curl -X POST http://localhost:8000/admin/import -F "file=@bestellungen.csv"
```

## Tests

```bash
uv run pytest
uv run ruff check .
uv run mypy app
```

## Konfiguration

`.env.example` kopieren und anpassen:

| Variable | Default | |
|---|---|---|
| `VEREINSNAME` | `ASG Ettlingen` | Auf dem Bon |
| `EVENT_JAHR` | `2026` | Auf dem Bon |
| `DATABASE_URL` | `sqlite:///./data/fischverkauf.db` | |
| `PRINTER_DEVICE` | `/dev/usb/lp0` | USB-Pfad des Druckers |
| `PRINTER_ENABLED` | `true` | `false` zum Deaktivieren |

## Hardware

- Raspberry Pi 4 Model B
- Epson TM-T20III (USB, 80mm)
- Beliebige Tablets / Handys als Kassenoberfläche
