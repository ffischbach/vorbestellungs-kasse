from fastapi import APIRouter, Depends, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.csv_import_service import CsvImportService
from app.services.printer_service import PrinterService

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def admin_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "admin.html")


@router.get("/status", response_class=HTMLResponse)
async def printer_status(request: Request) -> HTMLResponse:
    printer = PrinterService()
    return templates.TemplateResponse(
        request, "partials/printer_status.html", {"available": printer.is_available()}
    )


@router.post("/import", response_class=HTMLResponse)
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
        return templates.TemplateResponse(
            request, "partials/import_result.html", {"count": count}
        )
    except Exception as e:
        return templates.TemplateResponse(
            request, "partials/import_result.html", {"error": str(e)}, status_code=400
        )
