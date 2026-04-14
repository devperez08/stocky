from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Importamos las herramientas que necesitamos:
# 1. get_db: Para conectarnos a la base de datos
# 2. schemas: Para validar la entrada y salida de datos
# 3. service: Para ejecutar la lógica de negocio
from backend.app.core.database import get_db
from backend.app.schemas.product import Product, ProductCreate, ProductUpdate
from backend.app.services import product as product_service

# Creamos el (Router). 
# prefix="/products" significa que todas estas rutas empezarán con esa palabra.
# tags=["products"] ayuda a que en la documentación (/docs) aparezcan agrupadas.
router = APIRouter(
    prefix="/products",
    tags=["products"]
)

# --- 1. ENDPOINT PARA LISTAR (Plural) ---
@router.get("/", response_model=List[Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Este es el GET para obtener una lista. 
    Usamos 'skip' y 'limit' para no saturar el sistema (Paginación).
    """
    products = product_service.get_products(db, skip=skip, limit=limit)
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

# --- 3. ENDPOINT PARA CREAR ---
@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Recibe los datos del producto, los valida con ProductCreate
    y devuelve el producto creado con su nuevo ID y el código 201.
    """
    return product_service.create_product(db=db, product_data=product)

# --- 4. ENDPOINT PARA ACTUALIZAR ---
# PATCH es ideal para actualizaciones parciales (solo cambiar un precio, por ejemplo).
@router.patch("/{product_id}", response_model=Product)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    """
    Busca el producto y actualiza solo los campos que el usuario envía.
    """
    db_product = product_service.update_product(db=db, product_id=product_id, product_data=product)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Producto no encontrado"
        )
    return db_product

# --- 5. ENDPOINT PARA ELIMINAR ---
@router.delete("/{product_id}", response_model=Product)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Hace un 'Soft Delete'. No borra el registro físicamente,
    solo lo marca como 'is_active = False'.
    """
    db_product = product_service.delete_product(db=db, product_id=product_id)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Producto no encontrado"
        )
    return db_product
