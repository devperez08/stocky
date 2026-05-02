import re
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import create_access_token, hash_password, verify_password, get_current_store_id
from backend.app.models.store import PlanStatus, Store

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

class SignupRequest(BaseModel):
    store_name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimo 8 caracteres")

def _slugify_store_name(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "store"

def _build_unique_slug(db: Session, store_name: str) -> str:
    base_slug = _slugify_store_name(store_name)
    candidate = base_slug
    suffix = 2
    while db.query(Store).filter(Store.slug == candidate).first():
        candidate = f"{base_slug}-{suffix}"
        suffix += 1
    return candidate

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(Store).filter(Store.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta registrada con este correo electronico."
        )

    today = date.today()
    new_store = Store(
        name=data.store_name,
        slug=_build_unique_slug(db, data.store_name),
        email=data.email,
        password_hash=hash_password(data.password),
        trial_start_date=today,
        subscription_expiry_date=today + timedelta(days=14),
        plan_status=PlanStatus.TRIAL,
    )
    db.add(new_store)
    db.commit()
    db.refresh(new_store)

    token = create_access_token(
        {"store_id": new_store.id, "email": new_store.email, "sub": str(new_store.id)}
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "store_name": new_store.name,
        "trial_expires": str(new_store.subscription_expiry_date),
        "days_remaining": new_store.days_remaining,
    }

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint temporal de login.
    En este MVP, el 'username' es el email de la tienda.
    Busca la tienda por email y verifica el hash de la contraseña.
    Retorna un JWT con el ID de la tienda en el campo 'sub'.
    """
    # Buscamos la tienda por email
    store = db.query(Store).filter(Store.email == form_data.username).first()
    
    if not store or not verify_password(form_data.password, store.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas. Verifica tu correo y contrasena.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    plan_status = store.plan_status.value if hasattr(store.plan_status, "value") else str(store.plan_status)
    token = create_access_token(
        data={
            "store_id": store.id,
            "email": store.email,
            "store_name": store.name,
            "plan_status": plan_status,
            "sub": str(store.id),
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "store_name": store.name,
        "plan_status": plan_status,
        "days_remaining": store.days_remaining,
    }

@router.post("/token", include_in_schema=False)
def oauth2_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Alias OAuth2 para Swagger/UI y clientes estandar.
    Reutiliza exactamente la misma logica de /auth/login.
    """
    return login(form_data=form_data, db=db)

@router.get("/me")
def get_current_store(
    store_id: int = Depends(get_current_store_id),
    db: Session = Depends(get_db)
):
    """
    Retorna la información detallada de la tienda actual autenticada.
    Utilizado por el panel de configuración/suscripción.
    """
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
        
    return {
        "id": store.id,
        "name": store.name,
        "email": store.email,
        "plan_status": store.plan_status.value if hasattr(store.plan_status, "value") else str(store.plan_status),
        "subscription_expiry_date": str(store.subscription_expiry_date),
        "days_remaining": store.days_remaining,
        "trial_start_date": str(store.trial_start_date)
    }
