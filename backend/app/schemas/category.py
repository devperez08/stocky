# schema: Define qué información es obligatoria, opcional y sus validaciones para Categorías
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# 1. CATEGORÍA BASE: Atributos comunes
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Nombre único de la categoría")
    description: Optional[str] = Field(None, max_length=255, description="Descripción opcional")
    store_id: Optional[int] = None

# 2. PARA CREACIÓN: Lo que el usuario envía
class CategoryCreate(CategoryBase):
    pass

# 3. PARA RESPUESTA: Lo que la API devuelve (PRO-68)
class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# 4. PARA ACTUALIZACIÓN: Todo opcional para permitir PATCH/PUT parcial
class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    store_id: Optional[int] = None
