import pytest

def test_create_product_success(client):
    """Prueba la creación exitosa de un producto."""
    response = client.post("/products", json={
        "name": "Teclado Gaming",
        "sku": "TG-999",
        "price": 45.50,
        "stock_quantity": 50,
        "min_stock_alert": 5
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Teclado Gaming"
    assert data["sku"] == "TG-999"
    assert data["id"] is not None

def test_create_product_duplicate_sku(client):
    """Prueba que no se puedan crear productos con el mismo SKU."""
    # Primer producto
    client.post("/products", json={
        "name": "Producto A", "sku": "DUPE-001", "price": 10.0
    })
    # Intento de segundo producto con mismo SKU
    response = client.post("/products", json={
        "name": "Producto B", "sku": "DUPE-001", "price": 20.0
    })
    assert response.status_code == 409
    assert "ya existe" in response.json()["detail"].lower()

def test_get_products(client):
    """Prueba obtener la lista de productos."""
    client.post("/products", json={"name": "P1", "sku": "S1", "price": 10.0})
    client.post("/products", json={"name": "P2", "sku": "S2", "price": 20.0})
    
    response = client.get("/products")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_single_product(client):
    """Prueba obtener un producto específico."""
    client.post("/products", json={"name": "P1", "sku": "S1", "price": 10.0})
    response = client.get("/products/1")
    assert response.status_code == 200
    assert response.json()["sku"] == "S1"

def test_update_product(client):
    """Prueba actualizar la información de un producto."""
    client.post("/products", json={"name": "Viejo", "sku": "OLD-1", "price": 10.0})
    response = client.put("/products/1", json={"name": "Nuevo", "price": 15.0})
    assert response.status_code == 200
    assert response.json()["name"] == "Nuevo"
    assert response.json()["price"] == 15.0

def test_delete_product_soft(client):
    """Prueba el soft delete del producto."""
    client.post("/products", json={"name": "Borrar", "sku": "DEL-1", "price": 10.0})
    delete_response = client.delete("/products/1")
    assert delete_response.status_code == 200
    
    # Comprobar que ya no aparece en el listado activo
    get_response = client.get("/products")
    products = get_response.json()
    assert len(products) == 0
