# Script de inicialización de la base de datos
# Importa todos los modelos para que SQLAlchemy los registre y crea las tablas

from backend.app.core.database import Base, engine

# Importamos TODOS los modelos (orden importa: primero los que no dependen de nadie)
from backend.app.models.store import Store
from backend.app.models.user import User
from backend.app.models.supplier import Supplier
from backend.app.models.category import Category
from backend.app.models.product import Product
from backend.app.models.movement import Movement

def create_tables():
    print("🚀 Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ ¡6 tablas creadas con éxito!")
    print("   - stores, users, suppliers, categories, products, movements")

if __name__ == "__main__":
    create_tables()
