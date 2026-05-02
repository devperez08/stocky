# =============================================================================
# Modelo: Store (Tienda / Tenant)
# =============================================================================
# Representa cada negocio que usa Stocky como SaaS.
# Contiene:
#   - Datos del negocio (nombre, slug, contacto)
#   - Credenciales de acceso del administrador de la tienda
#   - Lógica SaaS: trial de 14 días y ciclo de suscripción
# =============================================================================

from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime,
    CheckConstraint, func
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
import datetime


class Store(Base):
    __tablename__ = "stores"
    __table_args__ = (
        CheckConstraint(
            "plan_status IN ('trial', 'active', 'expired')",
            name="ck_stores_plan_status"
        ),
    )

    id   = Column(Integer, primary_key=True, index=True)

    # ── Datos del negocio ────────────────────────────────────────────────────
    name    = Column(String(200), nullable=False)
    slug    = Column(String(100), unique=True, nullable=False)   # URL amigable  ej: "tienda-juan"
    address = Column(String(500), nullable=True)
    phone   = Column(String(20),  nullable=True)

    # ── Acceso / Auth del administrador de la tienda ─────────────────────────
    email         = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)          # NUNCA texto plano

    # ── SaaS: Trial y Suscripción ────────────────────────────────────────────
    trial_start_date         = Column(Date, nullable=False, default=datetime.date.today)
    subscription_expiry_date = Column(
        Date,
        nullable=False,
        default=lambda: datetime.date.today() + datetime.timedelta(days=14)
    )
    plan_status = Column(
        String(20),
        nullable=False,
        default="trial"   # trial → active → expired
    )

    # ── Estado y auditoría ───────────────────────────────────────────────────
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # ── Relaciones (un Store tiene muchos de cada tipo) ──────────────────────
    categories = relationship("Category",  back_populates="store", cascade="all, delete-orphan")
    products   = relationship("Product",   back_populates="store", cascade="all, delete-orphan")
    movements  = relationship("Movement",  back_populates="store", cascade="all, delete-orphan")
    users      = relationship("User",      back_populates="store")
    suppliers  = relationship("Supplier",  back_populates="store")
