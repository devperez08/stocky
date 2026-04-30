import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Add new columns to movements table if they don't exist
    # SQLite does not support IF NOT EXISTS in ADD COLUMN, so we catch the exception if it fails
    try:
        conn.execute(text("ALTER TABLE movements ADD COLUMN is_voided BOOLEAN NOT NULL DEFAULT 0;"))
        conn.execute(text("ALTER TABLE movements ADD COLUMN voided_at DATETIME;"))
        conn.execute(text("ALTER TABLE movements ADD COLUMN voided_by_movement_id INTEGER REFERENCES movements(id);"))
        conn.commit()
        print("✅ Columnas añadidas exitosamente.")
    except Exception as e:
        print(f"⚠️ Nota o error al migrar: {e}")
