from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.jinja import templates
from app.routers.sse import broadcaster
from app.services.order_service import (
    OrderAlreadyPickedUpError,
    OrderNotFoundError,
    OrderService,
)

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html")


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
