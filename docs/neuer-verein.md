# Für euren Verein anpassen

Kurzanleitung um das System für eine neue Organisation oder ein anderes Event einzurichten. Dauert ohne Pi-Setup ca. 10 Minuten.

---

## Was ihr braucht

- Ein Vorbestellungssystem das CSV-Exporte liefert (WooCommerce, Shopify, Pretix, Eventbrite oder eigenes)
- Optional: Raspberry Pi 4 + Epson-Bondrucker (Vollbetrieb) – oder nur ein Laptop für Tests
- Python 3.11+ oder `uv` für die lokale Entwicklungsumgebung

---

## Schritt 1 – Repo klonen

```bash
git clone https://github.com/ASG-Ettlingen/fischverkauf.git vorbestellungs-kasse
cd vorbestellungs-kasse
```

Für eigene Anpassungen empfiehlt sich ein Fork, damit ihr Updates einpflegen könnt.

---

## Schritt 2 – Konfiguration anpassen

```bash
cp .env.example .env
```

Mindestens diese Werte anpassen:

| Variable | Beispiel | Beschreibung |
|---|---|---|
| `VEREINSNAME` | `TC Musterstadt` | Erscheint auf dem Bon |
| `EVENT_NAME` | `Sommerfest` | Erscheint auf dem Bon |
| `EVENT_JAHR` | `2026` | Erscheint auf dem Bon |
| `ABHOLZEIT_LABEL` | `Abholzeit` | Bezeichnung für das Zeitfenster |
| `TOGO_LABEL` | `To-Go` | Badge-Text für Sonderbestellungen |

Wenn euer Vorbestellungssystem kein Zeitfenster-Feld hat: `abholzeit`-Spalte einfach weglassen – das Feld ist optional.

---

## Schritt 3 – CSV-Format wählen

### WooCommerce (Standard)

Eine Zeile pro Bestellung, Produkte als Spaltenpaare `item_1`/`quantity_1`, `item_2`/`quantity_2` …

```
CSV_FORMAT=pivoted
```

Spaltennamen entsprechen dem WooCommerce-SQL-Export. Nur anpassen wenn euer Export andere Bezeichnungen hat.

Testdatei: [`data/example.csv`](../data/example.csv)

### Shopify / Pretix / Eventbrite (line_items)

Eine Zeile pro Artikel – bei mehrteiligen Bestellungen wiederholt sich die `order_id`:

```
CSV_FORMAT=line_items
CSV_COL_ITEM_NAME=item_name    # Spalte mit Produktname (anpassen!)
CSV_COL_ITEM_QUANTITY=quantity  # Spalte mit Menge (anpassen!)
```

Die anderen Kundendaten-Spalten (`first_name`, `last_name`, …) werden aus der ersten Zeile der jeweiligen Bestellung gelesen.

Testdatei: [`data/example_line_items.csv`](../data/example_line_items.csv)

### Anderes System

Spaltennamen in `.env` anpassen:

```
CSV_COL_ORDER_ID=meine_bestellnummer
CSV_COL_TOTAL=gesamtpreis
CSV_COL_FIRST_NAME=vorname
# … usw.
```

---

## Schritt 4 – Lokal testen

```bash
uv sync --group dev          # einmalig
uv run uvicorn app.main:app --reload
```

Browser öffnen: [http://localhost:8000/admin](http://localhost:8000/admin)

CSV hochladen (Admin-Oberfläche) oder per curl:

```bash
# Beispiel-Datei (pivoted)
curl -X POST http://localhost:8000/admin/import -F "file=@data/example.csv"

# Beispiel-Datei (line_items)
curl -X POST http://localhost:8000/admin/import -F "file=@data/example_line_items.csv"
```

Danach [http://localhost:8000](http://localhost:8000) öffnen und Suche + Abholung prüfen.

---

## Schritt 5 – Auf Raspberry Pi deployen

Wenn der lokale Test passt: siehe [docs/einrichtung.md](einrichtung.md) für die vollständige Pi-Einrichtung.

Wichtigste Werte für den Pi noch in `.env` setzen:

```
PI_HOSTNAME=kasse          # Pi erscheint als kasse.local im Netzwerk
HOTSPOT_SSID=MeinVerein    # WLAN-Name des Hotspots
HOTSPOT_PASSWORD=Sicher123 # WLAN-Passwort (mind. 8 Zeichen)
```
