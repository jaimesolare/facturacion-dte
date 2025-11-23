from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from src.core.db import get_db, SessionLocal
from src.models import schemas
from src.services import dte_service
from src.repositories import dte_repository
import uuid

router = APIRouter()

async def background_dte_task(dte_id: uuid.UUID):
    """
    Wrapper para ejecutar la lógica de transmisión en background con su propia sesión de BD.
    """
    db = SessionLocal()
    try:
        await dte_service.transmit_dte_logic(db, dte_id)
    finally:
        db.close()

@router.post("/dte", response_model=schemas.DTECreateResponse, status_code=202)
async def create_dte_endpoint(dte_in: schemas.DTECreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Endpoint to initiate the DTE issuance process.
    Returns immediately with 'PROCESANDO' status.
    """
    try:
        # Validar que los datos correspondan al esquema de factura
        # TODO: Soportar otros tipos de DTE según dte_in.tipo_dte
        datos_factura = schemas.FacturaCreateSchema(**dte_in.datos_dte)
        
        # 1. Generar el JSON completo (Síncrono, rápido)
        full_payload = dte_service.generar_json_factura(db, datos_factura)
        
        # 2. Guardar en BD (Síncrono)
        db_dte = dte_repository.create_dte(db, dte_in.tipo_dte, full_payload)
        
        # 3. Encolar tarea de transmisión (Asíncrono)
        background_tasks.add_task(background_dte_task, db_dte.id)
        
        return {
            "codigo_generacion": db_dte.codigo_generacion,
            "estado": "PROCESANDO"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dte/{codigo_generacion}", response_model=schemas.DTEResponse)
def get_dte_status_endpoint(codigo_generacion: uuid.UUID, db: Session = Depends(get_db)):
    """
    Endpoint to get the status of a specific DTE.
    """
    db_dte = dte_repository.get_dte_by_codigo_generacion(db, codigo_generacion=codigo_generacion)
    if db_dte is None:
        raise HTTPException(status_code=404, detail="DTE not found")
    return db_dte

@router.post("/dte/{codigo_generacion}/invalidate", status_code=202)
async def invalidate_dte_endpoint(codigo_generacion: uuid.UUID, invalidation_in: schemas.InvalidateRequest, db: Session = Depends(get_db)):
    """
    Endpoint to initiate the DTE invalidation process.
    """
    try:
        await dte_service.process_invalidation(db, codigo_generacion, invalidation_in.motivo)
        return {"message": "Invalidation request accepted and is being processed."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
