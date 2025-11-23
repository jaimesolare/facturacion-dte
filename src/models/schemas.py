from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, date

# ===============================================================
# ESQUEMAS PARA LA CREACIÓN DE UN NUEVO DTE (FACTURA)
# ===============================================================

class ReceptorSchema(BaseModel):
    """Datos del cliente o receptor del DTE."""
    nit: str = Field(..., max_length=14, description="NIT del receptor")
    nrc: Optional[str] = Field(None, max_length=8, description="NRC del receptor (si aplica)")
    nombre: str = Field(..., max_length=250, description="Nombre completo o razón social del receptor")
    cod_actividad: str = Field(..., max_length=6, description="Código de actividad económica del receptor")
    desc_actividad: str = Field(..., max_length=500, description="Descripción de la actividad económica")
    direccion_calle: str = Field(..., max_length=200)
    direccion_complemento: Optional[str] = Field(None, max_length=200)
    direccion_municipio: str = Field(..., max_length=2, description="Código de 2 dígitos del municipio")
    direccion_departamento: str = Field(..., max_length=2, description="Código de 2 dígitos del departamento")
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)

class ItemSchema(BaseModel):
    """Datos para cada línea o item del cuerpo del documento."""
    num_item: int = Field(..., gt=0, description="Número correlativo del item (1, 2, 3...)")
    tipo_item: int = Field(1, description="1: Bienes, 2: Servicios")
    descripcion: str = Field(..., max_length=1000)
    cantidad: float = Field(..., gt=0)
    codigo_unidad_medida: str = Field(..., max_length=2, description="Código de unidad de medida (ej: 59 para 'Unidad')")
    precio_unitario: float = Field(..., ge=0)
    monto_descuento: float = Field(0.0, ge=0, description="Monto de descuento por item (si aplica)")
    venta_no_sujeta: float = Field(0.0, ge=0)
    venta_exenta: float = Field(0.0, ge=0)
    venta_gravada: float = Field(..., ge=0, description="Venta neta (sin IVA) del item")
    tributos: Optional[List[str]] = Field(None, description="Códigos de tributos aplicables al item (ej: '20' para IVA 13%)")

class CondicionOperacionSchema(BaseModel):
    """Define las condiciones de la transacción."""
    forma_pago: str = Field(..., max_length=2, description="Código de forma de pago (ej: '01' para Contado)")
    plazo: Optional[str] = Field(None, description="Plazo en días (si es crédito)")
    periodo_plazo: Optional[str] = Field(None, max_length=2, description="Periodo del plazo (ej: '01' Días, '02' Meses)")

class FacturaCreateSchema(BaseModel):
    """Esquema principal para la creación de una Factura de Venta (DTE 01)."""
    receptor: ReceptorSchema
    items: List[ItemSchema] = Field(..., min_items=1)
    condicion_operacion: CondicionOperacionSchema


# ===============================================================
# ESQUEMAS DE RESPUESTA Y OTROS
# ===============================================================

class DTECreate(BaseModel):
    tipo_dte: str
    datos_dte: Dict[str, Any]

class DTECreateResponse(BaseModel):
    codigo_generacion: UUID
    estado: str

class DTEResponse(BaseModel):
    codigo_generacion: UUID
    numero_control: Optional[str]
    sello_recepcion: Optional[str]
    estado: str
    fecha_emision: datetime
    documento_json: Dict[str, Any]

    class Config:
        from_attributes = True

class InvalidateRequest(BaseModel):
    motivo: str
