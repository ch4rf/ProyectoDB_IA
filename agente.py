import streamlit as st
import time
from core.db import DatabaseManager
from core.groq import GroqClient
from core.utils import validate_sql, identify_table, show_tables, show_updated_table

# === CONFIG ===
POSTGRES_URL = st.secrets["POSTGRES_URL"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# === CARGA DE PROMPTS ===
with open("prompts/sql_prompt.txt", "r", encoding="utf-8") as f:
    SQL_PROMPT = f.read()

with open("prompts/interpret_prompt.txt", "r", encoding="utf-8") as f:
    INTERPRET_PROMPT = f.read()

# === INSTANCIAS ===
db = DatabaseManager(POSTGRES_URL)
groq = GroqClient(GROQ_API_KEY)

# === MAIN ===
def main():
    st.set_page_config(page_title="Agente IA Escolar", layout="wide")
    st.markdown("<h1 style='text-align:center; color:#2E86C1;'>Agente Inteligente Escolar</h1>", unsafe_allow_html=True)

    conn = db.connect()
    if not conn:
        st.stop()

    # === SIDEBAR ===
    with st.sidebar:
        st.markdown("### Tablas disponibles")
        
        # Botón para recargar
        if st.button("Recargar tablas"):
            st.success("Tablas recargadas")
            st.rerun()  # ← RECARGA LA APP

        # Mostrar tablas
        show_tables(st, conn)

    # === INPUT ===
    st.subheader("Escribe tu consulta en lenguaje natural")
    query = st.text_input(
        "Ej: 'Añade un estudiante llamado Ana López de 20 años'",
        placeholder="Muestra estudiantes con promedio mayor a 7",
        key="user_query"
    )

    # === EJECUTAR ===
    if st.button("Ejecutar", type="primary", use_container_width=True) and query.strip():
        with st.spinner("Generando SQL..."):
            sql = groq.generate_sql(query, SQL_PROMPT)
            if sql:
                st.subheader("SQL Generado")
                st.code(sql, language="sql")

                if not validate_sql(sql):
                    st.error("Operación peligrosa bloqueada.")
                else:
                    df, msg, is_mod = db.execute(conn, sql)
                    st.info(msg)

                    table = identify_table(sql)
                    if is_mod and table:
                        show_updated_table(st, conn, table)

                    if not df.empty:
                        st.success(f"Mostrando {len(df)} filas")
                        st.dataframe(df, use_container_width=True)
                        with st.expander("Análisis IA", expanded=True):
                            summary = groq.interpret_results(query, df, 0, False, INTERPRET_PROMPT)
                            st.markdown(f"**Resumen:** {summary}")
                    else:
                        st.warning("Sin resultados.")
            else:
                st.error("No se pudo generar SQL.")

if __name__ == "__main__":
    main()