# Agente IA para Sistema Escolar (Streamlit + PostgreSQL)
Servicio web que recibe consultas en español, las transforma a SQL con Groq y ejecuta en PostgreSQL.

Incluye interfaz Streamlit para interactuar con la base de datos escolar.

Este proyecto contiene un agente de IA que convierte lenguaje natural en consultas SQL para un sistema de gestión escolar completo.

* Se utilizó la API de [https://groq.com/](https://groq.com/) versión gratuita

# Interfaz Web

Ejecutar `streamlit run agente.py`. La aplicación muestra una interfaz para hacer consultas en español y ver resultados.

## Esquema de Base de Datos

El sistema maneja las siguientes tablas:

* `estudiantes` - Datos de estudiantes con edad, contacto, fecha de inscripción
* `profesores` - Información de profesores y especialidades
* `materias` - Catálogo de materias con créditos y niveles
* `matriculas` - Relación estudiantes-materias con calificaciones
* `aulas` - Información de espacios físicos
* `horarios` - Programación de clases
* `asistencias` - Registro de presencia estudiantil
* `examenes` - Calificaciones de evaluaciones
* `pagos` - Historial de pagos estudiantiles

## Reglas NL a SQL

El servicio guía a la IA con reglas como:

* Especificar columnas explícitas en SELECT
* Usar JOIN para relaciones entre tablas
* Incluir WHERE específico en UPDATE/DELETE
* Validar operaciones peligrosas (DROP, TRUNCATE, ALTER)

## Funcionalidades

### Consultas SELECT

* "Mostrar estudiantes con calificación mayor a 8"
* "Promedio de calificaciones por materia"
* "Top 5 estudiantes con mejor promedio"
* "Estudiantes con más ausencias"

### Operaciones DML

* "Añadir nuevo estudiante Ana López de 17 años" (INSERT)
* "Actualizar teléfono de Juan Pérez a 555-1234" (UPDATE)
* "Eliminar matrícula de María Gómez en Matemáticas" (DELETE)

## Requisitos

* Python 3.8+
* PostgreSQL 13+
* API Key de Groq (gratuita)

## Instalación

```bash bash
pip install streamlit pandas psycopg2-binary requests
```

# Estructura del Proyecto

```bash text
ProyectoDB_IA/
├── agente.py  
├── core/
│   ├── db.py  
│   ├── groq.py  
│   └── utils.py  
├── .env  
└── README.md
```

# Configuración

Archivo `.env` requerido:

```bash text
GROQ_API_KEY=tu_clave_groq_aqui
POSTGRES_URL=postgresql://usuario:contraseña@localhost:5432/escuela_bd
```

# Ejecución

```text bash
streamlit run agente.py
```

La aplicación estará disponible en `http://localhost:8501`

# Características de Seguridad

* Validación de consultas peligrosas
* Confirmación implícita para operaciones DML
* Uso de parámetros para prevenir SQL injection
* Análisis de resultados antes de mostrar

# Ejemplos de Consultas

## Información Académica

* "Estudiantes inscritos en Matemáticas I"
* "Horarios de clase para el profesor Carlos Martínez"
* "Asistencias del mes actual por estudiante"

## Análisis y Reportes

* "Materias con mayor tasa de aprobación"
* "Promedio de calificaciones por nivel académico"
* "Estudiantes con pagos pendientes"