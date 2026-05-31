import os
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from app.config import settings
from app.models.order import Order


class PrinterNotAvailableError(Exception):
    pass


class PrinterService:
    def is_available(self) -> bool:
        return settings.printer_enabled and os.path.exists(settings.printer_device)

    def print_receipt(self, order: Order) -> None:
        if not settings.printer_enabled:
            return
        try:
            from escpos.printer import File  # type: ignore[import]

            printer = File(settings.printer_device)
            try:
                self._write_receipt(printer, order)
            finally:
                printer.close()
        except ImportError as e:
            raise PrinterNotAvailableError("python-escpos nicht installiert") from e
        except Exception as e:
            raise PrinterNotAvailableError(f"Drucker nicht erreichbar: {e}") from e

    def _write_receipt(self, printer: object, order: Order) -> None:
        from escpos.printer import File  # type: ignore[import]

        p: File = printer  # type: ignore[assignment]

        font = settings.printer_font.lower()
        sep = "─" * (52 if font == "b" else 42)

        p.set(align="center", bold=True, font=font)
        p.text(f"{settings.vereinsname}\n")
        p.text(f"{settings.event_name} {settings.event_jahr}\n")
        p.set(align="center", bold=False, font=font)
        p.text(sep + "\n")

        p.set(align="left", font=font)
        p.text(f"#{order.order_id} · {order.first_name} {order.last_name}\n")

        for item in order.items:
            p.text(f"  {item['quantity']}x  {item['name']}\n")

        p.text(sep + "\n")
        p.set(bold=True, font=font)
        p.text(f"Gesamt:    {order.net_total:.2f} EUR\n")
        p.set(bold=False, font=font)

        if order.abholzeit:
            p.text(f"{settings.abholzeit_label}: {order.abholzeit}\n")

        p.text(sep + "\n")

        tz = ZoneInfo(settings.timezone)
        ts = (order.picked_up_at or datetime.now(UTC)).astimezone(tz)
        p.text(f"Bezahlt:  {ts.strftime('%d.%m.%Y  %H:%M')}\n")
        p.text(f"Bon-Nr.:  #{order.order_id}\n")

        p.cut()
