// ==========================================
// LavaRESI - Frontend
// Inicio de sesión, turnos y tiempo real
// ==========================================

const $ = (id) => document.getElementById(id);

const NOMBRES = {
  LAVADORA: "Lavadora",
  SECADORA: "Secadora"
};

const ESTADOS = {
  LIBRE: ["Libre", "libre"],
  EN_USO: ["En uso", "en-uso"],
  PENDIENTE_RETIRO: ["Pendiente de retiro", "pendiente-retiro"],
  ENTRE_TANDAS: ["Entre tandas", "entre-tandas"]
};

let cuenta = null;
const avisosOcultos = new Set();   // avisos que la persona ya quitó (se ocultan al instante)
let maquinas = [];
let sesionConsultada = false;
let refrescando = false;
let otroRefresco = false;

let firmaMaquinas = "";
let firmaTurnos = "";
let firmaAvisos = "";

let socket = null;
let intentosSocket = 0;
let socketAbierto = false;   // NUEVO: dice si el WebSocket está conectado
let ultimoRefresco = 0;      // NUEVO: para el respaldo de consulta

// ==========================================
// FUNCIONES GENERALES
// ==========================================

function elemento(etiqueta, clase = "", contenido = "") {
  const e = document.createElement(etiqueta);

  if (clase) e.className = clase;

  e.textContent = contenido;
  return e;
}

function mensaje(id, texto, exito = false) {
  const e = $(id);

  e.textContent = texto;
  e.className = "mensaje" +
    (texto ? (exito ? " exito" : " error") : "");
}

// Contador de peticiones en curso: muestra la barra de carga
let pendientes = 0;

function cargando(delta) {
  pendientes = Math.max(0, pendientes + delta);
  document.body.classList.toggle("cargando", pendientes > 0);
}

async function api(ruta, metodo = "GET", datos = null) {
  cargando(1);

  try {
    return await peticion(ruta, metodo, datos);

  } finally {
    cargando(-1);
  }
}

async function peticion(ruta, metodo = "GET", datos = null) {
  const respuesta = await fetch("/api" + ruta, {
    method: metodo,
    credentials: "same-origin",
    headers: datos === null
      ? {}
      : { "Content-Type": "application/json" },
    body: datos === null
      ? undefined
      : JSON.stringify(datos)
  });

  const cuerpo = await respuesta.json().catch(() => ({}));

  if (!respuesta.ok) {
    const error = new Error(
      typeof cuerpo.detail === "string"
        ? cuerpo.detail
        : `Error del servidor (HTTP ${respuesta.status})`
    );

    error.status = respuesta.status;
    throw error;
  }

  return cuerpo;
}

// ==========================================
// NAVEGACIÓN
// ==========================================

function vista(nombre) {
  $("vista-cuenta").hidden = nombre !== "cuenta";
  $("vista-estado").hidden = nombre !== "estado";

  document.querySelectorAll(".nav").forEach(b => {
    b.classList.toggle(
      "activo",
      b.dataset.vista === nombre
    );
  });
}

// ==========================================
// CONTADORES DE LAS MÁQUINAS
// ==========================================

function formatoTiempo(segundos) {
  const t = Math.max(0, Math.ceil(Number(segundos) || 0));

  const minutos = Math.floor(t / 60);
  const segundosRestantes = t % 60;

  return (
    String(minutos).padStart(2, "0") +
    ":" +
    String(segundosRestantes).padStart(2, "0")
  );
}

// Cuenta localmente cada segundo, sin pedir datos al backend.
function avanzarContadores() {
  document.querySelectorAll("[data-fin]").forEach(nodo => {
    const restantes =
      (Number(nodo.dataset.fin) - Date.now()) / 1000;

    const texto = formatoTiempo(restantes);

    if (nodo.textContent !== texto) {
      nodo.textContent = texto;
    }
  });
}

setInterval(avanzarContadores, 250);

// ==========================================
// TARJETAS DE LAVADORA Y SECADORA
// ==========================================

function tarjetaMaquina(m) {
  const [etiqueta, clase] =
    ESTADOS[m.estado] || [m.estado, ""];

  const tarjeta = elemento("article", "maquina");
  const cabecera = elemento("div", "cabecera-maquina");

  cabecera.append(
    elemento("h3", "", NOMBRES[m.tipo] || m.tipo),
    elemento("span", "estado-badge " + clase, etiqueta)
  );

  tarjeta.append(cabecera);

  // Visitantes: resumen sin nombres.
  // Usuarios con sesión: cola detallada.
  const privado =
    cuenta !== null && Array.isArray(m.cola);

  const ocupante = privado ? m.ocupante : null;

  if (m.estado === "EN_USO") {
    tarjeta.append(
      elemento(
        "p",
        "",
        ocupante
          ? `${ocupante.nombre} · tanda ${ocupante.tandas_iniciadas}/${ocupante.tandas_totales}`
          : "Ciclo en curso"
      )
    );

    if (
      m.segundos_restantes !== null &&
      m.segundos_restantes !== undefined
    ) {
      const reloj = elemento(
        "p",
        "temporizador",
        formatoTiempo(m.segundos_restantes)
      );

      reloj.dataset.fin = String(
        Date.now() + Number(m.segundos_restantes) * 1000
      );

      tarjeta.append(reloj);
    }

  } else if (m.estado === "PENDIENTE_RETIRO") {
    tarjeta.append(
      elemento(
        "p",
        "suave",
        ocupante
          ? `${ocupante.nombre} debe retirar su ropa.`
          : "Esperando que retiren la ropa."
      )
    );

  } else if (m.estado === "ENTRE_TANDAS") {
    tarjeta.append(
      elemento(
        "p",
        "suave",
        ocupante
          ? `${ocupante.nombre} prepara otra tanda.`
          : "Preparando la siguiente tanda."
      )
    );

  } else {
    tarjeta.append(
      elemento("p", "suave", "Disponible para el siguiente turno.")
    );
  }

  // ---------- Listas de espera ----------
  const lista = elemento("div", "lista-cola");

  if (!privado) {
    const total = m.personas_en_espera ??
      (
        Array.isArray(m.cola)
          ? m.cola.filter(s => s.estado !== "EN_USO").length
          : null
      );

    lista.append(
      elemento(
        "div",
        "sin-espera",
        total === null
          ? "Iniciá sesión para ver la lista."
          : `${total} ${total === 1
            ? "persona en espera"
            : "personas en espera"
          }. Iniciá sesión para ver los nombres.`
      )
    );

  } else {
    const espera = m.cola.filter(s => s.estado !== "EN_USO");

    if (!espera.length) {
      lista.append(
        elemento("div", "sin-espera", "Sin personas en espera")
      );
    }

    espera.forEach(s => {
      const fila = elemento("div", "fila-cola");

      fila.append(
        elemento(
          "span",
          "",
          `${s.posicion}. ${s.nombre} · ${s.tandas_totales
          } ${s.tandas_totales === 1 ? "tanda" : "tandas"}`
        )
      );

      const texto = !s.disponible
        ? "Ausente"
        : s.estado === "AUTORIZADA"
          ? "Siguiente"
          : "En espera";

      fila.append(elemento("span", "pequeno", texto));

      lista.append(fila);
    });
  }

  tarjeta.append(lista);

  return tarjeta;
}

// ==========================================
// ACTUALIZACIÓN SIN PARPADEOS
// ==========================================

function pintarMaquinas() {
  // Excluimos el contador de la comparación para
  // no reconstruir las tarjetas cada segundo.
  const firma = JSON.stringify({
    privado: cuenta !== null,
    maquinas: maquinas.map(
      ({ segundos_restantes, ...otros }) => otros
    )
  });

  if (firma !== firmaMaquinas) {
    $("maquinas").replaceChildren(
      ...maquinas.map(tarjetaMaquina)
    );

    firmaMaquinas = firma;

  } else {
    // Recalibrar el reloj cuando exista desfase.
    $("maquinas")
      .querySelectorAll(".maquina")
      .forEach((tarjeta, i) => {
        const reloj = tarjeta.querySelector("[data-fin]");
        const segundos = maquinas[i]?.segundos_restantes;

        if (
          !reloj ||
          segundos === null ||
          segundos === undefined
        ) {
          return;
        }

        const finServidor =
          Date.now() + Number(segundos) * 1000;

        if (
          Math.abs(Number(reloj.dataset.fin) - finServidor) > 2000
        ) {
          reloj.dataset.fin = String(finServidor);
        }
      });
  }

  $("actualizado").textContent =
    "Actualizado: " + new Date().toLocaleTimeString("es-CR");
}

// ==========================================
// ACCIONES DE LOS TURNOS
// ==========================================

function botonAccion(texto, accion) {
  const boton = elemento("button", "secundario", texto);

  boton.type = "button";

  boton.addEventListener("click", async () => {
    boton.disabled = true;
    boton.textContent = "Cargando…";
    boton.classList.add("esperando");
    cargando(1);
    mensaje("msg-turno", "");

    try {
      await accion();
      await refrescar();

    } catch (e) {
      mensaje("msg-turno", e.message);

    } finally {
      boton.disabled = false;
      boton.textContent = texto;
      boton.classList.remove("esperando");
      cargando(-1);
    }
  });

  return boton;
}

// ==========================================
// MIS TURNOS
// ==========================================

function pintarTurnos() {
  if (!cuenta) return;

  const firma = JSON.stringify({
    turnos: cuenta.solicitudes,
    estados: maquinas.map(m => [m.id, m.estado])
  });

  if (firma === firmaTurnos) return;

  firmaTurnos = firma;

  const contenedor = $("mis-turnos");

  const tarjetas = (cuenta.solicitudes || []).map(s => {
    const maq = maquinas.find(m => m.id === s.maquina_id);

    const tarjeta = elemento("div", "turno");

    const titulo = elemento(
      "strong",
      "",
      NOMBRES[s.maquina] || "Máquina"
    );

    let texto = "";

    if (s.estado === "AUTORIZADA") {
      texto =
        "¡Es tu turno! Acercate a la terminal e ingresá tu PIN.";

    } else if (s.estado === "EN_USO") {
      texto =
        `En uso · tanda ${s.tandas_iniciadas}/${s.tandas_totales}`;

    } else {
      texto =
        `Puesto ${s.posicion} · ${s.tandas_totales} ${s.tandas_totales === 1 ? "tanda" : "tandas"
        }`;
    }

    tarjeta.append(
      titulo,
      elemento("p", "suave", texto)
    );

    // Cambiar disponibilidad sin perder el orden.
    if (
      s.estado === "EN_ESPERA" ||
      s.estado === "AUTORIZADA"
    ) {
      tarjeta.append(
        botonAccion(
          s.disponible
            ? "Marcarme ausente"
            : "Ya estoy disponible",

          () => api(
            `/solicitudes/${s.id}/disponibilidad`,
            "POST",
            { disponible: !s.disponible }
          )
        )
      );
    }

    // No cancelar un ciclo activo. Entre tandas,
    // el backend decide si permite terminar el turno.
    if (
      s.estado !== "EN_USO" ||
      maq?.estado === "ENTRE_TANDAS"
    ) {
      tarjeta.append(
        botonAccion(
          s.estado === "EN_USO"
            ? "Terminar mi turno"
            : "Cancelar solicitud",

          () => api(`/solicitudes/${s.id}/cancelar`, "POST")
        )
      );
    }

    return tarjeta;
  });

  contenedor.replaceChildren(
    ...(
      tarjetas.length
        ? tarjetas
        : [
          elemento("p", "suave", "No tenés solicitudes activas.")
        ]
    )
  );
}

// ==========================================
// NOTIFICACIONES
// ==========================================

function pintarAvisos() {
  if (!cuenta) return;

  const lista = (cuenta.notificaciones || []).filter(
    n => !n.leida && !avisosOcultos.has(n.id)
  );
  const firma = JSON.stringify(lista);

  if (firma === firmaAvisos) return;

  firmaAvisos = firma;

  const avisos = lista.length
    ? lista.map(n => {
      const item = elemento(
        "li",
        n.leida ? "" : "nueva",
        n.mensaje
      );

      if (n.fecha) {
        const valor = String(n.fecha);
        const normalizado =
          valor.replace(" ", "T") +
          (/[zZ]$|[+-]\d{2}:\d{2}$/.test(valor) ? "" : "Z");

        const fecha = new Date(normalizado);

        if (!Number.isNaN(fecha.getTime())) {
          item.append(
            elemento(
              "small",
              "suave",
              " · " + fecha.toLocaleString("es-CR")
            )
          );
        }
      }

      return item;
    })
    : [
      elemento("li", "suave", "Sin avisos por ahora.")
    ];

  $("avisos").replaceChildren(...avisos);
}

// ==========================================
// PANEL DE USUARIO
// ==========================================

function pintarCuenta() {
  const entro = cuenta !== null;

  $("nav-cuenta").textContent =
    entro ? "Mi cuenta" : "Ingresar";

  $("nav-estado").textContent =
    entro ? "Máquinas y listas" : "Ver disponibilidad";

  $("introduccion-acceso").hidden = entro;
  $("auth").hidden = entro;
  $("panel").hidden = !entro;

  $("titulo-estado").textContent =
    entro
      ? "Estado y listas de espera"
      : "Disponibilidad actual";

  $("nota-estado").textContent =
    entro
      ? "Consultá los turnos y el estado actualizado de las máquinas."
      : "Consultá si las máquinas están disponibles. Para ver nombres y pedir turnos, iniciá sesión.";

  $("abrir-acceso").hidden = entro;

  const sinLeer = entro
    ? (cuenta.notificaciones || []).filter(
        n => !n.leida && !avisosOcultos.has(n.id)
      ).length
    : 0;

  $("insignia").hidden = !sinLeer;

  if (!entro) return;

  $("insignia").textContent = sinLeer;

  $("saludo").textContent =
    "Hola, " + cuenta.usuario.nombre;

  pintarTurnos();
  pintarAvisos();
}

// ==========================================
// CONSULTAR DATOS DE FASTAPI
// ==========================================

async function refrescar(forzarSesion = false) {
  if (refrescando) {
    otroRefresco = true;
    return;
  }

  refrescando = true;
  ultimoRefresco = Date.now();

  try {
    const consultarSesion =
      forzarSesion ||
      !sesionConsultada ||
      cuenta !== null;

    const [respuestaEstado, respuestaYo] =
      await Promise.allSettled([
        api("/estado"),

        consultarSesion
          ? api("/yo")
          : Promise.resolve(null)
      ]);

    if (
      respuestaYo.status === "fulfilled" &&
      respuestaYo.value
    ) {
      cuenta = respuestaYo.value;
      sesionConsultada = true;

    } else if (
      respuestaYo.status === "rejected" &&
      respuestaYo.reason.status === 401
    ) {
      cuenta = null;
      sesionConsultada = true;

      firmaTurnos = "";
      firmaAvisos = "";
    }

    if (respuestaEstado.status === "fulfilled") {
      maquinas = respuestaEstado.value.maquinas || [];

      pintarMaquinas();

    } else {
      $("actualizado").textContent =
        "No se pudo conectar con FastAPI.";
    }

    pintarCuenta();

  } finally {
    refrescando = false;

    if (otroRefresco) {
      otroRefresco = false;
      void refrescar();
    }
  }
}

// ==========================================
// BOTONES DE NAVEGACIÓN
// ==========================================

document.querySelectorAll(".nav").forEach(b => {
  b.addEventListener("click", () => vista(b.dataset.vista));
});

$("vista-previa").addEventListener("click", () => vista("estado"));

$("abrir-acceso").addEventListener("click", () => vista("cuenta"));

// ==========================================
// PESTAÑAS INGRESAR / CREAR CUENTA
// ==========================================

document.querySelectorAll(".pestana").forEach(b => {
  b.addEventListener("click", () => {
    document.querySelectorAll(".pestana").forEach(x => {
      x.classList.toggle("activo", x === b);
    });

    $("form-login").hidden = b.dataset.form !== "login";
    $("form-registro").hidden = b.dataset.form !== "registro";

    mensaje("msg-auth", "");
  });
});

// ==========================================
// FORMULARIOS
// ==========================================

function conectarFormulario(id, ruta, mensajeId) {
  const form = $(id);

  form.addEventListener("submit", async e => {
    e.preventDefault();

    const boton = form.querySelector('button[type="submit"]');

    if (boton.disabled) return;

    const textoBoton = boton.textContent;
    boton.disabled = true;
    boton.textContent = "Cargando…";
    boton.classList.add("esperando");
    cargando(1);
    mensaje(mensajeId, "");

    const datos = Object.fromEntries(new FormData(form));

    if (ruta === "/solicitudes") {
      datos.maquina_id = Number(datos.maquina_id);
      datos.tandas = Number(datos.tandas);
    }

    try {
      await api(ruta, "POST", datos);

      if (
        ruta === "/auth/login" ||
        ruta === "/auth/registro"
      ) {
        sesionConsultada = false;
        firmaMaquinas = "";
      }

      form.reset();

      await refrescar(true);

      if (
        ruta === "/auth/login" ||
        ruta === "/auth/registro"
      ) {
        vista("estado");

      } else {
        mensaje(mensajeId, "Turno registrado correctamente.", true);
      }

    } catch (err) {
      mensaje(mensajeId, err.message);

    } finally {
      boton.disabled = false;
      boton.textContent = textoBoton;
      boton.classList.remove("esperando");
      cargando(-1);
    }
  });
}

conectarFormulario("form-login", "/auth/login", "msg-auth");
conectarFormulario("form-registro", "/auth/registro", "msg-auth");
conectarFormulario("form-turno", "/solicitudes", "msg-turno");

// ==========================================
// CERRAR SESIÓN
// ==========================================

$("salir").addEventListener("click", async () => {
  try {
    await api("/auth/logout", "POST");

    cuenta = null;
    avisosOcultos.clear();
    sesionConsultada = true;

    firmaMaquinas = "";
    firmaTurnos = "";
    firmaAvisos = "";

    maquinas = [];

    $("maquinas").replaceChildren(
      elemento("p", "suave", "Cargando disponibilidad…")
    );

    pintarCuenta();
    vista("cuenta");

    await refrescar();

  } catch (err) {
    mensaje("msg-turno", err.message);
  }
});

// ==========================================
// MARCAR NOTIFICACIONES COMO LEÍDAS
// ==========================================

$("leer").addEventListener("click", async () => {
  // Quitar de la pantalla YA, sin esperar al servidor.
  if (cuenta) {
    (cuenta.notificaciones || []).forEach(n => avisosOcultos.add(n.id));
    firmaAvisos = "";
    pintarCuenta();
  }

  try {
    await api("/notificaciones/leidas", "POST");

    await refrescar();

  } catch (err) {
    // Si falló, volver a mostrarlos.
    avisosOcultos.clear();
    firmaAvisos = "";
    mensaje("msg-turno", err.message);
    await refrescar();
  }
});

// ==========================================
// WEBSOCKET - ACTUALIZACIONES INMEDIATAS
// ==========================================

// El WebSocket solo avisa cuando algo cambia.
// Después, la página consulta FastAPI con la sesión
// del usuario. No se envían PIN ni contraseñas.

function conectarWebSocket() {
  const protocolo =
    location.protocol === "https:" ? "wss:" : "ws:";

  socket = new WebSocket(
    `${protocolo}//${location.host}/ws/estado`
  );

  socket.onopen = () => {
    intentosSocket = 0;
    socketAbierto = true;      // NUEVO
    void refrescar();
  };

  socket.onmessage = e => {
    try {
      const evento = JSON.parse(e.data);

      if (evento.tipo === "actualizar") {
        void refrescar();
      }

    } catch (_) {
      // Ignorar eventos inválidos.
    }
  };

  socket.onerror = () => {
    socket.close();
  };

  socket.onclose = () => {
    socketAbierto = false;     // NUEVO
    intentosSocket = Math.min(intentosSocket + 1, 5);

    const espera = Math.min(30000, 1000 * 2 ** intentosSocket);

    setTimeout(conectarWebSocket, espera);
  };
}

// ==========================================
// INICIO DEL SISTEMA
// ==========================================

// Esperar la comprobación de la sesión antes de mostrar la interfaz.
void refrescar(true).then(() => {
  vista("cuenta");
});

// Escuchar cambios del backend.
conectarWebSocket();

// Respaldo por si se pierde un evento o el WebSocket no conecta:
// con WebSocket activo consulta cada 15 s; sin él, cada 3 s.
setInterval(() => {
  if (document.hidden) return;

  const cada = socketAbierto ? 15000 : 3000;

  if (Date.now() - ultimoRefresco >= cada) {
    void refrescar();
  }
}, 1000);

// Al regresar a la pestaña, actualizar.
document.addEventListener("visibilitychange", () => {
  if (!document.hidden) {
    void refrescar();
  }
});