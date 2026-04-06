import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="App Clínica Peso Neonatal", layout="wide")

st.title("🩺 App Clínica - Control de Peso Neonatal")

# Inicializar datos
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Sala", "Paciente", "Peso Nacimiento", 
        "Día 1", "Día 2", "Día 3",
        "Δ g Día 1", "Δ g Día 2", "Δ g Día 3",
        "% Día 1", "% Día 2", "% Día 3", "% Total"
    ])

# Función cálculo

def calcular(df):
    for i in [1, 2, 3]:
        df[f"Δ g Día {i}"] = df["Peso Nacimiento"] - df[f"Día {i}"]
        df[f"% Día {i}"] = (df[f"Δ g Día {i}"] / df["Peso Nacimiento"]) * 100

    df["% Total"] = ((df["Peso Nacimiento"] - df[["Día 1","Día 2","Día 3"]].min(axis=1)) / df["Peso Nacimiento"]) * 100
    return df

# Ingreso de datos
with st.form("form"):
    col1, col2 = st.columns(2)

    with col1:
        sala = st.text_input("Sala")
        paciente = st.text_input("Paciente")
        pn = st.number_input("Peso Nacimiento (g)", min_value=0.0)

    with col2:
        d1 = st.number_input("Peso Día 1 (g)", min_value=0.0)
        d2 = st.number_input("Peso Día 2 (g)", min_value=0.0)
        d3 = st.number_input("Peso Día 3 (g)", min_value=0.0)

    submit = st.form_submit_button("➕ Agregar Paciente")

    if submit:
        new = pd.DataFrame([[sala, paciente, pn, d1, d2, d3, 0, 0, 0, 0, 0, 0, 0]], columns=st.session_state.data.columns)
        st.session_state.data = pd.concat([st.session_state.data, new], ignore_index=True)
        st.session_state.data = calcular(st.session_state.data)

# Colores clínicos

def color_filas(row):
    estilos = [''] * len(row)

    if row["% Día 1"] > 5:
        estilos = ['background-color: #ff4d4d'] * len(row)
    if row["% Día 2"] > 10:
        estilos = ['background-color: #ff4d4d'] * len(row)
    if row["% Total"] > 10:
        estilos = ['background-color: #b30000'] * len(row)

    return estilos

# Mostrar tabla
if not st.session_state.data.empty:
    st.subheader("📋 Tabla Clínica")
    df = st.session_state.data
    st.dataframe(df.style.apply(color_filas, axis=1), use_container_width=True)

# Filtros
st.subheader("🔎 Filtrar por sala")
if not st.session_state.data.empty:
    salas = st.session_state.data["Sala"].unique()
    filtro = st.selectbox("Seleccionar sala", ["Todas"] + list(salas))

    if filtro != "Todas":
        df_filtrado = st.session_state.data[st.session_state.data["Sala"] == filtro]
    else:
        df_filtrado = st.session_state.data

    st.dataframe(df_filtrado, use_container_width=True)

# Selección e impresión
st.subheader("🖨️ Selección para imprimir")

if not st.session_state.data.empty:
    filas = st.multiselect("Seleccionar pacientes", st.session_state.data.index)

    if filas:
        df_sel = st.session_state.data.loc[filas]
        st.write(df_sel)

        # Exportar CSV
        csv = df_sel.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Descargar CSV", csv, "reporte_neonatal.csv", "text/csv")

        # Exportar HTML imprimible
        html = df_sel.to_html(index=False)
        st.download_button("🖨️ Descargar para imprimir (HTML)", html, "reporte.html", "text/html")

# Limpiar datos
if st.button("🧹 Limpiar base completa"):
    st.session_state.data = pd.DataFrame(columns=st.session_state.data.columns)

# Footer
st.markdown("---")
st.caption(f"Última actualización: {datetime.now().strftime('%d-%m-%Y %H:%M')}")
