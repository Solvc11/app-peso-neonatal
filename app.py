import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="App Clínica Peso Neonatal", layout="wide")

st.title("🩺 App Clínica - Control de Peso Neonatal")

# Inicializar datos
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Sala",
        "Peso Nacimiento",
        "Peso 1DDV", "Δ g 1DDV", "% 1DDV",
        "Peso 2DDV", "Δ g 2DDV", "% 2DDV",
        "Peso 3DDV", "Δ g 3DDV", "% 3DDV",
        "ALERTA"
    ])

# Función cálculo

def calcular(df):
    for i in [1, 2, 3]:
        df[f"Δ g {i}DDV"] = (df["Peso Nacimiento"] - df[f"Peso {i}DDV"]).astype(int)
        df[f"% {i}DDV"] = ((df[f"Δ g {i}DDV"] / df["Peso Nacimiento"]) * 100).round(1)

    # ALERTA clínica
    condiciones = []
    for i in df.index:
        if df.loc[i, "% 3DDV"] > 10 or df.loc[i, "% 2DDV"] > 10:
            condiciones.append("🔴 Alto")
        elif df.loc[i, "% 1DDV"] > 5:
            condiciones.append("🟡 Moderado")
        else:
            condiciones.append("🟢 Normal")

    df["ALERTA"] = condiciones

    return df

# Ingreso de datos
with st.form("form"):
    col1, col2 = st.columns(2)

    with col1:
        sala = st.text_input("Sala")
        pn = st.number_input("Peso Nacimiento (g)", min_value=0, step=1, format="%d")

    with col2:
        d1 = st.number_input("Peso 1DDV (g)", min_value=0, step=1, format="%d")
        d2 = st.number_input("Peso 2DDV (g)", min_value=0, step=1, format="%d")
        d3 = st.number_input("Peso 3DDV (g)", min_value=0, step=1, format="%d")

    submit = st.form_submit_button("➕ Agregar Registro")

    if submit:
        new = pd.DataFrame([[sala, int(pn), int(d1), 0, 0, int(d2), 0, 0, int(d3), 0, 0, ""]], columns=st.session_state.data.columns)
        st.session_state.data = pd.concat([st.session_state.data, new], ignore_index=True)
        st.session_state.data = calcular(st.session_state.data)

# Estilo SOLO en celdas críticas

def highlight_cells(df):
    styles = pd.DataFrame('', index=df.index, columns=df.columns)

    for i in df.index:
        if df.loc[i, "% 1DDV"] > 5:
            styles.loc[i, "% 1DDV"] = 'background-color: #ffe066'
        if df.loc[i, "% 2DDV"] > 10:
            styles.loc[i, "% 2DDV"] = 'background-color: #ff4d4d'
        if df.loc[i, "% 3DDV"] > 10:
            styles.loc[i, "% 3DDV"] = 'background-color: #b30000'

    return styles

# Mostrar tabla compacta
if not st.session_state.data.empty:
    st.subheader("📋 Tabla Clínica")

    df_original = st.session_state.data.copy()
    df_display = df_original.copy()

    # Formato porcentaje visual
    for col in ["% 1DDV", "% 2DDV", "% 3DDV"]:
        df_display[col] = df_display[col].astype(str) + " %"

    st.dataframe(
        df_display.style
        .set_properties(**{'font-size': '12px'})
        .apply(lambda _: highlight_cells(df_original), axis=None),
        use_container_width=True
    )

    # 📊 Gráfico de pérdidas
    st.subheader("📊 Evolución de pérdida de peso (%)")

    df_chart = df_original[["% 1DDV", "% 2DDV", "% 3DDV"]]
    st.line_chart(df_chart)

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
    filas = st.multiselect("Seleccionar registros", st.session_state.data.index)

    if filas:
        df_sel = st.session_state.data.loc[filas]
        st.write(df_sel)

        csv = df_sel.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Descargar CSV", csv, "reporte_neonatal.csv", "text/csv")

        html = df_sel.to_html(index=False)
        st.download_button("🖨️ Descargar para imprimir (HTML)", html, "reporte.html", "text/html")

# Limpiar datos
if st.button("🧹 Limpiar base completa"):
    st.session_state.data = pd.DataFrame(columns=st.session_state.data.columns)

# Footer
st.markdown("---")
st.caption(f"Última actualización: {datetime.now().strftime('%d-%m-%Y %H:%M')}")
