
-- ============================================
-- LAVARESI - BASE DE DATOS SQLITE
-- ============================================

PRAGMA foreign_keys = ON;

-- 1. USUARIOS
-- Estudiantes registrados en el sistema.
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    usuario TEXT NOT NULL UNIQUE,
    pin_hash TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    activo INTEGER NOT NULL DEFAULT 1
        CHECK (activo IN (0, 1)),
    fecha_registro TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. MAQUINAS
-- Una lavadora y una secadora independientes.
CREATE TABLE IF NOT EXISTS maquinas (
    id INTEGER PRIMARY KEY,
    tipo TEXT NOT NULL UNIQUE
        CHECK (tipo IN ('LAVADORA', 'SECADORA')),
    estado TEXT NOT NULL DEFAULT 'LIBRE'
        CHECK (estado IN (
            'LIBRE',
            'EN_USO',
            'PENDIENTE_RETIRO',
            'ENTRE_TANDAS'
        ))
);

-- 3. SOLICITUDES
-- Un usuario registra de 1 a 3 tandas
-- para una maquina específica.
CREATE TABLE IF NOT EXISTS solicitudes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    maquina_id INTEGER NOT NULL,

    tandas_totales INTEGER NOT NULL
        CHECK (tandas_totales BETWEEN 1 AND 3),

    tandas_iniciadas INTEGER NOT NULL DEFAULT 0
        CHECK (tandas_iniciadas >= 0),

    -- 1 = Disponible, 0 = No disponible
    disponible INTEGER NOT NULL DEFAULT 1
        CHECK (disponible IN (0, 1)),

    estado TEXT NOT NULL DEFAULT 'EN_ESPERA'
        CHECK (estado IN (
            'EN_ESPERA',
            'AUTORIZADA',
            'EN_USO',
            'FINALIZADA',
            'CANCELADA'
        )),

    fecha_solicitud TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_finalizacion TEXT,

    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id),

    CHECK (tandas_iniciadas <= tandas_totales)
);

-- Evitar solicitudes activas duplicadas
-- de un mismo usuario para la misma maquina.
CREATE UNIQUE INDEX IF NOT EXISTS idx_solicitud_usuario_activa
ON solicitudes(usuario_id, maquina_id)
WHERE estado IN ('EN_ESPERA', 'AUTORIZADA', 'EN_USO');

-- Una sola solicitud ocupando cada maquina.
CREATE UNIQUE INDEX IF NOT EXISTS idx_maquina_ocupada
ON solicitudes(maquina_id)
WHERE estado = 'EN_USO';

-- Mantener orden de llegada de las colas.
CREATE INDEX IF NOT EXISTS idx_cola
ON solicitudes(maquina_id, estado, id);

-- 4. CICLOS
-- Cada tanda iniciada genera un ciclo.
CREATE TABLE IF NOT EXISTS ciclos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    solicitud_id INTEGER NOT NULL,
    numero_tanda INTEGER NOT NULL
        CHECK (numero_tanda BETWEEN 1 AND 3),

    duracion_minutos INTEGER NOT NULL
        CHECK (duracion_minutos BETWEEN 1 AND 180),

    estado TEXT NOT NULL DEFAULT 'EN_CURSO'
        CHECK (estado IN (
            'EN_CURSO',
            'PENDIENTE_RETIRO',
            'RETIRADO'
        )),

    fecha_inicio TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TEXT,
    fecha_retiro TEXT,

    FOREIGN KEY (solicitud_id) REFERENCES solicitudes(id),

    UNIQUE (solicitud_id, numero_tanda)
);

-- 5. NOTIFICACIONES
-- Avisos para los estudiantes desde la web.
CREATE TABLE IF NOT EXISTS notificaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    solicitud_id INTEGER,
    mensaje TEXT NOT NULL,

    leida INTEGER NOT NULL DEFAULT 0
        CHECK (leida IN (0, 1)),

    fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (solicitud_id) REFERENCES solicitudes(id)
);

-- ============================================
-- MAQUINAS INICIALES DEL PROTOTIPO
-- ============================================

INSERT OR IGNORE INTO maquinas (id, tipo, estado)
VALUES (1, 'LAVADORA', 'LIBRE');

INSERT OR IGNORE INTO maquinas (id, tipo, estado)
VALUES (2, 'SECADORA', 'LIBRE');
