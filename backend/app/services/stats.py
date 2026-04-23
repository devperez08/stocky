from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from backend.app.models.product import Product
from backend.app.models.movement import Movement
from backend.app.schemas.stats import StatsSummary, LowStockProduct, MovementsLast24h

def get_dashboard_summary(db: Session) -> dict:
    """
    Calcula y agrega todos los KPIs centrales del inventario en una única consulta transaccional.
    Esto evita hacer múltiples round-trips a la base de datos desde el frontend.
    """
    # 1. Valor total del inventario (Precio * Cantidad)
    # COALESCE / or 0.0 evita retornar None si no hay inventario
    total_value = db.query(
        func.sum(Product.price * Product.stock_quantity)
    ).filter(Product.is_active == True).scalar() or 0.0

    # 2. Conteo total de productos activos en catálogo
    total_products = db.query(func.count(Product.id)).filter(
        Product.is_active == True
    ).scalar() or 0

    # 3. Alertas de inventario crítico
    critical_stock_count = db.query(func.count(Product.id)).filter(
        Product.is_active == True,
        Product.stock_quantity <= Product.min_stock_alert
    ).scalar() or 0

    # 4. Top 5 productos críticos (ordenados por el de menor stock)
    low_stock_products_db = db.query(Product).filter(
        Product.is_active == True
    ).order_by(Product.stock_quantity.asc()).limit(5).all()

    # Formateo manual para calzar con el schema LowStockProduct
    low_stock_products = [
        {"id": p.id, "name": p.name, "stock": p.stock_quantity, "alert": p.min_stock_alert}
        for p in low_stock_products_db
    ]

    # 5. Actividad reciente: Movimientos agrupalos por tipo en las últimas 24H
    since = datetime.utcnow() - timedelta(hours=24)
    # Genera una lista de tuplas [(MovementType.ENTRY, 5), (MovementType.EXIT, 12)]
    movements_24h = db.query(
        Movement.movement_type,
        func.count(Movement.id).label("count")
    ).filter(Movement.created_at >= since).group_by(Movement.movement_type).all()

    # Convertimos la lista de tuplas a un diccionario amigable { "entry": 5, "exit": 12 }
    movements_dict = {str(m.movement_type.value): m.count for m in movements_24h}

    from backend.app.models.movement import MovementType
    # 6. Ingresos Totales por Ventas (Salidas)
    total_revenue = db.query(
        func.sum(Product.price * Movement.quantity)
    ).join(Movement, Movement.product_id == Product.id).filter(
        Movement.movement_type == MovementType.EXIT
    ).scalar() or 0.0

    # Empaquetamos todo
    return {
        "total_inventory_value": round(float(total_value), 2),
        "total_sales_revenue": round(float(total_revenue), 2),
        "total_active_products": total_products,
        "critical_stock_count": critical_stock_count,
        "low_stock_products": low_stock_products,
        "movements_last_24h": {
            "entries": movements_dict.get("entry", 0),
            "exits": movements_dict.get("exit", 0)
        }
    }
