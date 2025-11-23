# Data Models

**Feature**: Sistema de Emisión de DTE (El Salvador)

This document defines the primary data entities for the DTE system.

---

### 1. DTE (Documento Tributario Electrónico)

Represents a single electronic tax document. This is the central entity of the system.

- **Fields**:
  - `id` (UUID, Primary Key): Internal database identifier.
  - `codigo_generacion` (UUID, Unique, Indexed): The 36-character UUID that uniquely identifies the DTE for the MH. This is the main business key.
  - `numero_control` (String, Unique, Indexed): The 24-character control number.
  - `sello_recepcion` (String, Indexed, Nullable): The 40-character reception seal provided by the MH upon successful validation. It is `NULL` until the DTE is accepted.
  - `tipo_dte` (String, Indexed): The code for the DTE type (e.g., '01' for Factura, '03' for CCF).
  - `estado` (String, Indexed): The current status of the DTE. Values: `PROCESANDO`, `RECIBIDO`, `INVALIDADO`, `CONTINGENCIA`.
  - `documento_json` (JSONB): The full JSON payload of the DTE, as sent to or received from the MH.
  - `fecha_emision` (Timestamp): The timestamp when the DTE was issued.
  - `fecha_recepcion_mh` (Timestamp, Nullable): The timestamp when the MH accepted the DTE.
  - `receptor_nit` (String, Indexed, Nullable): The NIT of the DTE recipient, for querying purposes.
  - `monto_total` (Decimal, Indexed): The total amount of the transaction, for reporting.

- **Relationships**:
  - Has one-to-many relationship with `Evento` (a DTE can have multiple events, e.g., an invalidation event).

---

### 2. Evento

Represents a business event related to a DTE, such as an invalidation or a contingency declaration.

- **Fields**:
  - `id` (UUID, Primary Key): Internal database identifier.
  - `dte_id` (UUID, Foreign Key to DTE): The DTE this event is associated with.
  - `tipo_evento` (String, Indexed): The type of event (e.g., `INVALIDACION`, `CONTINGENCIA`).
  - `sello_recepcion_evento` (String, Nullable): The reception seal for the event itself.
  - `evento_json` (JSONB): The full JSON payload of the event sent to the MH.
  - `fecha_creacion` (Timestamp): The timestamp when the event was created.

- **Relationships**:
  - Belongs to one `DTE`.

---

### 3. Credenciales

Represents the security credentials required to operate with the MH API. This data should be stored encrypted.

- **Fields**:
  - `id` (Integer, Primary Key): Internal identifier.
  - `ambiente` (String, Unique): The environment (`PRUEBAS`, `PRODUCCION`).
  - `nit_usuario` (String): The NIT used for authentication.
  - `api_password_encrypted` (String): The encrypted API password.
  - `certificado_privado_encrypted` (String): The encrypted private key for the digital certificate.
  - `certificado_publico` (String): The public key for the digital certificate.
  - `token_jwt` (String, Nullable): The current JWT access token.
  - `token_expiracion` (Timestamp, Nullable): The expiration time of the current JWT.

- **Note**: This table will likely have only two rows, one for each environment. Access to this data must be severely restricted.
