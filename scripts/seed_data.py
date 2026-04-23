import sys
import os
from datetime import datetime, timedelta
import random

# Ajuste para importar desde el paquete backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.database import SessionLocal, engine, Base
from backend.app.models import store, user, supplier, category, product, movement
from backend.app.models.category import Category
from backend.app.models.product import Product
from backend.app.models.movement import Movement, MovementType

def seed():
    print("🚀 Iniciando seed de datos...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # --- 1. Categorías ---
        categories_data = [
            {"name": "Alimentos", "description": "Productos alimenticios y bebidas"},
            {"name": "Electrónica", "description": "Dispositivos y accesorios electrónicos"},
            {"name": "Papelería", "description": "Útiles de oficina y escolares"},
            {"name": "Aseo", "description": "Productos de limpieza y cuidado personal"},
            {"name": "Ropa", "description": "Prendas de vestir y accesorios"},
        ]
        
        categories = {}
        for cat_data in categories_data:
            existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
            if not existing:
                cat = Category(**cat_data)
                db.add(cat)
                db.flush()
                categories[cat_data["name"]] = cat
                print(f"  + Categoría creada: {cat.name}")
            else:
                categories[cat_data["name"]] = existing

        # --- 2. Productos ---
        products_data = [
            {"name": "Arroz Diana x 500g", "sku": "ALI-001", "price": 4500, "stock_quantity": 80, "min_stock_alert": 10, "category": "Alimentos"},
            {"name": "Aceite Girasol 1L", "sku": "ALI-002", "price": 12000, "stock_quantity": 4, "min_stock_alert": 5, "category": "Alimentos"}, # CRÍTICO
            {"name": "Pasta Dental 100ml", "sku": "ASE-001", "price": 8500, "stock_quantity": 25, "min_stock_alert": 5, "category": "Aseo"},
            {"name": "Jabón Líquido 500ml", "sku": "ASE-002", "price": 15000, "stock_quantity": 3, "min_stock_alert": 10, "category": "Aseo"}, # CRÍTICO
            {"name": "Mouse Inalámbrico", "sku": "ELE-001", "price": 45000, "stock_quantity": 15, "min_stock_alert": 3, "category": "Electrónica"},
            {"name": "Teclado Mecánico RGB", "sku": "ELE-002", "price": 180000, "stock_quantity": 8, "min_stock_alert": 2, "category": "Electrónica"},
            {"name": "Cargador USB-C 20W", "sku": "ELE-003", "price": 55000, "stock_quantity": 30, "min_stock_alert": 5, "category": "Electrónica"},
            {"name": "Cuaderno 100 Hojas", "sku": "PAP-001", "price": 12000, "stock_quantity": 100, "min_stock_alert": 20, "category": "Papelería"},
            {"name": "Esfero Tinta Negra", "sku": "PAP-002", "price": 2500, "stock_quantity": 200, "min_stock_alert": 50, "category": "Papelería"},
            {"name": "Resma Papel Carta", "sku": "PAP-003", "price": 35000, "stock_quantity": 12, "min_stock_alert": 15, "category": "Papelería"}, # CRÍTICO
            {"name": "Camiseta Algodón M", "sku": "ROP-001", "price": 35000, "stock_quantity": 40, "min_stock_alert": 10, "category": "Ropa"},
            {"name": "Pantalón Jean Azul", "sku": "ROP-002", "price": 85000, "stock_quantity": 20, "min_stock_alert": 5, "category": "Ropa"},
            {"name": "Medias Deportivas", "sku": "ROP-003", "price": 15000, "stock_quantity": 60, "min_stock_alert": 12, "category": "Ropa"},
            {"name": "Monitor 24 Pulgadas", "sku": "ELE-004", "price": 650000, "stock_quantity": 5, "min_stock_alert": 2, "category": "Electrónica"},
            {"name": "Leche Entera 1L", "sku": "ALI-003", "price": 5200, "stock_quantity": 120, "min_stock_alert": 24, "category": "Alimentos"},
        ]

        inserted_products = []
        for p_data in products_data:
            cat_name = p_data.pop("category")
            existing = db.query(Product).filter(Product.sku == p_data["sku"]).first()
            if not existing:
                category = categories.get(cat_name)
                product = Product(**p_data, category_id=category.id if category else None)
                db.add(product)
                db.flush()
                inserted_products.append(product)
                print(f"  + Producto creado: {product.name} ({product.sku})")
            else:
                inserted_products.append(existing)

        # --- 3. Movimientos ---
        # Generar movimientos aleatorios en los últimos 7 días
        if inserted_products:
            print("  + Generando movimientos aleatorios...")
            for _ in range(25):
                product = random.choice(inserted_products)
                m_type = random.choice([MovementType.ENTRY, MovementType.EXIT])
                
                # Para salidas, asegurar que no quede en negativo (aunque el servicio lo valide, aquí simulamos coherencia)
                qty = random.randint(1, 10)
                if m_type == MovementType.EXIT and product.stock_quantity < qty:
                    m_type = MovementType.ENTRY
                
                # Fecha aleatoria en los últimos 7 días
                days_ago = random.randint(0, 7)
                minutes_ago = random.randint(0, 1440)
                # Usamos now(timezone.utc) para evitar DeprecationWarning y unificamos formato
                from datetime import timezone
                created_at = datetime.now(timezone.utc) - timedelta(days=days_ago, minutes=minutes_ago)
                # Limpiar microsegundos para mayor compatibilidad con parseadores simples
                created_at = created_at.replace(microsecond=0)
                
                mov = Movement(
                    product_id=product.id,
                    movement_type=m_type,
                    quantity=qty,
                    reason="Seed data automatico",
                    created_at=created_at
                )
                
                # Actualizar el stock del producto en el objeto (simulando lo que hace el servicio)
                if m_type == MovementType.ENTRY:
                    product.stock_quantity += qty
                else:
                    product.stock_quantity -= qty
                
                db.add(mov)

        db.commit()
        print("✅ Seed completado exitosamente.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error durante el seed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
