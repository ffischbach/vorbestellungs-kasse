from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class OrderItem(BaseModel):
    name: str
    quantity: int


class OrderRead(BaseModel):
    id: int
    order_id: int
    net_total: Decimal
    first_name: str
    last_name: str
    email: str
    abholzeit: str | None
    togo: str | None
    items: list[OrderItem]
    picked_up: bool
    picked_up_at: datetime | None
    handed_out: bool
    handed_out_at: datetime | None

    model_config = {"from_attributes": True}


class ImportResult(BaseModel):
    imported: int
    message: str


class Stats(BaseModel):
    total: int
    picked_up: int
    open: int
    handed_out: int
    waiting_handout: int
