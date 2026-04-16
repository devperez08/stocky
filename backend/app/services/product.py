# service se encarga de hablar con la base de datos, permite hacer las operaciones CRUD

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from backend.app.models.product import Product # importamos el modelo de la tabla de productos
from backend.app.models.category import Category # importamos el modelo de categorias para validarla
from backend.app.schemas.product import ProductCreate # importamos el schema de creacion de producto
from backend.app.schemas.product import ProductUpdate # importamos el schema de actualizacion de producto

def get_product_by_sku(db: Session, sku: str):
    # Busca un producto por su SKU único. Lo usamos para validar duplicados
    return db.query(Product).filter(Product.sku == sku).first()

def get_product_by_id(db: Session, product_id: int): # product_id es el id del producto que queremos consultar
    return db.query(Product).filter(Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 50, name: str = None, category_id: int = None, low_stock: bool = False):
    """
    Obtiene la lista de productos aplicando filtros dinámicos y paginación.
    """
    # 1. Iniciamos la consulta filtrando solo los productos que no han sido borrados (soft-delete)
    query = db.query(Product).filter(Product.is_active == True)
    
    # 2. Búsqueda por nombre: Usamos 'ilike' para que no importe si es mayúscula o minúscula
    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))
        
    # 3. Filtrado por categoría: Solo si el frontend envía un ID válido
    if category_id:
        query = query.filter(Product.category_id == category_id)
        
    # 4. Alerta de Stock Bajo: Compara la cantidad actual contra el umbral configurado por el usuario
    if low_stock:
        query = query.filter(Product.stock_quantity <= Product.min_stock_alert)
        
    # 5. Paginación: 'skip' salta registros y 'limit' define cuántos traer (vital para el rendimiento)
    return query.offset(skip).limit(limit).all()
    
def create_product(db: Session, product_data: ProductCreate):
    # --- VALIDACIÓN 1: SKU duplicado (PRO-65) ---
    # Antes de crear nada, verificamos si el SKU ya existe en la base de datos.
    existing_product = get_product_by_sku(db, product_data.sku)
    if existing_product:
        # HTTP 409 Conflict: El recurso ya existe y no podemos crearlo de nuevo
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un producto con el SKU '{product_data.sku}'"
        )
    
    # --- VALIDACIÓN 2: Categoría existente (PRO-65) ---
    # Si el usuario envió un category_id, verificamos que esa categoría exista
    if product_data.category_id:
        category = db.query(Category).filter(Category.id == product_data.category_id).first()
        if not category:
            # HTTP 404 Not Found: La categoría referenciada no existe
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoría con id '{product_data.category_id}' no encontrada"
            )

    # 1. Descomprimimos los datos validados del schema en el modelo SQLAlchemy.
    # Usamos .model_dump() que es el estándar de Pydantic v2 (antes era .dict())
    new_product = Product(**product_data.model_dump())
    
    # 2. Lo agregamos a la sesión (la sala de espera de SQLAlchemy)
    db.add(new_product)
    
    # 3. Guardamos los cambios en la base de datos
    db.commit()
    
    # 4. Refrescamos para obtener el ID y campos generados por la DB
    db.refresh(new_product)
    
    return new_product

def delete_product(db: Session, product_id: int):
    # Reutilizamos nuestra propia función para buscar
    db_product = get_product_by_id(db, product_id)
    
    if db_product:
        # Si lo encontramos, lo desactivamos
        db_product.is_active = False
        db.commit()
        db.refresh(db_product)
        return db_product
    
    # Si no lo encontramos, devolvemos None para que el Router
    # sepa que debe dar un error 404.
    return None

def update_product(db: Session, product_id: int, product_data: ProductUpdate):
    # --- PASO 1: Buscar producto ---
    db_product = get_product_by_id(db, product_id)
    
    # Validación: Si no existe o está inactivo (soft-delete), retornamos None para dar 404
    if not db_product or not db_product.is_active:
        return None
    
    # --- VALIDACIÓN (PRO-66): Colisión de SKU ---
    # Si el usuario quiere cambiar el SKU, verificamos que no pertenezca a otro producto
    if product_data.sku is not None and product_data.sku != db_product.sku:
        existing_sku = get_product_by_sku(db, product_data.sku)
        if existing_sku:
            # HTTP 409 Conflict: El SKU ya está siendo usado
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El SKU '{product_data.sku}' ya está en uso por otro producto"
            )
    
    # --- PASO 2: Extraer campos a actualizar ---
    # Convertimos los datos nuevos a diccionario con model_dump() (Pydantic v2)
    # 'exclude_unset=True' le dice a Pydantic: "Solo tráeme los campos que el usuario envió"
    update_data = product_data.model_dump(exclude_unset=True)
    
    # --- PASO 3: Actualizar objeto ---
    # Recorremos el diccionario y actualizamos el objeto de la DB a nivel memoria
    for key, value in update_data.items():
        setattr(db_product, key, value) # Equivalente a db_product.campo = valor
    
    # --- PASO 4: Guardar y refrescar ---
    # Al hacer commit, SQLAlchemy auto-actualiza el campo 'updated_at' 
    # por la configuración 'onupdate=func.now()' en el modelo.
    db.commit()
    db.refresh(db_product)
    
    return db_product