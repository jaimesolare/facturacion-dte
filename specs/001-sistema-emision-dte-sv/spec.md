# Feature Specification: Sistema de Emisión de Documentos Tributarios Electrónicos (DTE) - El Salvador

**Feature Branch**: `001-sistema-emision-dte-sv`  
**Created**: 2025-10-28  
**Status**: Draft  
**Input**: User description: "Este plan de implementación detalla el desarrollo de un sistema interno de emisión de Documentos Tributarios Electrónicos (DTE) utilizando el Sistema de Transmisión DTE del Ministerio de Hacienda (MH) de El Salvador... Será importante conectarlo a un sistema de facturación que esté desarrollado en una base de datos más adelante."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Emisión de una Factura Electrónica (Priority: P1)

Como usuario del sistema, necesito poder generar, firmar y transmitir una Factura Electrónica (FE) estándar al Ministerio de Hacienda (MH), recibir el Sello de Recepción que valida el documento y entregarla al cliente final.

**Why this priority**: Es el flujo más fundamental y común, representando la capacidad básica del sistema para operar legalmente.

**Independent Test**: Se puede probar generando una única factura, transmitiéndola al ambiente de pruebas del MH, verificando que se reciba un Sello de Recepción válido y que se genere la representación gráfica (PDF) y el JSON para el cliente.

**Acceptance Scenarios**:

1.  **Given** un conjunto de datos de venta válidos, **When** el usuario solicita la emisión de una Factura Electrónica, **Then** el sistema genera un DTE en formato JSON, lo firma y lo transmite al MH.
2.  **Given** una transmisión exitosa, **When** el MH responde, **Then** el sistema recibe y almacena el Sello de Recepción de 40 caracteres, asociándolo al DTE correspondiente.
3.  **Given** un DTE con Sello de Recepción, **When** se finaliza el proceso, **Then** el sistema genera una versión legible en PDF con un código QR y envía tanto el PDF como el JSON al receptor del documento.

---

### User Story 2 - Operación en Modo de Contingencia (Priority: P2)

Como usuario del sistema, cuando los servicios del MH no están disponibles, necesito poder seguir generando DTEs en modo "offline" (contingencia) y luego reportarlos al MH una vez que el servicio se restablezca.

**Why this priority**: Asegura la continuidad del negocio, permitiendo que la facturación no se detenga por fallas externas.

**Independent Test**: Se puede probar simulando una falla de conexión al MH, generando varios DTEs en modo contingencia, y luego, al restaurar la conexión, transmitir el "Evento de Contingencia" y el lote de DTEs pendientes.

**Acceptance Scenarios**:

1.  **Given** que el servicio del MH no responde tras 3 intentos, **When** el usuario intenta emitir un DTE, **Then** el sistema genera el DTE marcándolo como "Modelo de Facturación: Diferido" y "Tipo de Transmisión: por contingencia".
2.  **Given** que la contingencia ha terminado, **When** el usuario inicia el proceso de sincronización, **Then** el sistema genera y transmite un "Evento de Contingencia" al MH detallando todos los DTEs emitidos offline.
3.  **Given** que el Evento de Contingencia fue aceptado por el MH, **When** el sistema procede a enviar los DTEs, **Then** el lote de DTEs generados durante la falla es transmitido y procesado por el MH en un plazo de 72 horas.

---

### User Story 3 - Invalidación de un DTE (Priority: P3)

Como usuario del sistema, si he emitido un DTE con errores, necesito poder anularlo mediante la transmisión de un "Evento de Invalidación" al MH.

**Why this priority**: Es un proceso correctivo esencial para mantener la integridad de los registros contables y fiscales.

**Independent Test**: Se puede probar emitiendo un DTE válido, y posteriormente generando y transmitiendo un evento de invalidación que haga referencia a ese DTE. El éxito se comprueba consultando el estado del DTE en el portal del MH.

**Acceptance Scenarios**:

1.  **Given** un DTE previamente emitido y aceptado por el MH, **When** el usuario identifica un error y solicita la invalidación, **Then** el sistema genera un "Evento de Invalidación" en formato JSON, firmado electrónicamente.
2.  **Given** un evento de invalidación generado, **When** se transmite al MH, **Then** el DTE original es marcado con el estado "INVALIDADO" en los registros del MH.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE generar los 11 tipos de DTE especificados por el MH en formato JSON (ECMA-404).
- **FR-002**: El sistema DEBE autenticarse con la API de Seguridad del MH para obtener un token de acceso JWT válido por 24 horas.
- **FR-003**: El sistema DEBE firmar localmente cada DTE y evento utilizando el certificado digital y el estándar JSON Web Signature (JWS).
- **FR-004**: El sistema DEBE generar un `Código de Generación` único universal (UUID v4) de 36 caracteres para cada DTE.
- **FR-005**: El sistema DEBE construir el `Número de Control` de 24 caracteres siguiendo la estructura definida por el MH.
- **FR-006**: El sistema DEBE transmitir el DTE firmado al endpoint `/fesv/recepciondte` y almacenar el `Sello de Recepción` devuelto.
- **FR-007**: El sistema DEBE implementar una política de reintentos (1 intento inicial + 2 reintentos) si la transmisión falla o excede los 5 segundos.
- **FR-008**: El sistema DEBE ser capaz de operar en modo de contingencia, generando DTEs offline y transmitiendo un `Evento de Contingencia` al MH en un plazo de 24 horas tras la restauración del servicio.
- **FR-009**: El sistema DEBE permitir la generación y transmisión de un `Evento de Invalidación` para anular DTEs con errores, respetando los plazos legales.
- **FR-010**: El sistema DEBE generar una representación gráfica (`Versión Legible`) en formato PDF para cada DTE, la cual debe incluir un código QR para la consulta pública del documento.
- **FR-011**: El sistema DEBE garantizar el almacenamiento y respaldo de todos los DTEs emitidos por un período obligatorio de 15 años.
- **FR-012**: El sistema DEBE utilizar y mantener actualizados los catálogos oficiales proporcionados por el MH.
- **FR-013**: El sistema DEBE ser diseñado de forma modular para permitir su futura integración con un sistema de facturación externo basado en una base de datos.

### Key Entities

- **DTE (Documento Tributario Electrónico)**: La unidad central del sistema. Representa un documento fiscal como una factura o nota de crédito. Atributos clave: Código de Generación, Número de Control, Cuerpo JSON, Sello de Recepción, Estado.
- **Evento**: Un mensaje de datos especial (también en JSON firmado) que modifica o describe el estado de un DTE. Tipos principales: Evento de Contingencia, Evento de Invalidación.
- **Credenciales**: Los activos de seguridad para operar. Incluye el Certificado de Firma Electrónica (clave pública y privada) y la Contraseña de la API.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los DTEs generados durante la fase de pruebas deben pasar las validaciones estructurales y de negocio del MH sin rechazos.
- **SC-002**: El tiempo total desde que se solicita la emisión de un DTE hasta que se recibe el Sello de Recepción del MH debe ser inferior a 10 segundos en condiciones normales.
- **SC-003**: El sistema debe activar correctamente el modo de contingencia después de 3 intentos de transmisión fallidos y debe ser capaz de sincronizar exitosamente los eventos y DTEs pendientes una vez restablecido el servicio.
- **SC-004**: El sistema debe superar con éxito el 100% de los casos de prueba mínimos exigidos por el MH para obtener la autorización de paso a producción.