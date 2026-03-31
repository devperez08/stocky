"""
¿Por qué múltiples schemas en lugar de uno solo?

Seguridad y claridad de contrato:
- `ProductCreate`: El cliente ENVÍA esto. No incluye `id` ni timestamps
  (el cliente no debería poder asignarlos → Mass Assignment vulnerability).
- `ProductUpdate`: Todos opcionales. Permite PATCH parcial sin enviar todo el objeto.
- `ProductResponse`: Lo que la API DEVUELVE. Incluye `id` y timestamps.

Si usáramos un único schema para todo, un cliente malicioso podría
intentar enviar un `id` o `created_at` para manipular la DB.
"""
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class ProductBase(BaseModel):
    """Campos comunes compartidos entre Create y Response."""
    name: str = Field(..., min_length=1, max_length=200, description="Nombre único del producto")
    description: str | None = Field(None, description="Descripción opcional")
    price: float = Field(..., gt=0, description="Precio debe ser mayor a 0")
    stock: int = Field(..., ge=0, description="Stock no puede ser negativo")
    low_stock_threshold: int = Field(10, ge=0, description="Umbral para alerta de stock bajo")

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        """
        ¿Por qué un validator extra si ya tenemos min_length=1?
        Porque " " (espacios) tiene longitud > 0 pero es un nombre inválido.
        Validamos en la entrada para no guardar datos sucios en la DB.
        """
        if not v.strip():
            raise ValueError("El nombre no puede ser solo espacios en blanco")
        return v.strip()


class ProductCreate(ProductBase):
    """Schema para POST /products. Solo lo que el cliente puede definir."""
    pass


class ProductUpdate(BaseModel):
    """
    Schema para PATCH /products/{id}.
    Todos los campos son opcionales: el cliente solo envía lo que quiere cambiar.
    """
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    price: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    low_stock_threshold: int | None = Field(None, ge=0)


class ProductResponse(ProductBase):
    """Schema para las respuestas de la API. Incluye datos generados por el servidor."""
    id: int
    created_at: datetime
    updated_at: datetime

    # `from_attributes=True` permite construir este schema desde un objeto ORM de SQLAlchemy.
    # Sin esto, Pydantic no sabría cómo leer los atributos del modelo.
    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    """Respuesta paginada para GET /products."""
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
