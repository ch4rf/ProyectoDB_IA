-- Tabla estudiantes 
CREATE TABLE estudiantes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    edad INTEGER CHECK (edad > 0),
    email VARCHAR(100) UNIQUE,
    telefono VARCHAR(15),
    direccion TEXT,
    fecha_inscripcion DATE DEFAULT CURRENT_DATE
);

-- Tabla profesores 
CREATE TABLE profesores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    especialidad VARCHAR(50),
    experiencia_anos INTEGER CHECK (experiencia_anos >= 0),
    email VARCHAR(100) UNIQUE,
    telefono VARCHAR(15)
);

-- Tabla materias 
CREATE TABLE materias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,  
    descripcion TEXT,
    creditos INTEGER CHECK (creditos > 0),
    nivel VARCHAR(20) CHECK (nivel IN ('Básico', 'Intermedio', 'Avanzado')),
    profesor_id INTEGER REFERENCES profesores(id) ON DELETE SET NULL
);

-- Tabla matriculas 
CREATE TABLE matriculas (
    id SERIAL PRIMARY KEY,
    estudiante_id INTEGER REFERENCES estudiantes(id) ON DELETE CASCADE,
    materia_id INTEGER REFERENCES materias(id) ON DELETE CASCADE,
    calificacion DECIMAL(3,1) CHECK (calificacion BETWEEN 0 AND 10),
    fecha_matricula DATE DEFAULT CURRENT_DATE,
    estado VARCHAR(20) CHECK (estado IN ('Activa', 'Completa', 'Retirada')),
    UNIQUE(estudiante_id, materia_id)
);

-- Tabla aulas 
CREATE TABLE aulas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,  -- 
    capacidad INTEGER CHECK (capacidad > 0),
    ubicacion VARCHAR(100)  
);

-- Tabla horarios 
CREATE TABLE horarios (
    id SERIAL PRIMARY KEY,
    materia_id INTEGER REFERENCES materias(id) ON DELETE CASCADE,
    aula_id INTEGER REFERENCES aulas(id) ON DELETE SET NULL,
    dia_semana VARCHAR(20) CHECK (dia_semana IN ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado')),
    hora_inicio TIME,
    hora_fin TIME CHECK (hora_fin > hora_inicio),
    UNIQUE(materia_id, dia_semana, hora_inicio)  
);

-- Tabla asistencias 
CREATE TABLE asistencias (
    id SERIAL PRIMARY KEY,
    matricula_id INTEGER REFERENCES matriculas(id) ON DELETE CASCADE,
    fecha DATE DEFAULT CURRENT_DATE,
    presente BOOLEAN DEFAULT TRUE,  
    observaciones TEXT,
    UNIQUE(matricula_id, fecha) 
);

-- Tabla examenes 
CREATE TABLE examenes (
    id SERIAL PRIMARY KEY,
    matricula_id INTEGER REFERENCES matriculas(id) ON DELETE CASCADE,
    tipo VARCHAR(20) CHECK (tipo IN ('Parcial', 'Final', 'Quiz')),
    calificacion DECIMAL(3,1) CHECK (calificacion BETWEEN 0 AND 10),
    fecha DATE DEFAULT CURRENT_DATE
);

-- Tabla pagos 
CREATE TABLE pagos (
    id SERIAL PRIMARY KEY,
    estudiante_id INTEGER REFERENCES estudiantes(id) ON DELETE CASCADE,
    monto DECIMAL(10,2) CHECK (monto > 0),
    fecha_pago DATE DEFAULT CURRENT_DATE,
    metodo VARCHAR(20) CHECK (metodo IN ('Efectivo', 'Tarjeta', 'Transferencia')),
    descripcion TEXT
);

-- Índices para performance
CREATE INDEX idx_estudiantes_nombre ON estudiantes (nombre, apellido);
CREATE INDEX idx_profesores_especialidad ON profesores (especialidad);
CREATE INDEX idx_materias_nombre ON materias (nombre);
CREATE INDEX idx_matriculas_estudiante ON matriculas (estudiante_id);
CREATE INDEX idx_asistencias_fecha ON asistencias (fecha);
CREATE INDEX idx_examenes_matricula ON examenes (matricula_id);
CREATE INDEX idx_pagos_estudiante ON pagos (estudiante_id);