import pandas as pd
import streamlit as st

def validate_sql(sql: str) -> bool:
    sql_upper = sql.upper()
    forbidden = ["DROP", "TRUNCATE", "ALTER"]
    if any(cmd in sql_upper for cmd in forbidden):
        return False
    if "INSERT" in sql_upper and "WHERE" in sql_upper:
        return False
    if ("UPDATE" in sql_upper or "DELETE" in sql_upper) and "WHERE" not in sql_upper:
        return False
    return True

def identify_table(sql: str) -> str | None:
    sql_upper = sql.upper()
    tables = ['ESTUDIANTES', 'PROFESORES', 'MATERIAS', 'MATRICULAS', 'AULAS', 'HORARIOS', 'ASISTENCIAS', 'EXAMENES', 'PAGOS']
    for t in tables:
        if f"INTO {t}" in sql_upper or f"UPDATE {t}" in sql_upper or f"FROM {t}" in sql_upper:
            return t.lower()
    return None

def show_tables(st, conn):  # ← SIN cache_key
    tablas = ['estudiantes', 'profesores', 'materias', 'matriculas', 'aulas', 'horarios', 'asistencias', 'examenes', 'pagos']
    for t in tablas:
        with st.expander(f"Vista completa de {t.upper()}", expanded=False):
            try:
                df = pd.read_sql(f"SELECT * FROM {t}", conn)
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Error cargando {t}: {e}")

def show_updated_table(st, conn, table: str):  
    if table:
        with st.expander(f"Tabla {table.upper()} actualizada", expanded=True):
            try:
                df = pd.read_sql(f"SELECT * FROM {table}", conn)
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Error mostrando {table}: {e}")