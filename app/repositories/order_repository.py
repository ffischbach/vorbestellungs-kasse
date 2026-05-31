from datetime import UTC, datetime

from sqlalchemy import ColumnElement, or_
from sqlalchemy.orm import Session

from app.models.order import Order


class OrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def search(self, query: str) -> list[Order]:
        q = f"%{query}%"
        filters: list[ColumnElement[bool]] = [
            Order.first_name.ilike(q),
            Order.last_name.ilike(q),
            Order.email.ilike(q),
        ]
        if query.isdigit():
            filters.append(Order.order_id == int(query))
        return self.db.query(Order).filter(or_(*filters)).all()

    def get_by_order_id(self, order_id: int) -> Order | None:
        return self.db.query(Order).filter(Order.order_id == order_id).first()

    def get_all(self) -> list[Order]:
        return self.db.query(Order).order_by(Order.last_name, Order.first_name).all()

    def get_open_orders(self) -> list[Order]:
        from sqlalchemy import nulls_last

        return (
            self.db.query(Order)
            .filter(Order.picked_up.is_(False))
            .order_by(nulls_last(Order.abholzeit), Order.last_name, Order.first_name)
            .all()
        )

    def get_recent_pickups(self, limit: int = 15) -> list[Order]:
        return (
            self.db.query(Order)
            .filter(Order.picked_up.is_(True))
            .order_by(Order.picked_up_at.desc())
            .limit(limit)
            .all()
        )

    def get_waiting_handout(self) -> list[Order]:
        return (
            self.db.query(Order)
            .filter(Order.picked_up.is_(True), Order.handed_out.is_(False))
            .order_by(Order.picked_up_at.asc())
            .all()
        )

    def mark_picked_up(self, order: Order, picked_up_at: datetime) -> Order:
        order.picked_up = True
        order.picked_up_at = picked_up_at
        self.db.commit()
        self.db.refresh(order)
        return order

    def mark_handed_out(self, order: Order) -> Order:
        order.handed_out = True
        order.handed_out_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(order)
        return order

    def bulk_create(self, orders: list[Order]) -> int:
        self.db.add_all(orders)
        self.db.commit()
        return len(orders)

    def delete_all(self) -> None:
        self.db.query(Order).delete()
        self.db.commit()

    def count(self) -> dict[str, int]:
        total = self.db.query(Order).count()
        picked_up = self.db.query(Order).filter(Order.picked_up.is_(True)).count()
        handed_out = self.db.query(Order).filter(Order.handed_out.is_(True)).count()
        return {
            "total": total,
            "picked_up": picked_up,
            "open": total - picked_up,
            "handed_out": handed_out,
            "waiting_handout": picked_up - handed_out,
        }

    def count_by_abholzeit(self) -> list[dict]:
        from sqlalchemy import func

        totals: dict[str | None, int] = {
            row[0]: row[1]
            for row in self.db.query(Order.abholzeit, func.count(Order.id))
            .group_by(Order.abholzeit)
            .all()
        }
        picked: dict[str | None, int] = {
            row[0]: row[1]
            for row in self.db.query(Order.abholzeit, func.count(Order.id))
            .filter(Order.picked_up.is_(True))
            .group_by(Order.abholzeit)
            .all()
        }
        return [
            {
                "abholzeit": slot or "Kein Zeitfenster",
                "total": total,
                "picked_up": picked.get(slot, 0),
                "open": total - picked.get(slot, 0),
            }
            for slot, total in sorted(totals.items(), key=lambda x: (x[0] is None, x[0] or ""))
        ]
