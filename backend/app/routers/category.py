# router: Endpoints para la gestión de categorías
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from backend.app.core.security import get_current_store_id
from backend.app.schemas.category import CategoryResponse, CategoryCreate, CategoryUpdate
from backend.app.services import category as category_service

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)

@router.get("/", response_model=List[CategoryResponse])
def read_categories(
    db: Session = Depends(get_db),
    store_id: int = Depends(get_current_store_id)
):
    """Lista todas las categorías de la tienda autenticada"""
    return category_service.get_categories(db, store_id=store_id)

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate, 
    db: Session = Depends(get_db),
    store_id: int = Depends(get_current_store_id)
):
    """Crea una nueva categoría para la tienda (Inyecta store_id del token)"""
    return category_service.create_category(db, category_data=category, store_id=store_id)

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int, 
    category: CategoryUpdate, 
    db: Session = Depends(get_db),
    store_id: int = Depends(get_current_store_id)
):
    """Actualiza una categoría propia"""
    db_category = category_service.update_category(
        db, 
        category_id=category_id, 
        category_data=category, 
        store_id=store_id
    )
    if not db_category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return db_category

@router.delete("/{category_id}")
def delete_category(
    category_id: int, 
    db: Session = Depends(get_db),
    store_id: int = Depends(get_current_store_id)
):
    """Elimina una categoría propia si no tiene productos activos"""
    db_category = category_service.delete_category(db, category_id=category_id, store_id=store_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return {"message": f"Categoría '{db_category.name}' eliminada exitosamente"}
