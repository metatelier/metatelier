const BACKEND_PORT = 8000;

// Rutas de API
const API_URL = '/api/productos';
const PEDIDOS_API_URL = '/api/pedidos';
const TEXTOS_API_URL = '/api/textos';
const LOGIN_API_URL = '/api/admin/login';
const EXPORT_BACKUP_URL = '/api/backup/export';
const IMPORT_BACKUP_URL = '/api/backup/import';

function formatFotoUrl(urlObj) {
    let url = urlObj;
    if (urlObj && urlObj.url) url = urlObj.url;
    
    if (!url) return '/uploads/tote_taupe.jpg';
    if (url.startsWith('http')) return url;
    if (window.location.port && window.location.port !== `${BACKEND_PORT}`) {
        return `http://${window.location.hostname || 'localhost'}:${BACKEND_PORT}${url}`;
    }
    return url;
}

const catalogo = document.getElementById('catalogo-container');
const catalogoTitulo = document.getElementById('catalogo-titulo');
const categoriasNav = document.getElementById('categorias-nav');

// Estado Global de la App
let todosProductos = [];
let todosPedidos = [];
let textosConfig = {};
let filtroActual = 'todas';
let busquedaActual = '';
let bolsaCompras = JSON.parse(localStorage.getItem('maison_cart') || '[]');
let adminPIN = sessionStorage.getItem('maison_admin_pin') || '';
let editandoId = null;

// --- 1. Cargar Boutique & Textos ---
async function cargarTienda() {
    try {
        await cargarTextosSitio();
        const res = await fetch(API_URL);
        todosProductos = await res.json();
        renderizarBarraCategorias();
        renderizarCatalogo();
        actualizarBolsaUI();
    } catch (err) {
        console.error("Error al conectar con el backend:", err);
    }
}

async function cargarTextosSitio() {
    try {
        const res = await fetch(TEXTOS_API_URL);
        if (res.ok) {
            textosConfig = await res.json();
            aplicarTextosEnDOM();
        }
    } catch (err) {
        console.error("Error cargando textos:", err);
    }
}

function aplicarTextosEnDOM() {
    if (!textosConfig) return;

    if (textosConfig.brandName) {
        const brandLogoText = document.getElementById('brand-logo-text');
        const txtFooterLogo = document.getElementById('txt-footer-logo');
        if (brandLogoText) brandLogoText.innerText = textosConfig.brandName;
        if (txtFooterLogo) txtFooterLogo.innerText = textosConfig.brandName;
        document.title = `${textosConfig.brandName} | Boutique de Haute Maroquinerie`;
    }

    if (textosConfig.headerSublogo) document.getElementById('txt-header-sublogo').innerText = textosConfig.headerSublogo;
    if (textosConfig.heroTag) document.getElementById('txt-hero-tag').innerText = textosConfig.heroTag;
    if (textosConfig.heroTitulo) document.getElementById('txt-hero-titulo').innerText = textosConfig.heroTitulo;
    if (textosConfig.heroDesc) document.getElementById('txt-hero-desc').innerText = textosConfig.heroDesc;
    if (textosConfig.heroScrollText) document.getElementById('txt-hero-scroll').innerText = textosConfig.heroScrollText;

    if (textosConfig.sectionTag) document.getElementById('txt-section-tag').innerText = textosConfig.sectionTag;
    if (textosConfig.sectionTitulo && filtroActual === 'todas') catalogoTitulo.innerText = textosConfig.sectionTitulo;

    // Footer
    if (textosConfig.footerTagline) document.getElementById('txt-footer-tagline').innerText = textosConfig.footerTagline;
    if (textosConfig.footerSub) document.getElementById('txt-footer-sub').innerText = textosConfig.footerSub;
    if (textosConfig.footerCol1Desc) document.getElementById('txt-footer-col1-desc').innerText = textosConfig.footerCol1Desc;
    if (textosConfig.footerCol3Desc) document.getElementById('txt-footer-col3-desc').innerText = textosConfig.footerCol3Desc;
    if (textosConfig.copyright) document.getElementById('txt-footer-copyright').innerText = textosConfig.copyright;
    if (textosConfig.badgeText) document.getElementById('txt-footer-badge').innerText = textosConfig.badgeText;
}

// Generación Dinámica de Barra de Categorías / Filtros
function renderizarBarraCategorias() {
    if (!categoriasNav) return;
    
    const categoriasSet = new Set();
    todosProductos.forEach(p => {
        if (p.categoria && p.categoria.trim()) {
            categoriasSet.add(p.categoria.trim());
        }
    });

    const listaCategorias = Array.from(categoriasSet);

    let html = `<button class="filter-btn ${filtroActual === 'todas' ? 'active' : ''}" data-filter="todas">${textosConfig.filterTodas || 'Todas las Piezas'}</button>`;
    
    listaCategorias.forEach(cat => {
        const isActive = (filtroActual.toLowerCase() === cat.toLowerCase());
        html += `<button class="filter-btn ${isActive ? 'active' : ''}" data-filter="${cat}">${cat}</button>`;
    });

    categoriasNav.innerHTML = html;

    categoriasNav.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            categoriasNav.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filtroActual = btn.dataset.filter;
            catalogoTitulo.innerText = filtroActual === 'todas' ? (textosConfig.sectionTitulo || 'Catálogo General') : filtroActual;
            renderizarCatalogo();
        });
    });
}

function renderizarCatalogo() {
    catalogo.innerHTML = '';
    
    let productosFiltrados = todosProductos.filter(p => {
        const coincideCategoria = (filtroActual === 'todas') || 
            (p.categoria && p.categoria.toLowerCase() === filtroActual.toLowerCase());
        
        const q = busquedaActual.toLowerCase().trim();
        const coincideBusqueda = !q || 
            p.nombre.toLowerCase().includes(q) || 
            (p.descripcion && p.descripcion.toLowerCase().includes(q)) || 
            (p.material && p.material.toLowerCase().includes(q)) ||
            (p.categoria && p.categoria.toLowerCase().includes(q));

        return coincideCategoria && coincideBusqueda;
    });

    if(productosFiltrados.length === 0) {
        catalogo.innerHTML = `
            <div style="text-align:center; padding: 60px 20px; color:#8B7E74;">
                <p style="font-family:var(--font-title); font-size:20px; font-style:italic; margin-bottom:10px;">No se encontraron piezas en esta selección.</p>
                <p style="font-size:12px;">Intenta ajustando los filtros o explora la colección completa.</p>
            </div>
        `;
        return;
    }

    productosFiltrados.forEach(p => {
        const div = document.createElement('div');
        div.className = 'producto';

        const rawFotos = (p.imagenes && p.imagenes.length > 0) ? p.imagenes : [p.imagen];
        const fotos = rawFotos.map(formatFotoUrl);
        const tieneVarias = fotos.length > 1;

        const agotadoHTML = p.agotado ? `<div style="position:absolute; top:0; left:0; right:0; bottom:0; background:rgba(255,255,255,0.7); display:flex; align-items:center; justify-content:center; z-index:10; pointer-events:none;"><span style="background:#000; color:#fff; padding:10px 20px; font-weight:bold; letter-spacing:2px; font-size:1.2rem;">AGOTADO</span></div>` : '';

        let carruselHTML = `
            <div class="producto-galeria" onclick="abrirDetalle(${p.id})">
                ${agotadoHTML}
                ${tieneVarias ? '<span class="swipe-hint">Deslizar &rsaquo;</span>' : ''}
                <div class="producto-carrusel" id="carrusel-${p.id}" ${p.agotado ? 'style="filter: grayscale(100%);"' : ''}>
        `;

        fotos.forEach(foto => {
            carruselHTML += `
                <div class="carrusel-slide">
                    <img src="${foto}" alt="${p.nombre}">
                </div>
            `;
        });

        carruselHTML += `</div>`;

        if (tieneVarias) {
            carruselHTML += `
                <button class="carrusel-arrow prev" onclick="event.stopPropagation(); scrollCarrusel(${p.id}, -1)" aria-label="Anterior">&lsaquo;</button>
                <button class="carrusel-arrow next" onclick="event.stopPropagation(); scrollCarrusel(${p.id}, 1)" aria-label="Siguiente">&rsaquo;</button>
                <div class="carrusel-puntos" id="puntos-${p.id}">
            `;
            fotos.forEach((_, index) => {
                carruselHTML += `<span class="punto ${index === 0 ? 'activo' : ''}"></span>`;
            });
            carruselHTML += `</div>`;
        }

        carruselHTML += `</div>`;

        div.innerHTML = carruselHTML + `
            <div class="producto-info">
                <span class="categoria">${p.categoria}</span>
                <h2 onclick="abrirDetalle(${p.id})">${p.nombre}</h2>
                <p class="descripcion">${p.descripcion}</p>
                <ul class="detalles">
                    <li><span>Material</span> <span>${p.material}</span></li>
                    <li><span>Medidas</span> <span>${p.dimensiones}</span></li>
                </ul>
                <div class="card-actions">
                    <button class="btn-comprar" onclick="abrirDetalle(${p.id})" ${p.agotado ? 'disabled style="opacity:0.5; cursor:not-allowed;"' : ''}>${p.agotado ? 'Agotado' : 'Explorar Pieza'}</button>
                </div>
            </div>
        `;

        catalogo.appendChild(div);

        if (tieneVarias) {
            const container = document.getElementById(`carrusel-${p.id}`);
            const puntos = document.querySelectorAll(`#puntos-${p.id} .punto`);
            
            container.addEventListener('scroll', () => {
                const width = container.clientWidth;
                const activeIndex = Math.round(container.scrollLeft / width);
                puntos.forEach((dot, idx) => {
                    dot.classList.toggle('activo', idx === activeIndex);
                });
            }, { passive: true });
        }
    });

    animarScroll();
}

window.scrollCarrusel = (id, direccion) => {
    const container = document.getElementById(`carrusel-${id}`);
    if (!container) return;
    const scrollAmount = container.clientWidth * direccion;
    container.scrollBy({ left: scrollAmount, behavior: 'smooth' });
};

function animarScroll() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) entry.target.classList.add('visible');
        });
    }, { threshold: 0.1 });
    document.querySelectorAll('.producto').forEach(p => observer.observe(p));
}

// --- 2. Búsqueda ---
const searchBar = document.getElementById('search-bar');
const inputBusqueda = document.getElementById('input-busqueda');

document.getElementById('btn-buscar-toggle').addEventListener('click', () => {
    searchBar.classList.toggle('active');
    if(searchBar.classList.contains('active')) {
        inputBusqueda.focus();
    }
});

document.getElementById('btn-cerrar-busqueda').addEventListener('click', () => {
    searchBar.classList.remove('active');
    inputBusqueda.value = '';
    busquedaActual = '';
    renderizarCatalogo();
});

inputBusqueda.addEventListener('input', (e) => {
    busquedaActual = e.target.value;
    renderizarCatalogo();
});

// --- 3. Bolsa de Compras ---
const cartDrawer = document.getElementById('cart-drawer');
const cartCount = document.getElementById('cart-count');
const cartItemsContainer = document.getElementById('cart-items');
const cartTotalEl = document.getElementById('cart-total');
const btnCheckout = document.getElementById('btn-checkout');

document.getElementById('btn-abrir-bolsa').addEventListener('click', () => cartDrawer.classList.add('active'));
document.getElementById('btn-cerrar-bolsa').addEventListener('click', () => cartDrawer.classList.remove('active'));
cartDrawer.addEventListener('click', (e) => {
    if (e.target === cartDrawer) cartDrawer.classList.remove('active');
});

window.agregarABolsa = (id) => {
    const prod = todosProductos.find(p => p.id === id);
    if (!prod) return;

    const fotoFinal = formatFotoUrl(prod.imagen || (prod.imagenes && prod.imagenes[0]));

    const existeIndex = bolsaCompras.findIndex(item => item.id === id);
    if (existeIndex > -1) {
        bolsaCompras[existeIndex].cantidad += 1;
    } else {
        bolsaCompras.push({
            id: prod.id,
            nombre: prod.nombre,
            precio: prod.precio,
            imagen: fotoFinal,
            cantidad: 1
        });
    }

    guardarBolsa();
    actualizarBolsaUI();
    mostrarToast(`"${prod.nombre}" añadida a tu bolsa`);
};

window.removerDeBolsa = (id) => {
    bolsaCompras = bolsaCompras.filter(item => item.id !== id);
    guardarBolsa();
    actualizarBolsaUI();
};

function guardarBolsa() {
    localStorage.setItem('maison_cart', JSON.stringify(bolsaCompras));
}

function calcularTotal() {
    return bolsaCompras.reduce((sum, item) => {
        const num = parseFloat(item.precio.replace(/[^0-9.]/g, '')) || 0;
        return sum + (num * item.cantidad);
    }, 0);
}

function actualizarBolsaUI() {
    const totalItems = bolsaCompras.reduce((acc, i) => acc + i.cantidad, 0);
    cartCount.innerText = totalItems;

    cartItemsContainer.innerHTML = '';
    if (bolsaCompras.length === 0) {
        cartItemsContainer.innerHTML = '<p class="cart-empty">Tu bolsa de compras está vacía.</p>';
        cartTotalEl.innerText = '$0.00 USD';
        btnCheckout.disabled = true;
        return;
    }

    btnCheckout.disabled = false;
    bolsaCompras.forEach(item => {
        const div = document.createElement('div');
        div.className = 'cart-item';
        div.innerHTML = `
            <img src="${formatFotoUrl(item.imagen)}" alt="${item.nombre}">
            <div class="cart-item-info">
                <h4>${item.nombre}</h4>
                <p>${item.cantidad} x ${formatFormatoPrecioUSD(item.precio)}</p>
            </div>
            <button class="cart-item-remove" onclick="removerDeBolsa(${item.id})">Remover</button>
        `;
        cartItemsContainer.appendChild(div);
    });

    const total = calcularTotal();
    cartTotalEl.innerText = `$ ${total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})} USD`;
}

function formatFormatoPrecioUSD(rawPrecio) {
    if (!rawPrecio) return '$0.00 USD';
    if (rawPrecio.toLowerCase().includes('usd')) return rawPrecio;
    const num = parseFloat(rawPrecio.replace(/[^0-9.]/g, ''));
    if (isNaN(num)) return `${rawPrecio} USD`;
    return `$ ${num.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})} USD`;
}

// --- 4. Modal Detalle Rápido (Precio debajo del botón en USD) ---
const modalDetalle = document.getElementById('modal-detalle');
const detalleGaleria = document.getElementById('detalle-galeria');
const detalleNombre = document.getElementById('detalle-nombre');
const detalleTitulo = document.getElementById('detalle-titulo');
const detalleCategoria = document.getElementById('detalle-categoria');
const detalleDescripcion = document.getElementById('detalle-descripcion');
const detalleMaterial = document.getElementById('detalle-material');
const detalleDimensiones = document.getElementById('detalle-dimensiones');
const detallePrecio = document.getElementById('detalle-precio');
const btnAddCartDetalle = document.getElementById('btn-add-cart-detalle');

window.abrirDetalle = (id) => {
    const p = todosProductos.find(item => item.id === id);
    if (!p) return;

    detalleNombre.innerText = p.nombre;
    detalleTitulo.innerText = p.nombre;
    detalleCategoria.innerText = p.categoria;
    detalleDescripcion.innerText = p.descripcion;
    detalleMaterial.innerText = p.material;
    detalleDimensiones.innerText = p.dimensiones;
    detallePrecio.innerText = formatFormatoPrecioUSD(p.precio);

    const rawFotos = (p.imagenes && p.imagenes.length > 0) ? p.imagenes : [p.imagen];
    const fotos = rawFotos.map(formatFotoUrl);

    let galeriaHTML = `<div class="producto-galeria" style="position:relative;">
        <div class="producto-carrusel" id="carrusel-det-${p.id}">`;
    fotos.forEach(f => {
        galeriaHTML += `<div class="carrusel-slide"><img src="${f}" alt="${p.nombre}"></div>`;
    });
    galeriaHTML += `</div>`;
    
    if (fotos.length > 1) {
        galeriaHTML += `
            <button class="carrusel-arrow prev" onclick="event.stopPropagation(); scrollCarrusel('det-${p.id}', -1)">&lsaquo;</button>
            <button class="carrusel-arrow next" onclick="event.stopPropagation(); scrollCarrusel('det-${p.id}', 1)">&rsaquo;</button>
            <div class="carrusel-puntos" id="puntos-det-${p.id}">
        `;
        fotos.forEach((_, index) => {
            galeriaHTML += `<span class="punto ${index === 0 ? 'activo' : ''}"></span>`;
        });
        galeriaHTML += `</div>`;
    }
    galeriaHTML += `</div>`;
    detalleGaleria.innerHTML = galeriaHTML;

    if (fotos.length > 1) {
        setTimeout(() => {
            const container = document.getElementById(`carrusel-det-${p.id}`);
            const puntos = document.querySelectorAll(`#puntos-det-${p.id} .punto`);
            container.addEventListener('scroll', () => {
                const width = container.clientWidth;
                const activeIndex = Math.round(container.scrollLeft / width);
                puntos.forEach((dot, idx) => {
                    dot.classList.toggle('activo', idx === activeIndex);
                });
            }, { passive: true });
        }, 100);
    }

    if (p.agotado) {
        btnAddCartDetalle.innerText = "Pieza Agotada";
        btnAddCartDetalle.disabled = true;
        btnAddCartDetalle.style.opacity = '0.5';
        btnAddCartDetalle.style.cursor = 'not-allowed';
        btnAddCartDetalle.onclick = null;
    } else {
        btnAddCartDetalle.innerText = "Añadir a la Bolsa";
        btnAddCartDetalle.disabled = false;
        btnAddCartDetalle.style.opacity = '1';
        btnAddCartDetalle.style.cursor = 'pointer';
        btnAddCartDetalle.onclick = () => {
            agregarABolsa(p.id);
            modalDetalle.classList.remove('activo');
        };
    }

    modalDetalle.classList.add('activo');
};

document.getElementById('btn-cerrar-detalle').addEventListener('click', () => modalDetalle.classList.remove('activo'));
modalDetalle.addEventListener('click', (e) => {
    if (e.target === modalDetalle) modalDetalle.classList.remove('activo');
});

// --- 5. Checkout Concierge ---
const modalCheckout = document.getElementById('modal-checkout');
const formCheckout = document.getElementById('form-checkout');
const checkoutResumenLista = document.getElementById('checkout-resumen-lista');
const checkoutTotalVal = document.getElementById('checkout-total-val');

btnCheckout.addEventListener('click', () => {
    cartDrawer.classList.remove('active');
    
    checkoutResumenLista.innerHTML = '';
    bolsaCompras.forEach(item => {
        const p = document.createElement('p');
        p.style.fontSize = '12px';
        p.style.display = 'flex';
        p.style.justifyContent = 'space-between';
        p.style.marginBottom = '6px';
        p.innerHTML = `<span>${item.cantidad}x ${item.nombre}</span> <span>${formatFormatoPrecioUSD(item.precio)}</span>`;
        checkoutResumenLista.appendChild(p);
    });

    const total = calcularTotal();
    checkoutTotalVal.innerText = `$ ${total.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})} USD`;
    modalCheckout.classList.add('activo');
});

document.getElementById('btn-cerrar-checkout').addEventListener('click', () => modalCheckout.classList.remove('activo'));
modalCheckout.addEventListener('click', (e) => {
    if (e.target === modalCheckout) modalCheckout.classList.remove('activo');
});

formCheckout.addEventListener('submit', async (e) => {
    e.preventDefault();
    const nombre = document.getElementById('cliente-nombre').value;
    const email = document.getElementById('cliente-email').value;
    const telefono = document.getElementById('cliente-telefono').value;
    const direccion = document.getElementById('cliente-direccion').value;
    const total = `$ ${calcularTotal().toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})} USD`;

    const payload = {
        nombre,
        email,
        telefono,
        direccion,
        items: bolsaCompras,
        total
    };

    try {
        const res = await fetch(PEDIDOS_API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (res.ok) {
            alert(`¡Gracias ${nombre}! Tu solicitud de reserva Concierge (Orden #${data.pedido ? data.pedido.id : ''}) ha sido enviada al atelier. Un asesor se pondrá en contacto contigo a la brevedad.`);
            
            bolsaCompras = [];
            guardarBolsa();
            actualizarBolsaUI();
            formCheckout.reset();
            modalCheckout.classList.remove('activo');
            mostrarToast('Solicitud enviada al atelier');

            if (adminPIN) cargarBuzonPedidos();
        } else {
            alert(data.error || 'Error al enviar la solicitud.');
        }
    } catch (err) {
        alert('Error de conexión al enviar el pedido.');
    }
});

// --- 6. Acceso Admin Secreto por Triple-Clic en el Badge del Footer ---
const btnAdminLock = document.getElementById('btn-admin-lock');
const btnLogoutAdmin = document.getElementById('btn-logout-admin');
const modalAdmin = document.getElementById('modal-admin');
const formAdmin = document.getElementById('form-producto');
const formProductoTitulo = document.getElementById('form-producto-titulo');
const btnSubmitProducto = document.getElementById('btn-submit-producto');
const btnCancelarEdicion = document.getElementById('btn-cancelar-edicion');
const inputImagenes = document.getElementById('imagenes');
const formTextos = document.getElementById('form-textos');
const listaAdmin = document.getElementById('lista-admin');
const buzonPedidosLista = document.getElementById('buzon-pedidos-lista');
const badgePedidosCount = document.getElementById('badge-pedidos-count');
const tabBadgePedidos = document.getElementById('tab-badge-pedidos');
const txtFooterBadge = document.getElementById('txt-footer-badge');

// Triple Clic Secreto en el elemento "Quiet Luxury Collection" del Footer
let clickCountBadge = 0;
let clickTimerBadge = null;

if (txtFooterBadge) {
    txtFooterBadge.addEventListener('click', () => {
        clickCountBadge++;
        if (clickCountBadge === 1) {
            clickTimerBadge = setTimeout(() => {
                clickCountBadge = 0;
            }, 1500);
        } else if (clickCountBadge >= 3) {
            clearTimeout(clickTimerBadge);
            clickCountBadge = 0;
            abrirPanelAdministrador();
        }
    });
}

// Pestañas Admin
const tabBuzonBtn = document.getElementById('tab-buzon-btn');
const tabInventarioBtn = document.getElementById('tab-inventario-btn');
const tabRespaldosBtn = document.getElementById('tab-respaldos-btn');
const tabBuzonContent = document.getElementById('tab-buzon-content');
const tabInventarioContent = document.getElementById('tab-inventario-content');
const tabRespaldosContent = document.getElementById('tab-respaldos-content');

if (tabBuzonBtn && tabInventarioBtn && tabRespaldosBtn) {
    tabBuzonBtn.addEventListener('click', () => {
        ocultarPestañas();
        tabBuzonBtn.classList.add('active');
        tabBuzonContent.classList.add('active');
        if (adminPIN) cargarBuzonPedidos();
    });

    tabInventarioBtn.addEventListener('click', () => {
        ocultarPestañas();
        tabInventarioBtn.classList.add('active');
        tabInventarioContent.classList.add('active');
        if (adminPIN) cargarListaAdmin();
    });

    tabRespaldosBtn.addEventListener('click', () => {
        ocultarPestañas();
        tabRespaldosBtn.classList.add('active');
        tabRespaldosContent.classList.add('active');
    });
}

function ocultarPestañas() {
    [tabBuzonBtn, tabInventarioBtn, tabRespaldosBtn].forEach(b => b.classList.remove('active'));
    [tabBuzonContent, tabInventarioContent, tabRespaldosContent].forEach(c => c.classList.remove('active'));
}


if (btnAdminLock) {
    btnAdminLock.addEventListener('click', async () => {
        abrirPanelAdministrador();
    });
}

if (btnLogoutAdmin) {
    btnLogoutAdmin.addEventListener('click', () => {
        adminPIN = '';
        sessionStorage.removeItem('maison_admin_pin');
        sessionStorage.removeItem('maison_admin_unlocked');
        modalAdmin.classList.remove('activo');
        mostrarToast('Sesión de Administrador cerrada correctamente');
    });
}

async function abrirPanelAdministrador() {
    if (!adminPIN) {
        const autenticado = await solicitarAutenticacionAdmin();
        if (!autenticado) return;
    }
    modalAdmin.classList.add('activo');
    cargarBuzonPedidos();
    cargarListaAdmin();
}

async function solicitarAutenticacionAdmin() {
    const pinIngresado = prompt('Ingresa la Contraseña de Administrador:');
    if (!pinIngresado) return false;

    try {
        const res = await fetch(LOGIN_API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pin: pinIngresado })
        });

        if (res.ok) {
            adminPIN = pinIngresado;
            sessionStorage.setItem('maison_admin_pin', adminPIN);
            sessionStorage.setItem('maison_admin_unlocked', 'true');
            mostrarToast('Autenticación exitosa');
            return true;
        } else {
            alert('PIN incorrecto. Acceso denegado.');
            return false;
        }
    } catch (err) {
        alert('Error de conexión con la API.');
        return false;
    }
}

document.getElementById('btn-cerrar-admin').addEventListener('click', () => modalAdmin.classList.remove('activo'));
modalAdmin.addEventListener('click', (e) => {
    if (e.target === modalAdmin) modalAdmin.classList.remove('activo');
});

// --- 7. Editor de Marca & Textos ---

// --- 8. Cargar y Administrar Inventario (Crear, Editar y Eliminar) ---
btnCancelarEdicion.addEventListener('click', () => resetearFormularioProducto());

function resetearFormularioProducto() {
    editandoId = null;
    formAdmin.reset();
    formProductoTitulo.innerText = "Publicar Nueva Pieza";
    btnSubmitProducto.innerText = "Publicar Pieza";
    btnCancelarEdicion.style.display = "none";
    inputImagenes.required = true;
}

window.prepararEdicionProducto = (id) => {
    const prod = todosProductos.find(p => p.id === id);
    if (!prod) return;

    editandoId = id;
    document.getElementById('nombre').value = prod.nombre || '';
    document.getElementById('codigo_unico').value = prod.codigo_unico || '';
    document.getElementById('agotado').checked = prod.agotado || false;
    document.getElementById('categoria').value = prod.categoria || '';
    document.getElementById('precio').value = prod.precio || '';
    document.getElementById('material').value = prod.material || '';
    document.getElementById('dimensiones').value = prod.dimensiones || '';
    document.getElementById('descripcion').value = prod.descripcion || '';

    inputImagenes.required = false;

    formProductoTitulo.innerText = `Editar Pieza: "${prod.nombre}"`;
    btnSubmitProducto.innerText = "Guardar Cambios de Pieza";
    btnCancelarEdicion.style.display = "inline-block";

    ocultarPestañas();
    tabInventarioBtn.classList.add('active');
    tabInventarioContent.classList.add('active');

    formAdmin.scrollIntoView({ behavior: 'smooth' });
};

formAdmin.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!adminPIN) {
        alert('Debes autenticarte primero.');
        return;
    }

    const formData = new FormData(formAdmin);
    const esEdicion = editandoId !== null;
    const targetUrl = esEdicion ? `${API_URL}/${editandoId}` : API_URL;
    const method = 'POST'; // Django uses POST for multipart form parsing
    
    try {
        const res = await fetch(targetUrl, { 
            method: method, 
            headers: {
                'x-admin-pin': adminPIN
            },
            body: formData 
        });

        if(res.ok) {
            resetearFormularioProducto();
            cargarTienda();
            cargarListaAdmin();
            mostrarToast(esEdicion ? '¡Pieza actualizada con éxito!' : '¡Pieza publicada con éxito en la boutique!');
        } else {
            const data = await res.json();
            alert(data.error || 'Hubo un error al procesar la pieza.');
        }
    } catch (error) {
        alert('Hubo un error de conexión al guardar la pieza.');
    }
});

async function cargarListaAdmin() {
    try {
        const res = await fetch(API_URL);
        todosProductos = await res.json();
        listaAdmin.innerHTML = '';
        if(todosProductos.length === 0) {
            listaAdmin.innerHTML = '<li style="color:var(--text-muted); font-style:italic;">No hay piezas registradas.</li>';
            return;
        }
        todosProductos.forEach(p => {
            const li = document.createElement('li');
            li.innerHTML = `
                <div>
                    <strong>${p.nombre}</strong> <span style="font-size:11px; color:var(--accent-gold);">[${p.categoria}]</span> - ${formatFormatoPrecioUSD(p.precio)}
                </div>
                <div class="actions-admin-item">
                    <button class="btn-editar-admin" onclick="prepararEdicionProducto(${p.id})">Editar</button>
                    <button class="btn-eliminar-item" onclick="eliminar(${p.id})">Eliminar</button>
                </div>
            `;
            listaAdmin.appendChild(li);
        });
    } catch (err) {
        console.error("Error al cargar lista admin:", err);
    }
}

window.eliminar = async (id) => {
    if(!adminPIN) {
        alert('Debes autenticarte con tu PIN de administrador.');
        return;
    }

    if(confirm('¿Deseas remover esta pieza de la boutique?')) {
        try {
            const res = await fetch(`${API_URL}/${id}`, { 
                method: 'DELETE',
                headers: {
                    'x-admin-pin': adminPIN
                }
            });

            if (res.ok) {
                if (editandoId === id) resetearFormularioProducto();
                cargarTienda();
                cargarListaAdmin();
                mostrarToast('Pieza eliminada');
            } else {
                alert('No se pudo eliminar. Verifique su PIN.');
            }
        } catch (err) {
            alert("Error al eliminar la pieza.");
        }
    }
};

// Cargar Buzón de Pedidos
async function cargarBuzonPedidos() {
    if (!adminPIN) return;
    try {
        const res = await fetch(PEDIDOS_API_URL, {
            headers: { 'x-admin-pin': adminPIN }
        });
        if (res.ok) {
            todosPedidos = await res.json();
            renderizarBuzonPedidos();
        }
    } catch (err) {
        console.error("Error al cargar buzón de pedidos:", err);
    }
}

function renderizarBuzonPedidos() {
    const count = todosPedidos.length;
    if (badgePedidosCount) badgePedidosCount.innerText = count;
    if (tabBadgePedidos) tabBadgePedidos.innerText = count;

    if (!buzonPedidosLista) return;
    buzonPedidosLista.innerHTML = '';

    if (count === 0) {
        buzonPedidosLista.innerHTML = `
            <div style="text-align:center; padding: 40px 10px; color:var(--text-muted);">
                <p style="font-family:var(--font-title); font-size:18px; font-style:italic; margin-bottom:6px;">Tu buzón de pedidos está vacío.</p>
                <p style="font-size:11px;">Las solicitudes de adquisición de tus clientes aparecerán aquí automáticamente.</p>
            </div>
        `;
        return;
    }

    let ventasConcretadas = 0;
    todosPedidos.forEach(p => {
        if (p.estado === 'Concretado') {
            const numTotal = parseFloat((p.total || '0').replace(/[^0-9.-]+/g,""));
            if (!isNaN(numTotal)) ventasConcretadas += numTotal;
        }
    });

    const crmHeader = document.createElement('div');
    crmHeader.innerHTML = `
        <div style="background:var(--primary-color); color:#fff; padding:15px; text-align:center; margin-bottom:20px; font-family:var(--font-title); font-size:18px;">
            Ventas Concretadas Totales: $${ventasConcretadas.toFixed(2)} USD
        </div>
    `;
    buzonPedidosLista.appendChild(crmHeader);

    todosPedidos.forEach(ped => {
        const div = document.createElement('div');
        div.className = 'pedido-card';

        const cleanPhone = (ped.cliente.telefono || '').replace(/[^0-9]/g, '');
        const waMessage = encodeURIComponent(`Hola ${ped.cliente.nombre}, te contactamos sobre tu solicitud de reserva #${ped.id}`);
        const waUrl = cleanPhone ? `https://wa.me/${cleanPhone}?text=${waMessage}` : '#';

        let itemsHTML = '';
        if (ped.items && ped.items.length > 0) {
            ped.items.forEach(it => {
                const sku = it.codigo_unico ? ` <span style="font-size:10px; color:#888;">(${it.codigo_unico})</span>` : '';
                itemsHTML += `
                    <div class="pedido-item-row">
                        <span>${it.cantidad}x ${it.nombre}${sku}</span>
                        <span>${formatFormatoPrecioUSD(it.precio)}</span>
                    </div>
                `;
            });
        }

        let badgeColor = '#b59d87'; // Pendiente
        if (ped.estado === 'Concretado') badgeColor = '#2e7d32';
        if (ped.estado === 'Cancelado') badgeColor = '#c62828';

        div.innerHTML = `
            <div class="pedido-card-header">
                <span class="pedido-id">Solicitud #${ped.id}</span>
                <span class="pedido-fecha">${ped.fecha || ''}</span>
            </div>
            <div style="text-align:right; padding:0 15px;">
                <span style="display:inline-block; padding:3px 8px; font-size:11px; background:${badgeColor}; color:#fff; font-weight:bold; letter-spacing:1px; text-transform:uppercase;">${ped.estado || 'Pendiente'}</span>
            </div>
            <div class="pedido-cliente-info">
                <strong>${ped.cliente.nombre}</strong>
                <span>${ped.cliente.email}</span>
                <span>${ped.cliente.telefono || 'No especificado'}</span>
                <span>${ped.cliente.direccion}</span>
                <div class="pedido-contact-actions" style="margin-top:15px; border-top:1px solid #f0f0f0; padding-top:10px;">
                    ${cleanPhone ? `<a href="${waUrl}" target="_blank" class="btn-whatsapp" style="text-decoration:none; display:inline-block; margin-right:10px;">WhatsApp</a>` : ''}
                    <a href="mailto:${ped.cliente.email}?subject=Solicitud de Adquisicion %23${ped.id}" class="btn-email-link" style="text-decoration:none;">Enviar Correo</a>
                </div>
            </div>
            <div class="pedido-items-box">
                ${itemsHTML}
                <div class="pedido-total-row">
                    <span>Total Estimado:</span>
                    <span>${ped.total}</span>
                </div>
            </div>
            <div style="padding:15px; display:flex; gap:10px; flex-wrap:wrap; border-top:1px solid #f0f0f0;">
                <button onclick="cambiarEstadoPedido(${ped.id}, 'Concretado')" style="flex:1; padding:10px; background:var(--primary-color); color:var(--bg-color); border:none; cursor:pointer; font-size:12px; letter-spacing:1px; text-transform:uppercase; transition: opacity 0.3s;" onmouseover="this.style.opacity=0.8" onmouseout="this.style.opacity=1">Concretar Venta</button>
                <button onclick="cambiarEstadoPedido(${ped.id}, 'Cancelado')" style="flex:1; padding:10px; background:transparent; color:#8b0000; border:1px solid #8b0000; cursor:pointer; font-size:12px; letter-spacing:1px; text-transform:uppercase; transition: background 0.3s;" onmouseover="this.style.background='#8b0000'; this.style.color='#fff';" onmouseout="this.style.background='transparent'; this.style.color='#8b0000';">Cancelar</button>
                <button onclick="cambiarEstadoPedido(${ped.id}, 'Pendiente')" style="flex:1; padding:10px; background:transparent; color:var(--text-muted); border:1px solid var(--border-color); cursor:pointer; font-size:12px; letter-spacing:1px; text-transform:uppercase; transition: background 0.3s;" onmouseover="this.style.background='var(--border-color)';" onmouseout="this.style.background='transparent';">Marcar Pendiente</button>
            </div>
            <button class="btn-eliminar-pedido" onclick="eliminarPedido(${ped.id})">Eliminar del Buzón</button>
        `;

        buzonPedidosLista.appendChild(div);
    });
}

window.cambiarEstadoPedido = async (id, estado) => {
    if (!adminPIN) return;
    try {
        const res = await fetch(`${PEDIDOS_API_URL}/${id}`, {
            method: 'POST',
            headers: { 
                'x-admin-pin': adminPIN,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ estado: estado })
        });

        if (res.ok) {
            mostrarToast(`Estado cambiado a ${estado}`);
            cargarBuzonPedidos();
        } else {
            alert('No se pudo cambiar el estado.');
        }
    } catch (err) {
        alert('Error de conexión al cambiar el estado.');
    }
};

window.eliminarPedido = async (id) => {
    if (!adminPIN) return;
    if (confirm(`¿Deseas eliminar la solicitud #${id} del buzón?`)) {
        try {
            const res = await fetch(`${PEDIDOS_API_URL}/${id}`, {
                method: 'DELETE',
                headers: { 'x-admin-pin': adminPIN }
            });

            if (res.ok) {
                mostrarToast('Solicitud eliminada del buzón');
                cargarBuzonPedidos();
            } else {
                alert('No se pudo eliminar el pedido.');
            }
        } catch (err) {
            alert('Error de conexión al eliminar el pedido.');
        }
    }
};

// --- 9. Exportación e Importación de Respaldos de Seguridad ---
const btnExportBackup = document.getElementById('btn-export-backup');
const btnImportBackup = document.getElementById('btn-import-backup');
const inputImportFile = document.getElementById('input-import-file');

if (btnExportBackup) {
    btnExportBackup.addEventListener('click', async () => {
        if (!adminPIN) {
            alert('Debes estar autenticado como Administrador.');
            return;
        }

        try {
            const res = await fetch(EXPORT_BACKUP_URL, {
                headers: { 'x-admin-pin': adminPIN }
            });

            if (res.ok) {
                const data = await res.json();
                const jsonStr = JSON.stringify(data, null, 2);
                const blob = new Blob([jsonStr], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                
                const fechaHoy = new Date().toISOString().slice(0, 10);
                const a = document.createElement('a');
                a.href = url;
                a.download = `maison_elegance_respaldo_${fechaHoy}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);

                mostrarToast('Copia de seguridad descargada en tu dispositivo');
            } else {
                alert('No se pudo descargar el respaldo. Verifica tu PIN.');
            }
        } catch (err) {
            alert('Error de conexión al exportar el respaldo.');
        }
    });
}

if (btnImportBackup && inputImportFile) {
    btnImportBackup.addEventListener('click', async () => {
        if (!adminPIN) {
            alert('Debes estar autenticado como Administrador.');
            return;
        }

        const file = inputImportFile.files[0];
        if (!file) {
            alert('Por favor selecciona un archivo .json de copia de seguridad primero.');
            return;
        }

        const reader = new FileReader();
        reader.onload = async (e) => {
            try {
                const jsonContent = JSON.parse(e.target.result);
                
                const res = await fetch(IMPORT_BACKUP_URL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'x-admin-pin': adminPIN
                    },
                    body: JSON.stringify(jsonContent)
                });

                if (res.ok) {
                    alert('¡Copia de seguridad restaurada con éxito! La página se actualizará ahora.');
                    cargarTienda();
                    if (adminPIN) {
                        cargarListaAdmin();
                        cargarBuzonPedidos();
                    }
                    mostrarToast('Restauración completada');
                } else {
                    alert('Error al importar el respaldo. Verifica tu PIN.');
                }
            } catch (err) {
                alert('El archivo seleccionado no es un respaldo JSON válido.');
            }
        };
        reader.readAsText(file);
    });
}

function mostrarToast(mensaje) {
    const toast = document.getElementById('toast-notification');
    const toastMsg = document.getElementById('toast-message');
    toastMsg.innerText = mensaje;
    toast.classList.add('visible');
    setTimeout(() => {
        toast.classList.remove('visible');
    }, 3000);
}

// Inicialización
cargarTienda();
