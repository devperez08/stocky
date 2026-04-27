from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from backend.app.models.movement import MovementType

class MovementCreate(BaseModel):
    product_id: int = Field(..., description="ID del producto que se va a mover")
    movement_type: MovementType = Field(..., description="'entry' (entrada/compra) o 'exit' (salida/venta)")
    quantity: int = Field(..., gt=0, description="La cantidad a mover debe ser estrictamente mayor a 0")
    unit_price: Optional[float] = Field(None, description="Precio unitario. Si no se provee, asume el precio o costo actual del producto.")
    reason: Optional[str] = Field(None, max_length=255, description="Motivo (ej: Compra al por mayor, Venta, Pérdida)")

    class Config:
        use_enum_values = True

class MovementResponse(BaseModel):
    id: int
    product_id: int
    product_name: str  # Campo calculado para que el FE no tenga que hacer joins manuales
    movement_type: MovementType
    quantity: int
    unit_price: float
    total_value: float = 0.0
    reason: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True
