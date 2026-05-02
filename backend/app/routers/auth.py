from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import create_access_token, verify_password
from backend.app.models.store import Store

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

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
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Creamos el token. El 'sub' (subject) será el ID de la tienda convertido a string.
    access_token = create_access_token(data={"sub": str(store.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "store_name": store.name
    }
