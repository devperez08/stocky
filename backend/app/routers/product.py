from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
import io

from backend.app.core.database import get_db
from backend.app.core.security import get_current_store_id
from backend.app.schemas.product import Product, ProductCreate, ProductUpdate, ProductResponse
from backend.app.services import product as product_service

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

# --- 1. ENDPOINT PARA LISTAR ---
@router.get("/", response_model=List[ProductResponse])
def read_products(
    skip: int = Query(0, ge=0), 
    limit: int = Query(200, le=500), 
    name: Optional[str] = None,
    category_id: Optional[int] = None,
    low_stock: bool = False,
    db: Session = Depends(get_db),
    store_id: int = Depends(get_current_store_id)
):
    """Obtiene la lista de productos de la tienda autenticada."""
    products = product_service.get_products(
        db, 
        store_id=store_id,
        skip=skip, 
        limit=limit, 
        name=name, 
        category_id=category_id, 
        low_stock=low_stock
    )
    return products

# --- 2. ENDPOINT PARA DETALLE ---
@router.get("/{product_id}", response_model=Product)
def read_product(
    product_id: int, 
    db: Session = Depends(get_db),
    store_id: int = Depends(get_current_store_id)
):
    """Busca un producto por ID dentro de la tienda."""
    db_product = product_service.get_product_by_id(db, product_id=product_id, store_id=store_id)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Producto no encontrado"
        )
    return db_product

# --- 3. ENDPOINT PARA CREAR ---
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate, 
    db: Session = Depends(get_db),
    store_id: int = Depends(get_current_store_id)
):
    """Crea un producto inyectando automáticamente el store_id del token."""
    return product_service.create_product(db=db, product_data=product, store_id=store_id)

# --- 4. ENDPOINT PARA ACTUALIZAR ---
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int, 
    product: ProductUpdate, 
    db: Session = Depends(get_db),
    store_id: int = Depends(get_current_store_id)
):
    """Actualiza un producto de la tienda."""
    db_product = product_service.update_product(
        db=db, 
        product_id=product_id, 
        product_data=product, 
        store_id=store_id
    )
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Producto no encontrado o inactivo"
        )
    return db_product

# --- 5. ENDPOINT PARA ELIMINAR ---
@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(
    product_id: int, 
    db: Session = Depends(get_db),
    store_id: int = Depends(get_current_store_id)
):
    """Realiza un soft-delete del producto de la tienda."""
    db_product = product_service.delete_product(db=db, product_id=product_id, store_id=store_id)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Producto no encontrado o ya ha sido desactivado"
        )
    return {
        "message": f"Producto '{db_product.name}' desactivado exitosamente", 
        "id": product_id
    }

# --- 6. ENDPOINT PARA IMPORTAR ---
@router.post("/import", status_code=status.HTTP_200_OK)
async def import_products_from_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    store_id: int = Depends(get_current_store_id)
):
    """Importación masiva aislada por tienda."""
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos .xlsx o .xls")

    content = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="No se pudo leer el archivo.")

    required_cols = {"sku", "name", "price"}
    missing = required_cols - set(df.columns.str.lower())
    if missing:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Columnas requeridas faltantes: {', '.join(missing)}")

    df.columns = df.columns.str.lower().str.strip()
    results = {"created": 0, "updated": 0, "skipped": 0, "errors": []}

    from backend.app.models.product import Product
    from backend.app.models.category import Category
    from sqlalchemy import func

    for idx, row in df.iterrows():
        try:
            sku = str(row["sku"]).strip()
            name = str(row["name"]).strip()
            price = float(row["price"])

            if not sku or not name or price < 0:
                raise ValueError("SKU, nombre o precio inválidos")

            # Buscar solo en la tienda del usuario
            existing = db.query(Product).filter(
                func.lower(Product.sku) == sku.lower(),
                Product.store_id == store_id
            ).first()

            category_id = None
            if "category" in df.columns and pd.notna(row.get("category")):
                cat_name = str(row["category"]).strip()
                category = db.query(Category).filter(
                    func.lower(Category.name) == cat_name.lower(),
                    Category.store_id == store_id
                ).first()
                if category:
                    category_id = category.id
                else:
                    new_cat = Category(name=cat_name, store_id=store_id)
                    db.add(new_cat)
                    db.commit()
                    db.refresh(new_cat)
                    category_id = new_cat.id

            if existing:
                existing.name = name
                existing.price = price
                if "description" in df.columns and pd.notna(row.get("description")):
                    existing.description = str(row["description"])
                if category_id:
                    existing.category_id = category_id
                results["updated"] += 1
            else:
                new_product = Product(
                    sku=sku, name=name, price=price, store_id=store_id,
                    stock_quantity=int(row.get("stock_quantity", 0)) if pd.notna(row.get("stock_quantity")) else 0,
                    min_stock_alert=int(row.get("min_stock_alert", 5)) if pd.notna(row.get("min_stock_alert")) else 5,
                    description=str(row["description"]) if "description" in df.columns and pd.notna(row.get("description")) else None,
                    category_id=category_id
                )
                db.add(new_product)
                results["created"] += 1
        except Exception as e:
            results["skipped"] += 1
            results["errors"].append({"row": int(idx) + 2, "error": str(e)})

    db.commit()
    return results
