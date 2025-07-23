import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import requests # <--- NUEVA IMPORTACIÓN
import io       # <--- NUEVA IMPORTACIÓN

# --- 1. Configuración de la Página del Dashboard ---
st.set_page_config(
    page_title="Avances PAPE-Censo del Bienestar al 20 junto 2025",
    page_icon="📊",
    layout="wide"
)

# 2. Función de Carga Mejorada (sin caché y usando 'requests')
# Se eliminó @st.cache_data temporalmente para forzar la recarga
def cargar_datos_desde_google_sheets():
    SHEET_ID = "1R6tJg9t0qEzBcZuZvoA55kaevsr-UmKAguoPcBp48Ss"
    GID_MANZANA = "0"
    GID_COLONIA = "557129763"
    GID_CRUDOS = "2039831845"
    GID_LIMPIOS = "901947724"
    
    base_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
    
    def fetch_csv(gid):
        url = f"{base_url}&gid={gid}"
        try:
            response = requests.get(url)
            response.raise_for_status() # Lanza un error si la petición falla (ej. 401, 404)
            # Usamos io.StringIO para que pandas lea el texto de la respuesta como si fuera un archivo
            return pd.read_csv(io.StringIO(response.text), low_memory=False)
        except requests.exceptions.RequestException as e:
            st.error(f"Error de red al intentar cargar la hoja con GID {gid}: {e}")
            return None

    df_manzana = fetch_csv(GID_MANZANA)
    df_colonia = fetch_csv(GID_COLONIA)
    df_crudo = fetch_csv(GID_CRUDOS)
    df_limpio = fetch_csv(GID_LIMPIOS)

    if all(df is not None for df in [df_manzana, df_colonia, df_crudo, df_limpio]):
        nombre_reporte = f"Reporte del G-Sheet ID: ...{SHEET_ID[-6:]}"
        return df_manzana, df_colonia, df_crudo, df_limpio, nombre_reporte
    else:
        return None, None, None, None, None

# --- 3. Cargar los Datos ---
df_manzana, df_colonia, df_crudo, df_limpio, nombre_reporte = cargar_datos_desde_google_sheets()

# --- 4. Construcción de la Interfaz del Dashboard ---
st.title("📊 Dashboard de Calidad de Datos Censo en campo")

if df_manzana is None:
    st.warning("No se pudieron cargar los datos. Por favor, revisa la configuración de URLs y GIDs en el script.")
else:
    st.success(f"Mostrando análisis: **{nombre_reporte}**")
    
    # KPIs de Avance de Captura vs Meta
    st.markdown("### Avance de Captura vs Meta")
    meta_registros = 16601
    conteo_registros = len(df_crudo)
    avance_registros = (conteo_registros / meta_registros) * 100
    st.metric("Avance de Registros", f"{conteo_registros:,} / {meta_registros:,}", f"{avance_registros:.1f}%")
    st.progress(avance_registros / 100)
    st.markdown("---")

    # Impacto del Proceso de Limpieza
    st.markdown("### Impacto del Proceso de Limpieza")
    conteo_limpio = len(df_limpio)
    registros_eliminados = conteo_registros - conteo_limpio
    col4, col5, col6 = st.columns(3)
    col4.metric("Registros en Base Cruda", f"{conteo_registros:,}")
    col5.metric("Registros en Base Limpia", f"{conteo_limpio:,}", delta=f"-{registros_eliminados} registros", delta_color="inverse")
    col6.metric("Calidad de la Base", f"{((conteo_limpio/conteo_registros)*100):.1f}%")
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
    envios_campana = 718; entregas_campana = 628; aperturas_campana = 455; clics_campana = 61
    tasa_entrega = (entregas_campana / envios_campana) * 100; tasa_apertura = (aperturas_campana / entregas_campana) * 100; tasa_clics_ctr = (clics_campana / entregas_campana) * 100
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    col_c1.metric("Envíos Totales", f"{envios_campana}"); col_c2.metric("Tasa de Entrega", f"{tasa_entrega:.1f}%", f"{entregas_campana} entregados"); col_c3.metric("Tasa de Apertura", f"{tasa_apertura:.1f}%", f"{aperturas_campana} aperturas"); col_c4.metric("Tasa de Clics (CTR)", f"{tasa_clics_ctr:.1f}%", f"{clics_campana} clics")
    st.markdown("---")


# --- Visualizaciones de Errores de Calidad (VERSIÓN CORREGIDA) ---
st.markdown("---")
st.markdown("### Visualización de Errores de Calidad")
plt.style.use('seaborn-v0_8-talk')

# Creamos dos columnas para poner los gráficos de manzana lado a lado
col7, col8 = st.columns(2)

with col7:
    # Este código está correctamente indentado porque va DENTRO del bloque 'with col7'
    st.markdown("##### Top 10 Áreas (AGEB-Manzana) por Errores")
    top_10_manzana = df_manzana.head(10).copy()
    top_10_manzana['etiqueta_area'] = top_10_manzana['ageb'].astype(str) + ' - ' + top_10_manzana['manzana'].astype(str)
    data_plot_manzana = top_10_manzana.set_index('etiqueta_area').sort_values(by='total_errores', ascending=True)
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.barh(data_plot_manzana.index, data_plot_manzana['total_errores'], color='#4a7ab5')
    ax1.set_xlabel('Número Total de Errores')
    plt.tight_layout()
    st.pyplot(fig1)

with col8:
    # Este código también está correctamente indentado
    st.markdown("##### Desglose de Errores de Correo (Top 10 Áreas)")
    email_error_cols = ['error_correo_vacio', 'error_dominio_correo']
    data_plot_email = top_10_manzana.copy()
    data_plot_email['total_email_errors'] = data_plot_email[email_error_cols].sum(axis=1)
    data_plot_email = data_plot_email.set_index('etiqueta_area').sort_values(by='total_email_errors', ascending=True)
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    data_plot_email[email_error_cols].plot(kind='barh', stacked=True, ax=ax2, color=['#d9534f', '#f0ad4e'])
    ax2.set_xlabel('Número de Errores de Correo')
    ax2.set_ylabel('')
    ax2.legend(title='Tipo de Error', labels=['Correo Vacío', 'Dominio Incorrecto'])
    plt.tight_layout()
    st.pyplot(fig2)

# Esta sección vuelve al nivel principal, sin indentación
st.markdown("---")
st.markdown("#### Top 10 Colonias por Total de Errores")
top_10_colonias = df_colonia.head(10).set_index('colonia_estandarizada').sort_values(by='total_errores', ascending=True)
fig3, ax3 = plt.subplots(figsize=(12, 7))
ax3.barh(top_10_colonias.index, top_10_colonias['total_errores'], color='#5cb85c')
ax3.set_xlabel('Número Total de Errores Identificados')
plt.tight_layout()
st.pyplot(fig3)

# --- Explorador de Datos de Errores (VERSIÓN CORREGIDA) ---
# Esta sección debe estar al mismo nivel que los títulos principales, sin indentación.

st.markdown("---")
st.markdown("### Explorador de Datos de Errores")

if st.checkbox("Mostrar reporte detallado por AGEB y Manzana"):
    # Esta línea está correctamente indentada porque depende del 'if'
    st.dataframe(df_manzana)

if st.checkbox("Mostrar reporte detallado por Colonia"):
    # Esta línea también está correctamente indentada
    st.dataframe(df_colonia)