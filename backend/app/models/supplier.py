# Tabla de proveedores — FUTURO
# De quién se compra la mercancía

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    contact_name = Column(String(200), nullable=True)  # Persona de contacto
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # ¿A qué local pertenece este proveedor?
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    store = relationship("Store", back_populates="suppliers")

    # Un proveedor puede suministrar muchos productos
    products = relationship("Product", back_populates="supplier")
