from sqlalchemy.orm import Session
from src.models.db_models import Producto
from src.models import schemas

def create_producto(db: Session, producto: schemas.ProductoCreate):
    db_producto = Producto(
        codigo=producto.codigo,
        nombre=producto.nombre,
        precio_unitario=producto.precio_unitario,
        tipo_item=producto.tipo_item
    )
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto

def get_productos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Producto).offset(skip).limit(limit).all()

def get_producto_by_codigo(db: Session, codigo: str):
    return db.query(Producto).filter(Producto.codigo == codigo).first()
