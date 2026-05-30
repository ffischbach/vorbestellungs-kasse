import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.jinja import templates
from app.repositories.order_repository import OrderRepository
from app.services.csv_import_service import CsvImportService
from app.services.printer_service import PrinterService

router = APIRouter(prefix="/admin", tags=["admin"])
_security = HTTPBasic()


def _require_admin(credentials: HTTPBasicCredentials = Depends(_security)) -> None:
    ok = secrets.compare_digest(
        credentials.password.encode(),
        settings.admin_password.encode(),
    )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falsches Passwort",
            headers={"WWW-Authenticate": "Basic"},
        )


@router.get("", response_class=HTMLResponse, dependencies=[Depends(_require_admin)])
async def admin_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "admin.html")


@router.get("/status", response_class=HTMLResponse)
async def printer_status(request: Request) -> HTMLResponse:
    printer = PrinterService()
    return templates.TemplateResponse(
        request, "partials/printer_status.html", {"available": printer.is_available()}
    )


@router.post("/import", response_class=HTMLResponse, dependencies=[Depends(_require_admin)])
async def import_csv(
    request: Request,
    file: UploadFile,
    replace: bool = True,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    try:
        content = (await file.read()).decode("utf-8")
        service = CsvImportService()
        count = service.import_to_db(content, db, replace=replace)
        return templates.TemplateResponse(request, "partials/import_result.html", {"count": count})
    except Exception as e:
        return templates.TemplateResponse(
            request, "partials/import_result.html", {"error": str(e)}, status_code=400
        )


@router.delete("/reset", response_class=HTMLResponse, dependencies=[Depends(_require_admin)])
async def reset_orders(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    try:
        OrderRepository(db).delete_all()
        return templates.TemplateResponse(request, "partials/reset_result.html", {})
    except Exception as e:
        return templates.TemplateResponse(
            request, "partials/reset_result.html", {"error": str(e)}, status_code=500
        )
