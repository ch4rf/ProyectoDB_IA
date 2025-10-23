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

-- Datos iniciales 
INSERT INTO profesores (nombre, apellido, especialidad, experiencia_anos, email, telefono) VALUES
('Juan', 'Rodríguez', 'Matemáticas', 10, 'juan@escuela.com', '555-1234'),
('María', 'Gómez', 'Historia', 8, 'maria@escuela.com', '555-5678'),
('Carlos', 'López', 'Física', 12, 'carlos@escuela.com', '555-9012'),
('Ana', 'Martínez', 'Inglés', 5, 'ana@escuela.com', '555-3456'),
('Luis', 'Pérez', 'Química', 7, 'luis@escuela.com', '555-7890'),
('Elena', 'Sánchez', 'Biología', 9, 'elena@escuela.com', '555-2345'),
('Miguel', 'Ramírez', 'Arte', 6, 'miguel@escuela.com', '555-6789'),
('Sofía', 'Vega', 'Educación Física', 4, 'sofia@escuela.com', '555-4321'),
('Diego', 'Ortega', 'Informática', 11, 'diego@escuela.com', '555-8765'),
('Laura', 'Torres', 'Literatura', 7, 'laura@escuela.com', '555-2109');

INSERT INTO materias (nombre, descripcion, creditos, nivel, profesor_id) VALUES
('Matemáticas I', 'Álgebra básica', 4, 'Básico', 1),
('Historia Antigua', 'Civilizaciones', 3, 'Intermedio', 2),
('Física Básica', 'Mecánica', 4, 'Básico', 3),
('Inglés Intermedio', 'Gramática', 3, 'Intermedio', 4),
('Química Orgánica', 'Compuestos', 4, 'Avanzado', 5),
('Biología Celular', 'Células y genética', 4, 'Intermedio', 6),
('Arte Moderno', 'Pintura y escultura', 2, 'Básico', 7),
('Educación Física I', 'Deportes básicos', 2, 'Básico', 8),
('Informática Básica', 'Programación intro', 3, 'Básico', 9),
('Literatura Española', 'Autores clásicos', 3, 'Intermedio', 10),
('Matemáticas II', 'Cálculo', 4, 'Avanzado', 1),
('Historia Contemporánea', 'Siglo XX', 3, 'Avanzado', 2),
('Física Avanzada', 'Electromagnetismo', 4, 'Avanzado', 3);

INSERT INTO aulas (nombre, capacidad, ubicacion) VALUES
('Aula 101', 30, 'Edificio A, Piso 1'),
('Aula 102', 25, 'Edificio A, Piso 1'),
('Aula 201', 40, 'Edificio B, Piso 2'),
('Laboratorio 1', 20, 'Edificio C, Sótano'),
('Gimnasio', 50, 'Edificio D, Planta Baja'),
('Aula 103', 30, 'Edificio A, Piso 1'),
('Laboratorio 2', 20, 'Edificio C, Sótano');

INSERT INTO estudiantes (nombre, apellido, edad, email, telefono, direccion, fecha_inscripcion) VALUES
('Pedro', 'Sánchez', 17, 'pedro@email.com', '555-1111', 'Calle 1, Ciudad', '2023-09-01'),
('Ana', 'López', 16, 'ana@email.com', '555-2222', 'Calle 2, Ciudad', '2023-09-01'),
('Juan', 'Pérez', 18, 'juanp@email.com', '555-3333', 'Calle 3, Ciudad', '2023-09-02'),
('María', 'García', 17, 'maria@email.com', '555-4444', 'Calle 4, Ciudad', '2023-09-03'),
('Carlos', 'Hernández', 16, 'carlos@email.com', '555-5555', 'Calle 5, Ciudad', '2023-09-04'),
('Laura', 'Torres', 18, 'laura@email.com', '555-6666', 'Calle 6, Ciudad', '2023-09-05'),
('Diego', 'Ramírez', 17, 'diego@email.com', '555-7777', 'Calle 7, Ciudad', '2023-09-06'),
('Sofía', 'Vega', 16, 'sofia@email.com', '555-8888', 'Calle 8, Ciudad', '2023-09-07'),
('Miguel', 'Ortega', 18, 'miguel@email.com', '555-9999', 'Calle 9, Ciudad', '2023-09-08'),
('Elena', 'Castillo', 17, 'elena@email.com', '555-0000', 'Calle 10, Ciudad', '2023-09-09'),
('Andrés', 'Morales', 16, 'andres@email.com', '555-1112', 'Calle 11, Ciudad', '2023-09-10'),
('Camila', 'Ríos', 18, 'camila@email.com', '555-2223', 'Calle 12, Ciudad', '2023-09-11'),
('Felipe', 'Castro', 17, 'felipe@email.com', '555-3334', 'Calle 13, Ciudad', '2023-09-12'),
('Gabriela', 'Mendoza', 16, 'gabriela@email.com', '555-4445', 'Calle 14, Ciudad', '2023-09-13'),
('Javier', 'Ruiz', 18, 'javier@email.com', '555-5556', 'Calle 15, Ciudad', '2023-09-14'),
('Valeria', 'Navarro', 17, 'valeria@email.com', '555-6667', 'Calle 16, Ciudad', '2023-09-15'),
('Ricardo', 'Díaz', 16, 'ricardo@email.com', '555-7778', 'Calle 17, Ciudad', '2023-09-16'),
('Paula', 'Ortiz', 18, 'paula@email.com', '555-8889', 'Calle 18, Ciudad', '2023-09-17'),
('Sergio', 'Vázquez', 17, 'sergio@email.com', '555-9990', 'Calle 19, Ciudad', '2023-09-18'),
('Natalia', 'Jiménez', 16, 'natalia@email.com', '555-0001', 'Calle 20, Ciudad', '2023-09-19');

INSERT INTO matriculas (estudiante_id, materia_id, calificacion, fecha_matricula, estado) VALUES
(1, 1, 8.5, '2023-09-10', 'Activa'),
(1, 2, 7.0, '2023-09-10', 'Completa'),
(2, 1, 9.2, '2023-09-10', 'Activa'),
(2, 3, 6.5, '2023-09-10', 'Retirada'),
(3, 1, 9.8, '2023-09-11', 'Completa'),
(3, 4, 8.0, '2023-09-11', 'Activa'),
(4, 5, 7.5, '2023-09-12', 'Completa'),
(5, 6, 8.8, '2023-09-13', 'Activa'),
(6, 7, 9.0, '2023-09-14', 'Completa'),
(7, 8, 7.2, '2023-09-15', 'Activa'),
(8, 9, 8.5, '2023-09-16', 'Completa'),
(9, 10, 9.0, '2023-09-17', 'Activa'),
(10, 11, 7.8, '2023-09-18', 'Completa'),
(11, 12, 8.5, '2023-09-19', 'Activa'),
(12, 13, 9.2, '2023-09-20', 'Completa'),
(13, 1, 7.0, '2023-09-21', 'Activa'),
(14, 2, 8.0, '2023-09-22', 'Completa'),
(15, 3, 9.5, '2023-09-23', 'Activa'),
(16, 4, 6.5, '2023-09-24', 'Retirada'),
(17, 5, 8.8, '2023-09-25', 'Completa'),
(18, 6, 7.5, '2023-09-26', 'Activa'),
(19, 7, 9.0, '2023-09-27', 'Completa'),
(20, 8, 8.2, '2023-09-28', 'Activa');

INSERT INTO horarios (materia_id, aula_id, dia_semana, hora_inicio, hora_fin) VALUES
(1, 1, 'Lunes', '08:00', '10:00'),
(2, 2, 'Martes', '10:00', '12:00'),
(3, 3, 'Miércoles', '08:00', '10:00'),
(4, 4, 'Jueves', '10:00', '12:00'),
(5, 1, 'Viernes', '08:00', '10:00'),
(6, 2, 'Lunes', '10:00', '12:00'),
(7, 3, 'Martes', '08:00', '10:00'),
(8, 4, 'Miércoles', '10:00', '12:00'),
(9, 1, 'Jueves', '08:00', '10:00'),
(10, 2, 'Viernes', '10:00', '12:00'),
(11, 3, 'Lunes', '08:00', '10:00'),
(12, 4, 'Martes', '10:00', '12:00'),
(13, 1, 'Miércoles', '08:00', '10:00');

INSERT INTO asistencias (matricula_id, fecha, presente, observaciones) VALUES
(1, '2023-09-15', TRUE, 'Presente'),
(1, '2023-09-16', FALSE, 'Ausente por enfermedad'),
(2, '2023-09-15', TRUE, ''),
(3, '2023-09-15', TRUE, ''),
(4, '2023-09-15', FALSE, 'Ausente'),
(5, '2023-09-16', TRUE, ''),
(6, '2023-09-16', TRUE, ''),
(7, '2023-09-16', TRUE, ''),
(8, '2023-09-17', FALSE, 'Ausente'),
(9, '2023-09-17', TRUE, ''),
(10, '2023-09-18', TRUE, ''),
(11, '2023-09-18', FALSE, 'Ausente'),
(12, '2023-09-19', TRUE, ''),
(13, '2023-09-19', TRUE, ''),
(14, '2023-09-20', TRUE, ''),
(15, '2023-09-20', FALSE, 'Ausente'),
(16, '2023-09-21', TRUE, ''),
(17, '2023-09-21', TRUE, ''),
(18, '2023-09-22', TRUE, ''),
(19, '2023-09-22', FALSE, 'Ausente'),
(20, '2023-09-23', TRUE, ''),
(21, '2023-09-23', TRUE, ''),
(22, '2023-09-24', TRUE, ''),
(23, '2023-09-24', FALSE, 'Ausente');

INSERT INTO examenes (matricula_id, tipo, calificacion, fecha) VALUES
(1, 'Parcial', 8.0, '2023-10-01'),
(1, 'Final', 9.0, '2023-12-15'),
(2, 'Parcial', 7.5, '2023-10-02'),
(3, 'Quiz', 9.5, '2023-10-03'),
(4, 'Parcial', 6.0, '2023-10-04'),
(5, 'Final', 8.5, '2023-12-16'),
(6, 'Parcial', 9.2, '2023-10-05'),
(7, 'Quiz', 7.8, '2023-10-06'),
(8, 'Final', 8.7, '2023-12-17'),
(9, 'Parcial', 9.0, '2023-10-07'),
(10, 'Quiz', 8.2, '2023-10-08'),
(11, 'Parcial', 7.5, '2023-10-09'),
(12, 'Final', 9.3, '2023-12-18'),
(13, 'Quiz', 8.0, '2023-10-10'),
(14, 'Parcial', 9.5, '2023-10-11'),
(15, 'Final', 7.0, '2023-12-19'),
(16, 'Quiz', 8.8, '2023-10-12'),
(17, 'Parcial', 9.2, '2023-10-13'),
(18, 'Final', 8.5, '2023-12-20'),
(19, 'Quiz', 7.5, '2023-10-14'),
(20, 'Parcial', 9.0, '2023-10-15'),
(21, 'Final', 8.0, '2023-12-21'),
(22, 'Quiz', 9.5, '2023-10-16'),
(23, 'Parcial', 7.2, '2023-10-17');

INSERT INTO pagos (estudiante_id, monto, fecha_pago, metodo, descripcion) VALUES
(1, 500.00, '2023-09-01', 'Tarjeta', 'Inscripción anual'),
(2, 500.00, '2023-09-01', 'Efectivo', 'Inscripción anual'),
(3, 250.00, '2023-09-02', 'Transferencia', 'Primer pago'),
(4, 500.00, '2023-09-03', 'Tarjeta', 'Inscripción anual'),
(5, 500.00, '2023-09-04', 'Efectivo', 'Inscripción anual'),
(6, 250.00, '2023-09-05', 'Transferencia', 'Primer pago'),
(7, 500.00, '2023-09-06', 'Tarjeta', 'Inscripción anual'),
(8, 500.00, '2023-09-07', 'Efectivo', 'Inscripción anual'),
(9, 250.00, '2023-09-08', 'Transferencia', 'Primer pago'),
(10, 500.00, '2023-09-09', 'Tarjeta', 'Inscripción anual'),
(11, 500.00, '2023-09-10', 'Efectivo', 'Inscripción anual'),
(12, 250.00, '2023-09-11', 'Transferencia', 'Primer pago'),
(13, 500.00, '2023-09-12', 'Tarjeta', 'Inscripción anual'),
(14, 500.00, '2023-09-13', 'Efectivo', 'Inscripción anual'),
(15, 250.00, '2023-09-14', 'Transferencia', 'Primer pago'),
(16, 500.00, '2023-09-15', 'Tarjeta', 'Inscripción anual'),
(17, 500.00, '2023-09-16', 'Efectivo', 'Inscripción anual'),
(18, 250.00, '2023-09-17', 'Transferencia', 'Primer pago'),
(19, 500.00, '2023-09-18', 'Tarjeta', 'Inscripción anual'),
(20, 500.00, '2023-09-19', 'Efectivo', 'Inscripción anual');
