from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.jinja import templates
from app.routers.sse import broadcaster
from app.services.order_service import (
    OrderAlreadyHandedOutError,
    OrderAlreadyPickedUpError,
    OrderNotFoundError,
    OrderNotPickedUpError,
    OrderService,
)
from app.services.printer_service import PrinterService

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html", {"active_page": "kasse"})


@router.get("/printer-status", response_class=HTMLResponse)
async def printer_status(request: Request) -> HTMLResponse:
    printer = PrinterService()
    return templates.TemplateResponse(
        request, "partials/printer_status.html", {"available": printer.is_available()}
    )


@router.get("/ausgabe", response_class=HTMLResponse)
async def ausgabe(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    service = OrderService(db)
    orders = service.get_waiting_handout()
    return templates.TemplateResponse(
        request, "ausgabe.html", {"orders": orders, "active_page": "ausgabe"}
    )


@router.get("/ausgabe/list", response_class=HTMLResponse)
async def ausgabe_list(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    service = OrderService(db)
    orders = service.get_waiting_handout()
    return templates.TemplateResponse(request, "partials/ausgabe_list.html", {"orders": orders})


@router.get("/orders/search", response_class=HTMLResponse)
async def search(request: Request, q: str = "", db: Session = Depends(get_db)) -> HTMLResponse:
    service = OrderService(db)
    orders = service.search(q) if q else []
    return templates.TemplateResponse(
        request, "partials/order_list.html", {"orders": orders, "query": q}
    )


@router.get("/orders/stats", response_class=HTMLResponse)
async def stats(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    service = OrderService(db)
    return templates.TemplateResponse(
        request, "partials/stats.html", {"stats": service.get_stats()}
    )


@router.get("/orders/overview", response_class=HTMLResponse)
async def overview(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    service = OrderService(db)
    data = service.get_overview()
    return templates.TemplateResponse(request, "partials/overview.html", data)


@router.get("/orders/{order_id}/card", response_class=HTMLResponse)
async def order_card(
    request: Request, order_id: int, db: Session = Depends(get_db)
) -> HTMLResponse:
    service = OrderService(db)
    try:
        order = service.get_by_id(order_id)
        return templates.TemplateResponse(request, "partials/order_card.html", {"order": order})
    except OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/orders/{order_id}/pickup", response_class=HTMLResponse)
async def pickup(request: Request, order_id: int, db: Session = Depends(get_db)) -> HTMLResponse:
    service = OrderService(db)
    try:
        order, printer_error = service.pickup(order_id)
        await broadcaster.broadcast({"type": "pickup", "order_id": order_id})
        return templates.TemplateResponse(
            request, "partials/order_card.html", {"order": order, "printer_error": printer_error}
        )
    except OrderAlreadyPickedUpError as e:
        return templates.TemplateResponse(
            request, "partials/error.html", {"message": str(e)}, status_code=409
        )
    except OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/orders/{order_id}/handout", response_class=HTMLResponse)
async def handout(request: Request, order_id: int, db: Session = Depends(get_db)) -> HTMLResponse:
    service = OrderService(db)
    try:
        service.hand_out(order_id)
        await broadcaster.broadcast({"type": "handout", "order_id": order_id})
        return HTMLResponse("")
    except OrderAlreadyHandedOutError as e:
        return templates.TemplateResponse(
            request, "partials/error.html", {"message": str(e)}, status_code=409
        )
    except OrderNotPickedUpError as e:
        return templates.TemplateResponse(
            request, "partials/error.html", {"message": str(e)}, status_code=400
        )
    except OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/orders/{order_id}/reprint", response_class=HTMLResponse)
async def reprint(request: Request, order_id: int, db: Session = Depends(get_db)) -> HTMLResponse:
    service = OrderService(db)
    try:
        order, printer_error = service.reprint(order_id)
        return templates.TemplateResponse(
            request, "partials/order_card.html", {"order": order, "printer_error": printer_error}
        )
    except OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
