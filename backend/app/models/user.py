# Tabla de usuarios del sistema — FUTURO
# Quién puede acceder al sistema y con qué rol

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(200), nullable=False)
    password_hash = Column(String(255), nullable=False)  # NUNCA guardar contraseñas en texto plano
    role = Column(String(20), nullable=False, default="operator")  # "admin", "operator", "viewer"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # ¿A qué local pertenece este usuario?
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    store = relationship("Store", back_populates="users")

    # Un usuario puede realizar muchos movimientos
    movements = relationship("Movement", back_populates="user")
