from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from backend.app.core.database import get_db
from backend.app.schemas.movement import MovementResponse, MovementCreate
from backend.app.services import movement as movement_service
from backend.app.models.movement import MovementType

router = APIRouter(
    prefix="/movements",
    tags=["movements"]
)

@router.post("/", response_model=MovementResponse, status_code=201)
def create_movement(movement: MovementCreate, db: Session = Depends(get_db)):
    """
    Registra una entrada (entry) o salida (exit) de inventario.
    Actualiza el stock del producto de forma atómica.
    - Fallará (404) si el producto no existe/está inactivo.
    - Fallará (400) si es salida y excede el stock actual.
    """
    return movement_service.create_movement(db=db, movement_data=movement)

@router.get("/", response_model=List[MovementResponse])
def get_movements(
    product_id: Optional[int] = Query(None, description="Filtrar por ID de producto"),
    movement_type: Optional[MovementType] = Query(None, description="Filtrar por 'entry' o 'exit'"),
    date_from: Optional[datetime] = Query(None, description="Desde fecha"),
    date_to: Optional[datetime] = Query(None, description="Hasta fecha"),
    skip: int = Query(0, ge=0),
    limit: int = Query(500, le=1000),
    db: Session = Depends(get_db)
):
    """
    Devuelve un historial interactivo del inventario. 
    Soporta múltiples filtros simultáneamente.
    """
    return movement_service.get_movements(
        db=db, 
        product_id=product_id, 
        movement_type=movement_type,
        date_from=date_from, 
        date_to=date_to, 
        skip=skip, 
        limit=limit
    )

@router.get("/product/{product_id}", response_model=List[MovementResponse])
def get_product_movements(
    product_id: int, 
    skip: int = Query(0, ge=0), 
    limit: int = Query(500, le=1000), 
    db: Session = Depends(get_db)
):
    """Atajo para ver rápidamente los movimientos de un producto en particular."""
    return movement_service.get_movements(
        db=db, 
        product_id=product_id, 
        skip=skip, 
        limit=limit
    )
