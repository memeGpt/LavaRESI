// LavaRESI - página web. Todo el texto de usuarios se inserta con textContent (sin innerHTML).
const $ = (s) => document.querySelector(s);
const NOMBRE_ESTADO = { LIBRE: "Libre", EN_USO: "En uso", PENDIENTE_RETIRO: "Retirar ropa", ENTRE_TANDAS: "Entre tandas" };
const NOMBRE_MAQUINA = { LAVADORA: "Lavadora", SECADORA: "Secadora" };

let estado = null;   // /api/estado
let yo = null;       // /api/yo (null si no hay sesión)

function h(tag, props = {}, ...hijos) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k === "class") el.className = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v);
  }
  el.append(...hijos.flat().filter((x) => x !== null && x !== undefined));
  return el;
}

async function api(ruta, metodo = "GET", cuerpo) {
  const r = await fetch("/api" + ruta, {
    method: metodo,
    headers: cuerpo ? { "Content-Type": "application/json" } : {},
    body: cuerpo ? JSON.stringify(cuerpo) : undefined,
  });
  const datos = await r.json().catch(() => ({}));
  if (!r.ok) {
    const d = datos.detail;
    throw new Error(typeof d === "string" ? d : "Revisa los datos ingresados");
  }
  return datos;
}

function mostrarMensaje(el, texto, bien = false) {
  el.textContent = texto;
  el.className = "mensaje" + (bien ? " bien" : "");
}

// ---------------------------------------------------------------- estado público
function mmss(seg) {
  const m = Math.floor(seg / 60), s = seg % 60;
  return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
}

function tarjetaMaquina(m) {
  const detalle = [];
  if (m.estado === "EN_USO" && m.ocupante) {
    detalle.push(h("p", {}, `${m.ocupante.nombre} · tanda ${m.ocupante.tandas_iniciadas}/${m.ocupante.tandas_totales}`));
    if (m.segundos_restantes !== null) {
      detalle.push(h("p", { class: "cuenta", "data-fin": Date.now() + m.segundos_restantes * 1000 }, mmss(m.segundos_restantes)));
    }
  } else if (m.estado === "PENDIENTE_RETIRO" && m.ocupante) {
    detalle.push(h("p", {}, `${m.ocupante.nombre} debe retirar su ropa en la terminal.`));
  } else if (m.estado === "ENTRE_TANDAS" && m.ocupante) {
    detalle.push(h("p", {}, `${m.ocupante.nombre} prepara su siguiente tanda.`));
  } else {
    detalle.push(h("p", { class: "suave" }, "Disponible para el siguiente turno."));
  }

  const espera = m.cola.filter((c) => c.estado !== "EN_USO");
  const cola = h("ul", { class: "cola" }, espera.length
    ? espera.map((c) => h("li", {},
        h("span", {}, `${c.posicion}. ${c.nombre} · ${c.tandas_totales} ${c.tandas_totales === 1 ? "tanda" : "tandas"}`),
        c.estado === "AUTORIZADA" ? h("span", { class: "etiqueta turno" }, "Siguiente")
          : !c.disponible ? h("span", { class: "etiqueta ausente" }, "Ausente") : h("span", { class: "etiqueta" }, "En espera")))
    : [h("li", { class: "suave" }, "Sin personas en espera")]);

  return h("article", { class: "tarjeta" },
    h("div", { class: "fila-entre" },
      h("h3", { style: "margin:0" }, NOMBRE_MAQUINA[m.tipo]),
      h("span", { class: "insignia-estado " + m.estado }, NOMBRE_ESTADO[m.estado])),
    ...detalle, cola);
}

function pintarEstado() {
  $("#maquinas").replaceChildren(...estado.maquinas.map(tarjetaMaquina));
  $("#actualizado").textContent = "Actualizado " + new Date().toLocaleTimeString("es-CR");
}

setInterval(() => {   // cuenta regresiva local entre consultas al servidor
  document.querySelectorAll("[data-fin]").forEach((el) => {
    el.textContent = mmss(Math.max(0, Math.round((el.dataset.fin - Date.now()) / 1000)));
  });
}, 1000);

// ---------------------------------------------------------------- cuenta
function textoSolicitud(s) {
  if (s.estado === "AUTORIZADA") return "¡Es tu turno! Ve a la terminal, ingresa tu PIN e inicia el ciclo.";
  if (s.estado === "EN_USO") return `En uso · tanda ${s.tandas_iniciadas} de ${s.tandas_totales}`;
  return `Puesto ${s.posicion} · ${s.tandas_totales} ${s.tandas_totales === 1 ? "tanda" : "tandas"}`;
}

async function accion(promesa, el) {
  try { await promesa; await refrescar(); }
  catch (e) { mostrarMensaje(el, e.message); }
}

function filaTurno(s) {
  const maquina = estado && estado.maquinas.find((m) => m.id === s.maquina_id);
  const puedeCancelar = s.estado !== "EN_USO" || (maquina && maquina.estado === "ENTRE_TANDAS");
  const esperando = s.estado === "EN_ESPERA" || s.estado === "AUTORIZADA";
  const acciones = [];
  if (esperando) {
    acciones.push(h("button", { class: "secundario",
      onclick: () => accion(api(`/solicitudes/${s.id}/disponibilidad`, "POST", { disponible: !s.disponible }), $("#msg-turno")) },
      s.disponible ? "Marcarme ausente" : "Ya estoy disponible"));
  }
  if (puedeCancelar) {
    acciones.push(h("button", { class: "secundario peligro",
      onclick: () => accion(api(`/solicitudes/${s.id}/cancelar`, "POST"), $("#msg-turno")) },
      s.estado === "EN_USO" ? "Terminar mi turno" : "Cancelar"));
  }
  return h("div", { class: "turno" },
    h("div", {}, h("strong", {}, NOMBRE_MAQUINA[s.maquina]), h("br"),
      h("span", { class: "suave" }, textoSolicitud(s)),
      !s.disponible ? h("span", { class: "etiqueta ausente", style: "margin-left:.5rem" }, "Ausente") : null),
    h("div", { class: "acciones" }, acciones));
}

function pintarCuenta() {
  const logueado = !!yo;
  $("#auth").hidden = logueado;
  $("#panel").hidden = !logueado;
  const insignia = $("#insignia");
  insignia.hidden = !logueado || yo.no_leidas === 0;
  if (!logueado) return;
  insignia.textContent = yo.no_leidas;
  $("#saludo").textContent = "Hola, " + yo.usuario.nombre;
  $("#mis-turnos").replaceChildren(...(yo.solicitudes.length
    ? yo.solicitudes.map(filaTurno)
    : [h("p", { class: "suave" }, "No tienes turnos activos.")]));
  $("#avisos").replaceChildren(...(yo.notificaciones.length
    ? yo.notificaciones.map((n) => h("li", { class: n.leida ? "" : "nueva" }, n.mensaje,
        h("time", {}, new Date(n.fecha.replace(" ", "T") + "Z").toLocaleString("es-CR"))))
    : [h("li", { class: "suave" }, "Sin avisos por ahora.")]));
}

// ---------------------------------------------------------------- refresco
async function refrescar() {
  try { estado = await api("/estado"); pintarEstado(); } catch (e) { $("#actualizado").textContent = "Sin conexión con el servidor"; }
  try { yo = await api("/yo"); } catch (e) { yo = null; }
  pintarCuenta();
  if (estado) pintarEstado();
}
setInterval(refrescar, 5000);

// ---------------------------------------------------------------- eventos
document.querySelectorAll(".nav").forEach((b) => b.addEventListener("click", () => {
  document.querySelectorAll(".nav").forEach((x) => x.classList.toggle("activo", x === b));
  $("#vista-estado").hidden = b.dataset.vista !== "estado";
  $("#vista-cuenta").hidden = b.dataset.vista !== "cuenta";
}));

document.querySelectorAll(".pestana").forEach((b) => b.addEventListener("click", () => {
  document.querySelectorAll(".pestana").forEach((x) => x.classList.toggle("activo", x === b));
  $("#form-login").hidden = b.dataset.form !== "login";
  $("#form-registro").hidden = b.dataset.form !== "registro";
  mostrarMensaje($("#msg-auth"), "");
}));

function enviarForm(form, ruta, msg, alExito) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const datos = Object.fromEntries(new FormData(form));
    for (const k of ["maquina_id", "tandas"]) if (k in datos) datos[k] = Number(datos[k]);
    try { await api(ruta, "POST", datos); form.reset(); mostrarMensaje(msg, ""); await refrescar(); alExito?.(); }
    catch (err) { mostrarMensaje(msg, err.message); }
  });
}
enviarForm($("#form-login"), "/auth/login", $("#msg-auth"));
enviarForm($("#form-registro"), "/auth/registro", $("#msg-auth"));
enviarForm($("#form-turno"), "/solicitudes", $("#msg-turno"), () => mostrarMensaje($("#msg-turno"), "Turno registrado.", true));

$("#salir").addEventListener("click", async () => { await api("/auth/logout", "POST"); yo = null; pintarCuenta(); });
$("#leer").addEventListener("click", () => accion(api("/notificaciones/leidas", "POST"), $("#msg-turno")));

refrescar();