import pytest
from sqlalchemy.orm import Session

from app.models.order import Order
from app.services.order_service import (
    OrderAlreadyHandedOutError,
    OrderAlreadyPickedUpError,
    OrderNotFoundError,
    OrderNotPickedUpError,
    OrderService,
)


def make_order(db: Session, **kwargs: object) -> Order:
    defaults: dict[str, object] = {
        "order_id": "1001",
        "net_total": 20.0,
        "first_name": "Anna",
        "last_name": "Schmidt",
        "email": "anna@example.com",
        "items": [{"name": "Forelle", "quantity": 1}],
        "picked_up": False,
    }
    order = Order(**{**defaults, **kwargs})
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def test_search_by_last_name(db: Session) -> None:
    make_order(db)
    results = OrderService(db).search("Schmidt")
    assert len(results) == 1
    assert results[0].last_name == "Schmidt"


def test_search_partial_match(db: Session) -> None:
    make_order(db)
    results = OrderService(db).search("chmi")
    assert len(results) == 1


def test_search_by_order_id(db: Session) -> None:
    make_order(db)
    results = OrderService(db).search("1001")
    assert len(results) == 1


def test_search_too_short_returns_empty(db: Session) -> None:
    make_order(db)
    results = OrderService(db).search("A")
    assert results == []


def test_pickup_marks_order(db: Session) -> None:
    make_order(db)
    order, printer_error = OrderService(db).pickup(1001)
    assert order.picked_up is True
    assert order.picked_up_at is not None


def test_pickup_returns_printer_error_on_failure(db: Session) -> None:
    make_order(db)
    _, printer_error = OrderService(db).pickup(1001)
    assert printer_error is not None


def test_double_pickup_raises(db: Session) -> None:
    make_order(db, picked_up=True)
    with pytest.raises(OrderAlreadyPickedUpError):
        OrderService(db).pickup("1001")


def test_pickup_unknown_order_raises(db: Session) -> None:
    with pytest.raises(OrderNotFoundError):
        OrderService(db).pickup("9999")


def test_reprint_returns_printer_error_on_failure(db: Session) -> None:
    make_order(db, picked_up=True)
    _, printer_error = OrderService(db).reprint("1001")
    assert printer_error is not None


def test_reprint_unknown_order_raises(db: Session) -> None:
    with pytest.raises(OrderNotFoundError):
        OrderService(db).reprint("9999")


def test_get_stats(db: Session) -> None:
    make_order(db, order_id="1", picked_up=True)
    make_order(db, order_id="2", picked_up=False)
    stats = OrderService(db).get_stats()
    assert stats["total"] == 2
    assert stats["picked_up"] == 1
    assert stats["open"] == 1
    assert stats["handed_out"] == 0
    assert stats["waiting_handout"] == 1


def test_handout_success(db: Session) -> None:
    make_order(db, picked_up=True)
    order = OrderService(db).hand_out("1001")
    assert order.handed_out is True
    assert order.handed_out_at is not None


def test_handout_not_picked_up_raises(db: Session) -> None:
    make_order(db)
    with pytest.raises(OrderNotPickedUpError):
        OrderService(db).hand_out("1001")


def test_handout_already_handed_out_raises(db: Session) -> None:
    make_order(db, picked_up=True, handed_out=True)
    with pytest.raises(OrderAlreadyHandedOutError):
        OrderService(db).hand_out("1001")


def test_handout_unknown_order_raises(db: Session) -> None:
    with pytest.raises(OrderNotFoundError):
        OrderService(db).hand_out("9999")


def test_get_waiting_handout(db: Session) -> None:
    make_order(db, order_id=1, picked_up=True, handed_out=False)
    make_order(db, order_id=2, picked_up=True, handed_out=True)
    make_order(db, order_id="3", picked_up=False)
    waiting = OrderService(db).get_waiting_handout()
    assert len(waiting) == 1
    assert waiting[0].order_id == "1"
