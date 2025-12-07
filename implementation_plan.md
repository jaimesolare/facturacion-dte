# Implementation Plan - System Expansion

## Goal Description
Expand the DTE system to include new requested modalities: **Reportes**, **Compras**, **Ventas**, **Facturar por Lotes**, and **Punto de Venta (POS)**. This involves creating the frontend structure and navigation for these modules.

## Proposed Changes

### Backend (`src/main.py`)
#### [MODIFY] [src/main.py](file:///c:/Users/14-DW0004LA/Desktop/facturacion/src/main.py)
- Add GET routes for:
    - `/reportes` -> `frontend/reportes.html`
    - `/compras` -> `frontend/compras.html`
    - `/ventas` -> `frontend/ventas.html`
    - `/lotes` -> `frontend/lotes.html`
    - `/pos` -> `frontend/pos.html`

### Frontend Pages (New)
#### [NEW] [frontend/reportes.html](file:///c:/Users/14-DW0004LA/Desktop/facturacion/frontend/reportes.html)
- Basic layout with charts placeholder and date filters.
#### [NEW] [frontend/compras.html](file:///c:/Users/14-DW0004LA/Desktop/facturacion/frontend/compras.html)
- Table for received DTEs (Compras) and button to register new expense.
#### [NEW] [frontend/ventas.html](file:///c:/Users/14-DW0004LA/Desktop/facturacion/frontend/ventas.html)
- Detailed history of issued DTEs with filters.
#### [NEW] [frontend/lotes.html](file:///c:/Users/14-DW0004LA/Desktop/facturacion/frontend/lotes.html)
- File upload interface for CSV/Excel batch processing.
#### [NEW] [frontend/pos.html](file:///c:/Users/14-DW0004LA/Desktop/facturacion/frontend/pos.html)
- Simplified interface: Product grid on left, Cart on right.

### Frontend Navigation (Update)
#### [MODIFY] All HTML files
- Update the `<nav class="nav-menu">` in `index.html`, `emitir.html`, `invalidar.html`, `productos.html` to include the new links.

## Verification Plan
1.  **Navigation Check**: Click every new link in the sidebar and verify it opens the correct page.
2.  **Page Rendering**: Verify each new page renders with the correct title and basic layout.
