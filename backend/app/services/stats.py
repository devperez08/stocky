from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from backend.app.models.product import Product
from backend.app.models.movement import Movement

def get_dashboard_summary(db: Session, store_id: int) -> dict:
    """
    Calcula KPIs del Dashboard filtrados estrictamente por tienda.
    """
    # 1. Valor total del inventario propio
    total_value = db.query(
        func.sum(Product.price * Product.stock_quantity)
    ).filter(Product.is_active == True, Product.store_id == store_id).scalar() or 0.0

    # 2. Conteo total de productos activos en la tienda
    total_products = db.query(func.count(Product.id)).filter(
        Product.is_active == True,
        Product.store_id == store_id
    ).scalar() or 0

    # 3. Alertas de inventario crítico de la tienda
    critical_stock_count = db.query(func.count(Product.id)).filter(
        Product.is_active == True,
        Product.store_id == store_id,
        Product.stock_quantity <= Product.min_stock_alert
    ).scalar() or 0

    # 4. Top 5 productos críticos
    low_stock_products_db = db.query(Product).filter(
        Product.is_active == True,
        Product.store_id == store_id,
        Product.stock_quantity <= Product.min_stock_alert
    ).order_by(Product.stock_quantity.asc()).limit(5).all()

    low_stock_products = [
        {"id": p.id, "name": p.name, "stock": p.stock_quantity, "alert": p.min_stock_alert}
        for p in low_stock_products_db
    ]

    # 5. Actividad reciente (24h) de la tienda
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    movements_24h = db.query(
        Movement.movement_type,
        func.count(Movement.id).label("count")
    ).filter(
        Movement.created_at >= since,
        Movement.store_id == store_id,
        Movement.is_voided == False
    ).group_by(Movement.movement_type).all()

    movements_dict = {str(m.movement_type.value): m.count for m in movements_24h}

    from backend.app.models.movement import MovementType
    # 6. Ingresos Totales por Ventas (30 días)
    since_30d = datetime.now(timezone.utc) - timedelta(days=30)
    total_revenue_30d = db.query(
        func.sum(Movement.unit_price * Movement.quantity)
    ).filter(
        Movement.movement_type == MovementType.EXIT,
        Movement.store_id == store_id,
        Movement.created_at >= since_30d,
        Movement.is_voided == False
    ).scalar() or 0.0

    # 7. Datos de ventas para gráfico (15 días)
    since_15d = datetime.now(timezone.utc) - timedelta(days=15)
    recent_movements = db.query(
        Movement.created_at, Movement.unit_price, Movement.quantity, Movement.movement_type
    ).filter(
        Movement.created_at >= since_15d,
        Movement.store_id == store_id,
        Movement.is_voided == False
    ).all()

    sales_by_date = {}
    for i in range(15, -1, -1):
        dt = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
        sales_by_date[dt] = 0.0
        
    for m_date, m_uprice, m_qty, m_type in recent_movements:
        if m_date:
            dt_str = m_date.strftime("%Y-%m-%d")
            if dt_str in sales_by_date:
                val = float(m_qty * m_uprice)
                if m_type == MovementType.EXIT:
                    sales_by_date[dt_str] += val
                
    sales_chart_data = [{"date": k, "revenue": round(v, 2)} for k, v in sales_by_date.items()]

    return {
        "total_inventory_value": round(float(total_value), 2),
        "total_sales_revenue_30d": round(float(total_revenue_30d), 2),
        "total_active_products": total_products,
        "critical_stock_count": critical_stock_count,
        "low_stock_products": low_stock_products,
        "movements_last_24h": {
            "entries": movements_dict.get("entry", 0),
            "exits": movements_dict.get("exit", 0)
        },
        "sales_over_time": sales_chart_data
    }
