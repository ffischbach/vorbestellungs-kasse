# Changelog

## v1.0.0 – 2026-05-30

Erstes stabiles Release.

### Features

- **CSV-Import** aus WooCommerce (pivotiertes Format) und anderen Shops wie Shopify, Pretix oder Eventbrite (line_items-Format, eine Zeile pro Artikel)
- **Echtzeit-Suche** nach Vor- und Nachname, E-Mail oder Bestellnummer (Teilstrings)
- **Abholbestätigung** mit automatischem Bondruck (ESC/POS, Epson TM-T20III)
- **Kassenzettel** mit Wechselgeldberechnung und Schnellbetragsauswahl
- **Doppeltes Abholen** zuverlässig verhindert (DB-Constraint + UI-Sperre)
- **SSE-Live-Sync** – alle Tablets sehen Statusänderungen sofort ohne Reload
- **Admin-Oberfläche** – CSV-Import, Druckerstatus, Daten-Reset
- **Vollständig offline** auf Raspberry Pi – eigener WLAN-Hotspot via hostapd/dnsmasq
- **Konfigurierbar** per `.env`: Vereinsname, Eventname, Labels, CSV-Spaltennamen, CSV-Format
- **Druckerausfall** blockiert nicht den Abholprozess – Fehlermeldung + Nachdrucken möglich
