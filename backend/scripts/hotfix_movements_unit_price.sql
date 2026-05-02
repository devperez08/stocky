-- =============================================================================
-- HOTFIX: Alinear columna movements.unit_value -> movements.unit_price
-- Objetivo: compatibilizar Supabase/Postgres con backend actual (stats/reportes).
-- =============================================================================
-- Ejecutar en SQL Editor de Supabase sobre el entorno afectado.
-- Este script es idempotente y preserva datos existentes.

BEGIN;

-- 1) Si existe unit_value y no existe unit_price, renombrar directo.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'movements'
          AND column_name = 'unit_value'
    )
    AND NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'movements'
          AND column_name = 'unit_price'
    ) THEN
        ALTER TABLE public.movements RENAME COLUMN unit_value TO unit_price;
    END IF;
END $$;

-- 2) Si por algún motivo existen ambas columnas, copiar datos faltantes.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'movements'
          AND column_name = 'unit_price'
    )
    AND EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'movements'
          AND column_name = 'unit_value'
    ) THEN
        EXECUTE '
            UPDATE public.movements
            SET unit_price = COALESCE(unit_price, unit_value, 0)
        ';
    END IF;
END $$;

-- 3) Asegurar contratos mínimos del backend ORM.
ALTER TABLE public.movements
    ALTER COLUMN unit_price SET DEFAULT 0,
    ALTER COLUMN unit_price SET NOT NULL;

-- 4) Limpieza opcional del legado si quedó unit_value.
ALTER TABLE public.movements
    DROP COLUMN IF EXISTS unit_value;

COMMIT;

-- Verificación rápida
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'movements'
  AND column_name IN ('unit_price', 'unit_value')
ORDER BY column_name;
