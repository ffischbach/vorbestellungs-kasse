from sqlalchemy.orm import Session

from app.services.csv_import_service import CsvImportService

# Tab-separiertes Format, wie es aus dem WooCommerce SQL-Export kommt.
# NULL-Werte als Literal-String "NULL", wie von MySQL exportiert.
SAMPLE_TSV = (
    "order_id\tnet_total\tfirst_name\tlast_name\temail\tcustomer_id\t"
    "abholzeit\ttogo\tnum_items_sold\treturning_customer\tdate_paid\t"
    "item_1\tquantity_1\titem_2\tquantity_2\titem_3\tquantity_3\t"
    "item_4\tquantity_4\titem_5\tquantity_5\titem_6\tquantity_6\t"
    "item_7\tquantity_7\titem_8\tquantity_8\titem_9\tquantity_9\t"
    "item_10\tquantity_10\n"
    "2055\t92.5\tMax\tMustermann\tmax-musterman@gmail.com\t878\t"
    "12:30-12:45\tzum_mitnehmen\t10\t0\t2026-03-18 15:27:59\t"
    "Zanderfilet gebacken\t3\tKartoffelsalat\t2\tSchollenfilet gebacken\t1\t"
    "Merlanfilet gebacken\t1\tSelbstgeräucherte Forelle - Abholung 12-13:30 Uhr\t2\t"
    "Selbstgeräucherte Dorade - Abholung 12-13:30 Uhr\t1\t"
    "NULL\tNULL\tNULL\tNULL\tNULL\tNULL\tNULL\tNULL"
)


def test_parse_real_export_format() -> None:
    service = CsvImportService()
    orders = service.parse(SAMPLE_TSV)
    assert len(orders) == 1
    order = orders[0]
    assert order.order_id == "2055"
    assert float(order.net_total) == 92.5
    assert order.first_name == "Max"
    assert order.last_name == "Mustermann"
    assert order.email == "max-musterman@gmail.com"
    assert order.abholzeit == "12:30-12:45"
    assert order.togo == "zum_mitnehmen"
    assert order.returning_customer is False


def test_parse_ignores_null_item_slots() -> None:
    service = CsvImportService()
    orders = service.parse(SAMPLE_TSV)
    # item_7 bis item_10 sind NULL → werden ignoriert
    assert len(orders[0].items) == 6


def test_parse_items_correctly() -> None:
    service = CsvImportService()
    items = service.parse(SAMPLE_TSV)[0].items
    assert items[0] == {"name": "Zanderfilet gebacken", "quantity": 3}
    assert items[4] == {
        "name": "Selbstgeräucherte Forelle - Abholung 12-13:30 Uhr",
        "quantity": 2,
    }


def test_parse_normalizes_email() -> None:
    service = CsvImportService()
    order = service.parse(SAMPLE_TSV)[0]
    assert order.email == order.email.lower()


def test_parse_date_paid() -> None:
    from datetime import UTC

    service = CsvImportService()
    order = service.parse(SAMPLE_TSV)[0]
    assert order.date_paid is not None
    assert order.date_paid.tzinfo == UTC
    assert order.date_paid.year == 2026
    assert order.date_paid.month == 3
    assert order.date_paid.day == 18


def test_import_to_db(db: Session) -> None:
    service = CsvImportService()
    count = service.import_to_db(SAMPLE_TSV, db)
    assert count == 1


def test_import_replace_clears_existing(db: Session) -> None:
    service = CsvImportService()
    service.import_to_db(SAMPLE_TSV, db)
    count = service.import_to_db(SAMPLE_TSV, db, replace=True)
    assert count == 1
