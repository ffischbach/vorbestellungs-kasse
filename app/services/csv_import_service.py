import csv
import io
from collections import defaultdict
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.config import settings
from app.models.order import Order
from app.repositories.order_repository import OrderRepository

_NULL_VALUES = {"NULL", "null", "None", ""}
_BOOL_TRUE_VALUES = {"1", "true", "True", "yes", "ja", "x"}


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


def _parse_date_paid(raw: str | None) -> datetime | None:
    if not raw:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=UTC)
        except ValueError:
            continue
    return None


def _build_order(row: dict, items: list[dict]) -> Order:
    customer_id_raw = _val(row.get("customer_id"))
    num_items_raw = _val(row.get("num_items_sold"))
    returning_raw = _val(row.get("returning_customer"))
    return Order(
        order_id=int(row[settings.csv_col_order_id]),
        net_total=float(row[settings.csv_col_total]),
        first_name=row[settings.csv_col_first_name].strip(),
        last_name=row[settings.csv_col_last_name].strip(),
        email=row[settings.csv_col_email].strip().lower(),
        customer_id=int(customer_id_raw) if customer_id_raw else None,
        abholzeit=_val(row.get(settings.csv_col_timeslot)),
        togo=_val(row.get(settings.csv_col_togo)),
        date_paid=_parse_date_paid(_val(row.get(settings.csv_col_date_paid))),
        num_items_sold=int(num_items_raw) if num_items_raw else None,
        returning_customer=(
            (returning_raw in _BOOL_TRUE_VALUES) if returning_raw is not None else None
        ),
        items=items,
    )


class CsvImportService:
    def parse(self, content: str) -> list[Order]:
        first_line = content.split("\n", 1)[0]
        delimiter = _detect_delimiter(first_line)
        reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)

        if settings.csv_format == "line_items":
            return self._parse_line_items(reader)
        return self._parse_pivoted(reader)

    def _parse_pivoted(self, reader: csv.DictReader) -> list[Order]:  # type: ignore[type-arg]
        orders = []
        for row in reader:
            items = []
            for i in range(1, settings.csv_item_slots + 1):
                name = _val(row.get(f"{settings.csv_col_item_prefix}{i}"))
                qty_raw = _val(row.get(f"{settings.csv_col_quantity_prefix}{i}"))
                if name and qty_raw:
                    try:
                        items.append({"name": name, "quantity": int(qty_raw)})
                    except ValueError:
                        pass
            orders.append(_build_order(row, items))
        return orders

    def _parse_line_items(self, reader: csv.DictReader) -> list[Order]:  # type: ignore[type-arg]
        groups: dict[int, list[dict]] = defaultdict(list)
        for row in reader:
            order_id = int(row[settings.csv_col_order_id])
            groups[order_id].append(row)

        orders = []
        for rows in groups.values():
            items = []
            for row in rows:
                name = _val(row.get(settings.csv_col_item_name))
                qty_raw = _val(row.get(settings.csv_col_item_quantity))
                if name and qty_raw:
                    try:
                        items.append({"name": name, "quantity": int(qty_raw)})
                    except ValueError:
                        pass
            orders.append(_build_order(rows[0], items))
        return orders

    def import_to_db(self, content: str, db: Session, replace: bool = True) -> int:
        repo = OrderRepository(db)
        if replace:
            repo.delete_all()
        orders = self.parse(content)
        return repo.bulk_create(orders)
