import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
import re

# --- 1. Configuración de la Página del Dashboard ---
st.set_page_config(
    page_title="Dashboard de Calidad de Datos Censo del Bienestar",
    page_icon="📊",
    layout="wide"
)

# --- 2. Función para Cargar Todos los Datos Necesarios ---
@st.cache_data
def cargar_todos_los_datos():
    # ... (esta función no necesita cambios, la omito por brevedad pero debe estar en tu script) ...
    ruta_base = Path.cwd()
    ruta_crudos = ruta_base / "01_datos_crudos"
    ruta_maestros = ruta_base / "02_datos_maestros"
    ruta_reportes = ruta_base / "03_reportes_calidad"
    try:
        ruta_reporte_excel = max(ruta_reportes.glob('*.xlsx'), key=lambda p: p.stat().st_mtime)
        ruta_maestra_limpia = max(ruta_maestros.glob('*.csv'), key=lambda p: p.stat().st_mtime)
        ruta_crudo_reciente = max(ruta_crudos.glob('*.csv'), key=lambda p: p.stat().st_mtime)
        df_manzana = pd.read_excel(ruta_reporte_excel, sheet_name='Errores_por_AGEB_Manzana')
        df_colonia = pd.read_excel(ruta_reporte_excel, sheet_name='Errores_por_Colonia')
        df_crudo = pd.read_csv(ruta_crudo_reciente, low_memory=False)
        df_limpio = pd.read_csv(ruta_maestra_limpia, low_memory=False)
        return df_manzana, df_colonia, df_crudo, df_limpio, ruta_reporte_excel.name, ruta_crudo_reciente.name
    except (FileNotFoundError, ValueError):
        return None, None, None, None, None, None

# --- 3. Cargar los Datos ---
df_manzana, df_colonia, df_crudo, df_limpio, nombre_reporte, nombre_crudo = cargar_todos_los_datos()

# --- 4. Construcción de la Interfaz del Dashboard ---
st.title("📊 Dashboard de Calidad de Datos en Campo")

if df_manzana is None:
    st.error("No se encontró ningún archivo de reporte o de datos en las carpetas. Por favor, ejecuta el pipeline de limpieza primero.")
else:
    # Mensaje de Contexto Mejorado
    fecha_str_match = re.search(r'(\d{8})', nombre_crudo)
    fecha_legible = ""
    if fecha_str_match:
        fecha_dt = datetime.strptime(fecha_str_match.group(1), '%Y%m%d')
        meses = {1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril', 5: 'mayo', 6: 'junio', 
                 7: 'julio', 8: 'agosto', 9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'}
        fecha_legible = f"{fecha_dt.day} de {meses[fecha_dt.month]} de {fecha_dt.year}"
    st.info(f"Mostrando análisis generado a partir de la base de datos cruda del **{fecha_legible}**.")
    
    # KPIs de Avance de Captura vs Meta
    st.markdown("### Avance de Captura vs Meta")
    meta_registros = 16601
    conteo_registros_crudos = len(df_crudo)
    avance_registros = (conteo_registros_crudos / meta_registros) * 100
    st.metric("Avance de Registros", f"{conteo_registros_crudos:,} / {meta_registros:,}", f"{avance_registros:.1f}%")
    st.progress(avance_registros / 100)
    st.markdown("---")

    # Impacto del Proceso de Limpieza
    st.markdown("### Impacto del Proceso de Limpieza")
    conteo_limpio = len(df_limpio)
    registros_eliminados = conteo_registros_crudos - conteo_limpio
    col4, col5, col6 = st.columns(3)
    col4.metric("Registros en Base Cruda", f"{conteo_registros_crudos:,}")
    col5.metric("Registros en Base Limpia", f"{conteo_limpio:,}", delta=f"-{registros_eliminados} registros", delta_color="inverse")
    col6.metric("Calidad de la Base", f"{((conteo_limpio/conteo_registros_crudos)*100):.1f}%")
    st.markdown("---")
    
    # --- NUEVO: Resumen de Información de Contacto en Base Limpia ---
    st.markdown("### Resumen de Información de Contacto (Base Limpia)")
    
    total_registros_limpios = len(df_limpio)
    
    # Asumimos que las columnas en la base limpia se llaman 'celular_e164' y 'email'
    conteo_celular = df_limpio['celular_e164'].replace('', np.nan).notna().sum()
    porcentaje_celular = (conteo_celular / total_registros_limpios) * 100
    
    conteo_correo = df_limpio['email'].replace('', np.nan).notna().sum()
    porcentaje_correo = (conteo_correo / total_registros_limpios) * 100

    col7, col8, col9 = st.columns(3)
    col7.metric("Total Registros Limpios", f"{total_registros_limpios:,}")
    col8.metric("Con Celular", f"{conteo_celular:,}", f"{porcentaje_celular:.1f}% del total")
    col9.metric("Con Correo", f"{conteo_correo:,}", f"{porcentaje_correo:.1f}% del total")

    st.markdown("---")

    # KPIs de Campaña de Comunicación (Fijos)
    st.markdown("### Resultados de Campaña de Comunicación (Referencia)")
    # ... (esta sección no necesita cambios) ...
    
    st.markdown("---")

    # Visualizaciones de Errores de Calidad
    st.markdown("### Visualización de Errores de Calidad")
    # ... (esta sección no necesita cambios) ...

    # Explorador de Datos de Errores
    st.markdown("### Explorador de Datos de Errores")
    # ... (esta sección no necesita cambios) ...