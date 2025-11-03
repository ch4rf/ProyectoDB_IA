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
            return f"Operación de {action} completada. Filas afectadas: {affected}."

        if df.empty:
            return "No se encontraron resultados que coincidan con la consulta."

        # ✅ ANÁLISIS MEJORADO DE COLUMNAS NUMÉRICAS
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        # ✅ FORZAR DETECCIÓN DE COLUMNAS CRÍTICAS
        critical_numeric_cols = ['calificacion', 'promedio', 'edad', 'creditos', 'monto', 'experiencia_anos']
        for col in critical_numeric_cols:
            if col in df.columns and col not in numeric_cols:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    if pd.api.types.is_numeric_dtype(df[col]):
                        numeric_cols = numeric_cols.union([col])
                except Exception as e:
                    st.warning(f"No se pudo convertir {col} a numérico: {e}")

        # ✅ CALCULAR ESTADÍSTICAS ROBUSTAS
        stats = {}
        for col in numeric_cols:
            data = pd.to_numeric(df[col], errors='coerce').dropna()
            if len(data) > 0:
                stats[col] = {
                    "min": float(data.min()),
                    "max": float(data.max()),
                    "avg": round(float(data.mean()), 2),
                    "count": len(data),
                    "null_count": df[col].isnull().sum(),
                    "total_rows": len(df)
                }

        # ✅ MUESTRA INTELIGENTE MEJORADA
        sample_size = min(5, len(df))
        
        df_for_sampling = df.copy()
        
        # Asegurar conversión numérica para muestreo
        for col in df_for_sampling.columns:
            if df_for_sampling[col].dtype == 'object':
                converted = pd.to_numeric(df_for_sampling[col], errors='coerce')
                if not converted.isna().all():
                    df_for_sampling[col] = converted

        try:
            # Estrategia de muestreo balanceado
            if 'calificacion' in df.columns and pd.api.types.is_numeric_dtype(df_for_sampling.get('calificacion')):
                # Tomar mejores y peores para análisis balanceado
                top_samples = df_for_sampling.nlargest(sample_size // 2, 'calificacion')
                bottom_samples = df_for_sampling.nsmallest(sample_size // 2, 'calificacion')
                df_sample = pd.concat([top_samples, bottom_samples]).drop_duplicates()
                df_sample = df.loc[df_sample.index]
            elif len(numeric_cols) > 0:
                df_sample = df_for_sampling.nlargest(sample_size, numeric_cols[0])
                df_sample = df.loc[df_sample.index]
            else:
                df_sample = df.sample(n=min(sample_size, len(df)), random_state=42) if len(df) > sample_size else df
                
        except Exception as e:
            st.warning(f"Usando muestreo simple debido a: {e}")
            df_sample = df.head(sample_size)

        def convert_o(obj):
            if isinstance(obj, (decimal.Decimal, np.integer)):
                return float(obj) if isinstance(obj, decimal.Decimal) else int(obj)
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()
            if isinstance(obj, float) and pd.isna(obj):
                return None
            return str(obj)

        muestra = df_sample.applymap(convert_o).to_dict('records')

        payload = {
            "model": "llama-3.1-8b-instant",
            "temperature": 0.1,
            "max_tokens": 200,
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
            with st.spinner("Analizando resultados..."):
                r = requests.post(self.api_url, headers=self.headers, json=payload, timeout=20)
                r.raise_for_status()
                return r.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            if len(df) > 0:
                return f"Análisis básico: {len(df)} registros encontrados. " \
                       f"Columnas: {', '.join(df.columns[:3])}{'...' if len(df.columns) > 3 else ''}"
            return "Resultados procesados correctamente."

    def _format_sql(self, sql: str) -> str:
        keywords = ['SELECT', 'FROM', 'JOIN', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY', 'INSERT INTO', 'UPDATE', 'SET', 'DELETE']
        formatted = sql
        for kw in keywords:
            formatted = formatted.replace(f' {kw} ', f'\n{kw} ')
        lines = formatted.split('\n')
        return '\n'.join(['  ' + line.strip() if line.strip() not in keywords else line.strip() for line in lines])