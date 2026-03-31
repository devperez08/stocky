"""
¿Por qué separar el modelo ORM de los schemas Pydantic?
El modelo ORM representa la TABLA en la base de datos.
Los schemas Pydantic representan los CONTRATOS de la API (lo que entra y sale).
Mezclarlos crea acoplamiento: si cambias la DB, rompes la API, y viceversa.
"""
from datetime import datetime
from sqlalchemy import String, Float, Integer, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Product(Base):
    """
    Tabla `products` en la base de datos.

    Usamos `Mapped` y `mapped_column` de SQLAlchemy 2.0 (estilo moderno).
    Esto da tipado estático completo y es más explícito que el estilo 1.x.
    """
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    name: Mapped[str] = mapped_column(
        String(200), unique=True, nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ¿Por qué Float y no Decimal?
    # Para este proyecto de inventario, Float es suficiente.
    # En sistemas financieros críticos usaríamos Decimal para evitar errores de redondeo.
    price: Mapped[float] = mapped_column(Float, nullable=False)

    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Umbral para alertas futuras: cuando stock <= low_stock_threshold,
    # el sistema podrá enviar notificaciones. Lo diseñamos desde YA.
    low_stock_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=10)

    # server_default=func.now() → la DB pone el timestamp, no Python.
    # Esto es más confiable porque no depende del reloj del servidor de aplicaciones.
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} name='{self.name}' stock={self.stock}>"
