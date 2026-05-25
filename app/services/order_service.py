from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.order import Order
from app.repositories.order_repository import OrderRepository
from app.services.printer_service import PrinterService


class OrderNotFoundError(Exception):
    pass


class OrderAlreadyPickedUpError(Exception):
    pass


class OrderService:
    def __init__(self, db: Session) -> None:
        self.repo = OrderRepository(db)
        self.printer = PrinterService()

    def search(self, query: str) -> list[Order]:
        if len(query) < 2:
            return []
        return self.repo.search(query)

    def get_all(self, status: str | None = None) -> list[Order]:
        orders = self.repo.get_all()
        if status == "open":
            return [o for o in orders if not o.picked_up]
        if status == "picked_up":
            return [o for o in orders if o.picked_up]
        return orders

    def get_stats(self) -> dict[str, int]:
        return self.repo.count()

    def get_overview(self) -> dict:
        return {
            "by_time": self.repo.count_by_abholzeit(),
        }

    def reprint(self, order_id: int) -> tuple[Order, str | None]:
        """Reprints the receipt for a picked-up order. Returns (order, printer_error)."""
        order = self.repo.get_by_order_id(order_id)
        if not order:
            raise OrderNotFoundError(f"Bestellung #{order_id} nicht gefunden")

        printer_error: str | None = None
        try:
            self.printer.print_receipt(order)
        except Exception as e:
            printer_error = str(e)

        return order, printer_error

    def pickup(self, order_id: int) -> tuple[Order, str | None]:
        """Marks order as picked up and prints receipt. Returns (order, printer_error)."""
        order = self.repo.get_by_order_id(order_id)
        if not order:
            raise OrderNotFoundError(f"Bestellung #{order_id} nicht gefunden")
        if order.picked_up:
            raise OrderAlreadyPickedUpError(f"Bestellung #{order_id} wurde bereits abgeholt")

        order = self.repo.mark_picked_up(order, datetime.now(UTC))

        printer_error: str | None = None
        try:
            self.printer.print_receipt(order)
        except Exception as e:
            printer_error = str(e)

        return order, printer_error
