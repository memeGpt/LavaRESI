// =====================================================================
//  LavaRESI — Carcasa paramétrica tipo lavadora
//  OpenSCAD 2021.01+   (unidades: mm)


/* [Qué mostrar] */
// ensamble | cuerpo | modulo_superior | pancita_ir | tapa_trasera | puerta | bisagra | pasador | pestillo | bandeja_uno | puente
// plantilla_lcd | plantilla_joystick | plantilla_superior | todo_impresion
PARTE = "ensamble";
// Mostrar componentes (maquetas) en el ensamble
VER_COMPONENTES = true;
// Hacer transparente la carcasa en el ensamble
CARCASA_TRANSPARENTE = true;
// Separar las piezas en el ensamble (vista explosionada, mm)
EXPLOSION = 0;

$fn = 48;
e = 0.01;

// ---------------------------------------------------------------------
//  HOLGURAS DE IMPRESIÓN
// ---------------------------------------------------------------------
tol      = 0.30;   // holgura por lado en ventanas/encajes (PLA típico 0.2–0.35)
pilot_d  = 2.8;    // agujero guía para tornillo M3 (calibrado con la plantilla: 2.8)
screw_d  = 3.4;    // agujero pasante para M3
stand_d  = 5.5;    // diámetro exterior de los postes (standoffs)

// ---------------------------------------------------------------------
//  CARCASA
// ---------------------------------------------------------------------
W   = 160;   // ancho
H   = 240;   // alto
D   = 80;    // fondo
wall = 2.5;  // paredes laterales / superior / inferior
pf   = 3.0;  // espesor del panel frontal
tb   = 2.5;  // espesor de la tapa trasera
r_ext = 6;   // radio de las esquinas (aristas paralelas al fondo)

// ---------------------------------------------------------------------
//  MEDIDAS DE LOS COMPONENTES  
// ---------------------------------------------------------------------
// --- LCD 1602 + adaptador I2C (PCF8574) ---
lcd_pcb      = [80.0, 36.0];  // placa verde: ancho x alto
lcd_pcb_t    = 1.6;
lcd_hole_d   = 3.5;           // agujeros de las esquinas
lcd_hole_sp  = [75.0, 31.0];  // distancia ENTRE CENTROS de agujeros (ancho, alto)
lcd_bezel    = [71.2, 24.2];  // marco negro del vidrio: ancho x alto
lcd_bezel_off= [0, 0];        // desplazamiento del centro del marco vs centro de la placa
lcd_bezel_h  = 7.0;           // altura del marco negro sobre la placa verde
lcd_protrude = 0.0;           // cuánto sobresale el marco del frente (0 = a ras)
lcd_back_h   = 13.0;          // altura del adaptador I2C por detrás (solo maqueta)

// --- Joystick KY-023 ---
jx_pcb       = [26.0, 34.0];  // ancho (lado del conector) x alto
jx_pcb_t     = 1.6;
jx_hole_d    = 3.2;
jx_hole_sp   = [20.0, 27.0];  // distancia ENTRE CENTROS de agujeros (ancho, alto)
jx_hole_off  = [0, 0];        // desplazamiento del patrón de agujeros vs centro placa
jx_stick_off = [0, 1.5];      // centro de la palanca vs centro placa (+ = lejos del conector)
jx_frame_h   = 12.0;          // de la cara de la placa al BORDE del domo negro en reposo (medido: 12)
                              //   = altura de los postes; el panel queda justo a esa altura
jx_dome_d    = 28.0;          // diámetro del domo negro (el que se mueve) — medido
jx_open_d    = jx_dome_d + 3; // agujero del panel: el domo sale por él y gira libre
jx_cap_d     = 20.0;          // tapa de goma de arriba (solo maqueta)
jx_post_h    = 3.0;           // postes del soporte trasero (espacio para las soldaduras de atrás)
jx_sop_t     = 2.5;           // espesor del soporte trasero

// --- Módulos pequeños KY-016 (RGB) y KY-022 (IR) ---
rgb_pcb      = [14.0, 16.0];  // plaquita RGB: ancho x largo (medido)
ir_pcb       = [15.5, 19.0];  // plaquita IR:  ancho x largo (medido)
ky_pcb_t     = 1.6;
// RGB
rgb_led_d    = 5.0;           // LED de 5 mm
rgb_led_flange = 5.8;         // pestaña de la base del LED (hace de tope)
rgb_led_from_edge = 5.0;      // centro del LED al borde superior de la placa (medido)
rgb_gap      = 7.0;           // cara de la placa → parte alta de la pestaña del LED
// IR
ir_body      = [6.0, 9.0];    // silueta del receptor vista desde arriba (medido)
ir_win       = ir_body + [1.0, 1.0];   // ventana = silueta + holgura → 7.0 × 10.0 (calibrado con la plantilla)
ir_from_edge = 6.0;           // centro del receptor al borde superior de la placa (medido)
ir_gap       = 2.0;           // cara de la placa → techo. Receptor 7 mm − 2 − techo 2 = asoma 3 mm
ir_rec_h     = 7.0;           // altura del receptor sobre la placa (medido)
ir_conn_h    = 4.0;           // altura del conector de cables sobre la placa (medido)
// "Pancita": el techo se abre sobre el conector y se cubre con una tapa hueca (pieza aparte)
ir_conn_v    = [7, 31];       // abertura en el techo (desde el centro del receptor hacia los pines)
ir_conn_w    = 13;            // ancho de la abertura
pz_h         = 5;             // cuánto sobresale la pancita sobre el techo
pz_wall      = 1.2;           // pared de la pancita
pz_fit       = 0.15;          // holgura del encaje (a presión; gota de pegamento si queda floja)
pz_lip       = 1.5;           // ceja que apoya sobre el techo alrededor de la abertura


// ---------------------------------------------------------------------
//  DISTRIBUCIÓN (posiciones en el frente, vistas desde adelante)
// ---------------------------------------------------------------------
lcd_c   = [64, 200];   // centro de la placa LCD (x, z)
jx_c    = [132, 200];  // centro de la PALANCA (x, z)
door_c  = [80, 78];    // centro de la puerta
door_d  = 60;
door_t  = 6;           // espesor de la puerta
door_win_d = 40;       // ventana en el frente de la caja
door_glass_d = 34;     // "vidrio" decorativo de la puerta       // ventana en el frente: al abrir la puerta se ve el interior
hinge_x = door_c[0] - door_d/2 - 3.5;   // eje de la bisagra (lado izquierdo)
hinge_y = -door_t/2;                    // eje delante del frente
hinge_k = 6;           // diámetro de los nudillos
hinge_pin = 2.1;       // agujero del pasador (filamento 1.75 mm o clip enderezado)
hinge_h = 30;          // alto total de la bisagra
pin_d   = 1.75;        // pasador: pedazo de filamento de 1.75 mm
pin_len = hinge_h + 2; // sobresale 1 mm arriba y abajo
// Pestillo de gancho (tipo microondas), en la manija, a la derecha
// agarradera hundida en la cara de la puerta, entre el vidrio y el borde
grip_u  = [18.5, 22.5]; // ancho de la ranura en la cara (desde el centro)
grip_under = 2;         // cuánto se mete por dentro hacia el borde (para enganchar el dedo)
grip_h  = 22;           // alto de la ranura
grip_d  = 4;            // profundidad (deja 2 mm de fondo)
lt_ua   = 27.5;          // cara exterior del brazo (u local de la puerta)
lt_t    = 1.4;         // espesor del brazo (lo que flexiona)
lt_w    = 5;           // ancho del gancho
lt_L    = 11;          // largo del brazo detrás de la puerta
lt_barb = 0.8;         // cuánto sobresale el diente
lt_in   = 1.2;         // rampa de entrada
lt_sock = 3;           // profundidad del encaje en la puerta
lt_ys   = lt_L - lt_in - lt_barb - 0.1;   // fondo del tope dentro de la caja (desde el frente)
logo_z  = 148;
LOGO    = "LavaRESI";

// Módulo superior (sección elevada)
TMW = 132; TMD = 48; TMH = 18;  // exterior
tt  = 2.0;                      // espesor del techo (por donde salen LEDs)
tm_y = D/2;                     // centro en Y sobre el cuerpo
tm_pitch = 36;                  // separación RGB1 – IR – RGB2
ky_hole_v = -12;                // posición (fondo) del LED/IR respecto al centro del módulo
boss_off = max(rgb_pcb[0], ir_pcb[0])/2 + 6;     // postes del puente a cada lado de la placa
tm_screw_u = TMW/2 - wall - 4;  // tornillos que unen el módulo al cuerpo

// Tapa trasera
cable_win = [45, 30];           // abertura para cables (ancho x alto)
cable_z   = 15;                 // borde inferior de la abertura
proto     = [55, 165];          // UN protoboard 830 puntos (63 columnas, vertical)
proto_n   = 2;                  // cuántos protoboards unidos lado a lado
// Bloque completo MEDIDO (2 protoboards unidos, una tira +/- compartida en el medio)
proto_blk = [100, 165];
proto_pos = [W/2 - proto_blk[0]/2, 55];                 // esquina inferior izquierda (x, z)
// Arduino UNO: va en la cara INTERNA del panel frontal, debajo del logo,
// con el USB y el jack hacia abajo (el cable baja y sale por la abertura trasera)
// Arduino UNO: en una BANDEJA que se desliza por rieles en la pared DERECHA,
// con el USB y el jack hacia abajo
tray_t    = 2.5;                // espesor de la bandeja
tray_zb   = 40;                 // borde inferior de la bandeja
tray_h    = 75;                 // alto de la bandeja
tray_y0   = pf + 0.2;           // la bandeja apoya en el frente...
tray_len  = D - tb - 0.5 - tray_y0;   // ...y la tapa trasera la trabaja atrás
uno_pos   = [12, tray_zb + 3];  // [y del borde, z del borde con USB] sobre la bandeja
uno_stand = 6;

// =====================================================================
//  UTILIDADES
// =====================================================================
// Pasa coordenadas del panel frontal (u = x, v = z, w = hacia adentro) al cuerpo
module FRONT() multmatrix([[1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]]) children();

module rbox(s, r) {               // caja con aristas verticales redondeadas
    hull() for (x=[r, s[0]-r], y=[r, s[1]-r]) translate([x,y,0]) cylinder(r=r, h=s[2]);
}
module standoff(h, d=stand_d, hole=pilot_d) {
    difference() {
        cylinder(d=d, h=h);
        translate([0,0,-e]) cylinder(d=hole, h=h+2*e);
    }
}
module label(t, s=3) linear_extrude(0.6+e) text(t, size=s, font="Liberation Sans:style=Bold", halign="center", valign="center");

function lcd_holes() = [for (i=[-1,1], j=[-1,1]) [i*lcd_hole_sp[0]/2, j*lcd_hole_sp[1]/2]];
function jx_holes()  = [for (i=[-1,1], j=[-1,1]) [jx_hole_off[0]+i*jx_hole_sp[0]/2, jx_hole_off[1]+j*jx_hole_sp[1]/2]];

// =====================================================================
//  FUNCIONES DEL PANEL (coordenadas locales: placa en w = 0..t, w crece hacia adentro)
//  Todo centrado en el centro de la placa del componente.
// =====================================================================
lcd_stand_h = lcd_bezel_h - pf - lcd_protrude;

module lcd_cut(t) {
    translate([lcd_bezel_off[0], lcd_bezel_off[1], -1])
        translate([-(lcd_bezel[0]+2*tol)/2, -(lcd_bezel[1]+2*tol)/2, 0])
            cube([lcd_bezel[0]+2*tol, lcd_bezel[1]+2*tol, t+2]);
}
module lcd_add(t) {
    for (p = lcd_holes()) translate([p[0], p[1], t-e]) standoff(lcd_stand_h+e);
}
module lcd_pilots(t) {   // el agujero sigue 2 mm dentro del panel (no sale por el frente)
    for (p = lcd_holes()) translate([p[0], p[1], t-2]) cylinder(d=pilot_d, h=2+e);
}

jx_pcb_c = -jx_stick_off;   // centro de placa respecto a la palanca
module jx_cut(t) {
    translate([0,0,-1]) cylinder(d=jx_open_d, h=t+2);
    translate([0,0,-e]) cylinder(d1=jx_open_d+3, d2=jx_open_d, h=1.5);   // chaflán frontal
}
// ---- Montaje del joystick ----------------------------------------------
// El domo barre casi hasta los agujeros de la placa, así que NO hay postes
// entre la placa y el panel cerca del domo. En su lugar:
//   * un SOPORTE impreso por detrás de la placa, con 4 postes cortos a los
//     agujeros (tornillos M3 entran por delante, la cabeza queda abajo del domo);
//   * 4 COLUMNAS en el panel, fuera de la zona del domo (arriba y abajo de la
//     placa), donde se atornilla ese soporte.
jx_sweep_r = sqrt(pow(jx_dome_d/2,2)+16);         // radio que barre el borde del domo
jx_col_d   = 6;
jx_col_h   = jx_frame_h + jx_pcb_t + jx_post_h;   // panel → cara del soporte
jx_cols    = [for (sx=[-1,1], sy=[-1,1]) [jx_pcb_c[0] + sx*(jx_pcb[0]/2 - 2.5), jx_pcb_c[1] + sy*(jx_pcb[1]/2 + 3.5)]];
for (c = jx_cols) let(d = norm(c) - jx_col_d/2)
    if (d < jx_sweep_r + 0.5) echo(str("AVISO joystick: una columna queda a ", d, " mm del eje y el domo barre ", jx_sweep_r));
module jx_add(t) {
    for (c = jx_cols) translate([c[0], c[1], t-e]) standoff(jx_col_h+e, d=jx_col_d);
}
// Soporte trasero (coordenadas de impresión: placa en z=0, postes hacia arriba).
// Origen = centro de la palanca, igual que en el panel.
module soporte_joystick() {
    W2 = jx_pcb[0]/2 + 0.5; H2 = jx_pcb[1]/2 + 3.5 + jx_col_d/2;
    difference() {
        translate([jx_pcb_c[0]-W2, jx_pcb_c[1]-H2, 0]) cube([2*W2, 2*H2, jx_sop_t]);
        // ventana central (soldaduras de potenciómetros y botón)
        translate([jx_pcb_c[0]-(jx_hole_sp[0]/2-3.5), jx_pcb_c[1]-(jx_hole_sp[1]/2-3.5), -1])
            cube([jx_hole_sp[0]-7, jx_hole_sp[1]-7, jx_sop_t+2]);
        // muesca para el conector de pines (lado de abajo)
        translate([jx_pcb_c[0]-7.5, jx_pcb_c[1]-H2-1, -1]) cube([15, H2-jx_pcb[1]/2+3, jx_sop_t+2]);
        // agujeros a las columnas
        for (c = jx_cols) translate([c[0], c[1], -1]) cylinder(d=screw_d, h=jx_sop_t+2);
        // agujero guía de la placa atraviesa también la base (más rosca para el M3x6)
        for (p = jx_holes()) translate([jx_pcb_c[0]+p[0], jx_pcb_c[1]+p[1], -1]) cylinder(d=pilot_d, h=jx_sop_t+2);
    }
    for (p = jx_holes()) translate([jx_pcb_c[0]+p[0], jx_pcb_c[1]+p[1], jx_sop_t-e]) standoff(jx_post_h+e, d=5.5);
}

// =====================================================================
//  CELDA DE MÓDULO PEQUEÑO (RGB o IR) — en coordenadas del techo del
//  módulo superior: techo en w = 0..tt, todo crece hacia w+ (hacia abajo
//  en el ensamble). Origen = centro del LED / receptor.
//  La placa queda con su borde superior hacia v-, conector hacia v+.
// =====================================================================
function ky_from_edge(ir) = ir ? ir_from_edge : rgb_led_from_edge;
function ky_gap(ir)       = ir ? ir_gap : rgb_gap;
function ky_size(ir)      = ir ? ir_pcb : rgb_pcb;
function ky_pcb_v0(ir)    = -ky_from_edge(ir);                 // borde superior de la placa
function ky_bridge_v(ir)  = ky_pcb_v0(ir) + ky_size(ir)[1]/2;       // puente a media placa

module ky_cut(ir) {
    if (ir) {
        translate([-(ir_win[0])/2, -(ir_win[1])/2, -1]) cube([ir_win[0], ir_win[1], tt+2]);
        // abertura sobre el conector (la cubre la pancita)
        translate([-ir_conn_w/2, ir_conn_v[0], -1]) cube([ir_conn_w, ir_conn_v[1]-ir_conn_v[0], tt+2]);
    }
    else    translate([0,0,-1]) cylinder(d=rgb_led_d+0.2, h=tt+2);
}
module ky_add(ir) {
    g  = ky_gap(ir);
    gw = 1.2;                                   // espesor de las guías
    cw = ky_size(ir)[0] + 2*tol;
    v0 = ky_pcb_v0(ir) - tol;
    gl = 12;                                    // largo de las guías
    gh = g + ky_pcb_t*0.6;                      // altura de las guías
    // guías laterales y tope delantero (ubican la placa)
    for (s=[-1,1]) translate([s>0 ? cw/2 : -cw/2-gw, v0, tt-e]) cube([gw, gl, gh]);
    translate([-cw/2-gw, v0-gw, tt-e]) cube([cw+2*gw, gw, gh]);
    // postes del puente
    for (s=[-1,1]) translate([s*boss_off, ky_bridge_v(ir), tt-e])
        standoff(g + ky_pcb_t + e, d=7);
}
module ky_cell(ir) { difference() { union() children(); ky_cut(ir); } ky_add(ir); }

// Pancita del IR (coordenadas del techo, origen = centro del receptor)
module rrect(w, l, r, h) { hull() for (x=[-w/2+r, w/2-r], y=[0+r, l-r]) translate([x,y,0]) cylinder(r=r, h=h); }
module pancita() {
    L  = ir_conn_v[1]-ir_conn_v[0];
    pw = ir_conn_w - 2*pz_fit;  pl = L - 2*pz_fit;                 // tapón que entra en la abertura
    bw = ir_conn_w + 2*pz_lip;  bl = L + 2*pz_lip;                 // base que apoya sobre el techo
    translate([0, ir_conn_v[0], 0]) difference() {
        union() {
            translate([0, pz_fit, 0]) rrect(pw, pl, 1, tt);                          // tapón (w 0..tt)
            translate([0, -pz_lip, 0]) mirror([0,0,1]) hull() {                      // cúpula (w 0..-pz_h)
                rrect(bw, bl, 3, e);
                translate([0, 2, pz_h-e]) rrect(bw-4, bl-4, 2, e);
            }
        }
        // hueco interior
        translate([0, pz_fit+pz_wall, -pz_h+pz_wall]) rrect(pw-2*pz_wall, pl-2*pz_wall, 0.5, pz_h-pz_wall+tt+1);
    }
}

// =====================================================================
//  PIEZA: PUENTE (sujetador de las plaquitas RGB/IR) — imprimir 3
// =====================================================================
br_t = 3; br_w = 7; pad_h = 0.6;
module puente() {
    L = 2*boss_off + 8;
    difference() {
        union() {
            translate([-L/2, -br_w/2, 0]) cube([L, br_w, br_t]);
            // dos almohadillas que presionan el borde de la placa (evitan soldaduras)
            for (s=[-1,1]) translate([s*(min(rgb_pcb[0], ir_pcb[0])/2-1.5)-1, -br_w/2, br_t-e]) cube([2, br_w, pad_h]);
        }
        for (s=[-1,1]) translate([s*boss_off, 0, -1]) cylinder(d=screw_d, h=br_t+2);
    }
}

// =====================================================================
//  PIEZA: CUERPO
// =====================================================================
module body_shell() {
    difference() {
        // exterior: aristas redondeadas paralelas a Y
        translate([0, D, 0]) rotate([90,0,0]) rbox([W, H, D], r_ext);
        // interior abierto atrás
        translate([wall, pf, wall]) cube([W-2*wall, D, H-2*wall]);
    }
}
col = 8;   // columnas de las esquinas traseras
function col_pos() = [for (x=[wall, W-wall-col], z=[wall, H-wall-col]) [x, z]];

module cuerpo() {
    difference() {
        union() {
            body_shell();
            // columnas para la tapa trasera
            for (p = col_pos()) translate([p[0], pf-e, p[1]]) cube([col, D-tb-pf+e, col]);
            // tope del pestillo (bloque detrás del frente, el gancho se traba en su cara del fondo)
            FRONT() translate([door_c[0]+lt_ua-lt_t-1.7-1.5, door_c[1]-lt_w/2-0.3-2.5, pf-e])
                cube([3.5+1.5+2.5, lt_w+0.6+5, lt_ys-pf+e]);
            // postes para la bisagra
            FRONT() for (dz=[-12, 12]) translate([hinge_x-7, door_c[1]+dz, pf-e]) cylinder(d=7, h=5);
            // rieles de la bandeja del UNO (pared derecha)
            uno_rails();
            // patas
            for (x=[14, W-26], y=[10, D-20]) translate([x, y, -3]) cube([12, 10, 3+e]);
        }
        // ventanas del frente
        FRONT() translate([lcd_c[0], lcd_c[1], 0]) lcd_cut(pf);
        FRONT() translate([lcd_c[0], lcd_c[1], 0]) lcd_pilots(pf);
        FRONT() translate([jx_c[0], jx_c[1], 0])   jx_cut(pf);
        // ventana para ver el interior
        FRONT() translate([door_c[0], door_c[1], -1]) cylinder(d=door_win_d, h=pf+2);
        // ranura del pestillo
        FRONT() translate([door_c[0]+lt_ua-lt_t-1.7, door_c[1]-lt_w/2-0.3, -1]) cube([3.5, lt_w+0.6, lt_ys+2]);
        // agujeros guía de la bisagra
        FRONT() for (dz=[-12, 12]) translate([hinge_x-7, door_c[1]+dz, -1]) cylinder(d=pilot_d, h=pf+6);
        // logo grabado
        translate([W/2, 0.8, logo_z]) rotate([90,0,0])
            linear_extrude(1.8) text(LOGO, size=16, font="Liberation Sans:style=Bold", halign="center", valign="center");
        // aro grabado alrededor de la puerta (decorativo)
        FRONT() translate([door_c[0], door_c[1], -1]) difference() {
            cylinder(d=door_d+8, h=1.6); translate([0,0,-1]) cylinder(d=door_d+5, h=4);
        }
        // agujeros guía en las columnas
        for (p = col_pos()) translate([p[0]+col/2, D-tb-12, p[1]+col/2]) rotate([-90,0,0]) cylinder(d=pilot_d, h=13);
        // ventanas en el techo (una por módulo) para pasar cables
        for (i=[-1,0,1]) translate([W/2 + i*tm_pitch - 14, tm_y - 19, H-wall-1]) cube([28, 38, wall+2]);
        // tornillos del módulo superior
        for (s=[-1,1]) translate([W/2 + s*tm_screw_u, tm_y, H-wall-1]) cylinder(d=screw_d, h=wall+2);
    }
    // postes del LCD y joystick (por dentro)
    FRONT() translate([lcd_c[0], lcd_c[1], 0]) lcd_add(pf);
    FRONT() translate([jx_c[0], jx_c[1], 0])   jx_add(pf);
}
// rieles en "L" para la bandeja del UNO, a lo largo del fondo (se imprimen verticales)
module uno_rails() {
    sl = tray_t + 0.4;                       // ranura
    for (bot=[true,false]) {
        ze = bot ? tray_zb - 0.2 : tray_zb + tray_h + 0.2;   // borde de la ranura
        sg = bot ? -1 : 1;
        translate([0, pf-e, 0]) {
            // apoyo
            translate([X0-sl-1.6, 0, bot ? ze-2.5 : ze]) cube([sl+1.6+e, tray_y0+tray_len+0.3-pf, 2.5]);
            // pestaña
            translate([X0-sl-1.6, 0, bot ? ze-e : ze-2]) cube([1.6, tray_y0+tray_len+0.3-pf, 2+e]);
        }
    }
}

// =====================================================================
//  PIEZA: MÓDULO SUPERIOR (sección elevada) — coordenadas de impresión:
//  techo sobre la cama (w = 0), paredes hacia arriba.
// =====================================================================
module modulo_superior() {
    difference() {
        translate([-TMW/2, -TMD/2, 0]) rbox([TMW, TMD, TMH], 3);
        translate([-TMW/2+wall, -TMD/2+wall, tt]) cube([TMW-2*wall, TMD-2*wall, TMH]);
        // agujeros LED / IR
        for (i=[-1,0,1]) translate([i*tm_pitch, ky_hole_v, 0]) ky_cut(i==0);
        // etiquetas grabadas encima
        for (i=[-1,0,1]) translate([i*tm_pitch, ky_hole_v-8.5, -e]) mirror([1,0,0])
            linear_extrude(0.5) text(i==0 ? "IR" : (i<0 ? "1" : "2"), size=4, font="Liberation Sans:style=Bold", halign="center", valign="center");
    }
    // celdas
    for (i=[-1,0,1]) translate([i*tm_pitch, ky_hole_v, 0]) ky_add(i==0);
    // bloques para tornillos de unión con el cuerpo
    for (s=[-1,1]) translate([s*tm_screw_u, 0, 0]) difference() {
        translate([-4, -6, tt-e]) cube([8, 12, TMH-tt+e]);
        translate([0, 0, TMH-12]) cylinder(d=pilot_d, h=13);
    }
}
// coloca el módulo en el ensamble (techo arriba)
module place_tm() translate([W/2, tm_y, H+TMH+EXPLOSION]) mirror([0,0,1]) children();

// =====================================================================
//  PIEZA: TAPA TRASERA — coordenadas de impresión: cara exterior en la cama
//  (u = x del cuerpo, v = z del cuerpo, w = hacia adentro)
// =====================================================================
uno_holes = [[13.97, 2.54], [15.24, 50.8], [66.04, 7.62], [66.04, 35.56]];
uno_size  = [68.58, 53.34];
// UNO en el panel frontal, visto desde atrás: borde USB hacia abajo
function uno_xy(p) = [uno_pos[0] + p[1], uno_pos[1] + p[0]];   // [y, z] en la pared derecha
X0 = W - wall;   // cara interna de la pared derecha

module tapa_trasera() {
    cw = W - 2*wall - 2*0.25;
    ch = H - 2*wall - 2*0.25;
    x0 = wall + 0.25; z0 = wall + 0.25;
    difference() {
        translate([x0, z0, 0]) cube([cw, ch, tb]);
        // abertura de cables
        translate([W/2 - cable_win[0]/2, cable_z, -1]) cube([cable_win[0], cable_win[1], tb+2]);
        // tornillos a las columnas (con avellanado por fuera)
        for (p = col_pos()) translate([p[0]+col/2, p[1]+col/2, -1]) {
            cylinder(d=screw_d, h=tb+2);
            cylinder(d1=6.6, d2=screw_d, h=1+1.6);
        }
    }
    // marco guía de los protoboards (esquinas en L, se pegan con su adhesivo)
    for (cx=[0,1], cz=[0,1]) {
        px = proto_pos[0] - 0.5 + cx*(proto_blk[0]+1);
        pz = proto_pos[1] - 0.5 + cz*(proto_blk[1]+1);
        translate([px, pz, tb-e]) scale([cx ? -1 : 1, cz ? -1 : 1, 1])
            translate([-1.2,-1.2,0]) { cube([12, 1.2, 2]); cube([1.2, 12, 2]); }
    }
}
module place_back() translate([0, D+EXPLOSION, 0]) multmatrix([[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]]) children();

// =====================================================================
//  PIEZA: PUERTA DECORATIVA 
// =====================================================================
// Coordenadas locales de la puerta: centro en el origen, cara trasera en z=0,
// frente en z=door_t. Se imprime con la cara trasera sobre la cama.
hz = door_t/2;
module puerta() {
    hu = hinge_x - door_c[0];          // eje de la bisagra (u local)
    difference() {
        union() {
            cylinder(d=door_d, h=door_t);
            translate([hu, -4.4, 0]) cube([-hu - door_d/2 + 3, 8.8, door_t]);      // brazo
            translate([hu, 4.4, hz]) rotate([90,0,0]) cylinder(d=hinge_k, h=8.8);  // nudillo
        }
        translate([0,0,door_t-1.8]) cylinder(d=door_glass_d, h=3);                 // "vidrio"
        // agarradera: ranura hundida con pestaña interior hacia el borde
        hull() {
            translate([grip_u[0], -grip_h/2, door_t-e]) cube([grip_u[1]-grip_u[0], grip_h, 1]);
            translate([grip_u[0], -grip_h/2+1, door_t-grip_d]) cube([grip_u[1]-grip_u[0]+grip_under, grip_h-2, e]);
        }
        translate([lt_ua-lt_t-0.1, -lt_w/2-0.1, -e]) cube([3+0.2, lt_w+0.2, lt_sock+0.1]);   // encaje del pestillo
        translate([hu, 10, hz]) rotate([90,0,0]) cylinder(d=hinge_pin, h=20);      // pasador
    }
    translate([0,0,door_t-1.8-e]) difference() {                                  // reflejo
        cylinder(d=door_glass_d, h=0.6);
        translate([3,3,-1]) cylinder(d=door_glass_d-2, h=3);
    }
}
// Pestillo (coordenadas locales de la puerta). Base dentro del encaje, brazo hacia
// la caja (z negativo) y diente hacia +u, con rampa de entrada y rampa de salida.
module pestillo_perfil() {   // perfil en el plano (u, z)
    polygon([
        [lt_ua-lt_t, lt_sock], [lt_ua-lt_t+3, lt_sock], [lt_ua-lt_t+3, 0], [lt_ua, 0],
        [lt_ua, -(lt_L-lt_in-lt_barb)],
        [lt_ua+lt_barb, -(lt_L-lt_in)],
        [lt_ua+0.15, -lt_L], [lt_ua-lt_t, -lt_L]
    ]);
}
module pestillo() {
    translate([0, lt_w/2, 0]) rotate([90,0,0]) linear_extrude(lt_w) pestillo_perfil();
}
// Hoja fija de la bisagra (se atornilla al frente). Coordenadas del cuerpo.
module bisagra() {
    kz = (hinge_h - 8.8 - 0.8)/2;     // alto de cada nudillo
    difference() {
        union() {
            translate([hinge_x-13, -2, door_c[1]-hinge_h/2]) cube([13, 2, hinge_h]);
            for (z0=[door_c[1]-hinge_h/2, door_c[1]+4.4+0.4])
                translate([hinge_x, hinge_y, z0]) cylinder(d=hinge_k, h=kz);
            translate([hinge_x-2, -2-hinge_k/2+1, door_c[1]-hinge_h/2]) cube([2, hinge_k/2+1, hinge_h]);
        }
        translate([hinge_x, hinge_y, door_c[1]-hinge_h]) cylinder(d=hinge_pin, h=2*hinge_h);
        for (dz=[-12, 12]) translate([hinge_x-7, 1, door_c[1]+dz]) rotate([90,0,0]) {
            cylinder(d=screw_d, h=5); translate([0,0,2.2]) cylinder(d1=screw_d, d2=6.4, h=1.6);
        }
    }
}
// Pasador de la bisagra: pedazo de filamento de 1.75 mm (coordenadas del cuerpo)
module pasador() {
    translate([hinge_x, hinge_y, door_c[1]-pin_len/2]) cylinder(d=pin_d, h=pin_len, $fn=16);
}
// Versión impresa (opcional, si no tienes filamento suelto): con cabeza, impresa acostada
module pasador_impreso() {
    rotate([0,90,0]) translate([0,0,0]) {
        cylinder(d=1.9, h=pin_len, $fn=16);
        translate([0,0,pin_len-1.2]) cylinder(d=3.6, h=1.2, $fn=24);   // cabeza (queda arriba)
    }
}
// Bandeja del UNO (coordenadas de impresión: placa en z=0, postes hacia arriba)
// u = y del cuerpo, v = z del cuerpo
module bandeja_uno() {
    translate([tray_y0, tray_zb, 0]) cube([tray_len, tray_h, tray_t]);
    for (p = uno_holes) translate([uno_xy(p)[0], uno_xy(p)[1], tray_t-e]) standoff(uno_stand+e, d=6);
}
module place_tray() translate([X0, 0, 0]) multmatrix([[0,0,-1,0],[1,0,0,0],[0,1,0,0],[0,0,0,1]]) children();
PUERTA_ABIERTA = 0;   // grados (para ver el ensamble con la puerta abierta)
module place_door() FRONT() translate([door_c[0], door_c[1], -EXPLOSION*0.5]) mirror([0,0,1])
    translate([hinge_x-door_c[0], 0, hz]) rotate([0, -PUERTA_ABIERTA, 0]) translate([-(hinge_x-door_c[0]), 0, -hz]) children();

// =====================================================================
//  PLANTILLAS DE CALCE 
// =====================================================================
module plantilla_lcd() {
    m = 6;
    difference() {
        translate([-lcd_pcb[0]/2-m, -lcd_pcb[1]/2-m, 0]) cube([lcd_pcb[0]+2*m, lcd_pcb[1]+2*m, pf]);
        lcd_cut(pf);
        lcd_pilots(pf);
        translate([0, -lcd_pcb[1]/2-m/2+0.3, pf-0.6]) label("LCD", 3);
    }
    lcd_add(pf);
}
module plantilla_joystick() {
    m = 5;
    sx = max(jx_pcb[0], jx_open_d) + 2*m; sy = jx_pcb[1] + 2*jx_col_d + 14;
    difference() {
        translate([jx_pcb_c[0]-sx/2, jx_pcb_c[1]-sy/2, 0]) cube([sx, sy, pf]);
        jx_cut(pf);
    }
    jx_add(pf);
    translate([45, 0, 0]) soporte_joystick();
}
module plantilla_superior() {
    // fila 1: celda RGB completa + celda IR completa (con su puente se prueba todo)
    // fila 2: escalera de agujeros LED y ventanas IR + postes de tornillo
    difference() {
        translate([-40, -32, 0]) cube([80, 82, tt]);
        translate([-18, 0, 0]) ky_cut(false);
        translate([ 18, 0, 0]) ky_cut(true);
        // escalera LED: 4.9 / 5.1 / 5.3 / 5.5
        for (i=[0:3]) translate([-30 + i*9, 40, -1]) cylinder(d=4.9+0.2*i, h=tt+2);
        for (i=[0:3]) translate([-30 + i*9, 45.5, tt-0.6]) label(str(49+2*i), 2.2);
        // escalera IR: -0.4 / +0.4
        for (i=[0:1]) translate([10 + i*14, 40, -1])
            translate([-(ir_win[0]-0.4+0.8*i)/2, -(ir_win[1]-0.4+0.8*i)/2, 0])
                cube([ir_win[0]-0.4+0.8*i, ir_win[1]-0.4+0.8*i, tt+2]);
        translate([10, 47.2, tt-0.6]) label("-", 3);
        translate([24, 47.2, tt-0.6]) label("+", 3);
        translate([-18, -13, tt-0.6]) label("RGB", 3);
        for (i=[0:2]) translate([-9 + i*9, -21.3, tt-0.6]) label(str(28+i), 2.2);   // 28 / 29 / 30
        translate([ 18, -13, tt-0.6]) label("IR", 3);
    }
    translate([-18, 0, 0]) ky_add(false);
    translate([ 18, 0, 0]) ky_add(true);
    // postes de prueba de tornillo M3: 2.8 / 2.9 / 3.0 (de izquierda a derecha)
    for (i=[0:2]) translate([-9 + i*9, -27, tt-e]) standoff(8, d=6, hole=2.8+0.1*i);
}

// =====================================================================
//  MAQUETAS DE COMPONENTES (solo para visualizar)
// =====================================================================
module m_lcd() {   // en coordenadas del panel, centrado en la placa
    pcb_w = lcd_bezel_h - lcd_protrude;                    // cara delantera de la placa
    color("green") translate([-lcd_pcb[0]/2, -lcd_pcb[1]/2, pcb_w]) difference() {
        cube([lcd_pcb[0], lcd_pcb[1], lcd_pcb_t]);
        for (p = lcd_holes()) translate([p[0]+lcd_pcb[0]/2, p[1]+lcd_pcb[1]/2, -1]) cylinder(d=lcd_hole_d, h=4);
    }
    color([0.1,0.1,0.1]) translate([lcd_bezel_off[0]-lcd_bezel[0]/2, lcd_bezel_off[1]-lcd_bezel[1]/2, pcb_w-lcd_bezel_h]) cube([lcd_bezel[0], lcd_bezel[1], lcd_bezel_h]);
    color([0.2,0.25,0.9]) translate([-32.25, -8.2, pcb_w-lcd_bezel_h-0.05]) cube([64.5, 16.4, 0.1]);
    // adaptador I2C con conector hacia la izquierda (visto de frente)
    color([0.1,0.1,0.1]) translate([-40+2, lcd_pcb[1]/2-21, pcb_w+lcd_pcb_t]) cube([42, 19, lcd_back_h]);
    color([0.15,0.15,0.15]) translate([-40-16, lcd_pcb[1]/2-20, pcb_w+lcd_pcb_t+lcd_back_h-3]) cube([18, 10.5, 2.6]); // dupont
}
module m_joystick() {   // en coordenadas del panel, centrado en la palanca
    pcb_w = pf + jx_frame_h;
    color([0.1,0.1,0.1]) translate([jx_pcb_c[0]-jx_pcb[0]/2, jx_pcb_c[1]-jx_pcb[1]/2, pcb_w]) cube([jx_pcb[0], jx_pcb[1], jx_pcb_t]);
    // base negra con potenciómetros (debajo del domo)
    color([0.12,0.12,0.12]) translate([-10, -10, pf+1]) cube([20, 20, jx_frame_h-1]);
    // domo: casquete esférico con su borde a la altura del panel
    color([0.2,0.2,0.22]) intersection() {
        translate([0,0,pcb_w-8]) sphere(r=sqrt(pow(jx_dome_d/2,2)+16));
        translate([-50,-50,-60]) cube([100,100,60+pf]);
    }
    // vástago y tapa de goma
    color([0.15,0.15,0.15]) translate([0,0,-16]) cylinder(d=9, h=10);
    color([0.3,0.3,0.33]) translate([0,0,-21]) cylinder(d=jx_cap_d, h=5);
    color([0.15,0.15,0.15]) translate([jx_pcb_c[0]-6.5, jx_pcb_c[1]-jx_pcb[1]/2-16, pcb_w-2.6]) cube([13, 16, 2.6]);
    // soporte trasero
    color([0.88,0.55,0.25]) translate([0,0,pf+jx_col_h+jx_sop_t]) mirror([0,0,1]) soporte_joystick();
}
module m_ky(ir) {      // en coordenadas del techo del módulo superior (w hacia abajo)
    g = ky_gap(ir);
    sz = ky_size(ir);
    color([0.1,0.1,0.1]) translate([-sz[0]/2, ky_pcb_v0(ir), tt+g]) cube([sz[0], sz[1], ky_pcb_t]);
    ch = ir ? ir_conn_h : 2.6;   // conector de cables (sube hacia el techo)
    color([0.15,0.15,0.15]) translate([-4.5, ky_pcb_v0(ir)+sz[1]-3, tt+g-ch]) cube([9, 17, ch]);
    if (ir) color("silver") translate([-ir_win[0]/2+0.4, -ir_win[1]/2+0.4, tt+g-ir_rec_h]) cube([ir_win[0]-0.8, ir_win[1]-0.8, ir_rec_h]);   // receptor
    else {
        color([1,1,1,0.85]) translate([0,0,-6]) { cylinder(d=rgb_led_d, h=6+tt+g-1); sphere(d=rgb_led_d); }
        color([1,1,1,0.85]) translate([0,0,tt]) cylinder(d=rgb_led_flange, h=1);
    }
}
module m_back() {      // en coordenadas de la tapa trasera
    color("white") translate([proto_pos[0], proto_pos[1], tb]) cube([proto_blk[0], proto_blk[1], 9.5]);
    color([0.1,0.1,0.1]) translate([W/2-14, proto_pos[1]+proto[1]-58, tb+9.5]) cube([28, 52, 12]); // ESP32 sobre la unión
}
module m_uno() {       // en coordenadas de la bandeja
    color([0.05,0.3,0.6]) translate([uno_pos[0], uno_pos[1], tray_t+uno_stand]) cube([uno_size[1], uno_size[0], 1.6]);
    color([0.6,0.6,0.6]) translate([uno_pos[0]+38-6, uno_pos[1]-6, tray_t+uno_stand+1.6]) cube([12, 16, 11]);   // USB-B
    color([0.1,0.1,0.1]) translate([uno_pos[0]+3, uno_pos[1]-2, tray_t+uno_stand+1.6]) cube([9, 14, 11]);       // jack
}

// =====================================================================
//  ENSAMBLE
// =====================================================================
module carcasa_color(c) { if (CARCASA_TRANSPARENTE) color([c[0],c[1],c[2],0.35]) children(); else color(c) children(); }

module ensamble() {
    carcasa_color([0.93,0.91,0.86]) cuerpo();
    carcasa_color([0.62,0.5,0.9]) place_tm() modulo_superior();
    color([0.62,0.5,0.9]) place_tm() translate([0, ky_hole_v, 0]) pancita();
    carcasa_color([0.85,0.83,0.78]) place_back() tapa_trasera();
    color([0.6,0.45,0.92]) place_door() puerta();
    color([0.95,0.6,0.2]) place_door() pestillo();
    color([0.6,0.45,0.92]) bisagra();
    color([0.95,0.95,0.95]) pasador();
    carcasa_color([0.85,0.83,0.78]) place_tray() bandeja_uno();
    if (VER_COMPONENTES) {
        FRONT() translate([lcd_c[0], lcd_c[1], 0]) m_lcd();
        FRONT() translate([jx_c[0], jx_c[1], 0])   m_joystick();
        place_tm() for (i=[-1,0,1]) translate([i*tm_pitch, ky_hole_v, 0]) { m_ky(i==0);
            color([0.6,0.6,0.6]) translate([0, ky_bridge_v(i==0), tt+ky_gap(i==0)+ky_pcb_t+pad_h+br_t]) mirror([0,0,1]) puente(); }
        place_back() m_back();
        place_tray() m_uno();
    }
}

// =====================================================================
//  SELECTOR
// =====================================================================
if (PARTE == "ensamble")            ensamble();
if (PARTE == "cuerpo")              rotate([90,0,0]) translate([0,0,0]) cuerpo();     // frente sobre la cama
if (PARTE == "modulo_superior")     modulo_superior();
if (PARTE == "tapa_trasera")        tapa_trasera();
if (PARTE == "puerta")              puerta();
if (PARTE == "soporte_joystick") soporte_joystick();
// pancita: se imprime con la parte plana de arriba sobre la cama
if (PARTE == "pancita_ir")  translate([0,0,pz_h]) pancita();
if (PARTE == "asm_pancita") place_tm() translate([0, ky_hole_v, 0]) pancita();
if (PARTE == "puente")              for (i=[0:2]) translate([0, i*10, 0]) puente();
if (PARTE == "plantilla_lcd")       plantilla_lcd();
if (PARTE == "plantilla_joystick")  plantilla_joystick();
if (PARTE == "plantilla_superior")  { plantilla_superior(); translate([0, -42, 0]) for (i=[0:1]) translate([0, -i*10, 0]) puente(); }

// --- piezas sueltas del ensamble (para el visor 3D) ---
if (PARTE == "asm_cuerpo")  cuerpo();
if (PARTE == "asm_tm")      place_tm() modulo_superior();
if (PARTE == "asm_tapa")    place_back() tapa_trasera();
if (PARTE == "asm_puerta")  place_door() puerta();
if (PARTE == "asm_lcd")     FRONT() translate([lcd_c[0], lcd_c[1], 0]) m_lcd();
if (PARTE == "asm_joy")     FRONT() translate([jx_c[0], jx_c[1], 0]) m_joystick();
if (PARTE == "asm_ky")      place_tm() for (i=[-1,0,1]) translate([i*tm_pitch, ky_hole_v, 0]) m_ky(i==0);
if (PARTE == "asm_puentes") place_tm() for (i=[-1,0,1]) translate([i*tm_pitch, ky_hole_v, 0])
                                translate([0, ky_bridge_v(i==0), tt+ky_gap(i==0)+ky_pcb_t+pad_h+br_t]) mirror([0,0,1]) puente();
if (PARTE == "asm_back")    place_back() m_back();
if (PARTE == "asm_uno")     place_tray() m_uno();
if (PARTE == "asm_bisagra") bisagra();
if (PARTE == "asm_pasador") pasador();
// opcional: 2 pasadores impresos (acostados, con cabeza); lo ideal es filamento de 1.75 mm
if (PARTE == "pasador")     intersection() {   // base plana para que la cabeza apoye en la cama
    for (i=[0:1]) translate([0, i*6, 0.95]) pasador_impreso();
    translate([-1, -5, 0]) cube([pin_len+2, 20, 5]);
}
if (PARTE == "asm_pestillo") place_door() pestillo();
// impreso acostado: el brazo flexiona dentro del plano de las capas (más resistente)
if (PARTE == "pestillo")    for (i=[0:1]) translate([0, i*12, 0]) linear_extrude(lt_w) rotate(-90) pestillo_perfil();
if (PARTE == "asm_bandeja") place_tray() bandeja_uno();
if (PARTE == "bisagra")     translate([0,0,-(door_c[1]-hinge_h/2)]) bisagra();       // de pie: nudillos verticales
// (espejada: así, al girarla para meterla en los rieles, los agujeros quedan donde el UNO)
if (PARTE == "bandeja_uno") mirror([1,0,0]) translate([-tray_y0, -tray_zb, 0]) bandeja_uno();
