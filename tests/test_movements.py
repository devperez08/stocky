import pytest

def test_movement_entry_success(client):
    """Prueba el registro exitoso de una entrada y actualización de stock."""
    # Crear producto inicial
    client.post("/products", json={
        "name": "Test", "sku": "T-1", "price": 1.0, "stock_quantity": 10
    })
    
    # Registrar entrada
    response = client.post("/movements", json={
        "product_id": 1,
        "movement_type": "entry",
        "quantity": 5,
        "reason": "Compra"
    })
    
    assert response.status_code == 201
    assert response.json()["quantity"] == 5
    
    # Verificar stock actualizado
    prod_response = client.get("/products/1")
    assert prod_response.json()["stock_quantity"] == 15

def test_movement_exit_success(client):
    """Prueba el registro exitoso de una salida."""
    client.post("/products", json={
        "name": "Test", "sku": "T-1", "price": 1.0, "stock_quantity": 10
    })
    
    response = client.post("/movements", json={
        "product_id": 1,
        "movement_type": "exit",
        "quantity": 3
    })
    
    assert response.status_code == 201
    
    # Verificar stock
    prod_response = client.get("/products/1")
    assert prod_response.json()["stock_quantity"] == 7

def test_movement_exit_insufficient_stock(client):
    """Prueba que falle la salida si no hay suficiente stock."""
    client.post("/products", json={
        "name": "Test", "sku": "T-1", "price": 1.0, "stock_quantity": 5
    })
    
    # Intentar sacar 10 teniendo solo 5
    response = client.post("/movements", json={
        "product_id": 1,
        "movement_type": "exit",
        "quantity": 10
    })
    
    assert response.status_code == 400
    assert "insuficiente" in response.json()["detail"].lower()
    
    # Verificar que el stock no cambió
    prod_response = client.get("/products/1")
    assert prod_response.json()["stock_quantity"] == 5

def test_get_movements_history(client):
    """Prueba obtener el historial de movimientos."""
    client.post("/products", json={"name": "T", "sku": "S", "price": 1.0})
    client.post("/movements", json={"product_id": 1, "movement_type": "entry", "quantity": 10})
    client.post("/movements", json={"product_id": 1, "movement_type": "exit", "quantity": 2})
    
    response = client.get("/movements")
    assert response.status_code == 200
    assert len(response.json()) == 2
