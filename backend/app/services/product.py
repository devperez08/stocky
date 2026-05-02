# service se encarga de hablar con la base de datos, permite hacer las operaciones CRUD
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from backend.app.models.product import Product # importamos el modelo de la tabla de productos
from backend.app.models.category import Category # importamos el modelo de categorias para validarla
from backend.app.schemas.product import ProductCreate # importamos el schema de creacion de producto
from backend.app.schemas.product import ProductUpdate # importamos el schema de actualizacion de producto

def get_product_by_sku(db: Session, sku: str, store_id: int):
    from sqlalchemy import func
    # Busca un producto por su SKU único dentro de la tienda.
    return db.query(Product).filter(
        func.lower(Product.sku) == sku.lower(),
        Product.store_id == store_id
    ).first()

def get_product_by_id(db: Session, product_id: int, store_id: int):
    return db.query(Product).filter(
        Product.id == product_id, 
        Product.store_id == store_id
    ).first()

def get_products(db: Session, store_id: int, skip: int = 0, limit: int = 200, name: str = None, category_id: int = None, low_stock: bool = False):
    """
    Obtiene la lista de productos de la tienda aplicando filtros dinámicos.
    """
    # 1. Iniciamos la consulta filtrando por tienda y solo los productos activos
    query = db.query(Product).options(joinedload(Product.category)).filter(
        Product.store_id == store_id,
        Product.is_active == True
    )
    
    # 2. Búsqueda por nombre
    if name:
        from sqlalchemy import func
        query = query.filter(func.lower(Product.name).like(f"%{name.lower()}%"))
        
    # 3. Filtrado por categoría
    if category_id:
        query = query.filter(Product.category_id == category_id)
        
    # 4. Alerta de Stock Bajo
    if low_stock:
        query = query.filter(Product.stock_quantity <= Product.min_stock_alert)
        
    # 5. Paginación
    return query.offset(skip).limit(limit).all()
    
def create_product(db: Session, product_data: ProductCreate, store_id: int):
    # --- VALIDACIÓN 1: SKU duplicado en la tienda ---
    existing_product = get_product_by_sku(db, product_data.sku, store_id)
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un producto con el SKU '{product_data.sku}'"
        )
    
    # --- VALIDACIÓN 2: Categoría perteneciente a la tienda ---
    if product_data.category_id:
        category = db.query(Category).filter(
            Category.id == product_data.category_id,
            Category.store_id == store_id
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoría con id '{product_data.category_id}' no encontrada en esta tienda"
            )

    # 1. Crear instancia inyectando store_id
    new_product = Product(**product_data.model_dump())
    new_product.store_id = store_id
    
    # 2. Persistir
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product

def delete_product(db: Session, product_id: int, store_id: int):
    db_product = get_product_by_id(db, product_id, store_id)
    
    if not db_product or not db_product.is_active:
        return None
        
    db_product.is_active = False
    db.commit()
    return db_product

def update_product(db: Session, product_id: int, product_data: ProductUpdate, store_id: int):
    # --- PASO 1: Buscar producto de la tienda ---
    db_product = get_product_by_id(db, product_id, store_id)
    
    if not db_product or not db_product.is_active:
        return None
    
    # --- VALIDACIÓN: Colisión de SKU en la tienda ---
    if product_data.sku is not None and product_data.sku != db_product.sku:
        existing_sku = get_product_by_sku(db, product_data.sku, store_id)
        if existing_sku:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El SKU '{product_data.sku}' ya está en uso por otro producto"
            )
    
    # --- PASO 2: Actualizar objeto ---
    update_data = product_data.model_dump(exclude_unset=True)
    # Protegemos store_id
    if "store_id" in update_data:
        del update_data["store_id"]

    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product