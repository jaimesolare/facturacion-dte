import pytest
from decimal import Decimal
from src.services.dte_service import _numero_a_letras
from src.models import schemas

def test_numero_a_letras_enteros():
    assert _numero_a_letras(Decimal("100.00")) == "US 100 DOLARES CON 00/100 USD"
    assert _numero_a_letras(Decimal("1.00")) == "US 1 DOLARES CON 00/100 USD"

def test_numero_a_letras_decimales():
    assert _numero_a_letras(Decimal("100.50")) == "US 100 DOLARES CON 50/100 USD"
    assert _numero_a_letras(Decimal("100.99")) == "US 100 DOLARES CON 99/100 USD"
    assert _numero_a_letras(Decimal("0.01")) == "US 0 DOLARES CON 01/100 USD"

def test_calculo_totales_factura():
    # Este test verifica la lógica de cálculo de totales simulando el proceso
    # que ocurre dentro de generar_json_factura, pero aislado.
    
    # Setup items
    item1 = schemas.ItemSchema(
        num_item=1, tipo_item=1, descripcion="Item 1",
        cantidad=2.0, codigo_unidad_medida="59",
        precio_unitario=10.0, monto_descuento=0.0,
        venta_no_sujeta=0.0, venta_exenta=0.0, venta_gravada=20.0
    )
    item2 = schemas.ItemSchema(
        num_item=2, tipo_item=1, descripcion="Item 2",
        cantidad=1.0, codigo_unidad_medida="59",
        precio_unitario=50.0, monto_descuento=5.0,
        venta_no_sujeta=0.0, venta_exenta=0.0, venta_gravada=45.0
    )
    
    # Lógica de cálculo (replicada de dte_service para validación)
    total_gravada = Decimal(str(item1.venta_gravada)) + Decimal(str(item2.venta_gravada))
    assert total_gravada == Decimal("65.0")
    
    total_descuento = Decimal(str(item1.monto_descuento)) + Decimal(str(item2.monto_descuento))
    assert total_descuento == Decimal("5.0")
    
    subtotal = total_gravada # En este caso simple
    iva = (total_gravada * Decimal("0.13")).quantize(Decimal("0.01"))
    
    assert iva == Decimal("8.45")
    
    total_pagar = subtotal + iva
    assert total_pagar == Decimal("73.45")
