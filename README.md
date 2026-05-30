# vorbestellungs-kasse

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

**Veranstaltung**

| Variable | Beispiel | Beschreibung |
|---|---|---|
| `VEREINSNAME` | `ASG Ettlingen` | Erscheint auf dem Bon |
| `EVENT_NAME` | `Fischerfest` | Erscheint auf dem Bon |
| `EVENT_JAHR` | `2026` | Erscheint auf dem Bon |

**Labels**

| Variable | Default | Beschreibung |
|---|---|---|
| `ABHOLZEIT_LABEL` | `Abholzeit` | Bezeichnung für das Zeitfenster-Feld |
| `TOGO_LABEL` | `To-Go` | Badge-Text für To-Go-Bestellungen |

**CSV-Spaltennamen** (nur anpassen wenn kein WooCommerce-Export)

| Variable | Default |
|---|---|
| `CSV_COL_ORDER_ID` | `order_id` |
| `CSV_COL_TOTAL` | `net_total` |
| `CSV_COL_FIRST_NAME` | `first_name` |
| `CSV_COL_LAST_NAME` | `last_name` |
| `CSV_COL_EMAIL` | `email` |
| `CSV_COL_TIMESLOT` | `abholzeit` |
| `CSV_COL_TOGO` | `togo` |
| `CSV_COL_ITEM_PREFIX` | `item_` |
| `CSV_COL_QUANTITY_PREFIX` | `quantity_` |
| `CSV_ITEM_SLOTS` | `10` |

**Infrastruktur** (Raspberry Pi, nur für `scripts/prepare.sh`)

| Variable | Default | Beschreibung |
|---|---|---|
| `PI_HOSTNAME` | `kasse` | Netzwerkname des Pi (`kasse.local`) |
| `HOTSPOT_SSID` | `MeinVerein` | WLAN-Name des Hotspots |
| `HOTSPOT_PASSWORD` | `MeinPasswort2026` | WLAN-Passwort |

**Technisch**

| Variable | Default | |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/vorbestellungs-kasse.db` | |
| `PRINTER_DEVICE` | `/dev/usb/lp0` | USB-Pfad des Druckers |
| `PRINTER_ENABLED` | `true` | `false` zum Deaktivieren |

## Hardware

- Raspberry Pi 4 Model B
- Epson TM-T20III (USB, 80mm)
- Beliebige Tablets / Handys als Kassenoberfläche
