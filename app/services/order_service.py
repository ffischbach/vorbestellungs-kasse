from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.order import Order
from app.repositories.order_repository import OrderRepository
from app.services.printer_service import PrinterService


class OrderNotFoundError(Exception):
    pass


class OrderAlreadyPickedUpError(Exception):
    pass


class OrderNotPickedUpError(Exception):
    pass


class OrderAlreadyHandedOutError(Exception):
    pass


class OrderService:
    def __init__(self, db: Session) -> None:
        self.repo = OrderRepository(db)

    def search(self, query: str) -> list[Order]:
        if len(query) < 2:
            return []
        return self.repo.search(query)

    def get_stats(self) -> dict[str, int]:
        return self.repo.count()

    def get_overview(self) -> dict:
        return {
            "by_time": self.repo.count_by_abholzeit(),
            "open_orders": self.repo.get_open_orders(),
            "product_totals": self.get_product_totals(),
            "recent_pickups": self.repo.get_recent_pickups(limit=20),
        }

    def get_open_orders(self) -> list[Order]:
        return self.repo.get_open_orders()

    def get_product_totals(self) -> list[dict]:
        totals: dict[str, int] = {}
        for order in self.repo.get_open_orders():
            for item in order.items:
                name = item.get("name", "")
                qty = int(item.get("quantity", 0))
                if name:
                    totals[name] = totals.get(name, 0) + qty
        return sorted(
            [{"name": k, "quantity": v} for k, v in totals.items()],
            key=lambda x: -x["quantity"],
        )

    def get_recent_pickups(self, limit: int = 15) -> list[Order]:
        return self.repo.get_recent_pickups(limit)

    def get_by_id(self, order_id: str) -> Order:
        order = self.repo.get_by_order_id(order_id)
        if not order:
            raise OrderNotFoundError(f"Bestellung #{order_id} nicht gefunden")
        return order

    def reprint(self, order_id: str) -> tuple[Order, str | None]:
        """Reprints the receipt for a picked-up order. Returns (order, printer_error)."""
        order = self.repo.get_by_order_id(order_id)
        if not order:
            raise OrderNotFoundError(f"Bestellung #{order_id} nicht gefunden")

        printer_error: str | None = None
        try:
            PrinterService().print_receipt(order)
        except Exception as e:
            printer_error = str(e)

        return order, printer_error

    def pickup(self, order_id: str) -> tuple[Order, str | None]:
        """Marks order as picked up and prints receipt. Returns (order, printer_error)."""
        order = self.repo.get_by_order_id(order_id)
        if not order:
            raise OrderNotFoundError(f"Bestellung #{order_id} nicht gefunden")
        if order.picked_up:
            raise OrderAlreadyPickedUpError(f"Bestellung #{order_id} wurde bereits bezahlt")

        order = self.repo.mark_picked_up(order, datetime.now(UTC))

        printer_error: str | None = None
        try:
            PrinterService().print_receipt(order)
        except Exception as e:
            printer_error = str(e)

        return order, printer_error

    def hand_out(self, order_id: str) -> Order:
        """Marks order as handed out. Returns updated order."""
        order = self.repo.get_by_order_id(order_id)
        if not order:
            raise OrderNotFoundError(f"Bestellung #{order_id} nicht gefunden")
        if not order.picked_up:
            raise OrderNotPickedUpError(f"Bestellung #{order_id} wurde noch nicht bezahlt")
        if order.handed_out:
            raise OrderAlreadyHandedOutError(f"Bestellung #{order_id} wurde bereits ausgegeben")
        return self.repo.mark_handed_out(order)

    def get_waiting_handout(self) -> list[Order]:
        return self.repo.get_waiting_handout()
