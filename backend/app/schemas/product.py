#schema: Define qué información es obligatoria, que es opcional, que tipo de dato es y que validaciones tiene

from pydantic import BaseModel, Field # BaseModel es la clase base para todos los esquemas, Field es para validar los campos. pydantic es una libreria que nos ayuda a validar los datos que recibimos en la API
from typing import Optional, List # Optional es para indicar que un campo es opcional, List es para indicar que un campo es una lista
from datetime import datetime # datetime es para indicar que un campo es una fecha

# 1. PRODUCTO BASE: El "ADN" común de los datos.
# Hereda de 'BaseModel' (de la librería Pydantic)
# para validar que los datos tengan el tipo y formato correcto automáticamente.
class ProductBase(BaseModel):
    # Todo lo definido aquí será compartido por los esquemas de creación y respuesta.
    
    # El nombre es obligatorio (str) y no puede estar vacío (min_length=1)
    name: str = Field(..., min_length=1, max_length=200)
    
    # El SKU (código único) es obligatorio
    sku: str = Field(..., min_length=1, max_length=100)
    
    # La descripción es opcional (Optional)
    description: Optional[str] = Field(None, max_length=500)
    
    # El precio no puede ser negativo (ge=0 -> Greater or Equal to 0)
    price: float = Field(0.0, ge=0)
    
    cost_price: Optional[float] = Field(0.0, ge=0)
    stock_quantity: int = Field(0, ge=0)
    min_stock_alert: int = Field(5, ge=0)
    is_active: bool = True
    
    # Estos IDs conectan con otras tablas (Store, Category, Supplier)
    category_id: Optional[int] = None
    store_id: Optional[int] = None
    supplier_id: Optional[int] = None

# 2. PRODUCTO PARA CREACIÓN: Lo que el usuario nos envía por el teclado.
# Hereda de ProductBase. Pide todo lo anterior pero NO pide ID ni fechas,
# ya que esas las genera el sistema después.
class ProductCreate(ProductBase):
    pass # 'pass' significa que hereda todo sin añadir nada nuevo.

# 3. PRODUCTO PARA RESPUESTA: Lo que la API le muestra al usuario en pantalla.

# Esquema básico de una categoría para incluirla dentro del producto
class CategoryBase(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

# Este es el esquema solicitado por PRO-64 para el listado
class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Campo anidado: Esto permite que al consultar un producto, 
    # FastAPI traiga automáticamente la información de su categoría.
    category: Optional[CategoryBase] = None

    class Config:
        from_attributes = True

# Herencia: 'Product' ahora hereda de 'ProductResponse'.
# Así mantenemos compatibilidad con el resto del sistema, pero obteniendo
# todas las mejoras (campos de ID, fechas y categoría anidada) automáticamente.
class Product(ProductResponse):
    pass

# 4. PRODUCTO PARA ACTUALIZACIÓN: Todo es opcional.
# Usamos esto para el método PATCH o PUT parcial.
class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, ge=0)
    cost_price: Optional[float] = Field(None, ge=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    min_stock_alert: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    category_id: Optional[int] = None
    store_id: Optional[int] = None
    supplier_id: Optional[int] = None
    
