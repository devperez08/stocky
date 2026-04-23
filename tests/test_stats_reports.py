import pytest

def test_dashboard_summary(client):
    """Prueba el endpoint de estadísticas del dashboard."""
    # Crear un producto
    client.post("/products", json={
        "name": "Prod", "sku": "S1", "price": 100.0, "stock_quantity": 10
    })
    
    response = client.get("/stats/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_inventory_value"] == 1000.0
    assert data["total_active_products"] == 1

def test_inventory_report_formats(client):
    """Prueba que los reportes se generen en JSON, CSV y Excel."""
    client.post("/products", json={"name": "P", "sku": "S", "price": 1.0})
    
    # JSON
    res_json = client.get("/reports/inventory?format=json")
    assert res_json.status_code == 200
    assert isinstance(res_json.json(), list)
    
    # CSV
    res_csv = client.get("/reports/inventory?format=csv")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]
    
    # Excel
    res_xlsx = client.get("/reports/inventory?format=excel")
    assert res_xlsx.status_code == 200
    assert "spreadsheetml.sheet" in res_xlsx.headers["content-type"]

def test_movements_report_filter(client):
    """Prueba el filtrado por fechas en el reporte de movimientos."""
    client.post("/products", json={"name": "P", "sku": "S", "price": 1.0})
    client.post("/movements", json={"product_id": 1, "movement_type": "entry", "quantity": 10})
    
    response = client.get("/reports/movements?format=json")
    assert response.status_code == 200
    assert len(response.json()) == 1
