import uuid
import asyncio
from typing import Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from decimal import Decimal, ROUND_HALF_UP

from src.models import schemas, db_models
from src.core.config import settings
from src.core.signing import firmar_documento
from src.core.client import MHClient
from src.repositories import dte_repository
from src.services.auth_service import AuthManager

logger = logging.getLogger(__name__)

def _numero_a_letras(monto: Decimal) -> str:
    """
    Convierte un monto Decimal a letras (formato moneda).
    Nota: Esta es una implementación simplificada. En producción usar una librería probada como num2words.
    """
    # Separar entero y decimal
    entero = int(monto)
    decimal = int(round((monto - entero) * 100))
    
    # Lógica básica para demostración (se puede expandir)
    # Aquí idealmente usaríamos una librería, pero para no añadir dependencias externas sin permiso:
    texto_entero = f"US {entero}" 
    
    return f"{texto_entero} DOLARES CON {decimal:02d}/100 USD"

def generar_json_factura(db: Session, datos_factura: schemas.FacturaCreateSchema) -> Dict[str, Any]:
    """
    Construye el diccionario Python que representa el JSON completo para un DTE tipo 01 (Factura).
    """
    # --- 1. Resumen de Totales (Usando Decimal) ---
    # Convertir inputs a Decimal para precisión
    items_processed = []
    total_venta_no_sujeta = Decimal(0)
    total_venta_exenta = Decimal(0)
    total_venta_gravada = Decimal(0)
    total_descuento = Decimal(0)

    for item in datos_factura.items:
        precio_uni = Decimal(str(item.precio_unitario))
        cantidad = Decimal(str(item.cantidad))
        monto_descu = Decimal(str(item.monto_descuento))
        
        # Recalcular valores por línea para asegurar consistencia
        venta_gravada = (precio_uni * cantidad) - monto_descu
        
        # Asumimos todo gravado para este ejemplo simple, adaptar según tipo_item
        total_venta_gravada += venta_gravada
        total_descuento += monto_descu
        
        items_processed.append({
            "numItem": item.num_item,
            "tipoItem": item.tipo_item,
            "descripcion": item.descripcion,
            "cantidad": float(cantidad),
            "codigoUnidadMedida": item.codigo_unidad_medida,
            "precioUni": float(precio_uni),
            "montoDescu": float(monto_descu),
            "ventaNoSuj": float(item.venta_no_sujeta),
            "ventaExenta": float(item.venta_exenta),
            "ventaGravada": float(venta_gravada),
            "tributos": item.tributos or ["20"]
        })

    subtotal_ventas = total_venta_no_sujeta + total_venta_exenta + total_venta_gravada
    subtotal = subtotal_ventas - total_descuento
    
    # IVA 13%
    iva = (total_venta_gravada * Decimal("0.13")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    monto_total_operacion = subtotal + iva
    total_a_pagar = monto_total_operacion
    
    total_letras = _numero_a_letras(total_a_pagar)

    resumen = {
        "totalNoSuj": float(total_venta_no_sujeta),
        "totalExenta": float(total_venta_exenta),
        "totalGravada": float(total_venta_gravada),
        "subTotalVentas": float(subtotal_ventas),
        "descuNoSuj": 0.0, "descuExenta": 0.0, 
        "descuGravada": float(total_descuento),
        "porcentajeDescuento": 0.0, 
        "totalDescu": float(total_descuento),
        "subTotal": float(subtotal),
        "ivaRete1": 0.0, "reteRenta": 0.0,
        "montoTotalOperacion": float(monto_total_operacion),
        "totalNoGravado": float(total_venta_no_sujeta + total_venta_exenta),
        "totalPagar": float(total_a_pagar),
        "totalLetras": total_letras,
        "totalIva": float(iva), "saldoFavor": 0.0,
        "condicionOperacion": int(datos_factura.condicion_operacion.forma_pago)
    }

    # --- 2. Generación de Correlativo ---
    numero_control = dte_repository.get_next_correlative(db, "01")

    # --- 3. Ensamblaje del DTE completo ---
    dte_payload = {
        "identificacion": {
            "version": 3, "ambiente": settings.MH_AMBIENTE, "tipoDte": "01",
            "numeroControl": numero_control,
            "codigoGeneracion": str(uuid.uuid4()).upper(),
            "tipoModelo": 1, "tipoOperacion": 1, "tipoContingencia": None,
            "motivoContin": None, 
            "fecEmi": datetime.now().strftime("%Y-%m-%d"),
            "horEmi": datetime.now().strftime("%H:%M:%S"), 
            "tipoMoneda": "USD"
        },
        "emisor": {
            "nit": settings.MH_NIT, 
            "nrc": "12345-6", # Debería venir de config también
            "nombre": "EMPRESA EMISORA DE PRUEBA S.A. DE C.V.",
            "codActividad": "62010", 
            "descActividad": "Actividades de informática",
            "direccion": {"departamento": "06", "municipio": "14", "complemento": "San Salvador"},
            "telefono": "2222-2222", 
            "email": "emisor@empresa.com"
        },
        "receptor": {
            "nit": datos_factura.receptor.nit, 
            "nrc": datos_factura.receptor.nrc,
            "nombre": datos_factura.receptor.nombre, 
            "codActividad": datos_factura.receptor.cod_actividad,
            "descActividad": datos_factura.receptor.desc_actividad,
            "direccion": {
                "departamento": datos_factura.receptor.direccion_departamento,
                "municipio": datos_factura.receptor.direccion_municipio,
                "complemento": datos_factura.receptor.direccion_complemento
            },
            "telefono": datos_factura.receptor.telefono, 
            "email": datos_factura.receptor.email
        },
        "cuerpoDocumento": items_processed,
        "resumen": resumen
    }
    return dte_payload


async def transmit_dte_logic(db: Session, dte_id: uuid.UUID):
    """
    Lógica de transmisión asíncrona. Recupera el DTE de la BD, lo firma y lo envía.
    """
    logger.info(f"Iniciando transmisión en segundo plano para DTE {dte_id}...")
    db_dte = dte_repository.get_dte_by_id(db, dte_id)
    if not db_dte:
        logger.error(f"DTE {dte_id} no encontrado para transmisión.")
        return

    try:
        full_payload = db_dte.documento_json
        
        # 3. Firmar el payload (CPU bound - ejecutar en thread pool)
        loop = asyncio.get_running_loop()
        signed_jws = await loop.run_in_executor(None, firmar_documento, full_payload)
        logger.info("Documento firmado exitosamente.")

        # 4. Obtener token de autenticación
        auth_manager = AuthManager()
        token = await auth_manager.get_mh_token()
        
        # 5. Transmitir al MH
        mh_client = MHClient()
        response_data = await mh_client.transmitir_dte(signed_jws, token)
        logger.info(f"Respuesta del MH recibida: {response_data}")

        # 6. Actualizar el DTE con la respuesta del MH
        dte_repository.update_dte_after_transmission(db, db_dte, response_data)
        logger.info(f"DTE actualizado en BD con estado: {db_dte.estado}")

    except Exception as e:
        logger.error(f"Error en transmisión de DTE {dte_id}: {e}", exc_info=True)
        dte_repository.update_dte_status(db, db_dte, "ERROR_TRANSMISION")

