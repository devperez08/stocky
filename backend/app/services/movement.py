from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from backend.app.models.movement import Movement, MovementType
from backend.app.models.product import Product
from backend.app.schemas.movement import MovementCreate

def create_movement(db: Session, movement_data: MovementCreate, store_id: int):
    """
    Crea un registro de movimiento y actualiza atómicamente el stock del producto de la tienda.
    """
    # 1. Asegurar que el producto pertenece a la tienda y está activo.
    product = db.query(Product).filter(
        Product.id == movement_data.product_id, 
        Product.store_id == store_id,
        Product.is_active == True
    ).with_for_update().first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    # 2. Lógica de negocio
    if movement_data.movement_type == MovementType.EXIT:
        if product.stock_quantity < movement_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente. Disponible: {product.stock_quantity}"
            )
        product.stock_quantity -= movement_data.quantity
    else:  # ENTRY
        if movement_data.unit_value:
            product.price = movement_data.unit_value
        product.stock_quantity += movement_data.quantity

    # 3. Preparar registro histórico
    final_price = movement_data.unit_value or product.price

    new_movement = Movement(
        product_id=movement_data.product_id,
        store_id=store_id, # Inyectado
        quantity=movement_data.quantity,
        unit_price=final_price,
        movement_type=movement_data.movement_type,
        reason=movement_data.reason
    )

    db.add(new_movement)
    db.commit()
    db.refresh(new_movement)
    
    return {
        "id": new_movement.id,
        "product_id": new_movement.product_id,
        "product_name": product.name,
        "movement_type": new_movement.movement_type,
        "quantity": new_movement.quantity,
        "unit_price": float(new_movement.unit_price),
        "total_value": float(new_movement.quantity * new_movement.unit_price),
        "reason": new_movement.reason,
        "created_at": new_movement.created_at,
        "is_voided": new_movement.is_voided
    }

def get_movements(
    db: Session, 
    store_id: int,
    product_id: Optional[int] = None, 
    movement_type: Optional[MovementType] = None, 
    date_from: Optional[datetime] = None, 
    date_to: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
):
    """Obtiene los movimientos de la tienda."""
    query = db.query(Movement).options(joinedload(Movement.product)).filter(
        Movement.store_id == store_id
    )
    
    if product_id:
        query = query.filter(Movement.product_id == product_id)
    if movement_type:
        query = query.filter(Movement.movement_type == movement_type)
    if date_from:
        query = query.filter(Movement.created_at >= date_from)
    if date_to:
        query = query.filter(Movement.created_at <= date_to)
        
    movements = query.order_by(Movement.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": m.id,
            "product_id": m.product_id,
            "product_name": m.product.name if m.product else "Desconocido",
            "movement_type": m.movement_type,
            "quantity": m.quantity,
            "unit_price": float(m.unit_price),
            "total_value": float(m.quantity * m.unit_price),
            "reason": m.reason,
            "created_at": m.created_at,
            "is_voided": m.is_voided
        }
        for m in movements
    ]
