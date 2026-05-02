-- =============================================================================
-- STOCKY — Migración de Schema SQL a PostgreSQL (Supabase)
-- PRO-98: Configuración de Supabase y Migración del Schema SQL a PostgreSQL
-- Sprint 7 — Migración Cloud, Supabase y Multi-Tenant
-- =============================================================================
-- INSTRUCCIONES:
--   1. Ir al SQL Editor de Supabase (https://supabase.com/dashboard)
--   2. Seleccionar el proyecto Stocky
--   3. Copiar y pegar este script completo
--   4. Ejecutar con el botón "Run"
-- =============================================================================

-- -------------------------------------------------------
-- LIMPIEZA (solo si se desea reiniciar desde cero)
-- -------------------------------------------------------
-- DROP TABLE IF EXISTS movements  CASCADE;
-- DROP TABLE IF EXISTS products   CASCADE;
-- DROP TABLE IF EXISTS categories CASCADE;
-- DROP TABLE IF EXISTS stores     CASCADE;


-- =============================================================================
-- 1. TABLA: stores (Multi-Tenant — una fila por negocio)
-- =============================================================================
-- Campos de negocio: nombre, slug amigable, contacto (email, teléfono, dirección)
-- Campos de acceso:  password_hash (auth del administrador de la tienda)
-- Campos SaaS:       trial (14 días gratis) + suscripción activa/vencida
-- =============================================================================
CREATE TABLE IF NOT EXISTS stores (
    id                       SERIAL PRIMARY KEY,

    -- Datos del negocio
    name                     VARCHAR(200)  NOT NULL,
    slug                     VARCHAR(100)  UNIQUE NOT NULL,     -- URL amigable ej: "tienda-juan"
    address                  VARCHAR(500),
    phone                    VARCHAR(20),

    -- Acceso / Auth
    email                    VARCHAR(255)  UNIQUE NOT NULL,
    password_hash            VARCHAR(255)  NOT NULL,

    -- SaaS: Trial y Suscripción
    trial_start_date         DATE          NOT NULL DEFAULT CURRENT_DATE,
    subscription_expiry_date DATE          NOT NULL DEFAULT (CURRENT_DATE + INTERVAL '14 days'),
    plan_status              VARCHAR(20)   NOT NULL DEFAULT 'trial'
                                 CHECK (plan_status IN ('trial', 'active', 'expired')),

    -- Estado y auditoría
    is_active                BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at               TIMESTAMPTZ   DEFAULT NOW(),
    updated_at               TIMESTAMPTZ
);

COMMENT ON TABLE stores IS 'Registro de negocios que usan Stocky. Cada fila = un tenant.';
COMMENT ON COLUMN stores.slug IS 'Identificador URL-amigable único del negocio.';
COMMENT ON COLUMN stores.plan_status IS 'Estado de suscripción: trial (14 días) | active | expired.';


-- =============================================================================
-- 2. TABLA: categories (Multi-Tenant)
-- =============================================================================
CREATE TABLE IF NOT EXISTS categories (
    id          SERIAL PRIMARY KEY,
    store_id    INTEGER       NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    name        VARCHAR(100)  NOT NULL,
    description VARCHAR(255),
    created_at  TIMESTAMPTZ   DEFAULT NOW(),

    UNIQUE (store_id, name)   -- Un store no puede tener dos categorías con el mismo nombre
);

COMMENT ON TABLE categories IS 'Categorías de productos por tienda.';

CREATE INDEX IF NOT EXISTS ix_categories_store_id ON categories(store_id);


-- =============================================================================
-- 3. TABLA: products (Multi-Tenant)
-- =============================================================================
CREATE TABLE IF NOT EXISTS products (
    id               SERIAL PRIMARY KEY,
    store_id         INTEGER       NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    name             VARCHAR(200)  NOT NULL,
    sku              VARCHAR(100)  NOT NULL,
    description      VARCHAR(500),
    price            FLOAT         NOT NULL DEFAULT 0.0 CHECK (price >= 0),
    cost_price       FLOAT                  DEFAULT 0.0,          -- Para cálculo de margen
    stock_quantity   INTEGER       NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    min_stock_alert  INTEGER       NOT NULL DEFAULT 5,
    category_id      INTEGER       REFERENCES categories(id) ON DELETE SET NULL,
    is_active        BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMPTZ   DEFAULT NOW(),
    updated_at       TIMESTAMPTZ,

    UNIQUE (store_id, sku)    -- SKU único por tienda
);

COMMENT ON TABLE products IS 'Catálogo de productos por tienda.';
COMMENT ON COLUMN products.cost_price IS 'Precio de compra (para calcular margen de ganancia).';
COMMENT ON COLUMN products.min_stock_alert IS 'Umbral para alertas de stock bajo.';

CREATE INDEX IF NOT EXISTS ix_products_store_id   ON products(store_id);
CREATE INDEX IF NOT EXISTS ix_products_name       ON products(store_id, name);
CREATE INDEX IF NOT EXISTS ix_products_category   ON products(category_id);


-- =============================================================================
-- 4. TABLA: movements (Multi-Tenant)
-- =============================================================================
CREATE TABLE IF NOT EXISTS movements (
    id                    SERIAL PRIMARY KEY,
    store_id              INTEGER       NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    product_id            INTEGER       NOT NULL REFERENCES products(id),
    movement_type         VARCHAR(10)   NOT NULL CHECK (movement_type IN ('entry', 'exit')),
    quantity              INTEGER       NOT NULL CHECK (quantity > 0),
    unit_value            FLOAT,
    reason                VARCHAR(255),
    -- Anulaciones (PRO-96)
    is_voided             BOOLEAN       NOT NULL DEFAULT FALSE,
    voided_at             TIMESTAMPTZ,
    voided_by_movement_id INTEGER       REFERENCES movements(id),
    created_at            TIMESTAMPTZ   DEFAULT NOW()
);

COMMENT ON TABLE movements IS 'Historial de entradas y salidas de stock por tienda.';
COMMENT ON COLUMN movements.is_voided IS 'TRUE si el movimiento fue anulado.';

CREATE INDEX IF NOT EXISTS ix_movements_store_id   ON movements(store_id);
CREATE INDEX IF NOT EXISTS ix_movements_product_id ON movements(product_id);
CREATE INDEX IF NOT EXISTS ix_movements_created_at ON movements(created_at);


-- =============================================================================
-- DATOS DE PRUEBA (verificación)
-- =============================================================================

-- Insertar una tienda de prueba
INSERT INTO stores (name, slug, email, password_hash, address, phone)
VALUES (
    'Tienda Demo Stocky',
    'tienda-demo-stocky',
    'demo@stocky.app',
    '$2b$12$placeholder_hash_for_testing_only',
    'Calle Principal 123, Ciudad',
    '+57 300 000 0000'
);

-- Insertar una categoría de prueba
INSERT INTO categories (store_id, name, description)
VALUES (
    (SELECT id FROM stores WHERE slug = 'tienda-demo-stocky'),
    'Electrónica',
    'Dispositivos y accesorios electrónicos'
);

-- Insertar un producto de prueba
INSERT INTO products (store_id, name, sku, description, price, cost_price, stock_quantity, min_stock_alert, category_id)
VALUES (
    (SELECT id FROM stores WHERE slug = 'tienda-demo-stocky'),
    'Audífonos Bluetooth',
    'AUDIO-BT-001',
    'Audífonos inalámbricos con cancelación de ruido',
    150000.00,
    80000.00,
    25,
    5,
    (SELECT id FROM categories WHERE name = 'Electrónica' AND store_id = (SELECT id FROM stores WHERE slug = 'tienda-demo-stocky'))
);

-- Insertar un movimiento de prueba
INSERT INTO movements (store_id, product_id, movement_type, quantity, unit_value, reason)
VALUES (
    (SELECT id FROM stores WHERE slug = 'tienda-demo-stocky'),
    (SELECT id FROM products WHERE sku = 'AUDIO-BT-001'),
    'entry',
    25,
    80000.00,
    'Stock inicial — Migración a Supabase'
);


-- =============================================================================
-- VERIFICACIÓN (ejecutar después del INSERT para confirmar la migración)
-- =============================================================================

-- Verificar tablas creadas
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('stores', 'categories', 'products', 'movements')
ORDER BY table_name;

-- Verificar índices creados
SELECT indexname, tablename
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename IN ('stores', 'categories', 'products', 'movements')
ORDER BY tablename, indexname;

-- Verificar datos de prueba
SELECT
    s.name  AS tienda,
    s.plan_status,
    s.trial_start_date,
    s.subscription_expiry_date,
    c.name  AS categoria,
    p.name  AS producto,
    p.stock_quantity,
    m.movement_type,
    m.quantity
FROM stores     s
JOIN categories c ON c.store_id  = s.id
JOIN products   p ON p.store_id  = s.id
JOIN movements  m ON m.product_id = p.id
WHERE s.slug = 'tienda-demo-stocky';
