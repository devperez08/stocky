# service se encarga de hablar con la base de datos, permite hacer las operaciones CRUD

from sqlalchemy.orm import Session
from backend.app.models.product import Product # importamos el modelo de la tabla
from backend.app.schemas.product import ProductCreate # importamos el schema de creacion de producto
from backend.app.schemas.product import ProductUpdate # importamos el schema de actualizacion de producto

def get_product_by_id(db: Session, product_id: int): # product_id es el id del producto que queremos consultar
    return db.query(Product).filter(Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    # Solo devolvemos los productos activos
    return db.query(Product).filter(Product.is_active == True).offset(skip).limit(limit).all()
    
def create_product(db: Session, product_data: ProductCreate): #product_data es la variable que recibe los datos del producto
    # 1. Creamos el objeto basado en el modelo Product
    # Usamos **product_data.dict() para "descomprimir" los datos del usuario
    new_product = Product(**product_data.dict())
    
    # 2. Lo agregamos a la sesión
    db.add(new_product)
    
    # 3. Guardamos los cambios
    db.commit()
    
    # 4. Refrescamos para tener el ID que le puso la base de datos
    db.refresh(new_product)
    
    return new_product

def delete_product(db: Session, product_id: int):
    # Reutilizamos nuestra propia función para buscar
    db_product = get_product_by_id(db, product_id)
    
    if db_product:
        # Si lo encontramos, lo desactivamos
        db_product.is_active = False
        db.commit()
        db.refresh(db_product)
        return db_product
    
    # Si no lo encontramos, devolvemos None para que el Router
    # sepa que debe dar un error 404.
    return None

def update_product(db: Session, product_id: int, product_data: ProductUpdate):
    # 1. buscar producto
    db_product = get_product_by_id(db, product_id)
    
    if not db_product:
        return None
    
    # 2. El truco: Convertimos los datos nuevos a un diccionario
    # 'exclude_unset=True' le dice a Pydantic: "Solo tráeme los campos que el usuario REALMENTE envió"
    update_data = product_data.dict(exclude_unset=True)
    
    # 3. Recorremos ese diccionario y actualizamos el objeto de la DB
    for key, value in update_data.items():
        setattr(db_product, key, value) # Esto es como hacer db_product.campo = valor
    
    # 4. Guardamos y refrescamos
    db.commit()
    db.refresh(db_product)
    
    return db_product