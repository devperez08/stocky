from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

# Importamos las herramientas que necesitamos:
# 1. get_db: Para conectarnos a la base de datos
# 2. schemas: Para validar la entrada y salida de datos
# 3. service: Para ejecutar la lógica de negocio
from backend.app.core.database import get_db
from backend.app.schemas.product import Product, ProductCreate, ProductUpdate, ProductResponse
from backend.app.services import product as product_service

# Creamos el (Router). 
# prefix="/products" significa que todas estas rutas empezarán con esa palabra.
# tags=["products"] ayuda a que en la documentación (/docs) aparezcan agrupadas.
router = APIRouter(
    prefix="/products",
    tags=["products"]
)

# --- 1. ENDPOINT PARA LISTAR (Plural) ---
@router.get("/", response_model=List[ProductResponse])
def read_products(
    skip: int = Query(0, ge=0), 
    limit: int = Query(200, le=500), 
    name: Optional[str] = None,
    category_id: Optional[int] = None,
    low_stock: bool = False,
    db: Session = Depends(get_db)
):
    """
    Este es el GET para obtener una lista con filtros y paginación.
    - skip/limit: Controlan la paginación.
    - name: Filtra por nombre (parcial).
    - category_id: Filtra por categoría específica.
    - low_stock: Si es true, muestra productos por agotarse.
    """
    products = product_service.get_products(
        db, 
        skip=skip, 
        limit=limit, 
        name=name, 
        category_id=category_id, 
        low_stock=low_stock
    )
    return products

# --- 2. ENDPOINT PARA DETALLE (Singular) ---
# Usamos {product_id} como una variable en la URL.
@router.get("/{product_id}", response_model=Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    """
    Este es el GET para buscar UN SOLO producto por su ID único.
    """
    db_product = product_service.get_product_by_id(db, product_id=product_id)
    # Si (service) no encuentra nada, devuelve un Error 404.
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Producto no encontrado"
        )
    return db_product

# --- 3. ENDPOINT PARA CREAR (PRO-65) ---
# Usamos ProductResponse para que la respuesta incluya la categoría anidada
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo producto. El servicio valida:
    - Que el SKU no esté duplicado (devuelve 409 si existe).
    - Que el category_id exista en la base de datos (devuelve 404 si no).
    Las validaciones de price >= 0 y stock >= 0 las hace Pydantic automáticamente (422).
    """
    return product_service.create_product(db=db, product_data=product)

# --- 4. ENDPOINT PARA ACTUALIZAR (PRO-66) ---
# Usamos PUT (como pide el ticket) para la actualización parcial y retornamos ProductResponse
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    """
    Busca el producto y actualiza solo los campos que el usuario envía.
    Validaciones en el servicio:
    - Retorna 404 si no existe o está inactivo.
    - Retorna 409 si el nuevo SKU choca con uno existente.
    """
    db_product = product_service.update_product(db=db, product_id=product_id, product_data=product)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Producto no encontrado o inactivo"
        )
    return db_product

# --- 5. ENDPOINT PARA ELIMINAR
# Devolvemos un msj de confirmación junto con el ID, y estatus explícito 200 OK
@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Realiza un 'Soft Delete'. No borra el registro físicamente,
    solo lo marca como 'is_active = False' para preserving the historical data.
    """
    db_product = product_service.delete_product(db=db, product_id=product_id)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Producto no encontrado o ya ha sido desactivado"
        )
    return {
        "message": f"Producto '{db_product.name}' desactivado exitosamente", 
        "id": product_id
    }
