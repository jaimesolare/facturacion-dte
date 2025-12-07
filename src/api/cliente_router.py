from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

router = APIRouter(prefix="/clientes", tags=["clientes"])

# In-memory database
CLIENTES_DB = []

class Cliente(BaseModel):
    id: Optional[str] = None
    nit: str
    nrc: Optional[str] = None
    nombre: str
    cod_actividad: str
    desc_actividad: str
    direccion: str
    departamento: str
    municipio: str
    telefono: Optional[str] = None
    email: Optional[str] = None

@router.get("/", response_model=List[Cliente])
async def get_clientes():
    return CLIENTES_DB

@router.post("/", response_model=Cliente)
async def create_cliente(cliente: Cliente):
    # Check if NIT already exists
    if any(c.nit == cliente.nit for c in CLIENTES_DB):
        raise HTTPException(status_code=400, detail="Cliente con este NIT ya existe")
    
    cliente.id = str(uuid.uuid4())
    CLIENTES_DB.append(cliente)
    return cliente

@router.delete("/{nit}")
async def delete_cliente(nit: str):
    global CLIENTES_DB
    original_len = len(CLIENTES_DB)
    CLIENTES_DB = [c for c in CLIENTES_DB if c.nit != nit]
    
    if len(CLIENTES_DB) == original_len:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    return {"message": "Cliente eliminado correctamente"}
