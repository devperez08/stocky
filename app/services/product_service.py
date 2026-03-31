"""
¿Por qué un archivo de servicio separado del router?

El servicio contiene la LÓGICA DE NEGOCIO pura:
- No sabe nada de HTTP (sin Request, Response, HTTPException).
- Solo habla con la DB vía SQLAlchemy.
- Esto lo hace 100% testeable sin levantar un servidor.

El router solo "traduce": convierte HTTP → llamada al servicio → respuesta HTTP.
Esta separación también permite reutilizar la lógica en tareas en background,
scripts CLI, o tests sin necesitar un cliente HTTP.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def get_all_products(
    db: Session, skip: int = 0, limit: int = 20
) -> tuple[list[Product], int]:
    """
    Devuelve una página de productos y el total de registros.
    ¿Por qué devolver el total también?
    Para que el cliente pueda calcular cuántas páginas existen sin hacer una segunda query.
    """
    total = db.query(func.count(Product.id)).scalar()
    products = db.query(Product).offset(skip).limit(limit).all()
    return products, total


def get_product_by_id(db: Session, product_id: int) -> Product | None:
    """Retorna None si no existe. El router decide qué error HTTP lanzar."""
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_name(db: Session, name: str) -> Product | None:
    return db.query(Product).filter(Product.name == name).first()


def create_product(db: Session, product_data: ProductCreate) -> Product:
    """
    ¿Por qué no hacemos el check de nombre duplicado aquí?
    Sí lo hacemos: el router lo llama antes de crear. Podríamos también
    dejarlo explotar con IntegrityError (la DB tiene UNIQUE constraint),
    pero dar un mensaje claro al usuario es mejor UX.
    """
    new_product = Product(**product_data.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)  # Recarga el objeto para obtener id, created_at, etc.
    return new_product


def update_product(
    db: Session, product: Product, update_data: ProductUpdate
) -> Product:
    """
    `exclude_unset=True` → solo actualiza los campos que el cliente REALMENTE envió.
    Sin esto, un PATCH con `{"name": "X"}` pondría todos los demás campos en None.
    """
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product) -> None:
    """Hard delete. Si en el futuro necesitamos soft-delete, solo cambiamos aquí."""
    db.delete(product)
    db.commit()
