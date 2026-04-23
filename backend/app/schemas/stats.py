from pydantic import BaseModel, Field
from typing import List, Dict

class LowStockProduct(BaseModel):
    id: int
    name: str = Field(..., description="Nombre del producto en estado crítico")
    stock: int = Field(..., description="Cantidad actual en inventario")
    alert: int = Field(..., description="Umbral mínimo configurado")

    class Config:
        from_attributes = True

class MovementsLast24h(BaseModel):
    entries: int = Field(default=0, description="Total de entradas en las últimas 24 hrs")
    exits: int = Field(default=0, description="Total de salidas (ventas) en las últimas 24 hrs")

class StatsSummary(BaseModel):
    total_inventory_value: float = Field(..., description="Valor total en dinero del inventario (precio unitario * stock)")
    total_sales_revenue: float = Field(default=0.0, description="Total recaudado por ventas (salidas de stock)")
    total_active_products: int = Field(..., description="Cantidad total de productos activos en catálogo")
    critical_stock_count: int = Field(..., description="Cuántos productos están por debajo de su umbral de alerta")
    low_stock_products: List[LowStockProduct] = Field(..., description="Top 5 productos con el inventario más bajo")
    movements_last_24h: MovementsLast24h = Field(..., description="Actividad del sistema en las últimas 24 horas")
