import enum # Para definir las opciones permitidas
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, func, Float, Index, CheckConstraint
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

# Opciones permitidas para el tipo de movimiento
class MovementType(str, enum.Enum):
    ENTRY = "entry"   # Entrada de stock (compras)
    EXIT = "exit"     # Salida de stock (ventas)

class Movement(Base):
    __tablename__ = "movements"
    __table_args__ = (
        Index("ix_movements_product_id", "product_id"),
        Index("ix_movements_created_at", "created_at"),
        Index("ix_movements_type", "movement_type"),
        CheckConstraint("quantity > 0", name="ck_movements_quantity_positive"),
    )

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False, default=0.0)
    reason = Column(String(255), nullable=True)  # Motivo: "Compra a proveedor", "Venta a cliente"
    movement_type = Column(Enum(MovementType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # --- RELACIONES ---
    # Multi-tenant
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    store = relationship("Store", back_populates="movements")

    # ¿Qué producto se movió?
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Relación para que el movimiento sepa de qué producto es
    product = relationship("Product", back_populates="movements")

    # ¿Quién realizó el movimiento? (FUTURO)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="movements")
