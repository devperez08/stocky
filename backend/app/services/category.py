# service: Lógica de negocio para Categorías y comunicación con la DB
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.models.category import Category
from backend.app.models.product import Product
from backend.app.schemas.category import CategoryCreate, CategoryUpdate

def get_categories(db: Session):
    """Retorna todas las categorías"""
    return db.query(Category).all()

def get_category_by_id(db: Session, category_id: int):
    """Busca una categoría por ID"""
    return db.query(Category).filter(Category.id == category_id).first()

def get_category_by_name(db: Session, name: str):
    """Busca una categoría por nombre para validar unicidad"""
    return db.query(Category).filter(Category.name == name).first()

def create_category(db: Session, category_data: CategoryCreate):
    """Crea una categoría verificando que el nombre sea único (PRO-68)"""
    # 1. Validar nombre único
    existing = get_category_by_name(db, category_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una categoría con el nombre '{category_data.name}'"
        )
    
    # 2. Persistir
    new_category = Category(**category_data.model_dump())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

def update_category(db: Session, category_id: int, category_data: CategoryUpdate):
    """Actualiza parcialmente una categoría"""
    db_category = get_category_by_id(db, category_id)
    if not db_category:
        return None
    
    # Validar nombre único si se está cambiando
    if category_data.name and category_data.name != db_category.name:
        existing = get_category_by_name(db, category_data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"No se puede renombrar: el nombre '{category_data.name}' ya está en uso"
            )

    update_data = category_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int):
    """Elimina una categoría si no tiene productos activos asociados (PRO-68)"""
    db_category = get_category_by_id(db, category_id)
    if not db_category:
        return None
    
    # --- VALIDACIÓN DE INTEGRIDAD (PRO-68) ---
    # Verificar si hay productos activos vinculados a esta categoría
    active_products_count = db.query(Product).filter(
        Product.category_id == category_id,
        Product.is_active == True
    ).count()
    
    if active_products_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar: la categoría '{db_category.name}' tiene {active_products_count} producto(s) activo(s) asociados."
        )
    
    # Borrado físico (Hard Delete) ya que no tiene dependencias activas
    db.delete(db_category)
    db.commit()
    return db_category
