from datetime import date
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_current_store_id
from backend.app.models.store import Store, PlanStatus

def check_subscription_active(
    store_id: int = Depends(get_current_store_id),
    db: Session = Depends(get_db)
) -> int:
    """
    Dependencia que verifica si la suscripción de la tienda está activa.
    Retorna el store_id si está activo, lanza HTTP 403 si expiró.
    """
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=401, detail="Tienda no encontrada")

    today = date.today()

    # Lazy update: marcar como expirado si la fecha ya pasó
    if store.subscription_expiry_date < today and store.plan_status != PlanStatus.EXPIRED:
        store.plan_status = PlanStatus.EXPIRED
        db.commit()

    if not store.is_subscription_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "subscription_expired",
                "message": (
                    "Tu período de prueba o suscripción ha vencido. "
                    "Activa tu plan para continuar gestionando tu inventario."
                ),
                "expiry_date": str(store.subscription_expiry_date),
                "days_overdue": abs(store.days_remaining)
            }
        )
    return store_id
