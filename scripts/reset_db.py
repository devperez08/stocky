import os
import sys

# Añadir el directorio raíz al path para poder importar backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.database import engine, Base
from backend.app.models.store import Store
from backend.app.models.user import User
from backend.app.models.category import Category
from backend.app.models.product import Product
from backend.app.models.movement import Movement

def reset_database():
    """
    Borra todas las tablas y las recrea desde cero (Limpia la base de datos).
    Ten cuidado: esto eliminará TODOS los datos registrados.
    """
    print("⚠️  Iniciando limpieza profunda de la base de datos...")
    
    # El orden importa por las llaves foráneas
    Base.metadata.drop_all(bind=engine)
    print("  - Tablas antiguas eliminadas.")
    
    Base.metadata.create_all(bind=engine)
    print("  - Estructura recreada exitosamente.")
    
    print("\n✅ Base de datos limpia y lista para producción.")

if __name__ == "__main__":
    confirm = input("¿Estás seguro de que quieres BORRAR TODO? (escribe 'SI' para confirmar): ")
    if confirm.upper() == "SI":
        reset_database()
    else:
        print("Operación cancelada.")
