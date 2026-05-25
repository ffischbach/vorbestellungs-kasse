import csv
import io

from sqlalchemy.orm import Session

from app.models.order import Order
from app.repositories.order_repository import OrderRepository

ITEM_SLOTS = 10
_NULL_VALUES = {"NULL", "null", "None", ""}


def _val(raw: str | None) -> str | None:
    """Returns None for SQL NULL strings and empty values, stripped string otherwise."""
    if raw is None:
        return None
    stripped = raw.strip()
    return None if stripped in _NULL_VALUES else stripped


def _detect_delimiter(header: str) -> str:
    """Sniffs delimiter from the header line; falls back to tab."""
    try:
        dialect = csv.Sniffer().sniff(header, delimiters=",;\t")
        return dialect.delimiter
    except csv.Error:
        return "\t"


class CsvImportService:
    def parse(self, content: str) -> list[Order]:
        first_line = content.split("\n", 1)[0]
        delimiter = _detect_delimiter(first_line)

        reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
        orders = []
        for row in reader:
            items = []
            for i in range(1, ITEM_SLOTS + 1):
                name = _val(row.get(f"item_{i}"))
                qty_raw = _val(row.get(f"quantity_{i}"))
                if name and qty_raw:
                    try:
                        items.append({"name": name, "quantity": int(qty_raw)})
                    except ValueError:
                        pass

            customer_id_raw = _val(row.get("customer_id"))
            num_items_raw = _val(row.get("num_items_sold"))
            returning_raw = _val(row.get("returning_customer"))

            orders.append(
                Order(
                    order_id=int(row["order_id"]),
                    net_total=float(row["net_total"]),
                    first_name=row["first_name"].strip(),
                    last_name=row["last_name"].strip(),
                    email=row["email"].strip().lower(),
                    customer_id=int(customer_id_raw) if customer_id_raw else None,
                    abholzeit=_val(row.get("abholzeit")),
                    togo=_val(row.get("togo")),
                    num_items_sold=int(num_items_raw) if num_items_raw else None,
                    returning_customer=returning_raw in ("1", "true", "True")
                    if returning_raw is not None
                    else None,
                    items=items,
                )
            )
        return orders

    def import_to_db(self, content: str, db: Session, replace: bool = True) -> int:
        repo = OrderRepository(db)
        if replace:
            repo.delete_all()
        orders = self.parse(content)
        return repo.bulk_create(orders)
