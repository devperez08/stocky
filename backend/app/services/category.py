# service: Lógica de negocio para Categorías y comunicación con la DB
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.models.category import Category
from backend.app.models.product import Product
from backend.app.schemas.category import CategoryCreate, CategoryUpdate

def get_categories(db: Session, store_id: int):
    """Retorna todas las categorías filtradas por tienda"""
    return db.query(Category).filter(Category.store_id == store_id).all()

def get_category_by_id(db: Session, category_id: int, store_id: int):
    """Busca una categoría por ID y tienda"""
    return db.query(Category).filter(Category.id == category_id, Category.store_id == store_id).first()

def get_category_by_name(db: Session, name: str, store_id: int):
    """Busca una categoría por nombre dentro de la misma tienda"""
    from sqlalchemy import func
    return db.query(Category).filter(
        func.lower(Category.name) == name.lower(),
        Category.store_id == store_id
    ).first()

def create_category(db: Session, category_data: CategoryCreate, store_id: int):
    """Crea una categoría verificando que el nombre sea único dentro de la tienda"""
    # 1. Validar nombre único
    existing = get_category_by_name(db, category_data.name, store_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una categoría con el nombre '{category_data.name}'"
        )
    
    # 2. Persistir inyectando el store_id
    new_category = Category(**category_data.model_dump())
    new_category.store_id = store_id # Forzar store_id del token
    
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

def update_category(db: Session, category_id: int, category_data: CategoryUpdate, store_id: int):
    """Actualiza parcialmente una categoría propia"""
    db_category = get_category_by_id(db, category_id, store_id)
    if not db_category:
        return None
    
    # Validar nombre único si se está cambiando
    if category_data.name and category_data.name != db_category.name:
        existing = get_category_by_name(db, category_data.name, store_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"No se puede renombrar: el nombre '{category_data.name}' ya está en uso"
            )

    update_data = category_data.model_dump(exclude_unset=True)
    # Protegemos store_id para que no se cambie vía API
    if "store_id" in update_data:
        del update_data["store_id"]
        
    for key, value in update_data.items():
        setattr(db_category, key, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int, store_id: int):
    """Elimina una categoría propia si no tiene productos activos asociados"""
    db_category = get_category_by_id(db, category_id, store_id)
    if not db_category:
        return None
    
    # --- VALIDACIÓN DE INTEGRIDAD ---
    # Verificar si hay productos activos vinculados a esta categoría (filtrar por store_id también por seguridad)
    active_products_count = db.query(Product).filter(
        Product.category_id == category_id,
        Product.store_id == store_id,
        Product.is_active == True
    ).count()
    
    if active_products_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar: la categoría '{db_category.name}' tiene {active_products_count} producto(s) activo(s) asociados."
        )
    
    # Borrado físico
    db.delete(db_category)
    db.commit()
    return db_category
