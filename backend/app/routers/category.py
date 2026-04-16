# router: Endpoints para la gestión de categorías
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from backend.app.schemas.category import CategoryResponse, CategoryCreate, CategoryUpdate
from backend.app.services import category as category_service

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)

@router.get("/", response_model=List[CategoryResponse])
def read_categories(db: Session = Depends(get_db)):
    """Lista todas las categorías registradas"""
    return category_service.get_categories(db)

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Crea una nueva categoría (Valida nombre único)"""
    return category_service.create_category(db, category_data=category)

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category: CategoryUpdate, db: Session = Depends(get_db)):
    """Actualiza parcialmente una categoría existente"""
    db_category = category_service.update_category(db, category_id=category_id, category_data=category)
    if not db_category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return db_category

@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """
    Elimina una categoría de forma permanente.
    Falla (400) si la categoría tiene productos activos asociados.
    """
    db_category = category_service.delete_category(db, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return {"message": f"Categoría '{db_category.name}' eliminada exitosamente"}
