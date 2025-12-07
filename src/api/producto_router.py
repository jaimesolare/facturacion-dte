from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.core.db import get_db
from src.models import schemas
from src.repositories import producto_repository

router = APIRouter()

@router.post("/productos", response_model=schemas.ProductoResponse, status_code=201)
def create_producto_endpoint(producto: schemas.ProductoCreate, db: Session = Depends(get_db)):
    db_producto = producto_repository.get_producto_by_codigo(db, codigo=producto.codigo)
    if db_producto:
        raise HTTPException(status_code=400, detail="Product code already registered")
    return producto_repository.create_producto(db=db, producto=producto)

@router.get("/productos", response_model=List[schemas.ProductoResponse])
def read_productos_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    productos = producto_repository.get_productos(db, skip=skip, limit=limit)
    return productos
