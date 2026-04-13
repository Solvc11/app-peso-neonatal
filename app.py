# ==============================
# 🧾 SELECCIÓN E IMPRESIÓN
# ==============================

st.subheader("🧾 Seleccionar pacientes para impresión")

# Si existe columna identificadora
if id_candidates:
    seleccion = st.multiselect(
        "Selecciona pacientes",
        options=df[id_col].unique(),
        default=df[id_col].unique()
    )
    df_filtrado = df[df[id_col].isin(seleccion)]
else:
    st.info("No se encontró columna identificadora, se imprimirá toda la tabla.")
    df_filtrado = df.copy()

# Vista previa
st.subheader("📋 Vista previa para impresión")
st.dataframe(df_filtrado)

# ==============================
# 🎨 FORMATO PARA IMPRESIÓN
# ==============================

def highlight_row(row):
    try:
        if row["% perdida 3ddv"] > 10:
            return ['background-color: #ffcccc'] * len(row)
    except:
        pass
    return [''] * len(row)

styled_print = df_filtrado.style.apply(highlight_row, axis=1)

# Crear HTML con formato clínico
html = f"""
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
        }}
        h2 {{
            text-align: center;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
        }}
        th, td {{
            border: 1px solid #ccc;
            padding: 6px;
            text-align: center;
        }}
        th {{
            background-color: #f2f2f2;
        }}
    </style>
</head>
<body>
    <h2>Informe de Peso Neonatal</h2>
    {styled_print.to_html(index=False)}
</body>
</html>
"""

# Botón de descarga
st.download_button(
    "🖨️ Descargar e imprimir selección",
    data=html,
    file_name="informe_peso_neonatal.html",
    mime="text/html"
)
