import streamlit as st
import requests
import json
import pandas as pd
import numpy as np
import decimal
import datetime

class GroqClient:
    def __init__(self, api_key: str, api_url: str = "https://api.groq.com/openai/v1/chat/completions"):
        self.api_key = api_key
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    def generate_sql(self, user_query: str, sql_prompt: str) -> str:
        if not self.api_key:
            st.error("Error: GROQ_API_KEY no configurada.")
            return ""

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": sql_prompt},
                {"role": "user", "content": user_query}
            ],
            "temperature": 0.1,
            "max_tokens": 500
        }
        try:
            r = requests.post(self.api_url, headers=self.headers, json=payload, timeout=15)
            r.raise_for_status()
            sql = r.json()["choices"][0]["message"]["content"].strip()
            return self._format_sql(sql)
        except Exception as e:
            st.error(f"Error generando SQL: {e}")
            return ""

    def interpret_results(self, query: str, df: pd.DataFrame, affected: int = 0, is_mod: bool = False, prompt: str = "") -> str:
        if is_mod:
            action = "inserción" if "INSERT" in query.upper() else "actualización" if "UPDATE" in query.upper() else "eliminación"
            return f"Filas afectadas: {affected}. La operación ({action}) se realizó correctamente."

        if df.empty:
            return "No se encontraron resultados."

        numeric_cols = df.select_dtypes(include=[np.number]).columns
        stats = {}
        for col in numeric_cols:
            data = pd.to_numeric(df[col], errors='coerce')
            stats[col] = {
                "min": float(data.min()) if not pd.isna(data.min()) else None,
                "max": float(data.max()) if not pd.isna(data.max()) else None,
                "avg": round(float(data.mean()), 2) if not pd.isna(data.mean()) else None
            }

        def convert_o(obj):
            if isinstance(obj, decimal.Decimal):
                return float(obj)
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()
            if isinstance(obj, (pd.Int64Dtype, np.int64)):
                return int(obj)
            if isinstance(obj, float) and pd.isna(obj):
                return None
            return str(obj)

        df_seguro = df.head(3).applymap(convert_o)
        muestra = df_seguro.to_dict('records')

        payload = {
            "model": "llama-3.1-8b-instant",
            "temperature": 0,
            "max_tokens": 120,
            "messages": [{
                "role": "system", 
                "content": prompt.format(
                    consulta_original=query,
                    columnas=", ".join(df.columns),
                    num_filas=len(df),
                    estadisticas_numericas=json.dumps(stats, ensure_ascii=False, default=str),
                    muestra_datos=json.dumps(muestra, indent=2, ensure_ascii=False, default=convert_o)
                )
            }]
        }

        try:
            with st.spinner("Generando resumen..."):
                r = requests.post(self.api_url, headers=self.headers, json=payload, timeout=15)
                r.raise_for_status()
                return r.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"Resumen básico: {len(df)} registros."

    def _format_sql(self, sql: str) -> str:
        keywords = ['SELECT', 'FROM', 'JOIN', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY', 'INSERT INTO', 'UPDATE', 'SET', 'DELETE']
        formatted = sql
        for kw in keywords:
            formatted = formatted.replace(f' {kw} ', f'\n{kw} ')
        lines = formatted.split('\n')
        return '\n'.join(['  ' + line.strip() if line.strip() not in keywords else line.strip() for line in lines])