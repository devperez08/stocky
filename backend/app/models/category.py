# Tabla de categorías — MVP
# Agrupa los productos (ej: "Bebidas", "Electrónica", "Calzado")

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func # Column para definir las columnas, Integer para números enteros, String para texto, DateTime para fechas, ForeignKey para llaves foráneas, func para funciones de base de datos
from backend.app.core.database import Base # Importamos la base que acabas de crear
from sqlalchemy.orm import relationship

class Category(Base):
    __tablename__ = "categories" # Nombre de la tabla en la base de datos

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Multi-tenant: ¿A qué local pertenece esta categoría?
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, index=True)
    store = relationship("Store", back_populates="categories")

    # Una categoría agrupa muchos productos
    products = relationship("Product", back_populates="category")
