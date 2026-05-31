from datetime import datetime, timezone

from fastapi.templating import Jinja2Templates

from app.config import settings


def _utc_iso(dt: datetime | None) -> str:
    """Return ISO 8601 string with UTC offset, even for timezone-naive datetimes from SQLite."""
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


templates = Jinja2Templates(directory="app/templates")
templates.env.globals["settings"] = settings
templates.env.filters["utc_iso"] = _utc_iso
