# Konfigurationsreferenz

Alle Einstellungen werden in der Datei `.env` vorgenommen (aus `.env.example` kopieren).
Kein Code ändern nötig.

---

## Veranstaltung

| Variable | Beispiel | Beschreibung |
|---|---|---|
| `VEREINSNAME` | `ASG Ettlingen` | Erscheint auf dem Bon |
| `EVENT_NAME` | `Fischerfest` | Erscheint auf dem Bon |
| `EVENT_JAHR` | `2026` | Erscheint auf dem Bon |

---

## Sicherheit

| Variable | Default | Beschreibung |
|---|---|---|
| `ADMIN_PASSWORD` | `bitte-aendern` | Passwort für `/admin` – **unbedingt ändern**. Benutzername ist immer `admin`. |

---

## Labels

| Variable | Default | Beschreibung |
|---|---|---|
| `ABHOLZEIT_LABEL` | `Abholzeit` | Bezeichnung für das Zeitfenster-Feld |
| `TOGO_LABEL` | `To-Go` | Badge-Text für To-Go-Bestellungen |

---

## CSV-Format

| Variable | Default | Beschreibung |
|---|---|---|
| `CSV_FORMAT` | `pivoted` | `pivoted` = WooCommerce (item_1/quantity_1 …); `line_items` = eine Zeile pro Artikel (Shopify, Pretix …) |

### Spaltennamen (pivoted)

| Variable | Default | Beschreibung |
|---|---|---|
| `CSV_COL_ORDER_ID` | `order_id` | |
| `CSV_COL_TOTAL` | `net_total` | |
| `CSV_COL_FIRST_NAME` | `first_name` | |
| `CSV_COL_LAST_NAME` | `last_name` | |
| `CSV_COL_EMAIL` | `email` | |
| `CSV_COL_TIMESLOT` | `abholzeit` | |
| `CSV_COL_TOGO` | `togo` | |
| `CSV_COL_ITEM_PREFIX` | `item_` | Präfix für Produktspalten |
| `CSV_COL_QUANTITY_PREFIX` | `quantity_` | Präfix für Mengenspalten |
| `CSV_ITEM_SLOTS` | `10` | Maximale Anzahl Produktspalten |

### Spaltennamen (line_items)

| Variable | Default | Beschreibung |
|---|---|---|
| `CSV_COL_ITEM_NAME` | `item_name` | Spalte mit Produktname |
| `CSV_COL_ITEM_QUANTITY` | `quantity` | Spalte mit Menge |

---

## Infrastruktur (Raspberry Pi)

Nur relevant für `scripts/prepare.sh`.

| Variable | Default | Beschreibung |
|---|---|---|
| `PI_HOSTNAME` | `kasse` | Netzwerkname des Pi (`kasse.local`) |
| `HOTSPOT_SSID` | `MeinVerein` | WLAN-Name des Hotspots |
| `HOTSPOT_PASSWORD` | `MeinPasswort2026` | WLAN-Passwort (mind. 8 Zeichen) |

---

## Technisch

| Variable | Default | Beschreibung |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/vorbestellungs-kasse.db` | Datenbankpfad |
| `PRINTER_DEVICE` | `/dev/usb/lp0` | USB-Gerätepfad des Druckers |
| `PRINTER_ENABLED` | `true` | `false` zum Deaktivieren (z. B. für Tests) |
| `PRINTER_FONT` | `a` | `a` = normal (42 Zeichen/Zeile), `b` = klein (52 Zeichen/Zeile) |
