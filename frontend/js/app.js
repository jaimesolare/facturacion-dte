const API_BASE_URL = 'http://127.0.0.1:8000';

// Helper to show status messages
function showStatus(elementId, message, isError = false) {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.textContent = message;
    el.className = isError ? 'status-message status-error' : 'status-message status-success';
    el.style.display = 'block';
    setTimeout(() => {
        el.style.display = 'none';
    }, 5000);
}

// --- CATALOGS ---
const DEPARTAMENTOS = {
    "01": "Ahuachapán", "02": "Santa Ana", "03": "Sonsonate",
    "04": "Chalatenango", "05": "La Libertad", "06": "San Salvador",
    "07": "Cuscatlán", "08": "La Paz", "09": "Cabañas",
    "10": "San Vicente", "11": "Usulután", "12": "San Miguel",
    "13": "Morazán", "14": "La Unión"
};

const MUNICIPIOS = {
    "06": { // San Salvador
        "01": "San Salvador", "02": "Ciudad Delgado", "03": "Mejicanos",
        "04": "Soyapango", "05": "Cuscatancingo", "06": "San Marcos",
        "07": "Ilopango", "08": "Nejapa", "09": "Apopa",
        "10": "San Martin", "11": "Panchimalco", "12": "Aguilares",
        "13": "Tonacatepeque", "14": "Santo Tomás", "15": "Santiago Texacuangos",
        "16": "El Paisnal", "17": "Guazapa", "18": "Rosario de Mora"
    },
    // Add other departments as needed (simplified for demo)
    "05": { // La Libertad
        "01": "Santa Tecla", "02": "Antiguo Cuscatlán", "03": "Huizúcar",
        "04": "Nuevo Cuscatlán", "05": "Quezaltepeque"
    }
};

// --- EMITIR LOGIC ---
async function initEmitir() {
    const form = document.getElementById('emitirForm');
    if (!form) return;

    // --- Catalogs ---
    const deptoSelect = document.getElementById('recDepto');
    const muniSelect = document.getElementById('recMuni');

    for (const [code, name] of Object.entries(DEPARTAMENTOS)) {
        const option = document.createElement('option');
        option.value = code;
        option.textContent = name;
        deptoSelect.appendChild(option);
    }

    deptoSelect.addEventListener('change', (e) => {
        const deptoCode = e.target.value;
        muniSelect.innerHTML = '<option value="">Seleccione...</option>';
        muniSelect.disabled = !deptoCode;
        if (deptoCode && MUNICIPIOS[deptoCode]) {
            for (const [code, name] of Object.entries(MUNICIPIOS[deptoCode])) {
                const option = document.createElement('option');
                option.value = code;
                option.textContent = name;
                muniSelect.appendChild(option);
            }
        }
    });

    // --- Products Datalist ---
    const productOptions = document.getElementById('productOptions');
    let productsMap = {};
    try {
        const res = await fetch(`${API_BASE_URL}/api/productos`);
        if (res.ok) {
            const products = await res.json();
            products.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.nombre;
                opt.dataset.price = p.precio_unitario;
                opt.dataset.id = p.codigo;
                productOptions.appendChild(opt);
                productsMap[p.nombre] = p;
            });
        }
    } catch (e) { console.error(e); }

    // --- Items Table ---
    const tbody = document.getElementById('itemsTableBody');
    const btnAddItem = document.getElementById('btnAddItem');
    const totalPagarEl = document.getElementById('totalPagar');

    function calculateTotals() {
        let total = 0;
        tbody.querySelectorAll('tr').forEach(row => {
            const qty = parseFloat(row.querySelector('.qty-input').value) || 0;
            const price = parseFloat(row.querySelector('.price-input').value) || 0;
            const rowTotal = qty * price;
            row.querySelector('.row-total').textContent = rowTotal.toFixed(2);
            total += rowTotal;
        });
        totalPagarEl.textContent = total.toFixed(2);
    }

    function addRow() {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><input type="number" class="qty-input" value="1" min="1" style="width: 60px;"></td>
            <td><input type="text" class="desc-input" list="productOptions" placeholder="Buscar producto..." style="width: 100%;"></td>
            <td><input type="number" class="price-input" step="0.01" value="0.00" style="width: 100px;"></td>
            <td>$<span class="row-total">0.00</span></td>
            <td><button type="button" class="btn-remove" style="color: var(--danger-color); border: none; background: none; cursor: pointer;"><i class="fa-solid fa-trash"></i></button></td>
        `;
        tbody.appendChild(row);

        // Events for this row
        const descInput = row.querySelector('.desc-input');
        const priceInput = row.querySelector('.price-input');
        const qtyInput = row.querySelector('.qty-input');
        const removeBtn = row.querySelector('.btn-remove');

        descInput.addEventListener('input', (e) => {
            const val = e.target.value;
            if (productsMap[val]) {
                priceInput.value = productsMap[val].precio_unitario.toFixed(2);
                calculateTotals();
            }
        });

        [qtyInput, priceInput].forEach(inp => {
            inp.addEventListener('input', calculateTotals);
        });

        removeBtn.addEventListener('click', () => {
            row.remove();
            calculateTotals();
        });
    }

    if (btnAddItem) {
        btnAddItem.addEventListener('click', addRow);
        addRow(); // Initial row
    }

    // --- Submit ---
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button[type="submit"]');
        const originalText = btn.textContent;
        btn.textContent = 'Procesando...';
        btn.disabled = true;

        const items = [];
        let numItem = 1;
        tbody.querySelectorAll('tr').forEach(row => {
            const qty = parseFloat(row.querySelector('.qty-input').value) || 0;
            const price = parseFloat(row.querySelector('.price-input').value) || 0;
            const desc = row.querySelector('.desc-input').value;
            if (desc && qty > 0) {
                items.push({
                    num_item: numItem++,
                    tipo_item: 1,
                    descripcion: desc,
                    cantidad: qty,
                    codigo_unidad_medida: "59",
                    precio_unitario: price,
                    monto_descuento: 0,
                    venta_no_sujeta: 0,
                    venta_exenta: 0,
                    venta_gravada: qty * price,
                    tributos: ["20"]
                });
            }
        });

        if (items.length === 0) {
            showStatus('emitirStatus', 'Debe agregar al menos un ítem válido.', true);
            btn.textContent = originalText;
            btn.disabled = false;
            return;
        }

        const payload = {
            tipo_dte: "01",
            datos_dte: {
                receptor: {
                    nit: document.getElementById('recNit').value,
                    nombre: document.getElementById('recNombre').value,
                    cod_actividad: document.getElementById('recCodAct').value,
                    desc_actividad: document.getElementById('recDescAct').value,
                    direccion_calle: document.getElementById('recDireccion').value,
                    direccion_municipio: document.getElementById('recMuni').value,
                    direccion_departamento: document.getElementById('recDepto').value,
                    email: document.getElementById('recEmail').value || null
                },
                items: items,
                condicion_operacion: { forma_pago: "01" }
            }
        };

        try {
            const response = await fetch(`${API_BASE_URL}/api/dte`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Error en la emisión');
            }

            const data = await response.json();
            showStatus('emitirStatus', `DTE Generado: ${data.codigo_generacion}`);
            e.target.reset();
            tbody.innerHTML = '';
            addRow();
            calculateTotals();
        } catch (error) {
            showStatus('emitirStatus', `Error: ${error.message}`, true);
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    });
}
// --- INVALIDATION LOGIC ---
function initInvalidar() {
    const invalidarForm = document.getElementById('invalidarForm');
    if (!invalidarForm) return;

    invalidarForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        const originalText = btn.textContent;
        btn.textContent = 'Invalidando...';
        btn.disabled = true;

        const codigo = document.getElementById('codigoGen').value;
        const motivo = document.getElementById('motivo').value;

        try {
            const response = await fetch(`${API_BASE_URL}/api/dte/${codigo}/invalidate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ motivo: motivo })
            });

            if (!response.ok) throw new Error('Error al invalidar');

            const data = await response.json();
            showStatus('invalidarStatus', 'Solicitud de invalidación enviada correctamente.');
            loadDashboardData(); // Refresh dashboard data after invalidation
        } catch (error) {
            showStatus('invalidarStatus', `Error: ${error.message}`, true);
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
            e.target.reset();
        }
    });
}

// --- PRODUCT LOGIC ---
// --- PRODUCT LOGIC ---
function initProductos() {
    const productoForm = document.getElementById('productoForm');
    if (!productoForm) return;

    // Handle Product Creation
    productoForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        const originalText = btn.textContent;
        btn.textContent = 'Guardando...';
        btn.disabled = true;

        const payload = {
            codigo: document.getElementById('prodCodigo').value,
            nombre: document.getElementById('prodNombre').value,
            precio_unitario: parseFloat(document.getElementById('prodPrecio').value),
            tipo_item: 1 // Default to Bien
        };

        try {
            const response = await fetch(`${API_BASE_URL}/api/productos`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Error al guardar');
            }

            showStatus('productoStatus', 'Producto guardado correctamente');
            e.target.reset();
            loadProducts(); // Refresh list
        } catch (error) {
            showStatus('productoStatus', `Error: ${error.message}`, true);
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    });

    // Load Products
    async function loadProducts() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/productos`);
            if (!response.ok) return;
            const products = await response.json();

            const list = document.getElementById('productosList');
            if (!list) return;
            list.innerHTML = '';

            if (products.length === 0) {
                list.innerHTML = '<p style="color: var(--text-secondary);">No hay productos registrados.</p>';
                return;
            }

            products.forEach(p => {
                const div = document.createElement('div');
                div.style.padding = '0.5rem';
                div.style.borderBottom = '1px solid var(--border-color)';
                div.style.display = 'flex';
                div.style.justifyContent = 'space-between';
                div.innerHTML = `
                    <span><strong>${p.codigo}</strong>: ${p.nombre}</span>
                    <span>$${p.precio_unitario.toFixed(2)}</span>
                `;
                list.appendChild(div);
            });
        } catch (error) {
            console.error('Error loading products:', error);
        }
    }

    // Initial load
    loadProducts();
}

// --- DASHBOARD LOGIC ---
async function loadDashboardData() {
    // Only run on dashboard
    const historyList = document.getElementById('historyList');
    const countEl = document.getElementById('documentosCount');

    if (!historyList && !countEl) return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/dte?limit=10`);
        if (!response.ok) return;
        const dtes = await response.json();

        // Update Count
        if (countEl) {
            countEl.textContent = dtes.length; // This is just recent count, ideally we'd have a count endpoint
        }

        // Update History List
        if (historyList) {
            historyList.innerHTML = '';
            if (dtes.length === 0) {
                historyList.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 1rem;">No hay movimientos recientes.</p>';
                return;
            }

            dtes.forEach(dte => {
                const div = document.createElement('div');
                div.style.padding = '0.75rem';
                div.style.borderBottom = '1px solid var(--border-color)';
                div.style.display = 'flex';
                div.style.justifyContent = 'space-between';
                div.style.alignItems = 'center';

                const statusColor = dte.estado === 'PROCESADO' ? 'var(--success-color)' :
                    dte.estado === 'INVALIDADO' ? 'var(--danger-color)' : 'var(--warning-color)';

                div.innerHTML = `
                    <div>
                        <strong style="display:block; font-size: 0.9rem;">${dte.codigo_generacion}</strong>
                        <span style="font-size: 0.8rem; color: var(--text-secondary);">${new Date(dte.fecha_emision).toLocaleString()}</span>
                    </div>
                    <span style="color: ${statusColor}; font-weight: 600; font-size: 0.85rem;">${dte.estado}</span>
                `;
                historyList.appendChild(div);
            });
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// --- VENTAS LOGIC ---
async function loadVentasData() {
    const tbody = document.getElementById('ventasTableBody');
    if (!tbody) return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/dte?limit=50`);
        if (!response.ok) throw new Error('Error loading');
        const dtes = await response.json();

        tbody.innerHTML = '';
        if (dtes.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem;">No hay ventas registradas.</td></tr>';
            return;
        }

        dtes.forEach(dte => {
            const row = document.createElement('tr');
            const statusColor = dte.estado === 'PROCESADO' ? 'var(--success-color)' :
                dte.estado === 'INVALIDADO' ? 'var(--danger-color)' : 'var(--warning-color)';

            row.innerHTML = `
                <td>${dte.codigo_generacion}</td>
                <td>${new Date(dte.fecha_emision).toLocaleString()}</td>
                <td>${dte.documento_json.identificacion?.receptor?.nombre || 'Consumidor Final'}</td>
                <td>$${dte.monto_total.toFixed(2)}</td>
                <td><span style="color: ${statusColor}; font-weight: 600;">${dte.estado}</span></td>
                <td>
                    <button class="btn-view-pdf" data-id="${dte.codigo_generacion}" style="background:none; border:none; color: var(--accent-color); cursor: pointer;">
                        <i class="fa-solid fa-file-pdf"></i> Ver PDF
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });

        // Add event listeners for PDF buttons
        document.querySelectorAll('.btn-view-pdf').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.currentTarget.dataset.id;
                alert(`Visualización de PDF para ${id} pendiente de implementación.`);
            });
        });

    } catch (e) {
        console.error("Error loading ventas:", e);
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--danger-color);">Error al cargar datos.</td></tr>';
    }
}

// --- POS LOGIC ---
// --- POS LOGIC ---
let posCart = [];

async function initPOS() {
    const grid = document.getElementById('posProductGrid');
    const cartItemsContainer = document.getElementById('posCartItems');
    const totalEl = document.getElementById('posTotalAmount');
    const checkoutBtn = document.getElementById('posCheckoutBtn');

    if (!grid || !cartItemsContainer) return;

    // Load Products
    try {
        const response = await fetch(`${API_BASE_URL}/api/productos`);
        if (!response.ok) throw new Error('Error loading products');
        const products = await response.json();

        grid.innerHTML = '';
        products.forEach(p => {
            const card = document.createElement('div');
            card.className = 'product-card';
            card.innerHTML = `
                <i class="fa-solid fa-box" style="font-size: 2rem; color: var(--accent-color); margin-bottom: 0.5rem;"></i>
                <h4 style="margin: 0.5rem 0;">${p.nombre}</h4>
                <p style="color: var(--success-color); font-weight: bold;">$${p.precio_unitario.toFixed(2)}</p>
            `;
            card.addEventListener('click', () => addToCart(p));
            grid.appendChild(card);
        });
    } catch (e) {
        console.error("Error loading POS products:", e);
        grid.innerHTML = '<p style="color: var(--danger-color);">Error al cargar productos.</p>';
    }

    // Cart Functions
    function addToCart(product) {
        const existing = posCart.find(item => item.codigo === product.codigo);
        if (existing) {
            existing.cantidad++;
        } else {
            posCart.push({ ...product, cantidad: 1 });
        }
        renderCart();
    }

    function renderCart() {
        cartItemsContainer.innerHTML = '';
        let total = 0;

        if (posCart.length === 0) {
            cartItemsContainer.innerHTML = '<p style="text-align: center; color: var(--text-secondary); margin-top: 2rem;">Carrito vacío</p>';
        } else {
            posCart.forEach((item, index) => {
                total += item.precio_unitario * item.cantidad;
                const div = document.createElement('div');
                div.style.display = 'flex';
                div.style.justifyContent = 'space-between';
                div.style.alignItems = 'center';
                div.style.marginBottom = '0.5rem';
                div.style.padding = '0.5rem';
                div.style.background = '#f9fafb';
                div.style.borderRadius = '0.25rem';

                div.innerHTML = `
                    <div>
                        <div style="font-weight: bold;">${item.nombre}</div>
                        <div style="font-size: 0.8rem; color: var(--text-secondary);">$${item.precio_unitario.toFixed(2)} x ${item.cantidad}</div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <strong style="color: var(--accent-color);">$${(item.precio_unitario * item.cantidad).toFixed(2)}</strong>
                        <button class="btn-remove-cart" data-index="${index}" style="background: none; border: none; color: var(--danger-color); cursor: pointer;">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </div>
                `;
                cartItemsContainer.appendChild(div);
            });
        }

        totalEl.textContent = `$${total.toFixed(2)}`;

        // Add remove listeners
        document.querySelectorAll('.btn-remove-cart').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const idx = parseInt(e.currentTarget.dataset.index);
                posCart.splice(idx, 1);
                renderCart();
            });
        });
    }

    // Checkout
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', () => {
            if (posCart.length === 0) {
                alert('El carrito está vacío.');
                return;
            }
            alert(`Cobro realizado por $${totalEl.textContent}. (Simulación)`);
            posCart = [];
            renderCart();
        });
    }
}

// --- CLIENTS LOGIC ---
function initClientes() {
    const clienteForm = document.getElementById('clienteForm');
    if (!clienteForm) return;

    // Initialize Catalogs
    const deptoSelect = document.getElementById('cliDepto');
    const muniSelect = document.getElementById('cliMuni');

    // Populate Departamentos
    for (const [code, name] of Object.entries(DEPARTAMENTOS)) {
        const option = document.createElement('option');
        option.value = code;
        option.textContent = name;
        deptoSelect.appendChild(option);
    }

    // Handle Depto Change
    deptoSelect.addEventListener('change', (e) => {
        const deptoCode = e.target.value;
        muniSelect.innerHTML = '<option value="">Seleccione...</option>';
        muniSelect.disabled = !deptoCode;

        if (deptoCode && MUNICIPIOS[deptoCode]) {
            for (const [code, name] of Object.entries(MUNICIPIOS[deptoCode])) {
                const option = document.createElement('option');
                option.value = code;
                option.textContent = name;
                muniSelect.appendChild(option);
            }
        }
    });

    // Handle Client Creation
    clienteForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        const originalText = btn.textContent;
        btn.textContent = 'Guardando...';
        btn.disabled = true;

        const payload = {
            nit: document.getElementById('cliNit').value,
            nrc: document.getElementById('cliNrc').value || null,
            nombre: document.getElementById('cliNombre').value,
            cod_actividad: document.getElementById('cliCodAct').value,
            desc_actividad: document.getElementById('cliDescAct').value,
            direccion: document.getElementById('cliDireccion').value,
            departamento: document.getElementById('cliDepto').value,
            municipio: document.getElementById('cliMuni').value,
            email: document.getElementById('cliEmail').value || null,
            telefono: document.getElementById('cliTelefono').value || null
        };

        try {
            const response = await fetch(`${API_BASE_URL}/api/clientes`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Error al guardar cliente');
            }

            showStatus('clienteStatus', 'Cliente guardado correctamente');
            e.target.reset();
            // Reset selects
            muniSelect.innerHTML = '<option value="">Seleccione Depto...</option>';
            muniSelect.disabled = true;
            loadClientes(); // Refresh list
        } catch (error) {
            showStatus('clienteStatus', `Error: ${error.message}`, true);
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    });

    // Load Clientes
    async function loadClientes() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/clientes`);
            if (!response.ok) return;
            const clientes = await response.json();

            const list = document.getElementById('clientesList');
            if (!list) return;
            list.innerHTML = '';

            if (clientes.length === 0) {
                list.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 1rem;">No hay clientes registrados.</p>';
                return;
            }

            clientes.forEach(c => {
                const div = document.createElement('div');
                div.style.padding = '1rem';
                div.style.borderBottom = '1px solid var(--border-color)';
                div.style.display = 'flex';
                div.style.justifyContent = 'space-between';
                div.style.alignItems = 'center';
                div.innerHTML = `
                    <div>
                        <strong style="display:block; font-size: 1rem;">${c.nombre}</strong>
                        <span style="font-size: 0.85rem; color: var(--text-secondary);">NIT: ${c.nit} | ${c.departamento}, ${c.municipio}</span>
                    </div>
                    <button class="btn-delete-cliente" data-nit="${c.nit}" style="background: none; border: none; color: var(--danger-color); cursor: pointer; padding: 0.5rem;">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                `;
                list.appendChild(div);
            });

            // Add delete listeners
            document.querySelectorAll('.btn-delete-cliente').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    if (!confirm('¿Está seguro de eliminar este cliente?')) return;
                    const nit = e.currentTarget.dataset.nit;
                    try {
                        const res = await fetch(`${API_BASE_URL}/api/clientes/${nit}`, { method: 'DELETE' });
                        if (res.ok) {
                            loadClientes();
                            showStatus('clienteStatus', 'Cliente eliminado.');
                        } else {
                            throw new Error('Error al eliminar');
                        }
                    } catch (err) {
                        showStatus('clienteStatus', `Error: ${err.message}`, true);
                    }
                });
            });

        } catch (error) {
            console.error('Error loading clientes:', error);
            const list = document.getElementById('clientesList');
            if (list) list.innerHTML = '<p style="color: var(--danger-color);">Error al cargar clientes.</p>';
        }
    }

    // Initial load
    loadClientes();
}

// Initial load for POS
if (document.getElementById('posProductGrid')) {
    initPOS();
}

// Initial load for Emitir
if (document.getElementById('emitirForm')) {
    initEmitir();
}

// Initial load for Invalidar
if (document.getElementById('invalidarForm')) {
    initInvalidar();
}

// Initial load for Productos
if (document.getElementById('productoForm')) {
    initProductos();
}

// Initial load for Clientes
if (document.getElementById('clienteForm')) {
    initClientes();
}

// Initial load for Ventas
if (document.getElementById('ventasTableBody')) {
    loadVentasData();
}

// Initial load for Dashboard
if (document.getElementById('documentosCount')) {
    loadDashboardData();
}
