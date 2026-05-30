import os
from datetime import UTC, datetime

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

        p.set(align="center", bold=True, double_height=True)
        p.text(f"{settings.vereinsname}\n")
        p.text(f"Fischerfest {settings.event_jahr}\n")
        p.set(align="center", bold=False, double_height=False)
        p.text("─" * 32 + "\n")

        p.set(align="left")
        p.text(f"Bestellung #{order.order_id}\n")
        p.text(f"{order.first_name} {order.last_name}\n\n")

        for item in order.items:
            p.text(f"  {item['quantity']}x  {item['name']}\n")

        p.text("\n" + "─" * 32 + "\n")
        p.set(bold=True)
        p.text(f"Gesamt:    {order.net_total:.2f} EUR\n")
        p.set(bold=False)

        if order.abholzeit:
            p.text(f"Abholzeit: {order.abholzeit}\n")

        p.text("─" * 32 + "\n")

        ts = order.picked_up_at or datetime.now(UTC)
        p.text(f"Abgeholt: {ts.strftime('%d.%m.%Y  %H:%M')}\n")
        p.text(f"Bon-Nr.:  #{order.order_id}\n")

        p.cut()
