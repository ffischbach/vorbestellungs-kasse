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
    first_name_raw = (row.get(settings.csv_col_first_name) or "").strip()
    last_name_raw = (row.get(settings.csv_col_last_name) or "").strip()
    if last_name_raw:
        first_name, last_name = first_name_raw, last_name_raw
    else:
        parts = first_name_raw.split(None, 1)
        first_name = parts[0] if parts else ""
        last_name = parts[1] if len(parts) > 1 else ""
    return Order(
        order_id=row[settings.csv_col_order_id].strip(),
        net_total=float(row[settings.csv_col_total]),
        first_name=first_name,
        last_name=last_name,
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
        groups: dict[str, list[dict]] = defaultdict(list)
        for row in reader:
            order_id = row[settings.csv_col_order_id].strip()
            groups[order_id].append(row)

        orders = []
        for rows in groups.values():
            items = []
            line_price_total = 0.0
            for row in rows:
                name = _val(row.get(settings.csv_col_item_name))
                qty_raw = _val(row.get(settings.csv_col_item_quantity))
                if name and qty_raw:
                    try:
                        qty = int(qty_raw)
                        items.append({"name": name, "quantity": qty})
                        if settings.csv_col_line_price:
                            price_raw = _val(row.get(settings.csv_col_line_price))
                            if price_raw:
                                line_price_total += float(price_raw) * qty
                    except ValueError:
                        pass
            first_row = rows[0]
            if settings.csv_col_line_price:
                first_row = dict(first_row)
                first_row[settings.csv_col_total] = str(round(line_price_total, 2))
            orders.append(_build_order(first_row, items))
        return orders

    def import_to_db(self, content: str, db: Session, replace: bool = True) -> int:
        repo = OrderRepository(db)
        if replace:
            repo.delete_all()
        orders = self.parse(content)
        return repo.bulk_create(orders)
