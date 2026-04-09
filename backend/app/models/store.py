# Tabla de tiendas/locales (Multi-Tenant) — FUTURO
# Cada local que alquile Stocky tendrá un registro aquí

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)  # URL amigable (ej: "tienda-juan")
    address = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones: Un local tiene muchos usuarios, categorías, productos, proveedores
    users = relationship("User", back_populates="store")
    categories = relationship("Category", back_populates="store")
    products = relationship("Product", back_populates="store")
    suppliers = relationship("Supplier", back_populates="store")
    movements = relationship("Movement", back_populates="store")
