from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Vorbestellungs-Kasse"
    vereinsname: str = "ASG Ettlingen"
    event_name: str = "Veranstaltung"
    event_jahr: int = 2026

    database_url: str = "sqlite:///./data/vorbestellungs-kasse.db"

    admin_password: str = "admin"

    printer_device: str = "/dev/usb/lp0"
    printer_enabled: bool = True
    printer_font: str = "b"  # "a" = normal (42 Zeichen/Zeile), "b" = klein (52 Zeichen/Zeile)

    host: str = "0.0.0.0"
    port: int = 8000

    timezone: str = "Europe/Berlin"

    # UI-Labels
    abholzeit_label: str = "Abholzeit"
    togo_label: str = "To-Go"

    # "pivoted" = WooCommerce (item_1/quantity_1…) | "line_items" = eine Zeile pro Artikel
    csv_format: str = "pivoted"

    # CSV-Spaltennamen (Standard: WooCommerce-Export)
    csv_col_order_id: str = "order_id"
    csv_col_total: str = "net_total"
    csv_col_first_name: str = "first_name"
    csv_col_last_name: str = "last_name"
    csv_col_email: str = "email"
    csv_col_timeslot: str = "abholzeit"
    csv_col_togo: str = "togo"
    csv_col_date_paid: str = "date_paid"

    # Pivoted-Format (WooCommerce)
    csv_col_item_prefix: str = "item_"
    csv_col_quantity_prefix: str = "quantity_"
    csv_item_slots: int = 10

    # Line-Items-Format (Shopify, Pretix, …)
    csv_col_item_name: str = "item_name"
    csv_col_item_quantity: str = "quantity"
    # Wenn gesetzt: Stückpreis-Spalte für line_items –
    # Gesamtsumme wird als sum(Preis×Menge) berechnet.
    # Leer lassen wenn csv_col_total bereits die Bestellsumme enthält (WooCommerce-Verhalten).
    csv_col_line_price: str = ""


settings = Settings()
