"""
El router es la capa más delgada posible.
Su única responsabilidad: traducir peticiones HTTP a llamadas al servicio.

Patrón empleado:
- Recibe la request, valida con Pydantic (automático).
- Llama al servicio con los datos limpios.
- Lanza HTTPException si el servicio no encuentra datos.
- Retorna la respuesta tipada.

¿Por qué usar `Annotated` con `Depends`?
Es el patrón moderno de FastAPI. Evita repetir el tipo en cada endpoint
y hace el código más limpio y fácil de testear (puedes mockear `get_db`).
"""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)
from app.services import product_service

router = APIRouter(prefix="/products", tags=["Products"])

# Tipo reutilizable para la inyección de DB en todos los endpoints
DbSession = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=ProductListResponse, summary="Listar productos")
def list_products(
    db: DbSession,
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(20, ge=1, le=100, description="Items por página"),
):
    """
    Devuelve una lista paginada de productos.
    `page` y `page_size` son query params: GET /products?page=2&page_size=10
    """
    skip = (page - 1) * page_size
    products, total = product_service.get_all_products(db, skip=skip, limit=page_size)
    return ProductListResponse(items=products, total=total, page=page, page_size=page_size)


@router.get("/{product_id}", response_model=ProductResponse, summary="Obtener producto por ID")
def get_product(product_id: int, db: DbSession):
    product = product_service.get_product_by_id(db, product_id)
    # Guard clause: si no existe, fallamos rápido con un error claro.
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con id={product_id} no encontrado",
        )
    return product


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto",
)
def create_product(product_data: ProductCreate, db: DbSession):
    """
    ¿Por qué revisamos el nombre antes de crear?
    La DB tiene un UNIQUE constraint, pero su error (IntegrityError) es genérico.
    Devolver 409 Conflict con un mensaje claro es mejor experiencia que un 500.
    """
    existing = product_service.get_product_by_name(db, product_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un producto con el nombre '{product_data.name}'",
        )
    return product_service.create_product(db, product_data)


@router.patch("/{product_id}", response_model=ProductResponse, summary="Actualizar producto parcialmente")
def update_product(product_id: int, update_data: ProductUpdate, db: DbSession):
    """PATCH permite actualizar solo los campos enviados, sin tocar el resto."""
    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con id={product_id} no encontrado",
        )
    # Si quieren cambiar el nombre, verificamos que no esté tomado por otro producto
    if update_data.name and update_data.name != product.name:
        existing = product_service.get_product_by_name(db, update_data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un producto con el nombre '{update_data.name}'",
            )
    return product_service.update_product(db, product, update_data)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar producto",
)
def delete_product(product_id: int, db: DbSession):
    """
    Retorna 204 No Content (sin body).
    ¿Por qué 204 y no 200?
    El estándar HTTP dice que DELETE exitoso sin body de respuesta = 204.
    """
    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con id={product_id} no encontrado",
        )
    product_service.delete_product(db, product)
