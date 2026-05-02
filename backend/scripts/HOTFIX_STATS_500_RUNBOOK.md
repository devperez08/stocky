# Hotfix Runbook - Stats/Reports 500

## Problema

En Supabase, la tabla `public.movements` tiene la columna `unit_value`, mientras que el backend consulta `unit_price`. Esto dispara errores SQL (`column "unit_price" does not exist`) y termina en `500` para dashboard/reportes.

## Evidencia verificada

- Falla:
  - `select sum(unit_price * quantity) as total_sales from public.movements;`
- Funciona:
  - `select sum(unit_value * quantity) as total_sales from public.movements where is_voided = false;`

## Archivos del hotfix

- `backend/scripts/hotfix_movements_unit_price.sql`
  - Renombra/corrige `unit_value -> unit_price` sin perder datos.
  - Es idempotente para ejecuciones repetidas.
- `backend/scripts/supabase_migration.sql`
  - Corregido para usar `unit_price` en nuevas migraciones.

## Ejecucion en Supabase

1. Abrir SQL Editor del proyecto cloud.
2. Ejecutar completo `backend/scripts/hotfix_movements_unit_price.sql`.

## Verificacion post-hotfix (DB)

```sql
select column_name, data_type, is_nullable
from information_schema.columns
where table_schema='public' and table_name='movements'
  and column_name in ('unit_price','unit_value')
order by column_name;
```

Esperado:
- Existe `unit_price`.
- No existe `unit_value`.

## Verificacion post-hotfix (API)

Con un JWT valido:

```bash
curl -H "Authorization: Bearer <TOKEN>" "<API_URL>/stats/summary"
curl -H "Authorization: Bearer <TOKEN>" "<API_URL>/reports/inventory?format=json"
curl -H "Authorization: Bearer <TOKEN>" "<API_URL>/reports/movements?format=json"
```

Esperado:
- HTTP 200 en los tres endpoints.
- Dashboard y reportes cargan datos sin `500`.

## Siguiente iteracion

Implementar perfil post-login para campos opcionales de tienda (`phone`, `address` y relacionados), manteniendo signup ligero.
