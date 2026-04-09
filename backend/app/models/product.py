from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    sku = Column(String(100), unique=True, nullable=False)  # Código de barras / Identificador único
    description = Column(String(500), nullable=True)
    price = Column(Float, nullable=False, default=0.0)  # Precio de venta
    cost_price = Column(Float, nullable=True, default=0.0)  # Precio de compra (para calcular margen de ganancia)
    stock_quantity = Column(Integer, nullable=False, default=0)
    min_stock_alert = Column(Integer, nullable=False, default=5)  # Umbral de alerta de stock bajo
    is_active = Column(Boolean, default=True)  # Soft-delete: desactivar sin borrar

    # --- LA CONEXIÓN (relaciones) ---
    # Foreignkey nombre de la tabla y la columna destino (categories.id)
    # id_categoria_padre es el nombre de la columna que se va a crear en la tabla products
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    store = relationship("Store", back_populates="products")

    # ¿A qué categoría pertenece?
    # Multi-tenant
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    store = relationship("Store", back_populates="products")

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # relationship nombre de la clase y la columna destino. back_populates es la tabla que tiene la relacion
    # category es el nombre de la relacion
    category = relationship("Category", back_populates="products")

    # ¿Quién lo provee? (FUTURO)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    supplier = relationship("Supplier", back_populates="products")

    # Historial de movimientos de este producto
    movements = relationship("Movement", back_populates="product")

    # Fechas automáticas
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
