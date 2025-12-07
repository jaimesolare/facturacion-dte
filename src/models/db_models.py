from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Integer, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from src.core.db import Base

class DTE(Base):
    __tablename__ = "dtes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo_generacion = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)
    numero_control = Column(String, unique=True, nullable=False, index=True)
    sello_recepcion = Column(String, index=True, nullable=True)
    tipo_dte = Column(String, index=True, nullable=False)
    estado = Column(String, index=True, nullable=False, default="PROCESANDO")
    documento_json = Column(JSON, nullable=False)
    fecha_emision = Column(DateTime, server_default=func.now())
    fecha_recepcion_mh = Column(DateTime, nullable=True)
    receptor_nit = Column(String, index=True, nullable=True)
    monto_total = Column(Numeric(18, 2), index=True, nullable=False)

class Evento(Base):
    __tablename__ = "eventos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dte_id = Column(UUID(as_uuid=True), ForeignKey("dtes.id"), nullable=False)
    tipo_evento = Column(String, index=True, nullable=False)
    sello_recepcion_evento = Column(String, nullable=True)
    evento_json = Column(JSON, nullable=False)
    fecha_creacion = Column(DateTime, server_default=func.now())

class Credenciales(Base):
    __tablename__ = "credenciales"

    id = Column(Integer, primary_key=True)
    ambiente = Column(String, unique=True, nullable=False)
    nit_usuario = Column(String, nullable=False)
    api_password_encrypted = Column(String, nullable=False)
    certificado_privado_encrypted = Column(String, nullable=False)
    certificado_publico = Column(String, nullable=False)
    token_jwt = Column(String, nullable=True)
    token_expiracion = Column(DateTime, nullable=True)

class Serie(Base):
    __tablename__ = "series"

    id = Column(Integer, primary_key=True)
    tipo_dte = Column(String(2), nullable=False, index=True)
    serie = Column(String(10), nullable=False)
    correlativo_actual = Column(Integer, nullable=False, server_default='0')

class Producto(Base):
    __tablename__ = "productos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String, unique=True, nullable=False, index=True)
    nombre = Column(String, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    tipo_item = Column(Integer, default=1, nullable=False) # 1=Bien, 2=Servicio
