from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    net_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    customer_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    abholzeit: Mapped[str | None] = mapped_column(String, nullable=True)
    togo: Mapped[str | None] = mapped_column(String, nullable=True)
    num_items_sold: Mapped[int | None] = mapped_column(Integer, nullable=True)
    returning_customer: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    date_paid: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    items: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)

    picked_up: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    picked_up_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
