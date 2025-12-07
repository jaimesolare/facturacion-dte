from sqlalchemy.orm import Session
from src.models import db_models, schemas
import uuid

from datetime import datetime
from sqlalchemy.exc import NoResultFound

def get_next_correlative(db: Session, tipo_dte: str) -> str:
    """
    Obtiene el siguiente número de control para un tipo de DTE dado.
    Incrementa el contador en la base de datos de manera atómica (o casi).
    """
    # Buscar la serie para este tipo de DTE
    # Bloqueamos la fila para evitar condiciones de carrera
    serie_record = db.query(db_models.Serie).filter(
        db_models.Serie.tipo_dte == tipo_dte
    ).with_for_update().first()

    if not serie_record:
        # Si no existe, creamos una por defecto (esto es útil para desarrollo)
        # En producción debería existir previamente.
        serie_record = db_models.Serie(
            tipo_dte=tipo_dte,
            serie="DTE-01-C01", # Ejemplo de serie
            correlativo_actual=0
        )
        db.add(serie_record)
        db.flush() # Para obtener el ID si fuera necesario, pero aquí necesitamos el objeto

    # Incrementar correlativo
    serie_record.correlativo_actual += 1
    db.add(serie_record) # Marcar para update
    # No hacemos commit aquí, dejamos que la transacción principal lo haga
    # o hacemos flush si necesitamos el valor ya.
    db.flush() 
    
    # Formatear: SERIE + CORRELATIVO (pad 15 chars según MH o lo que sea estándar)
    # MH standard: DTE-XX-MDV00001-000000000000001
    # Aquí usaremos un formato simplificado compatible con el ejemplo anterior pero dinámico
    # DTE-01-C001-00000001
    
    correlativo_str = str(serie_record.correlativo_actual).zfill(15)
    numero_control = f"{serie_record.serie}-{correlativo_str}"
    
    return numero_control

def get_dte_by_id(db: Session, dte_id: uuid.UUID) -> db_models.DTE:
    return db.query(db_models.DTE).filter(db_models.DTE.id == dte_id).first()

def get_dte_by_codigo_generacion(db: Session, codigo_generacion: uuid.UUID):
    return db.query(db_models.DTE).filter(db_models.DTE.codigo_generacion == codigo_generacion).first()

def create_dte(db: Session, tipo_dte: str, payload: dict) -> db_models.DTE:
    """
    Creates a new DTE record in the database before transmission.
    """
    identificacion = payload.get("identificacion", {})
    codigo_generacion_str = identificacion.get("codigoGeneracion")
    numero_control = identificacion.get("numeroControl")
    
    # Convert string UUID to object if needed, or keep as is depending on model.
    # Model expects UUID object for codigo_generacion.
    codigo_generacion = uuid.UUID(codigo_generacion_str) if codigo_generacion_str else uuid.uuid4()
    
    db_dte = db_models.DTE(
        codigo_generacion=codigo_generacion,
        numero_control=numero_control,
        tipo_dte=tipo_dte,
        documento_json=payload,
        estado="PROCESANDO",
        monto_total=payload.get("resumen", {}).get("totalPagar", 0) 
    )
    db.add(db_dte)
    db.commit()
    db.refresh(db_dte)
    return db_dte

def update_dte_after_transmission(db: Session, db_dte: db_models.DTE, response_data: dict) -> db_models.DTE:
    """
    Updates a DTE record with the response from the MH API.
    """
    db_dte.estado = response_data.get("estado")
    db_dte.sello_recepcion = response_data.get("selloRecepcion")
    db_dte.fecha_recepcion_mh = datetime.utcnow() # Or parse from response if available
    db.commit()
    db.refresh(db_dte)
    return db_dte

def update_dte_status(db: Session, db_dte: db_models.DTE, new_status: str) -> db_models.DTE:
    db_dte.estado = new_status
    db.commit()
    db.refresh(db_dte)
    return db_dte

def get_all_dtes(db: Session, limit: int = 100):
    return db.query(db_models.DTE).order_by(db_models.DTE.fecha_emision.desc()).limit(limit).all()
