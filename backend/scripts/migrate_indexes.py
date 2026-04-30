import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_products_name ON products(name)"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_products_category ON products(category_id)"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_movements_created_at ON movements(created_at)"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_movements_product_id ON movements(product_id)"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_movements_type ON movements(movement_type)"))
    conn.commit()
    print("✅ Índices creados exitosamente.")
