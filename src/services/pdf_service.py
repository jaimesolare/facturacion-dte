from fpdf import FPDF
import qrcode
from io import BytesIO

def generate_dte_pdf(dte_data: dict) -> bytes:
    """
    Generates a simple PDF representation of a DTE.

    Args:
        dte_data: The dictionary containing DTE information.

    Returns:
        The PDF content as bytes.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Title
    pdf.cell(200, 10, txt="Documento Tributario Electrónico (DTE)", ln=True, align='C')

    # DTE Info
    pdf.cell(200, 10, txt=f"Código de Generación: {dte_data.get('codigo_generacion')}", ln=True)
    pdf.cell(200, 10, txt=f"Número de Control: {dte_data.get('numero_control')}", ln=True)
    pdf.cell(200, 10, txt=f"Sello de Recepción: {dte_data.get('sello_recepcion')}", ln=True)
    pdf.cell(200, 10, txt=f"Estado: {dte_data.get('estado')}", ln=True)

    # QR Code
    qr_data = f"https://admin.factura.gob.sv/consultaPublica?codigoGeneracion={dte_data.get('codigo_generacion')}"
    qr = qrcode.make(qr_data)
    
    # Save QR to a buffer
    qr_buffer = BytesIO()
    qr.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    # Add QR to PDF
    pdf.image(qr_buffer, x=150, y=30, w=50)

    pdf.ln(20)
    pdf.cell(200, 10, txt="Este es un marcador de posición para la Versión Legible del DTE.", ln=True, align='C')

    return pdf.output(dest='S').encode('latin-1')
