<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Century 21 Diamante - CRM Inteligente</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>

    <style>
        .scrollbar-hide::-webkit-scrollbar { display: none; }
        .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
        .bg-c21-black { background-color: #212121; }
        .bg-c21-gold { background-color: #BE9A5A; }
        .text-c21-gold { color: #BE9A5A; }
        .bg-chat-pattern { background-color: #f4f5f7; }

        @media (max-width: 767px) {
            body.chat-mobile-active #panel-lista { display: none !important; }
            body:not(.chat-mobile-active) #panel-chat { display: none !important; }
            body.chat-mobile-active #panel-chat { display: flex !important; }
        }

        .typing-indicator span {
            display: inline-block;
            width: 6px;
            height: 6px;
            background-color: #BE9A5A;
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
            margin-right: 3px;
        }
        .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
        .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
    </style>
</head>
<body class="bg-gray-100 flex overflow-hidden font-sans text-gray-800" style="position: fixed; inset: 0;">

    <div id="panel-lista" class="w-full md:w-[380px] bg-white border-r border-gray-300 flex flex-col z-20 shadow-lg h-full flex-shrink-0">
        
        <div class="bg-c21-black p-5 flex justify-between items-center shadow-md z-10">
            <h2 class="font-bold text-lg text-c21-gold tracking-wide flex items-center">
                <i class="fa-solid fa-gem mr-2"></i> Monitor C21
            </h2>
            <div class="flex items-center space-x-4">
                <span class="text-[10px] border border-c21-gold text-c21-gold px-2 py-1 rounded-full uppercase tracking-wider font-semibold hidden md:inline-block">En vivo</span>
                
                <button onclick="abrirModalReportes()" class="text-c21-gold hover:text-white transition-colors" title="Analítica y Reportes">
                    <i class="fa-solid fa-chart-column text-lg"></i>
                </button>
                
                <button onclick="abrirModalAsesores()" class="text-c21-gold hover:text-white transition-colors" title="Gestión de Asesores">
                    <i class="fa-solid fa-users-cog text-lg"></i>
                </button>
            </div>
        </div>

        <div class="bg-white p-3 border-b border-gray-200 flex flex-col space-y-2 shadow-sm z-0">
            <div class="flex space-x-2">
                <div class="relative flex-1">
                    <i class="fa-solid fa-search absolute left-4 top-3 text-gray-400 text-sm"></i>
                    <input type="text" id="buscador" placeholder="Buscar prospecto..." class="w-full bg-gray-100 rounded-full py-2 pl-10 pr-4 text-sm focus:outline-none focus:ring-1 focus:ring-c21-gold transition-shadow" oninput="filtrarClientes()">
                </div>
                <button id="btn-filtro-humano" onclick="toggleFiltroHumano()" class="bg-gray-100 text-gray-500 p-2 rounded-full w-10 h-10 flex items-center justify-center hover:bg-gray-200 focus:outline-none transition-colors shadow-inner" title="Ver chats atendidos por humano">
                    <i class="fa-solid fa-user-tie"></i>
                </button>
                <button id="btn-filtro-noleidos" onclick="toggleFiltroNoLeidos()" class="bg-gray-100 text-gray-500 p-2 rounded-full w-10 h-10 flex items-center justify-center hover:bg-gray-200 focus:outline-none transition-colors shadow-inner relative" title="Ver mensajes pendientes">
                    <i class="fa-solid fa-bell"></i>
                </button>
            </div>
            
            <div class="relative">
                <i class="fa-solid fa-filter absolute left-4 top-2 text-gray-400 text-xs"></i>
                <select id="filtro-asesor" onchange="filtrarClientes()" class="w-full bg-gray-50 border border-gray-200 rounded-full py-1.5 pl-10 pr-4 text-xs focus:outline-none focus:ring-1 focus:ring-c21-gold text-gray-600 appearance-none cursor-pointer shadow-sm">
                    <option value="todos">Todos los prospectos (Cualquier asignación)</option>
                    <option value="sin_asignar">Solo prospectos sin asesor</option>
                    </select>
                <i class="fa-solid fa-chevron-down absolute right-4 top-2.5 text-gray-400 text-[10px] pointer-events-none"></i>
            </div>
        </div>

        <div id="listaClientes" class="flex-1 overflow-y-auto bg-white scrollbar-hide pb-20 md:pb-0">
            <p class="text-center text-gray-400 mt-10 text-sm">Cargando conversaciones...</p>
        </div>
    </div>

    <div id="panel-chat" class="hidden md:flex flex-1 flex-col relative h-full bg-chat-pattern min-w-0">
        <div id="empty-state" class="hidden md:flex absolute inset-0 items-center justify-center bg-gray-50 z-20">
            <div class="text-center text-gray-400">
                <i class="fa-solid fa-gem text-6xl mb-4 text-gray-300"></i>
                <h3 class="text-xl font-light tracking-wide text-gray-500">Selecciona un prospecto</h3>
            </div>
        </div>

        <div class="bg-white px-4 md:px-8 py-3 flex justify-between items-center border-b border-gray-200 shadow-sm z-10 h-[75px] flex-shrink-0">
            <div class="flex items-center min-w-0 pr-2">
                <button onclick="volverALista()" class="md:hidden mr-3 text-gray-500 hover:text-c21-gold focus:outline-none text-xl p-2 -ml-2">
                    <i class="fa-solid fa-arrow-left"></i>
                </button>
                <div class="min-w-0">
                    <h2 id="nombreCliente" class="font-bold text-gray-800 text-lg leading-tight truncate">Cliente</h2>
                    <p id="telefonoCliente" class="text-xs text-gray-500 truncate"></p>
                </div>
            </div>
            
            <div class="flex items-center space-x-2 md:space-x-3 bg-gray-50 px-2 md:px-4 py-2 rounded-lg border border-gray-200 flex-shrink-0">
                <span id="bot-status-text" class="text-[10px] md:text-sm font-bold text-c21-gold w-16 md:w-20 text-right">IA Activa</span>
                <button id="btn-toggle" onclick="toggleBot()" class="w-10 md:w-12 h-5 md:h-6 rounded-full bg-c21-black relative transition-colors duration-300 focus:outline-none">
                    <div id="toggle-knob" class="w-4 md:w-5 h-4 md:h-5 bg-white rounded-full absolute top-[2px] md:top-0.5 left-0.5 transform translate-x-5 md:translate-x-6 transition-transform duration-300 shadow-md"></div>
                </button>
            </div>
        </div>

        <div id="chatMensajes" class="flex-1 overflow-y-auto p-4 md:p-8 flex flex-col space-y-4"></div>

        <div id="quick-replies" class="hidden w-full bg-[#f0f2f5] px-4 py-2 flex items-center space-x-2 overflow-x-auto scrollbar-hide border-t border-gray-200 flex-shrink-0">
            <span class="text-xs text-gray-400 font-bold ml-2 mr-1"><i class="fa-solid fa-bolt"></i></span>
            <button onclick="usarPlantilla('¡Hola! Soy tu asesor asignado de Century 21. ¿A qué hora prefieres que te llame?')" class="whitespace-nowrap bg-white border border-gray-300 text-gray-600 px-4 py-1.5 rounded-full text-xs font-bold shadow-sm hover:border-c21-gold hover:text-c21-gold transition-colors">Saludo y Cita</button>
            <button onclick="usarPlantilla('Para darte un mejor servicio, ¿buscas comprar o rentar?')" class="whitespace-nowrap bg-white border border-gray-300 text-gray-600 px-4 py-1.5 rounded-full text-xs font-bold shadow-sm hover:border-c21-gold hover:text-c21-gold transition-colors">Pedir Detalles</button>
            <button onclick="usarPlantilla('Dame un momento, estoy revisando nuestro inventario para enviarte las mejores opciones.')" class="whitespace-nowrap bg-white border border-gray-300 text-gray-600 px-4 py-1.5 rounded-full text-xs font-bold shadow-sm hover:border-c21-gold hover:text-c21-gold transition-colors">En espera</button>
        </div>

        <div id="chat-input-area" class="bg-white px-4 md:px-6 py-3 flex items-center border-t border-gray-200 h-[70px] md:h-[80px] flex-shrink-0 hidden">
            <input type="text" id="input-mensaje" placeholder="Escribe un mensaje..." class="flex-1 rounded-full bg-gray-100 border-none px-4 md:px-6 py-2.5 md:py-3 focus:outline-none focus:ring-1 focus:ring-c21-gold shadow-inner text-sm text-gray-700" onkeypress="handleEnter(event)">
            <button onclick="enviarMensajeAsesor()" class="ml-3 md:ml-4 bg-c21-gold text-white w-10 md:w-12 h-10 md:h-12 rounded-full flex items-center justify-center hover:bg-[#a88850] transition shadow-md focus:outline-none">
                <i class="fa-solid fa-paper-plane transform translate-x-[-1px]"></i>
            </button>
        </div>
    </div>

    <div id="modal-asesores" class="hidden fixed inset-0 bg-black bg-opacity-60 z-50 flex items-center justify-center backdrop-blur-sm transition-opacity">
        <div class="bg-white w-11/12 md:w-[480px] rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
            <div class="bg-c21-black px-6 py-5 flex justify-between items-center shadow-md">
                <h3 class="text-c21-gold font-bold text-lg"><i class="fa-solid fa-users mr-2"></i> Gestión de Asesores</h3>
                <button onclick="cerrarModalAsesores()" class="text-gray-400 hover:text-white transition-colors focus:outline-none"><i class="fa-solid fa-times text-xl"></i></button>
            </div>
            
            <div class="bg-gray-50 px-6 py-4 border-b border-gray-200">
                <p class="text-xs text-gray-500 font-bold mb-2 uppercase tracking-wide">Añadir Nuevo Asesor</p>
                <div class="flex space-x-2">
                    <input type="text" id="nuevo-asesor-nombre" placeholder="Nombre completo" class="w-1/2 rounded border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-c21-gold shadow-sm">
                    <input type="text" id="nuevo-asesor-telefono" placeholder="Ej. +52427..." class="w-1/2 rounded border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-c21-gold shadow-sm">
                    <button onclick="agregarAsesor()" class="bg-c21-gold text-white px-4 py-2 rounded font-bold shadow-md hover:bg-[#a88850] transition-colors focus:outline-none">
                        <i class="fa-solid fa-plus"></i>
                    </button>
                </div>
            </div>

            <div class="p-6 flex-1 overflow-y-auto bg-white" id="lista-asesores-modal"></div>
        </div>
    </div>

    <div id="modal-reportes" class="hidden fixed inset-0 bg-black bg-opacity-60 z-50 flex items-center justify-center backdrop-blur-sm transition-opacity">
        <div class="bg-white w-11/12 md:w-[500px] rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
            <div class="bg-c21-black px-6 py-5 flex justify-between items-center shadow-md">
                <h3 class="text-c21-gold font-bold text-lg"><i class="fa-solid fa-building-circle-check mr-2"></i> Propiedades Consultadas</h3>
                <button onclick="cerrarModalReportes()" class="text-gray-400 hover:text-white transition-colors focus:outline-none"><i class="fa-solid fa-times text-xl"></i></button>
            </div>
            <div class="p-4 bg-gray-50 border-b border-gray-200 text-sm text-gray-600 text-center">
                Descarga el reporte de prospectos interesados por cada propiedad.
            </div>
            <div class="p-0 flex-1 overflow-y-auto bg-white" id="lista-propiedades-reporte"></div>
            <div id="loader-reportes" class="p-10 hidden text-center">
                <i class="fa-solid fa-spinner fa-spin text-3xl text-c21-gold mb-3"></i>
                <p class="text-gray-500 text-sm">Cargando base de datos...</p>
            </div>
        </div>
    </div>

    <script>
        let todosLosClientes = [];
        let clienteSeleccionado = null;
        let estadoBotActual = true;
        let requiresScroll = false;
        let bloqueadoPorEnvio = false;
        
        let filtroTexto = "";
        let filtroSoloHumanos = false;
        let filtroNoLeidos = false;
        let filtroAsesor = "todos"; // NUEVA VARIABLE PARA EL FILTRO

        let datosReporteActual = [];
        let claveReporteActual = "";

        const isMobile = () => window.innerWidth < 768;
        function mostrarChatMovil() { if(isMobile()) document.body.classList.add('chat-mobile-active'); }
        function volverALista() { if(isMobile()) document.body.classList.remove('chat-mobile-active'); }

        function formatearEnlaces(texto) {
            let procesado = texto.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, function(match, nombre, url) {
                return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="underline font-bold text-blue-400 hover:text-blue-300 break-all cursor-pointer" title="Abrir enlace">${nombre} <i class="fa-solid fa-external-link-alt text-[10px] ml-1"></i></a>`;
            });
            const urlSueltasRegex = /(^|\s)(https?:\/\/[^\s)]+)/g;
            procesado = procesado.replace(urlSueltasRegex, function(match, espacioAtras, url) {
                let puntuacionFinal = '';
                let lastChar = url.slice(-1);
                if (['.', ',', ';', ':'].includes(lastChar)) {
                    url = url.slice(0, -1);
                    puntuacionFinal = lastChar;
                }
                return `${espacioAtras}<a href="${url}" target="_blank" rel="noopener noreferrer" class="underline font-bold hover:opacity-75 break-all cursor-pointer" title="Abrir enlace">${url}</a>${puntuacionFinal}`;
            });
            return procesado;
        }

        async function cargarClientes() {
            try {
                const res = await fetch("/conversaciones");
                todosLosClientes = await res.json();
                actualizarDropdownAsesores(); // LLAMADA AL NUEVO GENERADOR DE FILTRO
                renderListaClientes();
            } catch (error) {}
        }

        // =========================================================
        // NUEVA FUNCIÓN: ACTUALIZAR EL MENÚ DESPLEGABLE
        // =========================================================
        function actualizarDropdownAsesores() {
            const select = document.getElementById("filtro-asesor");
            const valorActual = select.value;
            
            let opcionesHTML = `
                <option value="todos">Todos los prospectos (Cualquier asignación)</option>
                <option value="sin_asignar">Solo prospectos sin asesor o de Oficina</option>
            `;
            
            // Extraer nombres unicos de asesores que no sean de oficina
            const asesoresUnicos = [...new Set(todosLosClientes
                .map(c => c.seguimiento)
                .filter(s => s && s.trim() !== "" && !s.toLowerCase().includes("oficina")))
            ];
            
            asesoresUnicos.sort().forEach(asesor => {
                opcionesHTML += `<option value="${asesor}">Asesor: ${asesor}</option>`;
            });
            
            select.innerHTML = opcionesHTML;
            // Restaurar el valor por si se actualizó la lista pero queremos seguir filtrando
            select.value = asesoresUnicos.includes(valorActual) || valorActual === "todos" || valorActual === "sin_asignar" ? valorActual : "todos";
        }

        // SE ACTUALIZÓ PARA LEER EL NUEVO DROPDOWN
        function filtrarClientes() {
            filtroTexto = document.getElementById("buscador").value.toLowerCase();
            filtroAsesor = document.getElementById("filtro-asesor").value;
            renderListaClientes();
        }

        function toggleFiltroHumano() {
            filtroSoloHumanos = !filtroSoloHumanos;
            if(filtroSoloHumanos) filtroNoLeidos = false;
            actualizarBotonesFiltro();
            renderListaClientes();
        }

        function toggleFiltroNoLeidos() {
            filtroNoLeidos = !filtroNoLeidos;
            if(filtroNoLeidos) filtroSoloHumanos = false;
            actualizarBotonesFiltro();
            renderListaClientes();
        }

        function actualizarBotonesFiltro() {
            const btnHumano = document.getElementById("btn-filtro-humano");
            const btnNoLeidos = document.getElementById("btn-filtro-noleidos");
            if(filtroSoloHumanos) {
                btnHumano.classList.replace("bg-gray-100", "bg-c21-black");
                btnHumano.classList.replace("text-gray-500", "text-c21-gold");
            } else {
                btnHumano.classList.replace("bg-c21-black", "bg-gray-100");
                btnHumano.classList.replace("text-c21-gold", "text-gray-500");
            }
            if(filtroNoLeidos) {
                btnNoLeidos.classList.replace("bg-gray-100", "bg-c21-gold");
                btnNoLeidos.classList.replace("text-gray-500", "text-white");
            } else {
                btnNoLeidos.classList.replace("bg-c21-gold", "bg-gray-100");
                btnNoLeidos.classList.replace("text-white", "text-gray-500");
            }
        }

        function renderListaClientes() {
            const lista = document.getElementById("listaClientes");
            lista.innerHTML = "";

            if (!Array.isArray(todosLosClientes) || todosLosClientes.length === 0) {
                lista.innerHTML = `<p class="text-center text-gray-400 mt-10 text-sm italic">Sin conversaciones recientes.</p>`;
                return;
            }

            let clientesFiltrados = todosLosClientes.filter(c => {
                const nombre = c.display ? String(c.display).toLowerCase() : "";
                const tel = c.telefono ? String(c.telefono).toLowerCase() : "";
                const textoBuscado = filtroTexto ? String(filtroTexto).toLowerCase() : "";
                const seguimiento = c.seguimiento ? c.seguimiento : "";
                
                const cumpleTexto = nombre.includes(textoBuscado) || tel.includes(textoBuscado);
                const isBotOn = (c.bot_encendido !== false);
                const isUnread = (!isBotOn && c.leido === false);
                const cumpleHumano = filtroSoloHumanos ? (!isBotOn) : true;
                const cumpleNoLeido = filtroNoLeidos ? isUnread : true;
                
                // LÓGICA DEL NUEVO FILTRO POR ASESOR
                let cumpleAsesor = true;
                if (filtroAsesor === "sin_asignar") {
                    cumpleAsesor = seguimiento.trim() === "" || seguimiento.toLowerCase().includes("oficina");
                } else if (filtroAsesor !== "todos") {
                    cumpleAsesor = seguimiento === filtroAsesor;
                }
                
                return cumpleTexto && cumpleHumano && cumpleNoLeido && cumpleAsesor;
            });

            if(clientesFiltrados.length === 0) {
                lista.innerHTML = `<p class="text-center text-gray-400 mt-10 text-sm italic">No hay resultados para tu filtro.</p>`;
                return;
            }

            clientesFiltrados.forEach(c => {
                try {
                    const isBotOn = c.bot_encendido !== false;
                    const isActive = clienteSeleccionado === c.telefono;
                    const isUnread = (!isBotOn && c.leido === false);

                    const div = document.createElement("div");
                    div.className = `p-4 border-b border-gray-100 cursor-pointer transition-all duration-200 flex justify-between items-center ${isActive && !isMobile() ? 'bg-gray-100 border-l-4 border-l-c21-gold shadow-inner' : 'hover:bg-gray-50 border-l-4 border-transparent'}`;
                    
                    div.onclick = () => {
                        requiresScroll = true;
                        clienteSeleccionado = c.telefono; 
                        renderListaClientes(); 
                        cargarChat(c.telefono, c.display, isBotOn, isUnread);
                        mostrarChatMovil();
                    };

                    const safeTelefono = c.telefono ? String(c.telefono).replace('whatsapp:', '') : 'Desconocido';
                    const safeMensaje = c.ultimo_mensaje ? String(c.ultimo_mensaje) : "Sin mensajes";
                    const safeDisplay = c.display ? String(c.display) : safeTelefono;
                    const fontWeight = isUnread ? 'font-extrabold text-gray-900' : (isActive ? 'font-bold text-c21-gold' : 'font-bold text-gray-800');
                    const dotIndicator = isUnread ? `<span class="inline-block w-2 h-2 bg-green-500 rounded-full ml-2 shadow-sm animate-pulse"></span>` : '';

                    // NUEVO: LA ETIQUETA DORADA DEL ASESOR ASIGNADO
                    const badgeAsesor = c.seguimiento && c.seguimiento.trim() !== "" && !c.seguimiento.toLowerCase().includes("oficina") 
                        ? `<p class="text-[10px] text-[#A88850] font-bold mt-1.5 uppercase tracking-wide"><i class="fa-solid fa-headset mr-1"></i>${c.seguimiento}</p>` 
                        : '';

                    div.innerHTML = `
                        <div class="flex-1 min-w-0 pr-4">
                            <div class="flex items-center">
                                <p class="${fontWeight} text-sm truncate transition-colors">${safeDisplay}</p>
                                ${dotIndicator}
                            </div>
                            <p class="text-xs text-gray-500 mb-1">${safeTelefono}</p>
                            <p class="text-xs ${isUnread ? 'text-gray-800 font-semibold' : 'text-gray-400'} truncate italic">${safeMensaje}</p>
                            ${badgeAsesor}
                        </div>
                        <div class="flex-shrink-0 flex flex-col items-end space-y-1">
                            ${isBotOn 
                                ? '<span class="bg-c21-black text-c21-gold text-[9px] px-2 py-1 rounded font-bold tracking-wide shadow-sm"><i class="fa-solid fa-robot"></i> IA</span>' 
                                : '<span class="bg-c21-gold text-white text-[9px] px-2 py-1 rounded font-bold tracking-wide shadow-sm"><i class="fa-solid fa-user"></i> HUMANO</span>'}
                        </div>
                    `;
                    lista.appendChild(div);
                } catch (e) {}
            });
        }

        async function cargarChat(telefono, nombre, bot_encendido, isUnread) {
            if(bloqueadoPorEnvio) return;

            clienteSeleccionado = telefono;
            estadoBotActual = bot_encendido;
            
            if(!isMobile()) document.getElementById("empty-state").style.display = "none";
            
            document.getElementById("chat-input-area").classList.remove("hidden");
            document.getElementById("chat-input-area").classList.add("flex");
            document.getElementById("quick-replies").classList.remove("hidden");
            document.getElementById("quick-replies").classList.add("flex");

            document.getElementById("nombreCliente").textContent = nombre;
            document.getElementById("telefonoCliente").textContent = String(telefono).replace('whatsapp:', '');
            actualizarUIBoton();

            if(isUnread) {
                fetch(`/api/marcar_leido/${encodeURIComponent(telefono)}`, { method: 'POST' });
                let clienteMemoria = todosLosClientes.find(c => c.telefono === telefono);
                if(clienteMemoria) clienteMemoria.leido = true;
                renderListaClientes();
            }

            try {
                const res = await fetch(`/chat/${encodeURIComponent(telefono)}`);
                const data = await res.json();
                const chat = document.getElementById("chatMensajes");
                chat.innerHTML = "";

                if(data.length === 0 || !data[0].observaciones_generales){
                    chat.innerHTML = `<div class="text-center text-gray-400 mt-10 text-sm">Aún no hay mensajes.</div>`;
                    return;
                }

                const lineas = data[0].observaciones_generales.split(/\r?\n/);
                let mensajesAgrupados = [];
                let mensajeActual = null;

                lineas.forEach(linea => {
                    if(!linea.trim() && !mensajeActual) return;
                    const esNuevoMensaje = linea.match(/^(?:\[\d{2}:\d{2}\]\s*)?(Cliente:|Bot:|Asesor:)/);
                    if (esNuevoMensaje) {
                        if (mensajeActual) mensajesAgrupados.push(mensajeActual);
                        mensajeActual = linea;
                    } else if (mensajeActual) {
                        mensajeActual += "\n" + linea;
                    }
                });
                if (mensajeActual) mensajesAgrupados.push(mensajeActual);

                mensajesAgrupados.forEach(rawContent => {
                    let timeHtml = "";
                    const timeMatch = rawContent.match(/^\[(\d{2}:\d{2})\]\s*/);
                    
                    if (timeMatch) {
                        timeHtml = `<span class="text-[10px] opacity-60 ml-3 float-right mt-3 font-medium">${timeMatch[1]}</span>`;
                        rawContent = rawContent.replace(timeMatch[0], "");
                    }

                    if (rawContent.startsWith("Cliente:")) {
                        let text = rawContent.replace('Cliente:', '').trim();
                        text = formatearEnlaces(text);
                        chat.innerHTML += `<div class="flex justify-start"><div class="bg-white text-gray-800 p-3 md:p-4 rounded-xl rounded-tl-sm max-w-[85%] md:max-w-2xl shadow-sm border border-gray-100"><p class="text-[13px] md:text-[14px] whitespace-pre-wrap leading-relaxed">${text}${timeHtml}</p></div></div>`;
                    } else if (rawContent.startsWith("Bot:")) {
                        let text = rawContent.replace('Bot:', '').trim();
                        text = formatearEnlaces(text);
                        chat.innerHTML += `<div class="flex justify-end"><div class="bg-c21-black text-white p-3 md:p-4 rounded-xl rounded-tr-sm max-w-[85%] md:max-w-2xl shadow-md border border-gray-800"><span class="text-[9px] md:text-[10px] font-bold text-c21-gold block mb-1 uppercase tracking-wider"><i class="fa-solid fa-robot mr-1"></i> IA Diamante</span><p class="text-[13px] md:text-[14px] whitespace-pre-wrap leading-relaxed text-gray-100">${text}${timeHtml}</p></div></div>`;
                    } else if (rawContent.startsWith("Asesor:")) {
                        let text = rawContent.replace('Asesor:', '').trim();
                        text = formatearEnlaces(text); 
                        chat.innerHTML += `<div class="flex justify-end"><div class="bg-c21-gold text-white p-3 md:p-4 rounded-xl rounded-tr-sm max-w-[85%] md:max-w-2xl shadow-md"><span class="text-[9px] md:text-[10px] font-bold text-[#fcfcfc] block mb-1 uppercase tracking-wider"><i class="fa-solid fa-user-tie mr-1"></i> Tú</span><p class="text-[13px] md:text-[14px] whitespace-pre-wrap leading-relaxed">${text}${timeHtml}</p></div></div>`;
                    }
                });

                if (requiresScroll) {
                    setTimeout(() => { chat.scrollTop = chat.scrollHeight; }, 50);
                    requiresScroll = false;
                }
            } catch (error) {}
        }

        function usarPlantilla(texto) {
            const input = document.getElementById("input-mensaje");
            input.value = texto;
            input.focus();
        }

        function handleEnter(event) {
            if (event.key === 'Enter') enviarMensajeAsesor();
        }

        async function enviarMensajeAsesor() {
            const input = document.getElementById("input-mensaje");
            const texto = input.value.trim();
            if (!texto || !clienteSeleccionado) return;

            input.value = "";
            bloqueadoPorEnvio = true;

            const chat = document.getElementById("chatMensajes");
            chat.innerHTML += `<div class="flex justify-end" id="temp-typing"><div class="bg-c21-gold text-white p-4 rounded-xl rounded-tr-sm max-w-[85%] shadow-md opacity-80"><div class="typing-indicator flex items-center h-4"><span></span><span></span><span></span></div></div></div>`;
            chat.scrollTop = chat.scrollHeight;

            try {
                await fetch(`/api/enviar_mensaje/${encodeURIComponent(clienteSeleccionado)}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mensaje: texto })
                });

                if (estadoBotActual) {
                    estadoBotActual = false;
                    actualizarUIBoton();
                }

                requiresScroll = true;
                bloqueadoPorEnvio = false; 
                cargarChat(clienteSeleccionado, document.getElementById("nombreCliente").textContent, estadoBotActual, false);
                cargarClientes();

            } catch (error) { bloqueadoPorEnvio = false; }
        }

        function toggleBot() {
            if (!clienteSeleccionado) return;
            estadoBotActual = !estadoBotActual;
            actualizarUIBoton();

            fetch(`/toggle_bot/${encodeURIComponent(clienteSeleccionado)}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ estado: estadoBotActual })
            }).then(() => cargarClientes());
        }

        function actualizarUIBoton() {
            const btn = document.getElementById('btn-toggle');
            const knob = document.getElementById('toggle-knob');
            const text = document.getElementById('bot-status-text');

            if (estadoBotActual) {
                btn.classList.replace('bg-c21-gold', 'bg-c21-black');
                knob.classList.remove(isMobile() ? 'translate-x-5' : 'translate-x-6');
                knob.classList.add(isMobile() ? 'translate-x-5' : 'translate-x-6');
                text.textContent = "IA Activa";
                text.className = "text-[10px] md:text-sm font-bold text-c21-gold w-16 md:w-20 text-right";
            } else {
                btn.classList.replace('bg-c21-black', 'bg-c21-gold');
                knob.classList.remove(isMobile() ? 'translate-x-5' : 'translate-x-6');
                text.textContent = "Humano";
                text.className = "text-[10px] md:text-sm font-bold text-gray-500 w-16 md:w-20 text-right";
            }
        }

        function abrirModalAsesores() {
            document.getElementById('modal-asesores').classList.remove('hidden');
            cargarAsesoresModal();
        }

        function cerrarModalAsesores() {
            document.getElementById('modal-asesores').classList.add('hidden');
            document.getElementById('nuevo-asesor-nombre').value = '';
            document.getElementById('nuevo-asesor-telefono').value = '';
        }

        async function cargarAsesoresModal() {
            const container = document.getElementById('lista-asesores-modal');
            container.innerHTML = `<p class="text-center text-gray-400 text-sm mt-5"><i class="fa-solid fa-spinner fa-spin mr-2"></i>Cargando red...</p>`;
            
            try {
                const res = await fetch("/api/asesores");
                const asesores = await res.json();
                
                if(!asesores || asesores.length === 0) {
                    container.innerHTML = `<p class="text-center text-gray-400 text-sm mt-5">No hay asesores registrados.</p>`;
                    return;
                }

                container.innerHTML = "";
                asesores.forEach(a => {
                    const isActivo = a.activo;
                    const displayTel = (a.telefono || "Sin número").replace('whatsapp:', '');
                    const row = document.createElement('div');
                    row.className = "flex justify-between items-center py-4 border-b border-gray-100 hover:bg-gray-50 px-2 transition-colors";
                    
                    row.innerHTML = `
                        <div class="flex items-center min-w-0 flex-1">
                            <div class="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-500 mr-4 shadow-inner flex-shrink-0">
                                <i class="fa-solid fa-user"></i>
                            </div>
                            <div class="min-w-0 pr-2">
                                <p class="font-bold text-gray-800 text-sm truncate">${a.nombre}</p>
                                <p class="text-[10px] text-gray-500 truncate">${displayTel}</p>
                                <p class="text-[10px] uppercase tracking-wide font-bold mt-1 ${isActivo ? 'text-green-500' : 'text-gray-400'}">${isActivo ? 'En Guardia' : 'Fuera de Turno'}</p>
                            </div>
                        </div>
                        <div class="flex items-center space-x-3 flex-shrink-0">
                            <button onclick="toggleAsesorActivo(${a.id}, ${isActivo})" class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${isActivo ? 'bg-green-500' : 'bg-gray-300'}">
                                <span class="inline-block h-4 w-4 transform rounded-full bg-white transition shadow-sm ${isActivo ? 'translate-x-6' : 'translate-x-1'}"></span>
                            </button>
                            <button onclick="eliminarAsesor(${a.id})" class="text-red-400 hover:text-red-600 focus:outline-none transition-colors" title="Eliminar Asesor">
                                <i class="fa-solid fa-trash-can"></i>
                            </button>
                        </div>
                    `;
                    container.appendChild(row);
                });
            } catch (error) {}
        }

        async function agregarAsesor() {
            const nombre = document.getElementById('nuevo-asesor-nombre').value.trim();
            const telefono = document.getElementById('nuevo-asesor-telefono').value.trim();

            if (!nombre || !telefono) {
                alert("Por favor, ingresa el nombre y el número de teléfono del asesor.");
                return;
            }

            try {
                const res = await fetch("/api/asesores", {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nombre: nombre, telefono: telefono })
                });
                
                const data = await res.json();
                if (data.status === "ok") {
                    document.getElementById('nuevo-asesor-nombre').value = '';
                    document.getElementById('nuevo-asesor-telefono').value = '';
                    cargarAsesoresModal(); 
                } else {
                    alert("El servidor rechazó la acción. Detalles del error:\n\n" + data.detalle);
                }
            } catch (error) {
                alert("Hubo un error de conexión. Verifica que el servidor (FastAPI) esté encendido.");
            }
        }

        async function eliminarAsesor(id) {
            const confirmar = confirm("¿Estás seguro de que deseas eliminar permanentemente a este asesor del sistema?");
            if (!confirmar) return;

            try {
                const res = await fetch(`/api/asesores/${id}`, { method: 'DELETE' });
                const data = await res.json();
                if (data.status === "ok") {
                    cargarAsesoresModal(); 
                } else {
                    alert("No se pudo eliminar al asesor.");
                }
            } catch (error) {
                alert("Hubo un error de conexión al intentar borrar.");
            }
        }

        async function toggleAsesorActivo(id, estadoActual) {
            const nuevoEstado = !estadoActual;
            try {
                await fetch(`/api/asesores/${id}/toggle`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ estado: nuevoEstado })
                });
                cargarAsesoresModal();
            } catch (error) {}
        }

        async function abrirModalReportes() {
            document.getElementById('modal-reportes').classList.remove('hidden');
            document.getElementById('lista-propiedades-reporte').innerHTML = '';
            document.getElementById('loader-reportes').classList.remove('hidden');

            try {
                const res = await fetch("/api/reportes/resumen");
                const data = await res.json();
                document.getElementById('loader-reportes').classList.add('hidden');

                const contenedor = document.getElementById('lista-propiedades-reporte');
                
                if(data.status === "ok" && data.resultados && data.resultados.length > 0) {
                    data.resultados.forEach(item => {
                        contenedor.innerHTML += `
                            <div class="flex justify-between items-center p-5 border-b border-gray-100 hover:bg-gray-50 transition-colors">
                                <div>
                                    <p class="font-bold text-gray-800 text-lg">Propiedad: <span class="text-c21-gold">${item.clave}</span></p>
                                    <p class="text-xs text-gray-500 mt-1"><i class="fa-solid fa-users mr-1"></i> ${item.interesados} prospecto(s) interesado(s)</p>
                                </div>
                                <button onclick="descargarExcelDirecto('${item.clave}')" class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-bold shadow-md transition-colors flex items-center focus:outline-none">
                                    <i class="fa-solid fa-file-excel mr-2"></i> Descargar
                                </button>
                            </div>
                        `;
                    });
                } else {
                    contenedor.innerHTML = `<div class="p-8 text-center text-gray-400 italic mt-5">Aún no hay clientes que hayan preguntado por propiedades específicas.</div>`;
                }
            } catch (e) {
                document.getElementById('loader-reportes').classList.add('hidden');
                alert("Error al cargar la lista de propiedades.");
            }
        }

        function cerrarModalReportes() {
            document.getElementById('modal-reportes').classList.add('hidden');
        }

        async function descargarExcelDirecto(clave) {
            try {
                const res = await fetch(`/api/reportes/propiedad/${encodeURIComponent(clave)}`);
                const responseData = await res.json();
                
                if(responseData.status === "ok" && responseData.resultados && responseData.resultados.length > 0) {
                    
                    const datosParaExcel = responseData.resultados.map(c => {
                        let chatLimpio = String(c.observaciones_generales || "").replace(/\n/g, "  •  ");
                        let presupuestoLimpio = c.presupuesto ? parseFloat(String(c.presupuesto).replace(/,/g, "")) : 0;
                        let telefonoLimpio = String(c.telefono || "S/N").replace("whatsapp:", "");

                        return {
                            "ID Prospecto": c.id || "S/N",
                            "Nombre de Cliente": c.nombre_cliente || "Desconocido",
                            "Teléfono": telefonoLimpio, 
                            "Fecha de Contacto": c.fecha_contacto || "",
                            "Hora de Contacto": c.hora_contacto || "",
                            "Presupuesto Estimado": presupuestoLimpio,
                            "Historial de Chat": chatLimpio
                        };
                    });

                    const worksheet = XLSX.utils.json_to_sheet(datosParaExcel);
                    worksheet['!cols'] = [
                        { wch: 15 },  
                        { wch: 30 },  
                        { wch: 20 },  
                        { wch: 18 },  
                        { wch: 18 },  
                        { wch: 25 },  
                        { wch: 120 }  
                    ];
                    const workbook = XLSX.utils.book_new();
                    XLSX.utils.book_append_sheet(workbook, worksheet, "Prospectos");
                    XLSX.writeFile(workbook, `Reporte_Propiedad_${clave}.xlsx`);
                    
                } else {
                    alert("No se encontraron datos para descargar.");
                }
            } catch (e) {
                alert("Error al intentar descargar el archivo Excel.");
            }
        }

        setInterval(() => {
            cargarClientes();
            if(clienteSeleccionado && !bloqueadoPorEnvio) {
                cargarChat(clienteSeleccionado, document.getElementById("nombreCliente").textContent, estadoBotActual, false);
            }
        }, 3000);
        
        cargarClientes();
    </script>
</body>
</html>