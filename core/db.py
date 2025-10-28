import streamlit as st
import psycopg2
import pandas as pd
import time

class DatabaseManager:
    def __init__(self, postgres_url: str):
        self.postgres_url = postgres_url

    @st.cache_resource
    def connect(_self):
        try:
            conn = psycopg2.connect(_self.postgres_url)
            conn.autocommit = True
            return conn
        except Exception as e:
            st.error(f"Error conectando a PostgreSQL: {e}")
            return None

    def execute(self, conn, sql: str):
        cur = conn.cursor()
        start = time.time()
        try:
            if sql.strip().upper().startswith("SELECT"):
                cur.execute(sql)
                cols = [desc[0] for desc in cur.description]
                data = cur.fetchall()
                df = pd.DataFrame(data, columns=cols)
                duration = round(time.time() - start, 3)
                return df, f"Consulta exitosa ({len(df)} filas, {duration}s).", False
            else:
                cur.execute(sql)
                affected = cur.rowcount
                duration = round(time.time() - start, 3)
                return pd.DataFrame(), f"Operación ejecutada. Filas afectadas: {affected} ({duration}s).", True
        except Exception as e:
            return pd.DataFrame(), f"Error ejecutando SQL: {e}", False
        finally:
            cur.close()