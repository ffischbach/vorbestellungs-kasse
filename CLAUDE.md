# Fischerfest – Digitales Bestellabholsystem

## Projektüberblick

Ein Angelverein veranstaltet ein jährliches Fischereifest, bei dem Kunden
Fisch vorab online vorbestellen können. Am Eventtag holen Kunden ihre
Bestellungen ab und bezahlen bar.

**Problem heute:** Papierlisten, manuelle Kasseneingabe, fehleranfällig.  
**Ziel:** Digitaler, zuverlässiger Abholprozess – auch ohne technisches Personal.

---

## Hardware

| Gerät | Spezifikation | Rolle |
|---|---|---|
| Raspberry Pi 4 Model B | Pi OS 64-bit (2026) | Server, Hotspot, Druckserver |
| Epson TM-T20III (011) | USB-Anschluss, 24V Netzteil (PS-180), 80mm Thermopapier | Bondrucker |
| Tablets / Smartphones | Mehrere, browser-fähig | Kassenoberfläche für Mitarbeiter |

---

## Betriebskontext und Rahmenbedingungen

### Infrastruktur
- **Kein Internet vor Ort** – das System muss vollständig offline funktionieren
- Der Raspberry Pi betreibt einen **eigenen WLAN-Hotspot**, mit dem sich alle
  Tablets verbinden
- Stromversorgung über Verlängerungskabel (Outdoor-Event)
- **Kein IT-Personal** am Eventtag – Vereinsmitglieder richten alles ein
- **Aufbau-Verantwortung:** Vereins-Admin (eine Person)

### Betrieb
- **Einmal jährlich**, ca. 4–8 Stunden aktiv
- **300–500 Vorbestellungen** werden erwartet
- Mehrere Tablets laufen **parallel** – Bestellungen dürfen nicht doppelt
  abgeholt werden können
- Der Aufbau am Morgen muss einfach und schnell gehen (Ziel: unter 15 Minuten)

### UI/UX-Anforderungen
- Oberfläche auf **Deutsch**
- **Touch-optimiert** – große Schaltflächen, klar lesbar auf Tablet und Handy
- **Übersichtlich und intuitiv** – Mitarbeiter brauchen keine Einweisung
- Fehler müssen **klar kommuniziert** werden (z.B. Drucker nicht verbunden,
  Bestellung bereits abgeholt)
- Bei 300–500 Einträgen muss die Suche **sofort und zuverlässig** filtern –
  scrollen durch eine vollständige Liste ist keine Option

### Fehlerresistenz
- Ein Druckerfehler darf den Abholprozess **nicht blockieren** – die Bestellung
  wird trotzdem als abgeholt markiert, der Fehler wird angezeigt
- Bei Stromausfall oder Neustart soll der Datenstand erhalten bleiben
- Das System soll so gebaut sein, dass typische Bedienungsfehler abgefangen
  werden (z.B. versehentliches doppeltes Tippen auf „Abholen")

---

## Datenbasis – CSV-Export

Die Vorbestellungen werden als CSV bereitgestellt. Das System unterstützt zwei
Formate (gesteuert via `CSV_FORMAT`):

- **`pivoted`** (Standard, WooCommerce): Eine Zeile pro Bestellung, Produkte
  als Spaltenpaare `item_1`/`quantity_1` … `item_10`/`quantity_10`
- **`line_items`** (Shopify, Pretix, Eventbrite …): Eine Zeile pro Artikel,
  mehrere Zeilen pro Bestellung

### CSV-Spalten (pivoted / WooCommerce)

| Spalte | Typ | Beschreibung |
|---|---|---|
| `order_id` | Integer (z.B. `2234`) | Eindeutige Bestellnummer |
| `net_total` | Decimal | Bestellsumme (netto) |
| `first_name` | String | Vorname des Kunden |
| `last_name` | String | Nachname des Kunden |
| `email` | String | E-Mail-Adresse des Kunden |
| `customer_id` | Integer | Interne Kunden-ID |
| `abholzeit` | String | Gebuchtes Abholzeitfenster (custom field) |
| `togo` | String | To-go-Kennzeichnung (custom field) |
| `num_items_sold` | Integer | Anzahl der bestellten Artikel (gesamt) |
| `returning_customer` | Boolean | Bestandskunde ja/nein |
| `date_paid` | Datetime | Bezahlzeitpunkt |
| `item_1` … `item_10` | String | Produktname (Slot 1–10, kann leer sein) |
| `quantity_1` … `quantity_10` | Integer | Menge zum jeweiligen Produkt |

### Hinweise zum Format
- Spaltennamen sind über `CSV_COL_*`-Variablen in `.env` konfigurierbar
- Leere Produkt-Slots (`item_N` = NULL) werden beim Import ignoriert
- `abholzeit` kann leer sein (kein Zeitfenster gebucht)

---

## Prozess

```
1. VOR dem Event (Vorbereitung, einmalig)
   SQL-Query auf WooCommerce-Datenbank ausführen → CSV exportieren
   └── CSV auf den Raspberry Pi importieren

2. AM Event (Aufbau, ~15 Minuten)
   Pi starten → Hotspot und App starten automatisch
   Drucker per USB anschließen und einschalten
   Tablets mit dem Hotspot verbinden und Browser öffnen
   Systemstatus prüfen (Drucker verbunden? Daten geladen?)

3. AM Event (Betrieb – pro Kunde)
   Kunde erscheint an der Kasse
   └── Mitarbeiter sucht Bestellung
       nach Name (Vor- oder Nachname)
       nach E-Mail-Adresse
       nach Bestellnummer (order_id)
   └── Treffer wird angezeigt:
       Kundenname, Bestellnummer, Abholzeit, alle Artikel + Mengen, Gesamtsumme
   └── Kunde zahlt bar
   └── Mitarbeiter bestätigt Zahlung mit einem Tap
       ├── Bon wird automatisch gedruckt
       ├── Bestellung wird als „bezahlt" markiert (mit Zeitstempel, dauerhaft)
       └── Bestellung erscheint automatisch in der Ausgabe-Ansicht

4. NACH dem Event
   Pi sauber herunterfahren
   Optional: Daten sichern oder löschen
```

---

## Bon-Inhalt

Der Bon muss folgende Informationen ausweisen:

```
[Vereinsname]
Fischerfest [Jahr]
──────────────────────────────
Bestellung #2234
Max Mustermann

  2x  Forelle (küchenfertig)
  1x  Karpfen (ganz)
  3x  Hecht (filetiert)

──────────────────────────────
Gesamt:        42,00 €
Abholzeit:     11:00 – 12:00
──────────────────────────────
Bezahlt:  14.06.2025  11:23
Bon-Nr.:  #2234
```

- Alle bestellten Produkte mit Menge
- Bestellsumme (`net_total`)
- Abholzeitfenster (`abholzeit`), falls vorhanden
- Zahlungszeitpunkt (Uhrzeit der Bestätigung durch Mitarbeiter)

---

## Funktionale Anforderungen

### Suche
- Suche nach **Vorname**, **Nachname**, **E-Mail** oder **Bestellnummer**
- Suche filtert in Echtzeit während der Eingabe
- Bei 300–500 Einträgen muss die Suche performant bleiben
- Teilstrings sollen funktionieren (z.B. „Muster" findet „Mustermann")

### Abholzeitfenster
- `abholzeit` wird in der Bestellansicht und auf dem Bon angezeigt
- Optional: Filterung/Gruppierung nach Zeitfenster in der Übersicht
  (erleichtert Stoßzeiten-Management)

### Bestellstatus
- Klar sichtbar ob eine Bestellung **offen** oder **bezahlt** ist
- Bezahlte Bestellungen sind durchgestrichen oder ausgegraut – weiterhin
  sichtbar und auffindbar
- Doppeltes Bezahlen wird mit einer eindeutigen Fehlermeldung verhindert

### Übersicht
- Zähler: wie viele Bestellungen offen / bezahlt / gesamt
- Filterbar nach Status (alle / nur offen / nur bezahlt)

### Systemstatus
- Jederzeit sichtbar ob Drucker verbunden und betriebsbereit ist

### Admin-Bereich (`/admin`)
- Geschützt mit HTTP Basic Auth (Benutzername: `admin`, Passwort: `ADMIN_PASSWORD`)
- CSV importieren (mit Vorschau des Formats und Beispiel-Download)
- Alle Bestellungen zurücksetzen (Datenbank leeren)

---

## Nicht-funktionale Anforderungen

- Vollständig **offline** – keine externe Abhängigkeit
- **Mehrere Clients gleichzeitig** ohne Datenkonflikte
- Stabil über **4–8 Stunden** ohne Neustart
- Aufbau in **unter 15 Minuten** durch eine Person

---

## Datenschutz

Kundendaten (Name, E-Mail-Adresse) werden lokal auf dem Pi gespeichert.

- Daten werden **nur für diesen Event** verwendet
- Keine Übertragung ins Internet
- Nach dem Event sollten Daten einfach löschbar sein
- Minimalismus: nur die für den Abholprozess notwendigen Daten speichern

---

## Rollen

| Rolle | Gerät | Aufgaben |
|---|---|---|
| **Kassierer** | Tablet / Handy | Bestellungen suchen, Abholung bestätigen |
| **Vereins-Admin** | Laptop (einmalig vorab) | CSV importieren, System einrichten, Updates einspielen |
| **Vereins-Admin** | vor Ort am Eventtag | Aufbau, Drucker anschließen, Systemstart prüfen |

Der Kassierer braucht **keine technischen Kenntnisse**.

---

## Nicht-Ziele (explizit außerhalb des Scope)

- ❌ Online-Shop / Vorbestellungsprozess selbst
- ❌ Elektronische Zahlung (Kartenzahlung, PayPal etc.)
- ❌ Lagerverwaltung oder Produktkatalog
- ❌ Kundenbenachrichtigungen (E-Mail, SMS)
- ❌ Mehrsprachigkeit
- ❌ Benutzerverwaltung / Login für Kassierer
- ❌ Betrieb mit Internet-Anbindung als Voraussetzung
- ❌ Direktanbindung an WooCommerce (Import immer via CSV)

---

## Abnahmekriterien

Das System gilt als fertig wenn:

- [ ] CSV-Import aus WooCommerce-Export funktioniert zuverlässig
- [ ] Suche nach Name, E-Mail und Bestellnummer funktioniert (inkl. Teilstrings)
- [ ] Bestelldetails werden vollständig angezeigt (Artikel, Mengen, Summe, Abholzeit)
- [ ] Bestellung kann mit einem Tap als bezahlt markiert werden
- [ ] Bon wird automatisch gedruckt (Produkte, Mengen, Summe, Abholzeit)
- [ ] Doppeltes Bezahlen ist zuverlässig verhindert
- [ ] Mehrere Tablets können parallel genutzt werden ohne Konflikte
- [ ] System läuft stabil 4–8 Stunden ohne Eingriff
- [ ] Druckerfehler blockiert nicht den Bezahlprozess
- [ ] Aufbau am Eventtag dauert unter 15 Minuten
- [ ] Ein Vereinsmitglied ohne IT-Kenntnis kann die Oberfläche bedienen

---

## Tech Stack

| Schicht | Technologie | Begründung |
|---|---|---|
| Backend | Python 3.11 + FastAPI + Uvicorn | Vorinstalliert auf Pi OS, schnell, async |
| Datenbank | SQLite (WAL-Modus) + Alembic | Kein Server, dateibasiert, concurrent-safe; Migrationen automatisch beim Start |
| Frontend | HTMX + Alpine.js + Tailwind CSS | Kein Build-Schritt, offline-fähig, lokal gebundelt |
| Echtzeit | Server-Sent Events (SSE) | Pickup-Events an alle Tablets ohne WebSocket-Overhead |
| Drucker | python-escpos | ESC/POS-Protokoll, TM-T20III über USB |
| Betrieb | systemd + hostapd + dnsmasq | Auto-Start, eigener WLAN-Hotspot |
| Paketmanager | uv | Schnell, deterministisch, lockfile-basiert |

**Statische Assets** (HTMX 2.0.3, Alpine.js 3.14.1, Tailwind CSS 2.2.19) sind
direkt im `static/`-Ordner committed – kein CDN-Aufruf, vollständig offline.
Tailwind v2 wird als vollständig pre-built CSS ausgeliefert (kein Build-Schritt).

---

## Projektstruktur

```
fischverkauf/
├── .github/workflows/ci.yml       # GitHub Actions CI
├── alembic/                       # Datenbankmigrationen
├── alembic.ini                    # Alembic-Konfiguration
├── app/
│   ├── main.py                    # FastAPI App, Lifespan (führt Alembic-Migrationen aus)
│   ├── config.py                  # Zentrale Konfiguration (pydantic-settings)
│   ├── database.py                # SQLite Engine, WAL-Modus, get_db()
│   ├── jinja.py                   # Jinja2-Templates-Instanz
│   ├── models/order.py            # SQLAlchemy ORM-Modell
│   ├── schemas/order.py           # Pydantic-Schemas (Request/Response)
│   ├── repositories/              # Datenzugriff (alle SQL-Queries hier)
│   │   └── order_repository.py
│   ├── services/                  # Business-Logik
│   │   ├── order_service.py       # Abholflow, Suche, Stats
│   │   ├── printer_service.py     # ESC/POS-Druck
│   │   └── csv_import_service.py  # Import für pivoted + line_items Format
│   ├── routers/                   # HTTP-Endpunkte
│   │   ├── orders.py              # Suche, Abholung, Stats
│   │   ├── admin.py               # CSV-Import, Reset (HTTP Basic Auth)
│   │   └── sse.py                 # Server-Sent Events
│   └── templates/                 # Jinja2 HTML (HTMX-Partials)
│       ├── base.html
│       ├── index.html             # Kassensicht
│       ├── admin.html             # Admin-Bereich
│       ├── ausgabe.html           # Ausgabeliste
│       └── partials/
│           ├── order_card.html
│           ├── order_list.html
│           ├── ausgabe_card.html
│           ├── ausgabe_list.html
│           ├── overview.html
│           ├── stats.html
│           ├── printer_status.html
│           ├── import_result.html
│           ├── reset_result.html
│           └── error.html
├── static/                        # JS/CSS lokal (kein CDN)
│   ├── htmx.min.js
│   ├── alpine.min.js
│   ├── tailwind.min.css
│   └── app.css
├── tests/
│   ├── conftest.py                # pytest fixtures (In-Memory SQLite)
│   ├── test_orders.py
│   ├── test_csv_import.py
│   └── testdata/                  # Beispiel-CSVs für Tests
├── data/                          # SQLite DB + CSV – nicht ins Repo!
├── docs/                          # Betriebsdokumentation
│   ├── einrichtung.md             # Pi-Setup Schritt für Schritt
│   ├── eventtag.md                # Checkliste Eventtag
│   ├── konfiguration.md           # Alle .env-Variablen erklärt
│   ├── neuer-verein.md            # Anpassung für andere Vereine/Events
│   └── troubleshooting.md
├── systemd/vorbestellungs-kasse.service
├── scripts/
│   ├── prepare.sh                 # Einmaliges Setup mit Internet (zuhause)
│   ├── status.sh                  # Optionaler Statuscheck am Eventtag
│   └── sync.sh                    # Lokale Änderungen per rsync auf den Pi übertragen
├── pyproject.toml                 # Dependencies + Tool-Konfiguration
└── .env.example
```

### Architekturprinzip: Layered Architecture

```
Router  →  Service  →  Repository  →  SQLAlchemy / SQLite
           (Logik)     (SQL)
```

- **Router** kennt nur HTTP (Request/Response, Templates)
- **Service** enthält Business-Logik, kennt kein HTTP
- **Repository** enthält alle SQL-Queries, kennt keine Business-Logik
- Services sind dadurch ohne HTTP-Kontext testbar

---

## Entwicklungs-Workflow

### Ersteinrichtung (Entwicklung, mit uv)

```bash
# uv installieren: https://docs.astral.sh/uv/getting-started/installation/
uv sync --group dev
uv run pre-commit install
cp .env.example .env
```

### Lokaler Entwicklungsserver

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Tests

```bash
uv run pytest                       # Alle Tests
uv run pytest -v                    # Verbose
uv run pytest tests/test_orders.py  # Einzelne Datei
```

### Lint & Format

```bash
uv run ruff check .     # Linting
uv run ruff format .    # Formatierung
uv run mypy app         # Typchecks
```

### Datenbankmigrationen (Alembic)

Alembic läuft **automatisch beim App-Start** (`lifespan` in `main.py` führt
`alembic upgrade head` aus). Für neue Migrationen:

```bash
uv run alembic revision --autogenerate -m "beschreibung"
uv run alembic upgrade head   # lokal anwenden
```

Nie manuell SQL patchen – immer Alembic verwenden.

---

## CI/CD

**GitHub Actions** läuft bei jedem Push und Pull Request auf `main`:

| Job | Was | Tool |
|---|---|---|
| Lint & Format | Code-Stil prüfen | `ruff check` + `ruff format --check` |
| Type Check | Typen validieren | `mypy app` |
| Tests | Einheits- und Integrationstests | `pytest` |

Deployment auf den Pi bleibt **manuell** (git pull + systemctl restart) –
kein CD nötig für diesen Anwendungsfall.

### pre-commit

Vor jedem Commit laufen automatisch `ruff` (Lint + Fix) und Format-Checks.

---

## Konfiguration

Alle konfigurierbaren Werte stehen in `.env` (aus `.env.example` kopieren).
Nie Konfigurationswerte hardcoden – immer `app/config.py` nutzen.

### Veranstaltung & App

| Variable | Default | Beschreibung |
|---|---|---|
| `VEREINSNAME` | `ASG Ettlingen` | Erscheint auf dem Bon |
| `EVENT_NAME` | `Veranstaltung` | Veranstaltungsname (z.B. `Fischerfest`) |
| `EVENT_JAHR` | `2026` | Erscheint auf dem Bon |
| `ADMIN_PASSWORD` | `admin` | Passwort für den Admin-Bereich (`/admin`) |

### Datenbank & Server

| Variable | Default | Beschreibung |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/vorbestellungs-kasse.db` | Datenbankpfad |
| `HOST` | `0.0.0.0` | Bind-Adresse des Servers |
| `PORT` | `8000` | Port des Servers |

### Drucker

| Variable | Default | Beschreibung |
|---|---|---|
| `PRINTER_DEVICE` | `/dev/usb/lp0` | USB-Gerätepfad Drucker |
| `PRINTER_ENABLED` | `true` | Druck deaktivieren (z.B. für Tests) |
| `PRINTER_FONT` | `b` | `a` = normal (42 Zeichen/Zeile), `b` = klein (52 Zeichen/Zeile) |

### CSV-Import

| Variable | Default | Beschreibung |
|---|---|---|
| `CSV_FORMAT` | `pivoted` | `pivoted` = WooCommerce-Standard; `line_items` = Shopify/Pretix/Eventbrite |
| `CSV_COL_ORDER_ID` | `order_id` | Spaltennamen konfigurierbar – Details in `.env.example` |

Alle `CSV_COL_*`-Variablen erlauben die Anpassung an abweichende Spaltennamen.
Vollständige Liste in `.env.example` und `docs/konfiguration.md`.

### Infrastruktur (für `scripts/prepare.sh`)

| Variable | Default | Beschreibung |
|---|---|---|
| `PI_HOSTNAME` | `kasse` | Netzwerkname des Pi (erreichbar als `kasse.local`) |
| `HOTSPOT_SSID` | `MeinVerein` | WLAN-Name des Hotspots |
| `HOTSPOT_PASSWORD` | `MeinPasswort2026` | WLAN-Passwort |

---

## Deployment auf Raspberry Pi

Das Setup verwendet `python3 -m venv` + `pip` – kein uv, kein curl, keine
externen Installer. Python 3.11+ ist auf Pi OS vorinstalliert.

```bash
# Einmaliges Setup zuhause (braucht Internet)
bash scripts/prepare.sh

# Nach Updates (braucht Internet)
git pull
bash scripts/prepare.sh

# Lokale Änderungen direkt per rsync übertragen (Entwicklung)
bash scripts/sync.sh [pi@kasse.local]

# Am Eventtag: Pi starten – alles läuft automatisch
# Optional: Systemstatus und URL anzeigen
bash scripts/status.sh

# Logs prüfen
sudo journalctl -u vorbestellungs-kasse -f

# CSV importieren (Admin-Endpunkt, HTTP Basic Auth)
curl -u admin:PASSWORT -X POST http://localhost:8000/admin/import \
  -F "file=@bestellungen.csv"
```

**Drucker-Gerätepfad:** Der Epson TM-T20III erscheint unter Linux typischerweise
als `/dev/usb/lp0`. Falls abweichend: `ls /dev/usb/` nach dem Einstecken prüfen
und `PRINTER_DEVICE` in `.env` anpassen.
