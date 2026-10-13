/* ======================================================
   LAB STOCK
   IES 9-018
   Sistema de Gestión de Inventario
====================================================== */


/* ======================================================
   DATOS
====================================================== */


/*
    El inventario comienza completamente vacío.

    Más adelante este array será reemplazado
    por los datos provenientes de la base de datos.
*/

let inventario = [];


/*
    Los pedidos también comienzan vacíos.

    Por ahora funcionan solamente durante
    la sesión actual de la página.
*/

let pedidos = [];


/*
    Armario seleccionado actualmente.
*/

let armarioSeleccionado = null;



async function cargarInventario() {

    try {

        const respuesta = await fetch("/api/inventario");

        if (!respuesta.ok) {
            throw new Error("No se pudo cargar el inventario");
        }

        inventario = await respuesta.json();

        mostrarInventario();
        crearArmarios();
        actualizarResumen();

    } catch (error) {

        console.error("Error al cargar inventario:", error);

    }

}

async function cargarPedidos() {

    try {

        const respuesta = await fetch("/api/pedidos");

        if (!respuesta.ok) {

            throw new Error(
                "No se pudieron cargar los pedidos"
            );

        }

        pedidos = await respuesta.json();

        mostrarPedidos();

        actualizarResumen();

    } catch (error) {

        console.error(
            "Error al cargar pedidos:",
            error
        );

    }

}

/* ======================================================
   ELEMENTOS HTML
====================================================== */


const contenedorArmarios =
    document.getElementById("contenedorArmarios");


const tablaInventario =
    document.getElementById("tablaInventario");


const inventarioVacio =
    document.getElementById("inventarioVacio");


const buscadorMaterial =
    document.getElementById("buscadorMaterial");


const filtroArmario =
    document.getElementById("filtroArmario");


const tituloInventario =
    document.getElementById("tituloInventario");


const btnMostrarTodos =
    document.getElementById("btnMostrarTodos");


const totalMateriales =
    document.getElementById("totalMateriales");


const totalStockBajo =
    document.getElementById("totalStockBajo");


const totalPedidos =
    document.getElementById("totalPedidos");


/* PEDIDOS */

const modalPedido =
    document.getElementById("modalPedido");


const btnNuevoPedido =
    document.getElementById("btnNuevoPedido");


const btnNuevoPedido2 =
    document.getElementById("btnNuevoPedido2");


const cerrarModal =
    document.getElementById("cerrarModal");


const cancelarPedido =
    document.getElementById("cancelarPedido");


const formPedido =
    document.getElementById("formPedido");


const materialesPedido =
    document.getElementById("materialesPedido");


const btnAgregarMaterial =
    document.getElementById("btnAgregarMaterial");


const contenedorPedidos =
    document.getElementById("contenedorPedidos");


const pedidosVacio =
    document.getElementById("pedidosVacio");

/* ALTA DE MATERIAL */

const btnAltaMaterial =
    document.getElementById("btnAltaMaterial");

const modalAltaMaterial =
    document.getElementById("modalAltaMaterial");

const cerrarModalAlta =
    document.getElementById("cerrarModalAlta");

const cancelarAltaMaterial =
    document.getElementById("cancelarAltaMaterial");

const formAltaMaterial =
    document.getElementById("formAltaMaterial");


/* ======================================================
   ARMARIOS
====================================================== */


function crearArmarios() {

    contenedorArmarios.innerHTML = "";


    for (let numero = 1; numero <= 12; numero++) {

        const cantidadMateriales =
            inventario.filter(
                producto => producto.armario === numero
            ).length;


        const armario =
            document.createElement("div");


        armario.classList.add("armario");


        armario.dataset.armario = numero;


        armario.innerHTML = `

            <div class="numero-armario">

                <span>🗄</span>

                <h3>
                    Armario ${numero}
                </h3>

            </div>

            <p>
                ${cantidadMateriales} materiales registrados
            </p>

            <div class="datos-armario">

                <span>
                    Consultar contenido
                </span>

                <strong>
                    Ver →
                </strong>

            </div>

        `;


        armario.addEventListener(
            "click",
            () => seleccionarArmario(numero)
        );


        contenedorArmarios.appendChild(armario);

    }

}


/* ======================================================
   SELECCIONAR ARMARIO
====================================================== */


function seleccionarArmario(numero) {


    /*
        Si el usuario vuelve a tocar
        el mismo armario, se cierra.
    */

    if (armarioSeleccionado === numero) {

        mostrarTodos();

        return;

    }


    armarioSeleccionado = numero;


    filtroArmario.value = numero;


    tituloInventario.textContent =
        `Inventario · Armario ${numero}`;


    btnMostrarTodos.classList.remove("oculto");


    actualizarArmariosActivos();


    mostrarInventario();


    document
        .getElementById("inventario")
        .scrollIntoView({
            behavior: "smooth"
        });

}


/* ======================================================
   MOSTRAR TODOS
====================================================== */


function mostrarTodos() {

    armarioSeleccionado = null;


    filtroArmario.value = "";


    tituloInventario.textContent =
        "Inventario completo";


    btnMostrarTodos.classList.add("oculto");


    actualizarArmariosActivos();


    mostrarInventario();

}


/* ======================================================
   ARMARIO ACTIVO
====================================================== */


function actualizarArmariosActivos() {

    const armarios =
        document.querySelectorAll(".armario");


    armarios.forEach(armario => {

        const numero =
            Number(armario.dataset.armario);


        if (numero === armarioSeleccionado) {

            armario.classList.add("armario-activo");

        } else {

            armario.classList.remove("armario-activo");

        }

    });

}


/* ======================================================
   MOSTRAR INVENTARIO
====================================================== */


function mostrarInventario() {


    tablaInventario.innerHTML = "";


    const textoBusqueda =
        buscadorMaterial
            .value
            .toLowerCase()
            .trim();


    const numeroArmario =
        filtroArmario.value;


    let resultados =
        inventario.filter(producto => {


            const coincideBusqueda =

                producto.nombre
                    .toLowerCase()
                    .includes(textoBusqueda)

                ||

                producto.codigo
                    .toLowerCase()
                    .includes(textoBusqueda);


            const coincideArmario =

                numeroArmario === ""

                ||

                producto.armario ===
                Number(numeroArmario);


            return coincideBusqueda &&
                   coincideArmario;

        });


    /*
        INVENTARIO VACÍO
    */

    if (resultados.length === 0) {

        inventarioVacio.style.display = "block";

        return;

    }


    inventarioVacio.style.display = "none";


    /*
        CREACIÓN DE FILAS
    */

    resultados.forEach(producto => {


        const fila =
            document.createElement("tr");


        let estado =
            "Disponible";


        let claseEstado =
            "disponible";


        if (producto.stock === 0) {
            estado = "Agotado";
            claseEstado = "critico";
        }
        else if (producto.stock <= producto.stock_minimo) {
            estado = "Stock bajo";
            claseEstado = "bajo";
        }


        fila.innerHTML = `

            <td>
                ${producto.codigo}
            </td>

            <td>
                ${producto.nombre}
            </td>

            <td>
                Armario ${producto.armario}
            </td>

            <td>
                ${producto.estante || "-"}
                ${producto.sector ? " · " + producto.sector : ""}
            </td>

            <td>
                ${producto.stock}
            </td>

            <td>
                ${producto.stock_minimo}
            </td>

            <td>
                <span class="estado ${claseEstado}">
                    ${estado}
                </span>
        </td>

    `;  


        tablaInventario.appendChild(fila);

    });

}


/* ======================================================
   BUSCADOR
====================================================== */


buscadorMaterial.addEventListener(
    "input",
    mostrarInventario
);


/* ======================================================
   FILTRO ARMARIO
====================================================== */


filtroArmario.addEventListener(
    "change",
    () => {


        if (filtroArmario.value === "") {

            armarioSeleccionado = null;

            tituloInventario.textContent =
                "Inventario completo";

            btnMostrarTodos.classList.add("oculto");

        }

        else {

            armarioSeleccionado =
                Number(filtroArmario.value);


            tituloInventario.textContent =
                `Inventario · Armario ${armarioSeleccionado}`;


            btnMostrarTodos.classList.remove("oculto");

        }


        actualizarArmariosActivos();


        mostrarInventario();

    }
);


/* ======================================================
   BOTÓN MOSTRAR TODOS
====================================================== */


btnMostrarTodos.addEventListener(
    "click",
    mostrarTodos
);


/* ======================================================
   ESTADÍSTICAS
====================================================== */


function actualizarResumen() {


    totalMateriales.textContent =
        inventario.length;


    const stockBajo =
        inventario.filter(producto =>

            producto.stock <=
            producto.stock_minimo

        ).length;


    totalStockBajo.textContent =
        stockBajo;


    const pendientes =
        pedidos.filter(
            pedido =>
                pedido.estado === "Pendiente"
        ).length;


    totalPedidos.textContent =
        pendientes;

}


/* ======================================================
   MODAL PEDIDOS
====================================================== */


function abrirModalPedido() {

    modalPedido.classList.add("modal-activo");


    /*
        Si todavía no hay ninguna fila
        para materiales, creamos una.
    */

    if (
        materialesPedido.children.length === 0
    ) {

        agregarFilaMaterial();

    }

}


function cerrarModalPedido() {

    modalPedido.classList.remove(
        "modal-activo"
    );


    formPedido.reset();


    materialesPedido.innerHTML = "";

}


/* ======================================================
   MODAL ALTA DE MATERIAL
====================================================== */

function abrirModalAltaMaterial() {

    modalAltaMaterial.classList.add("modal-activo");

}


function cerrarModalAltaMaterial() {

    modalAltaMaterial.classList.remove("modal-activo");

    formAltaMaterial.reset();

}

btnAltaMaterial.addEventListener(
    "click",
    evento => {

        evento.preventDefault();

        abrirModalAltaMaterial();

    }
);


cerrarModalAlta.addEventListener(
    "click",
    cerrarModalAltaMaterial
);


cancelarAltaMaterial.addEventListener(
    "click",
    cerrarModalAltaMaterial
);


modalAltaMaterial.addEventListener(
    "click",
    evento => {

        if (evento.target === modalAltaMaterial) {

            cerrarModalAltaMaterial();

        }

    }
);

formAltaMaterial.addEventListener(
    "submit",
    async evento => {

        evento.preventDefault();

        console.log("Enviando alta de material...");

        const nuevoMaterial = {

            codigo:
                document
                    .getElementById("codigoMaterial")
                    .value
                    .trim(),

            nombre:
                document
                    .getElementById("nombreMaterial")
                    .value
                    .trim(),

            categoria:
                document
                    .getElementById("categoriaMaterial")
                    .value
                    .trim(),

            unidad_medida:
                document
                    .getElementById("unidadMaterial")
                    .value,

            stock_minimo:
                Number(
                    document
                        .getElementById("stockMinimoMaterial")
                        .value
                ),

            cantidad:
                Number(
                    document
                        .getElementById("cantidadMaterial")
                        .value
                ),

            armario:
                Number(
                    document
                        .getElementById("armarioMaterial")
                        .value
                ),

            estante:
                document
                    .getElementById("estanteMaterial")
                    .value
                    .trim(),

            sector:
                document
                    .getElementById("sectorMaterial")
                    .value
                    .trim(),

            descripcion:
                document
                    .getElementById("descripcionMaterial")
                    .value
                    .trim()
        };


        try {

            const respuesta = await fetch(
                "/api/materiales",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify(nuevoMaterial)
                }
            );


            const resultado =
                await respuesta.json();


            if (!respuesta.ok) {

                throw new Error(
                    resultado.error ||
                    "No se pudo registrar el material"
                );

            }


            mostrarNotificacion(
                "Material registrado correctamente",
                "success"

            );


            cerrarModalAltaMaterial();


            await cargarInventario();


        } catch (error) {

            console.error(
                "Error al registrar material:",
                error
            );


            alert(
                "Error al registrar el material: "
                + error.message
            );

        }

    }
);


/* ======================================================
   BOTONES MODAL
====================================================== */


btnNuevoPedido.addEventListener(
    "click",
    abrirModalPedido
);


btnNuevoPedido2.addEventListener(
    "click",
    abrirModalPedido
);


cerrarModal.addEventListener(
    "click",
    cerrarModalPedido
);


cancelarPedido.addEventListener(
    "click",
    cerrarModalPedido
);


/* ======================================================
   CERRAR HACIENDO CLICK AFUERA
====================================================== */


modalPedido.addEventListener(
    "click",
    evento => {

        if (evento.target === modalPedido) {

            cerrarModalPedido();

        }

    }
);


/* ======================================================
   AGREGAR MATERIAL AL PEDIDO
====================================================== */


function agregarFilaMaterial() {

    const fila = document.createElement("div");

    fila.classList.add("fila-material");

    fila.innerHTML = `

        <div class="campo campo-material">

            <label>
                Material
            </label>

            <input
                type="text"
                class="pedido-material"
                placeholder="Escriba el material..."
                autocomplete="off"
                required
            >

            <div class="sugerencias-materiales"></div>

        </div>


        <div class="campo">

            <label>
                Ubicación
            </label>

            <input
                type="text"
                class="pedido-ubicacion"
                placeholder="Se completa automáticamente"
                readonly
            >

        </div>


        <div class="campo">

            <label>
                Cantidad
            </label>

            <input
                type="number"
                class="pedido-cantidad"
                min="1"
                value="1"
                required
            >

        </div>


        <button
            type="button"
            class="eliminar-material"
            title="Eliminar material"
        >
            ×
        </button>

    `;


    const inputMaterial =
        fila.querySelector(".pedido-material");

    const inputUbicacion =
        fila.querySelector(".pedido-ubicacion");

    const sugerencias =
        fila.querySelector(".sugerencias-materiales");


    inputMaterial.addEventListener(
        "input",
        () => buscarMaterialPedido(
            inputMaterial,
            inputUbicacion,
            sugerencias
        )
    );

    inputMaterial.addEventListener(
        "focus",
        () => buscarMaterialPedido(
            inputMaterial,
            inputUbicacion,
            sugerencias
        )
    );


    fila
        .querySelector(".eliminar-material")
        .addEventListener(
            "click",
            () => fila.remove()
        );


    materialesPedido.appendChild(fila);

}


/* ======================================================
   OPCIONES ARMARIOS
====================================================== */


function crearOpcionesArmarios() {

    let opciones = "";


    for (let numero = 1; numero <= 12; numero++) {

        opciones += `

            <option value="${numero}">
                Armario ${numero}
            </option>

        `;

    }


    return opciones;

}


/* ======================================================
   BOTÓN AGREGAR MATERIAL
====================================================== */


btnAgregarMaterial.addEventListener(
    "click",
    agregarFilaMaterial
);


/* ======================================================
   CREAR PEDIDO
====================================================== */


formPedido.addEventListener(
    "submit",
    async evento => {

        evento.preventDefault();

        const filas =
            document.querySelectorAll(
                ".fila-material"
            );

        if (filas.length === 0) {

            mostrarNotificacion(
                "Debe agregar al menos un material.",
                "error"
            );

            return;
        }

        const materiales = [];
        let stockValido = true;

        filas.forEach(fila => {

            const productoId =
                Number(
                    fila
                        .querySelector(
                            ".pedido-material"
                        )
                        .dataset.productoId
                );

            const producto =
                inventario.find(
                    item =>
                        item.id_material === productoId
                );

            if (!producto) {

                mostrarNotificacion(
                    "Seleccione un material válido del inventario.",
                    "error"
                );

                stockValido = false;

                return;
            }

            const cantidad =
                Number(
                    fila
                        .querySelector(
                            ".pedido-cantidad"
                        )
                        .value
                );

            if (cantidad <= 0) {

                mostrarNotificacion(
                    "La cantidad solicitada debe ser mayor a 0.",
                    "error"
                );

                stockValido = false;

                return;
            }

            if (cantidad > producto.stock) {

                mostrarNotificacion(
                    `Stock insuficiente para ${producto.nombre}. Disponible: ${producto.stock}`,
                    "error"
                );

                stockValido = false;

                return;
            }

            materiales.push({

                productoId:
                    producto.id_material,

                codigo:
                    producto.codigo,

                nombre:
                    producto.nombre,

                armario:
                    producto.armario,

                ubicacion:
                    `${producto.estante || ""}${producto.sector ? " · " + producto.sector : ""}`,

                cantidad,

                stockDisponible:
                    producto.stock

            });

        });

        /*
            Si alguno de los materiales
            no pasó las validaciones,
            no se crea el pedido.
        */
        if (!stockValido) {
            return;
        }

        const nuevoPedido = {

            id:
                pedidos.length + 1,

            responsable:
                document
                    .getElementById(
                        "responsablePedido"
                    )
                    .value,

            practica:
                document
                    .getElementById(
                        "practicaPedido"
                    )
                    .value,

            fecha:
                document
                    .getElementById(
                        "fechaPedido"
                    )
                    .value,

            materiales,

            estado:
                "Pendiente"

        };

        try {

            const respuesta =
                await fetch(
                    "/api/pedidos",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                nuevoPedido
                            )
                    }
                );

            const resultado =
                await respuesta.json();

            if (!respuesta.ok) {

                throw new Error(
                    resultado.error ||
                    "No se pudo crear el pedido"
                );
            }

            mostrarNotificacion(
                "Pedido creado correctamente",
                "success"
            );

            cerrarModalPedido();

            await cargarPedidos();

        } catch (error) {

            console.error(
                "Error al crear pedido:",
                error
            );

            mostrarNotificacion(
                error.message,
                "error"
            );

        }

    }
);


/* ======================================================
   MOSTRAR PEDIDOS
====================================================== */

function mostrarPedidos() {

    contenedorPedidos.innerHTML = "";

    if (pedidos.length === 0) {

        pedidosVacio.style.display =
            "block";

        return;
    }

    pedidosVacio.style.display =
        "none";


    pedidos.forEach(pedido => {

        const tarjeta =
            document.createElement("div");

        tarjeta.classList.add("pedido");


        /*
            Ordenamos los materiales
            según armario.
        */

        const materialesOrdenados =
            [...pedido.materiales]
                .sort(
                    (a, b) =>
                        a.armario -
                        b.armario
                );


        let listado = "";


        materialesOrdenados.forEach(
            material => {

                listado += `

                    <p>

                        <strong>
                            Armario ${material.armario}
                        </strong>

                        ${material.cantidad}
                        ×
                        ${material.nombre}

                    </p>

                `;

            }
        );


        tarjeta.innerHTML = `

            <div class="pedido-header">

                <div>

                    <span>
                        Pedido #${String(
                            pedido.id
                        ).padStart(4, "0")}
                    </span>

                    <h3>
                        ${pedido.practica}
                    </h3>

                </div>

                <span class="${pedido.estado.toLowerCase()}">
                    ${pedido.estado}
                </span>

            </div>


            <p>
                Responsable:
                ${pedido.responsable}
            </p>


            <p>
                Fecha:
                ${pedido.fecha}
            </p>


            <div class="lista-pedido">

                ${listado}

            </div>


            ${
                pedido.estado === "Pendiente"
                    ? `
                        <button
                            class="btn-preparar"
                            data-id="${pedido.id}"
                        >
                            Preparar pedido
                        </button>
                    `
                    : ""
            }


            ${
                pedido.estado === "Preparado"
                    ? `
                        <button
                            class="btn-entregar"
                            data-id="${pedido.id}"
                        >
                            Entregar pedido
                        </button>
                    `
                    : ""
            }

        `;


        contenedorPedidos.appendChild(
            tarjeta
        );

    });


    /* =========================================
       BOTONES PREPARAR
    ========================================= */

    const botonesPreparar =
        document.querySelectorAll(
            ".btn-preparar"
        );


    botonesPreparar.forEach(boton => {

        boton.addEventListener(
            "click",
            () => {

                const idPedido =
                    Number(
                        boton.dataset.id
                    );

                prepararPedido(
                    idPedido
                );

            }
        );

    });


    /* =========================================
       BOTONES ENTREGAR
    ========================================= */

    const botonesEntregar =
        document.querySelectorAll(
            ".btn-entregar"
        );


    botonesEntregar.forEach(boton => {

        boton.addEventListener(
            "click",
            () => {

                const idPedido =
                    Number(
                        boton.dataset.id
                    );

                entregarPedido(
                    idPedido
                );

            }
        );

    });

}


/* ======================================================
   PREPARAR PEDIDO
====================================================== */

async function prepararPedido(idPedido) {

    try {

        const respuesta =
            await fetch(
                `/api/pedidos/${idPedido}/preparar`,
                {
                    method: "PATCH"
                }
            );


        const resultado =
            await respuesta.json();


        if (!respuesta.ok) {

            throw new Error(
                resultado.error ||
                "No se pudo preparar el pedido"
            );

        }


        mostrarNotificacion(
            "Pedido preparado correctamente",
            "success"
        );


        await cargarPedidos();


    } catch (error) {

        console.error(
            "Error al preparar pedido:",
            error
        );


        mostrarNotificacion(
            error.message,
            "error"
        );

    }

}


/* ======================================================
   ENTREGAR PEDIDO
====================================================== */

async function entregarPedido(idPedido) {

    try {

        const respuesta =
            await fetch(
                `/api/pedidos/${idPedido}/entregar`,
                {
                    method: "PATCH"
                }
            );


        const resultado =
            await respuesta.json();


        if (!respuesta.ok) {

            throw new Error(
                resultado.error ||
                "No se pudo entregar el pedido"
            );

        }


        mostrarNotificacion(
            "Pedido entregado correctamente",
            "success"
        );


        await cargarPedidos();


        await cargarInventario();


    } catch (error) {

        console.error(
            "Error al entregar pedido:",
            error
        );


        mostrarNotificacion(
            error.message,
            "error"
        );

    }

}


/* ======================================================
   PREPARAR PEDIDO
====================================================== */

async function prepararPedido(idPedido) {

    try {

        const respuesta =
            await fetch(
                `/api/pedidos/${idPedido}/preparar`,
                {
                    method: "PATCH"
                }
            );

        const resultado =
            await respuesta.json();

        if (!respuesta.ok) {

            throw new Error(
                resultado.error ||
                "No se pudo preparar el pedido"
            );
        }

        mostrarNotificacion(
            "Pedido preparado correctamente",
            "success"
        );

        await cargarPedidos();

    } catch (error) {

        console.error(
            "Error al preparar pedido:",
            error
        );

        mostrarNotificacion(
            error.message,
            "error"
        );

    }

}


/* ======================================================
   ENTREGAR PEDIDO
====================================================== */

async function entregarPedido(idPedido) {

    try {

        const respuesta =
            await fetch(
                `/api/pedidos/${idPedido}/entregar`,
                {
                    method: "PATCH"
                }
            );

        const resultado =
            await respuesta.json();

        if (!respuesta.ok) {

            throw new Error(
                resultado.error ||
                "No se pudo entregar el pedido"
            );
        }

        mostrarNotificacion(
            "Pedido entregado correctamente",
            "success"
        );

        await cargarPedidos();

        await cargarInventario();

    } catch (error) {

        console.error(
            "Error al entregar pedido:",
            error
        );

        mostrarNotificacion(
            error.message,
            "error"
        );

    }

}

/* ======================================================
   INICIALIZACIÓN
====================================================== */


cargarInventario();

cargarPedidos();


function buscarMaterialPedido(
    inputMaterial,
    inputUbicacion,
    contenedorSugerencias
) {

    const texto =
        inputMaterial
            .value
            .toLowerCase()
            .trim();


    contenedorSugerencias.innerHTML = "";

    inputUbicacion.value = "";


    const resultados =
        inventario.filter(producto => {

            if (texto === "") {
                return true;
            }

            return (
                producto.nombre
                    .toLowerCase()
                    .includes(texto)

                ||

                producto.codigo
                    .toLowerCase()
                    .includes(texto)
            );

        });


    resultados.forEach(producto => {

        const opcion =
            document.createElement("div");


        opcion.classList.add(
            "sugerencia-material"
        );


        opcion.innerHTML = `

            <strong>
                ${producto.nombre}
            </strong>

            <span>
                Armario ${producto.armario}
                ${producto.estante ? " · " + producto.estante : ""}
                ${producto.sector ? " · " + producto.sector : ""}
            </span>

            <small>
                Stock disponible: ${producto.stock}
            </small>

        `;


        opcion.addEventListener(
            "click",
            () => {

                inputMaterial.value =
                    producto.nombre;


                inputMaterial.dataset.productoId =
                    producto.id_material;


                inputUbicacion.value =
                    `Armario ${producto.armario}` +
                    (producto.estante
                        ? ` · ${producto.estante}`
                        : "") +
                    (producto.sector
                        ? ` · ${producto.sector}`
                        : "");


                contenedorSugerencias.innerHTML =
                    "";

            }
        );


        contenedorSugerencias.appendChild(
            opcion
        );

    });

}


async function cargarPedidos() {

    try {

        const respuesta = await fetch("/api/pedidos");

        if (!respuesta.ok) {

            throw new Error(
                "No se pudieron cargar los pedidos"
            );

        }

        pedidos = await respuesta.json();

        mostrarPedidos();

        actualizarResumen();

    } catch (error) {

        console.error(
            "Error al cargar pedidos:",
            error
        );

    }

}

/* ======================================================
   NOTIFICACIONES
====================================================== */

function mostrarNotificacion(mensaje, tipo = "success") {

    const notificacion =
        document.createElement("div");

    notificacion.classList.add(
        "notificacion",
        `notificacion-${tipo}`
    );

    notificacion.innerHTML = `

        <div class="notificacion-icono">
            ${tipo === "success" ? "✓" : "!"}
        </div>

        <div class="notificacion-contenido">

            <strong>
                ${tipo === "success"
                    ? "Operación exitosa"
                    : "Atención"}
            </strong>

            <span>
                ${mensaje}
            </span>

        </div>

        <button class="notificacion-cerrar">
            ×
        </button>

    `;

    document.body.appendChild(notificacion);

    setTimeout(() => {
        notificacion.classList.add(
            "notificacion-visible"
        );
    }, 50);

    const cerrar = () => {

        notificacion.classList.remove(
            "notificacion-visible"
        );

        setTimeout(() => {
            notificacion.remove();
        }, 300);
    };

    notificacion
        .querySelector(".notificacion-cerrar")
        .addEventListener(
            "click",
            cerrar
        );

    setTimeout(cerrar, 4000);
}