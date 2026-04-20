from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from backend.app.models.movement import Movement, MovementType
from backend.app.models.product import Product
from backend.app.schemas.movement import MovementCreate

def create_movement(db: Session, movement_data: MovementCreate):
    """
    Crea un registro de movimiento y actualiza atómicamente el stock del producto.
    Lanza HTTPException(404) si el producto no existe o está inactivo.
    Lanza HTTPException(400) si es una SALIDA y no hay suficiente stock.
    """
    # 1. Bloquear y asegurar que el producto existe/está activo.
    product = db.query(Product).filter(
        Product.id == movement_data.product_id, 
        Product.is_active == True
    ).with_for_update().first() # Usar with_for_update() asegura concurrencia a nivel BD

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    # 2. Lógica de negocio (entradas suman, salidas restan) y validación (PRO-70)
    if movement_data.movement_type == MovementType.EXIT:
        if product.stock_quantity < movement_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente. Disponible: {product.stock_quantity}, solicitado: {movement_data.quantity}"
            )
        product.stock_quantity -= movement_data.quantity
    else:  # MovementType.ENTRY
        product.stock_quantity += movement_data.quantity

    # 3. Preparar registro histórico
    new_movement = Movement(
        product_id=movement_data.product_id,
        quantity=movement_data.quantity,
        movement_type=movement_data.movement_type,
        reason=movement_data.reason
        # asumiendo que store_id & user_id aún no son requeridos en esta iteración.
    )

    # 4. Comprometer la Transacción (Atómica)
    db.add(new_movement)
    # Se ejecuta todo en bloque (Actualizar el Producto + Insertar el Movimiento). Si algo falla, se hace rollback automático
    db.commit()
    db.refresh(new_movement)
    
    # Pre-cargar el nombre para la respuesta
    return {
        "id": new_movement.id,
        "product_id": new_movement.product_id,
        "product_name": product.name,
        "movement_type": new_movement.movement_type,
        "quantity": new_movement.quantity,
        "reason": new_movement.reason,
        "created_at": new_movement.created_at
    }

def get_movements(
    db: Session, 
    product_id: Optional[int] = None, 
    movement_type: Optional[MovementType] = None, 
    date_from: Optional[datetime] = None, 
    date_to: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
):
    """Obtiene los movimientos del inventario filtrados dinámicamente y con la relación 'product' cargada."""
    # Usamos joinedload para evitar consultas N+1 y optimizar el aplanamiento del nombre del producto
    query = db.query(Movement).options(joinedload(Movement.product))
    
    if product_id:
        query = query.filter(Movement.product_id == product_id)
    if movement_type:
        query = query.filter(Movement.movement_type == movement_type)
    if date_from:
        query = query.filter(Movement.created_at >= date_from)
    if date_to:
        query = query.filter(Movement.created_at <= date_to)
        
    movements = query.order_by(Movement.created_at.desc()).offset(skip).limit(limit).all()
    
    # Adaptar para cumplir MovementResponse
    results = []
    for m in movements:
        results.append({
            "id": m.id,
            "product_id": m.product_id,
            "product_name": m.product.name if m.product else "Desconocido",
            "movement_type": m.movement_type,
            "quantity": m.quantity,
            "reason": m.reason,
            "created_at": m.created_at
        })
    return results
