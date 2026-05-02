from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from backend.app.core.database import get_db
from backend.app.core.subscription import check_subscription_active
from backend.app.schemas.movement import MovementResponse, MovementCreate
from backend.app.services import movement as movement_service
from backend.app.models.movement import MovementType

router = APIRouter(
    prefix="/movements",
    tags=["movements"]
)

@router.post("/", response_model=MovementResponse, status_code=201)
def create_movement(
    movement: MovementCreate, 
    db: Session = Depends(get_db),
    store_id: int = Depends(check_subscription_active)
):
    """Registra una entrada o salida inyectando store_id."""
    return movement_service.create_movement(db=db, movement_data=movement, store_id=store_id)

@router.get("/", response_model=List[MovementResponse])
def get_movements(
    product_id: Optional[int] = Query(None, description="Filtrar por ID de producto"),
    movement_type: Optional[MovementType] = Query(None, description="Filtrar por 'entry' o 'exit'"),
    date_from: Optional[datetime] = Query(None, description="Desde fecha"),
    date_to: Optional[datetime] = Query(None, description="Hasta fecha"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    store_id: int = Depends(check_subscription_active)
):
    """Devuelve historial de movimientos de la tienda."""
    return movement_service.get_movements(
        db=db, 
        store_id=store_id,
        product_id=product_id, 
        movement_type=movement_type,
        date_from=date_from, 
        date_to=date_to, 
        skip=skip, 
        limit=limit
    )

@router.delete("/{movement_id}", status_code=200)
def void_movement(
    movement_id: int, 
    db: Session = Depends(get_db),
    store_id: int = Depends(check_subscription_active)
):
    """Anula un movimiento propio y revierte el stock."""
    from backend.app.models.movement import Movement
    from backend.app.models.product import Product
    
    movement = db.query(Movement).filter(
        Movement.id == movement_id,
        Movement.store_id == store_id,
        Movement.is_voided == False
    ).first()
    
    if not movement:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado o ya anulado")

    product = db.query(Product).filter(
        Product.id == movement.product_id,
        Product.store_id == store_id
    ).first()

    if movement.movement_type == MovementType.EXIT:
        product.stock_quantity += movement.quantity
        inverse_type = MovementType.ENTRY
    else:
        if product.stock_quantity < movement.quantity:
            raise HTTPException(status_code=400, detail="Stock insuficiente para revertir")
        product.stock_quantity -= movement.quantity
        inverse_type = MovementType.EXIT

    inverse_movement = Movement(
        product_id=movement.product_id,
        store_id=store_id,
        movement_type=inverse_type,
        quantity=movement.quantity,
        unit_price=movement.unit_price,
        reason=f"🔄 Anulación automática del movimiento #{movement_id}",
    )
    db.add(inverse_movement)
    movement.is_voided = True
    movement.voided_at = datetime.utcnow()

    db.commit()
    return {"message": "Movimiento anulado correctamente"}
