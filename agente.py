import streamlit as st
import psycopg2
import json
import requests
import pandas as pd
import time
import decimal
import datetime
import numpy as np

# CONFIGURACIÓN

GROQ_API_KEY = ""
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
POSTGRES_URL = ""

# PROMPT PARA LA BASE 

ESQUEMA_DB = """
Eres un experto en SQL para PostgreSQL. Tu tarea es generar SOLO el código SQL válido y ejecutable basado en el esquema de la base de datos y la consulta del usuario en lenguaje natural. NO agregues explicaciones, comentarios, formato Markdown, ni nada extra: solo el SQL puro. No termines con ';' ni agregues caracteres especiales innecesarios. Si la consulta es inválida o imposible, genera un SELECT vacío como SELECT 1 WHERE 1=0.

Esquema detallado (incluyendo tipos de datos y constraints clave):
- estudiantes(id SERIAL PRIMARY KEY, nombre VARCHAR(50) NOT NULL, apellido VARCHAR(50) NOT NULL, edad INTEGER CHECK (edad > 0), email VARCHAR(100) UNIQUE, telefono VARCHAR(15), direccion TEXT, fecha_inscripcion DATE DEFAULT CURRENT_DATE)
- profesores(id SERIAL PRIMARY KEY, nombre VARCHAR(50) NOT NULL, apellido VARCHAR(50) NOT NULL, especialidad VARCHAR(50), experiencia_anos INTEGER CHECK (experiencia_anos >= 0), email VARCHAR(100) UNIQUE, telefono VARCHAR(15))
- materias(id SERIAL PRIMARY KEY, nombre VARCHAR(50) NOT NULL UNIQUE, descripcion TEXT, creditos INTEGER CHECK (creditos > 0), nivel VARCHAR(20) CHECK (nivel IN ('Básico', 'Intermedio', 'Avanzado')), profesor_id INTEGER REFERENCES profesores(id) ON DELETE SET NULL)
- matriculas(id SERIAL PRIMARY KEY, estudiante_id INTEGER REFERENCES estudiantes(id) ON DELETE CASCADE, materia_id INTEGER REFERENCES materias(id) ON DELETE CASCADE, calificacion DECIMAL(3,1) CHECK (calificacion BETWEEN 0 AND 10), fecha_matricula DATE DEFAULT CURRENT_DATE, estado VARCHAR(20) CHECK (estado IN ('Activa', 'Completa', 'Retirada')), UNIQUE(estudiante_id, materia_id))
- aulas(id SERIAL PRIMARY KEY, nombre VARCHAR(50) NOT NULL UNIQUE, capacidad INTEGER CHECK (capacidad > 0), ubicacion VARCHAR(100))
- horarios(id SERIAL PRIMARY KEY, materia_id INTEGER REFERENCES materias(id) ON DELETE CASCADE, aula_id INTEGER REFERENCES aulas(id) ON DELETE SET NULL, dia_semana VARCHAR(20) CHECK (dia_semana IN ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado')), hora_inicio TIME, hora_fin TIME CHECK (hora_fin > hora_inicio), UNIQUE(materia_id, dia_semana, hora_inicio))
- asistencias(id SERIAL PRIMARY KEY, matricula_id INTEGER REFERENCES matriculas(id) ON DELETE CASCADE, fecha DATE DEFAULT CURRENT_DATE, presente BOOLEAN DEFAULT TRUE, observaciones TEXT, UNIQUE(matricula_id, fecha))
- examenes(id SERIAL PRIMARY KEY, matricula_id INTEGER REFERENCES matriculas(id) ON DELETE CASCADE, tipo VARCHAR(20) CHECK (tipo IN ('Parcial', 'Final', 'Quiz')), calificacion DECIMAL(3,1) CHECK (calificacion BETWEEN 0 AND 10), fecha DATE DEFAULT CURRENT_DATE)
- pagos(id SERIAL PRIMARY KEY, estudiante_id INTEGER REFERENCES estudiantes(id) ON DELETE CASCADE, monto DECIMAL(10,2) CHECK (monto > 0), fecha_pago DATE DEFAULT CURRENT_DATE, metodo VARCHAR(20) CHECK (metodo IN ('Efectivo', 'Tarjeta', 'Transferencia')), descripcion TEXT)

Reglas generales estrictas para generar SQL:
- Siempre usa el esquema exacto: no inventes columnas, tablas ni valores. Usa nombres de columnas tal como están definidos.
- Usa alias estandarizados para claridad y consistencia: 'e' para estudiantes, 'p' para profesores, 'mat' para materias, 'm' para matriculas, 'a' para aulas, 'h' para horarios, 'as' para asistencias, 'ex' para examenes, 'pa' para pagos. Siempre referencia columnas con alias (ej: e.nombre, no nombre).
- Para consultas de lectura, usa INNER JOIN por default; LEFT JOIN solo si se piden datos opcionales (ej: 'incluyendo nulos').
- Para agregaciones (promedios, conteos, sums): usa AVG, COUNT, SUM, etc., y siempre GROUP BY en todas las columnas no agregadas. Usa HAVING para filtros post-agregación (ej: AVG > X).
- Para filtros: usa WHERE. Para fechas, usa formato 'YYYY-MM-DD' y >= para 'después del [fecha]' si incluye el día, o > si estrictamente posterior. Para booleanos, usa TRUE/FALSE. Para cadenas, usa ILIKE '%texto%' para búsquedas parciales insensibles a mayúsculas si ambiguo; LIKE para exactas.
- Para ordenamientos: incluye ORDER BY si se menciona 'mayor', 'menor', 'recientes', 'top'; DESC para descendente en rankings.
- Para límites: usa LIMIT N si se pide 'top N' o similar.
- Maneja complejidad: Descompón consultas en subqueries o CTE si lógico (ej: promedios anidados). Prioriza eficiencia: usa índices como idx_estudiantes_nombre.
- Permitir INSERT, UPDATE, DELETE solo si la consulta lo pide explícitamente (ej: 'añade', 'inserta', 'actualiza', 'elimina'). Para DELETE y UPDATE, SIEMPRE incluye WHERE específico para evitar modificaciones masivas. Ejemplo: 'Elimina estudiantes' debe ser SELECT 1 WHERE 1=0 (inválido, no específico); 'Elimina estudiante Juan Pérez' debe incluir WHERE e.nombre = 'Juan' AND e.apellido = 'Pérez'.
- Si ambiguo, elige interpretación lógica mínima: usa columnas más relevantes (ej: calificacion de matriculas para 'calificacion', examenes.calificacion para 'en examenes').
- No agregues filtros, columnas o joins no pedidos en la consulta: mantén mínimo viable. No agregues ORDER BY o LIMIT si no se menciona.
- Si no hay datos posibles, está bien devolver 0 rows para SELECT o 0 filas afectadas para INSERT/UPDATE/DELETE.

Reglas específicas para evitar errores comunes:
- Para 'curso' o 'materia': siempre referencia mat.nombre (de materias), nunca de otras tablas.
- Para calificaciones: usa m.calificacion para matriculas generales, ex.calificacion para examenes específicos.
- Para fechas: Prioriza e.fecha_inscripcion para 'inscritos después de'; m.fecha_matricula para 'matriculados después de'; ex.fecha para 'examenes después de'. Nunca confundas entre tablas.
- Para conteos: Usa COUNT(DISTINCT m.estudiante_id) para número de estudiantes; COUNT(ex.id) para número de examenes.
- Para joins: Siempre cadena lógica: estudiantes a matriculas (e.id = m.estudiante_id), matriculas a materias (m.materia_id = mat.id), matriculas a examenes (m.id = ex.matricula_id), materias a profesores (mat.profesor_id = p.id). Nunca joins directos saltando tablas.
- No agreges 'estado = 'Activa'' u otros filtros a menos que se mencione explícitamente (ej: 'matriculados activamente').
- Consistencia: Siempre usa alias en SELECT y WHERE (ej: SELECT e.nombre, NO nombre). Corrige confusiones como m.nombre (matriculas no tiene nombre).
- Para INSERT: Usa valores explícitos de la consulta o valores por defecto (ej: CURRENT_DATE para fechas). Respeta constraints (ej: UNIQUE, CHECK).
- Para UPDATE: Solo actualiza columnas mencionadas, con WHERE específico. Ejemplo: 'Actualiza calificación de Juan Pérez en Matemáticas I a 8.5' debe ser UPDATE matriculas m SET calificacion = 8.5 WHERE m.estudiante_id = (SELECT e.id FROM estudiantes e WHERE e.nombre = 'Juan' AND e.apellido = 'Pérez') AND m.materia_id = (SELECT mat.id FROM materias mat WHERE mat.nombre = 'Matemáticas I').
- Para DELETE: Siempre usa WHERE específico. Ejemplo: 'Elimina matrícula de Juan Pérez en Física' debe be DELETE FROM matriculas m WHERE m.estudiante_id = (SELECT e.id FROM estudiantes e WHERE e.nombre = 'Juan' AND e.apellido = 'Pérez') AND m.materia_id = (SELECT mat.id FROM materias mat WHERE mat.nombre = 'Física').

Ejemplos obligatorios (usa patrones exactos para consultas similares; NO los incluyas en output):
- Consulta: "Muestra estudiantes con edad mayor a 17" -> SELECT e.nombre, e.apellido, e.edad FROM estudiantes e WHERE e.edad > 17
- Consulta: "Promedio de calificaciones por estudiante" -> SELECT e.nombre, e.apellido, AVG(m.calificacion) AS promedio FROM estudiantes e JOIN matriculas m ON e.id = m.estudiante_id GROUP BY e.id, e.nombre, e.apellido
- Consulta: "Añade un estudiante llamado Ana López de 20 años" -> INSERT INTO estudiantes (nombre, apellido, edad) VALUES ('Ana', 'López', 20)
- Consulta: "Actualiza la calificación de Juan Pérez en Matemáticas I a 8.5" -> UPDATE matriculas m SET calificacion = 8.5 WHERE m.estudiante_id = (SELECT e.id FROM estudiantes e WHERE e.nombre = 'Juan' AND e.apellido = 'Pérez') AND m.materia_id = (SELECT mat.id FROM materias mat WHERE mat.nombre = 'Matemáticas I')
- Consulta: "Elimina la matrícula de María Gómez en Física Avanzada" -> DELETE FROM matriculas m WHERE m.estudiante_id = (SELECT e.id FROM estudiantes e WHERE e.nombre = 'María' AND e.apellido = 'Gómez') AND m.materia_id = (SELECT mat.id FROM materias mat WHERE mat.nombre = 'Física Avanzada')
- Consulta: "Añade un examen final para Juan Pérez en Matemáticas I con calificación 9.0" -> INSERT INTO examenes (matricula_id, tipo, calificacion, fecha) SELECT m.id, 'Final', 9.0, CURRENT_DATE FROM matriculas m JOIN estudiantes e ON m.estudiante_id = e.id JOIN materias mat ON m.materia_id = mat.id WHERE e.nombre = 'Juan' AND e.apellido = 'Pérez' AND mat.nombre = 'Matemáticas I'

Responde SOLO con el SQL generado.
"""

# PROMPT PARA INTERPRETACIÓN

PROMPT_INTERPRETACION = """
Eres un asistente que resume resultados de consultas SQL en lenguaje natural simple y factual en español. 

Tu tarea:
- Genera SOLO 1-2 oraciones cortas resumiendo hechos clave.
- Para SELECT: Usa 'Número de filas: {num_filas}' como total de registros. Incluye columnas principales, rango de valores numéricos (min, max, avg si aplica), y un ejemplo de la muestra.
- Para INSERT, UPDATE, DELETE: Usa 'Filas afectadas: {num_filas}' y describe la acción (ej: 'Se insertaron X estudiantes').
- Usa las estadísticas numéricas exactas proporcionadas (ej: min, max, avg de calificacion) para rangos: "calificaciones desde X (mín) hasta Y (máx)".
- NO infieras de la muestra sola; combina con stats del total.
- Habla de 'registros' o 'filas', no entidades a menos que exacto.
- Si hay valores numéricos: menciona min/max/avg si relevantes.

Información EXACTA:
- Consulta original: {consulta_original}
- Columnas: {columnas}
- Número de filas: {num_filas} (TOTAL REAL, o filas afectadas para INSERT/UPDATE/DELETE)
- Estadísticas numéricas del total (solo para columnas como calificacion): {estadisticas_numericas}
- Muestra de datos (primeras filas ordenadas, solo ejemplo): {muestra_datos}

Responde SOLO con el resumen factual.
"""

# CONEXIÓN

@st.cache_resource
def conectar_db():
    try:
        conn = psycopg2.connect(POSTGRES_URL)
        conn.autocommit = True
        return conn
    except Exception as e:
        st.error(f"Error conectando a PostgreSQL: {e}")
        return None

# FUNCIONES

def validar_sql(sql: str) -> bool:
    prohibidas = ["DROP", "TRUNCATE", "ALTER"]
    return not any(p in sql.upper() for p in prohibidas)

def identificar_tabla_afectada(sql: str) -> str:
    sql = sql.upper()
    tablas = ['ESTUDIANTES', 'PROFESORES', 'MATERIAS', 'MATRICULAS', 'AULAS', 'HORARIOS', 'ASISTENCIAS', 'EXAMENES', 'PAGOS']
    for tabla in tablas:
        if f"INTO {tabla}" in sql or f"UPDATE {tabla}" in sql or f"FROM {tabla}" in sql:
            return tabla.lower()
    return None

def generar_sql_desde_nl(consulta: str) -> str:
    if not GROQ_API_KEY or GROQ_API_KEY == "":
        st.error("Error: GROQ_API_KEY está vacía o no configurada. Ve a https://console.groq.com para obtener una.")
        return ""
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": ESQUEMA_DB},
            {"role": "user", "content": consulta}
        ],
        "temperature": 0.1,
        "max_tokens": 500,
        "n": 1
    }
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    try:
        r = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=15)
        r.raise_for_status()
        data = r.json()
        # FORMATO SQL
        def format_sql(sql: str) -> str:
            keywords = ['SELECT', 'FROM', 'JOIN', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY', 'INSERT INTO', 'UPDATE', 'SET', 'DELETE']
            formatted_sql = sql
            for keyword in keywords:
                formatted_sql = formatted_sql.replace(f' {keyword} ', f'\n{keyword} ')
            lines = formatted_sql.split('\n')
            formatted_sql = '\n'.join(['  ' + line.strip() if line.strip() not in keywords else line.strip() for line in lines])
            return formatted_sql
        return format_sql(data["choices"][0]["message"]["content"].strip())
    except requests.exceptions.HTTPError as e:
        if r.status_code == 400:
            try:
                error_detail = r.json().get("error", {}).get("message", "Error desconocido")
                st.error(f"Error 400 de Groq: {error_detail}. Verifica tu clave API y modelo.")
            except:
                st.error(f"Error 400 de Groq: Respuesta inválida. Detalle: {r.text[:200]}")
        else:
            st.error(f"Error HTTP {r.status_code}: {e}")
        return ""
    except Exception as e:
        st.error(f"Error al generando SQL: {e}")
        return ""

def generar_interpretacion(consulta_original: str, df: pd.DataFrame, filas_afectadas: int = 0, es_modificacion: bool = False) -> str:
    if es_modificacion:
        return f"Filas afectadas: {filas_afectadas}. La operación ({'inserción' if consulta_original.upper().startswith('INSERT') else 'actualización' if consulta_original.upper().startswith('UPDATE') else 'eliminación'}) se realizó correctamente."
    
    if df.empty:
        return "No se encontraron resultados para esta consulta."
    
    if not GROQ_API_KEY or GROQ_API_KEY == "":
        return f"Resumen: {len(df)} registros con columnas {', '.join(df.columns)}."
    
    def convert_o(obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return str(obj)
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    estadisticas_numericas = {}
    for col in numeric_cols:
        col_data = pd.to_numeric(df[col], errors='coerce')
        estadisticas_numericas[col] = {
            "min": col_data.min(),
            "max": col_data.max(),
            "avg": round(col_data.mean(), 2) if not col_data.empty else None
        }
    
    df_seguro = df.head(3).applymap(convert_o)
    muestra = df_seguro.to_dict('records')
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "temperature": 0,
        "max_tokens": 120,
        "messages": [
            {"role": "system", "content": PROMPT_INTERPRETACION.format(
                consulta_original=consulta_original,
                columnas=", ".join(df.columns),
                num_filas=len(df),
                estadisticas_numericas=json.dumps(estadisticas_numericas, ensure_ascii=False),
                muestra_datos=json.dumps(muestra, indent=2, ensure_ascii=False, default=convert_o)
            )}
        ]
    }
    
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    try:
        with st.spinner("Generando resumen..."):
            r = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=15)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Resumen básico: {len(df)} registros, calificación desde {df['calificacion'].min()} hasta {df['calificacion'].max()}."

def ejecutar_sql(conn, sql: str):
    cur = conn.cursor()
    start = time.time()
    try:
        if sql.upper().startswith("SELECT"):
            cur.execute(sql)
            cols = [desc[0] for desc in cur.description]
            data = cur.fetchall()
            df = pd.DataFrame(data, columns=cols)
            duracion = round(time.time() - start, 3)
            return df, f"Consulta exitosa ({len(df)} filas, {len(cols)} columnas, {duracion}s).", False
        else:
            cur.execute(sql)
            filas_afectadas = cur.rowcount
            duracion = round(time.time() - start, 3)
            return pd.DataFrame(), f"Operación ejecutada. Filas afectadas: {filas_afectadas} ({duracion}s).", True
    except Exception as e:
        return pd.DataFrame(), f"Error ejecutando SQL: {e}", False
    finally:
        cur.close()

def mostrar_tablas(conn, cache_key: str):
    tablas = ['estudiantes', 'profesores', 'materias', 'matriculas', 'aulas', 'horarios', 'asistencias', 'examenes', 'pagos']
    for t in tablas:
        try:
            with st.expander(f"Vista completa de {t.upper()}", expanded=False):
                df = pd.read_sql(f"SELECT * FROM {t}", conn, params={'cache_key': cache_key})
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Error cargando {t}: {e}")

def mostrar_tabla_afectada(conn, tabla: str):
    if tabla:
        try:
            with st.expander(f"Tabla {tabla.upper()} actualizada", expanded=True):
                df = pd.read_sql(f"SELECT * FROM {tabla}", conn)
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Error mostrando tabla {tabla}: {e}")

# STREAMLIT

def main():
    st.set_page_config(page_title="Agente IA", layout="wide")
    st.markdown("<h1 style='text-align:center; color:#2E86C1;'>Agente Inteligente</h1>", unsafe_allow_html=True)

    conn = conectar_db()
    if not conn:
        st.stop()

    if 'cache_key' not in st.session_state:
        st.session_state.cache_key = str(time.time())

    with st.sidebar:
        st.markdown("### Tablas disponibles")
        mostrar_tablas(conn, st.session_state.cache_key)

    st.subheader("Escribe tu consulta")
    consulta_nl = st.text_input("Ejemplo: 'Añade un estudiante llamado Ana López de 20 años' o 'Muestra los estudiantes con promedio mayor a 7'", key="consulta_nl")

    ejecutar = st.button("Ejecutar consulta", type="primary", use_container_width=True)

    if ejecutar and consulta_nl.strip():
        with st.spinner("Analizando y generando SQL..."):
            sql = generar_sql_desde_nl(consulta_nl)
            if sql:
                st.subheader("SQL generado")
                st.code(sql, language="sql")
                
                if not validar_sql(sql):
                    st.error("Consulta peligrosa detectada. No se permiten DROP, TRUNCATE ni ALTER.")
                else:
                    df, msg, es_modificacion = ejecutar_sql(conn, sql)
                    st.info(msg)
                    
                    if es_modificacion:
                        st.session_state.cache_key = str(time.time())
                    
                    tabla_afectada = identificar_tabla_afectada(sql)
                    
                    if es_modificacion:
                        st.success(f"Operación completada: {msg}")
                        if tabla_afectada:
                            mostrar_tabla_afectada(conn, tabla_afectada)
                    elif df is not None and not df.empty:
                        st.success(f"Mostrando {len(df)} filas x {len(df.columns)} columnas")
                        st.dataframe(df, use_container_width=True)
                        with st.expander("Interpretación de resultados", expanded=True):
                            interpretacion = generar_interpretacion(consulta_nl, df, len(df), False)
                            st.markdown(f"**Análisis IA:** {interpretacion}")
                    else:
                        st.warning("Sin resultados para mostrar.")
                        st.info("Esto puede indicar que no hay datos que cumplan con los criterios de tu consulta o que la operación no devolvió datos.")
            else:
                st.error("No se pudo generar una consulta válida.")

if __name__ == "__main__":
    main()