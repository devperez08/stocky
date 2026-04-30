from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime
from backend.app.models.movement import MovementType

class MovementCreate(BaseModel):
    product_id: int = Field(..., description="ID del producto que se va a mover")
    movement_type: MovementType = Field(..., description="'entry' (entrada/compra) o 'exit' (salida/venta)")
    quantity: int = Field(..., gt=0, description="La cantidad a mover debe ser estrictamente mayor a 0")
    unit_value: Optional[float] = Field(None, gt=0, description="Obligatorio para entradas")
    reason: Optional[str] = Field(None, max_length=255, description="Motivo (ej: Compra al por mayor, Venta, Pérdida)")

    @model_validator(mode="after")
    def validate_unit_value_for_entry(self) -> "MovementCreate":
        if self.movement_type == MovementType.ENTRY and self.unit_value is None:
            raise ValueError("El campo 'unit_value' es obligatorio para movimientos de entrada.")
        return self

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
    is_voided: bool = False

    class Config:
        from_attributes = True
