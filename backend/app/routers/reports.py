import io
import pandas as pd
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from backend.app.core.database import get_db
from backend.app.core.security import get_current_store_id
from backend.app.models.product import Product
from backend.app.models.movement import Movement, MovementType

router = APIRouter(
    prefix="/reports",
    tags=["reports"]
)

def _build_streaming_response(buffer, fmt: str, filename_base: str):
    if fmt == "csv":
        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename_base}.csv"}
        )
    else:  # excel
        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.read()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename_base}.xlsx"}
        )

@router.get("/inventory")
def inventory_report(
    format: str = Query("json", description="Formato de salida: 'json', 'csv' o 'excel'"),
    db: Session = Depends(get_db),
    store_id: int = Depends(get_current_store_id)
):
    """Reporte de inventario filtrado por tienda."""
    products = db.query(Product).options(
        joinedload(Product.category)
    ).filter(Product.is_active == True, Product.store_id == store_id).all()

    data = [
        {
            "id": p.id,
            "nombre": p.name,
            "sku": p.sku,
            "categoria": p.category.name if p.category else "Sin categoría",
            "precio_unitario": p.price,
            "stock_actual": p.stock_quantity,
            "valor_total": round(p.price * p.stock_quantity, 2),
            "alerta_minima": p.min_stock_alert,
            "estado_stock": "⚠️ Crítico" if p.stock_quantity <= p.min_stock_alert else "✅ Normal",
            "creado_en": p.created_at.strftime("%Y-%m-%d") if p.created_at else None
        }
        for p in products
    ]

    if format == "json":
        return data

    df = pd.DataFrame(data)
    if format == "csv":
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, encoding="utf-8-sig")
        return _build_streaming_response(buffer, "csv", "inventario_stocky")
    elif format == "excel":
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Inventario")
        return _build_streaming_response(buffer, "excel", "inventario_stocky")

@router.get("/movements")
def movements_report(
    format: str = Query("json", description="Formato de salida: 'json', 'csv' o 'excel'"),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    store_id: int = Depends(get_current_store_id)
):
    """Reporte de movimientos filtrado por tienda."""
    query = db.query(Movement).options(joinedload(Movement.product)).filter(
        Movement.store_id == store_id
    )

    if date_from:
        query = query.filter(Movement.created_at >= date_from)
    if date_to:
        query = query.filter(Movement.created_at <= date_to)

    movements = query.order_by(Movement.created_at.desc()).all()

    data = [
        {
            "id": m.id,
            "producto": m.product.name if m.product else "Desconocido",
            "tipo": "Entrada" if m.movement_type == MovementType.ENTRY else "Salida",
            "cantidad": m.quantity,
            "precio_unidad": float(m.unit_price),
            "total": float(m.quantity * m.unit_price),
            "motivo": m.reason or "Sin especificar",
            "fecha": m.created_at.strftime("%Y-%m-%d %H:%M") if m.created_at else None
        }
        for m in movements
    ]

    if format == "json":
        return data

    df = pd.DataFrame(data)
    if format == "csv":
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, encoding="utf-8-sig")
        return _build_streaming_response(buffer, "csv", "movimientos_stocky")
    elif format == "excel":
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Movimientos")
        return _build_streaming_response(buffer, "excel", "movimientos_stocky")
