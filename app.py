# ============================================================
# Filtro de Productos por Clave — Streamlit App
# ============================================================
# Aplicación web para filtrar productos de un archivo Excel
# usando claves de un segundo archivo Excel.
#
# Ejecutar con:  streamlit run app.py
# ============================================================

import streamlit as st
import pandas as pd
from io import BytesIO

# ── Configuración de la página ──────────────────────────────
st.set_page_config(
    page_title="Filtro de Productos por Clave",
    page_icon="📦",
    layout="centered",
)

# ── Estilos personalizados ──────────────────────────────────
st.markdown(
    """
    <style>
    /* Tipografía general */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Encabezado principal */
    .main-title {
        text-align: center;
        font-size: 2.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1e3a5f, #4a90d9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center;
        color: #666;
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }

    /* Cards para las secciones de carga */
    .upload-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .upload-card h3 {
        margin-top: 0;
        color: #1e3a5f;
    }

    /* Botón de procesar */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #1e3a5f, #4a90d9);
        color: white;
        font-weight: 600;
        font-size: 1.1rem;
        padding: 0.75rem;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        transition: transform 0.15s, box-shadow 0.15s;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(74, 144, 217, 0.35);
    }

    /* Métricas */
    .metric-row {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    .metric-box {
        flex: 1;
        background: linear-gradient(135deg, #eef4fb, #d6e6f9);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .metric-box .number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e3a5f;
    }
    .metric-box .label {
        font-size: 0.85rem;
        color: #4a6a8a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Encabezado ──────────────────────────────────────────────
st.markdown('<p class="main-title">📦 Filtro de Productos por Clave</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-title">'
    "Sube un archivo principal de productos y un archivo con claves. "
    "El sistema filtrará los productos cuyas claves coincidan y generará "
    "un nuevo archivo Excel para descargar."
    "</p>",
    unsafe_allow_html=True,
)

# ── Funciones auxiliares ────────────────────────────────────


@st.cache_data(show_spinner=False)
def leer_excel(archivo: BytesIO, nombre: str) -> pd.DataFrame:
    """Lee un archivo Excel tratando la columna 'Clave' como texto."""
    try:
        df = pd.read_excel(archivo, dtype={"Clave": str}, engine="openpyxl")
    except Exception:
        # Fallback para archivos .xls (formato antiguo)
        df = pd.read_excel(archivo, dtype={"Clave": str})

    # Asegurar que la columna Clave sea string y eliminar espacios
    if "Clave" in df.columns:
        df["Clave"] = df["Clave"].astype(str).str.strip()

    return df


def generar_excel(df: pd.DataFrame) -> bytes:
    """Genera un archivo Excel en memoria a partir de un DataFrame."""
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Productos Filtrados")
    return buffer.getvalue()


# ── Sección 1: Archivo principal ────────────────────────────
st.markdown(
    '<div class="upload-card">'
    "<h3>📂 Archivo principal de productos</h3>"
    "<p>Este archivo debe contener al menos las columnas: "
    "<strong>Clave</strong>, <strong>Producto</strong>, "
    "<strong>Unidad de Medida</strong> e "
    "<strong>Inventarios Teóricos</strong>.</p>"
    "</div>",
    unsafe_allow_html=True,
)
archivo_principal = st.file_uploader(
    "Subir archivo principal de productos (Excel)",
    type=["xlsx", "xls"],
    key="principal",
)

# ── Sección 2: Archivo de claves ────────────────────────────
st.markdown(
    '<div class="upload-card">'
    "<h3>🔑 Archivo con claves a buscar</h3>"
    "<p>Este archivo debe contener al menos la columna "
    "<strong>Clave</strong>.</p>"
    "</div>",
    unsafe_allow_html=True,
)
archivo_claves = st.file_uploader(
    "Subir archivo con claves a buscar",
    type=["xlsx", "xls"],
    key="claves",
)

# ── Separador visual ────────────────────────────────────────
st.markdown("---")

# ── Botón de procesamiento ──────────────────────────────────
procesar = st.button("🚀 Procesar archivos")

if procesar:
    # ── Validación de carga ──────────────────────────────────
    if archivo_principal is None and archivo_claves is None:
        st.warning("⚠️ No has cargado ningún archivo. Sube ambos archivos para continuar.")
        st.stop()
    if archivo_principal is None:
        st.warning("⚠️ Falta el archivo principal de productos.")
        st.stop()
    if archivo_claves is None:
        st.warning("⚠️ Falta el archivo con claves a buscar.")
        st.stop()

    # ── Lectura de archivos ──────────────────────────────────
    with st.spinner("Leyendo archivos…"):
        try:
            df_principal = leer_excel(archivo_principal, "principal")
        except Exception as e:
            st.error(f"❌ Error al leer el archivo principal: {e}")
            st.stop()

        try:
            df_claves = leer_excel(archivo_claves, "claves")
        except Exception as e:
            st.error(f"❌ Error al leer el archivo de claves: {e}")
            st.stop()

    # ── Validación de columnas ───────────────────────────────
    columnas_requeridas = {"Clave", "Producto", "Unidad de Medida", "Inventarios Teóricos"}
    columnas_faltantes = columnas_requeridas - set(df_principal.columns)

    if columnas_faltantes:
        st.error(
            f"❌ El archivo principal no contiene las columnas requeridas: "
            f"**{', '.join(sorted(columnas_faltantes))}**.\n\n"
            f"Columnas encontradas: {', '.join(df_principal.columns.tolist())}"
        )
        st.stop()

    if "Clave" not in df_claves.columns:
        st.error(
            "❌ El archivo de claves no contiene la columna **Clave**.\n\n"
            f"Columnas encontradas: {', '.join(df_claves.columns.tolist())}"
        )
        st.stop()

    # ── Validación de contenido ──────────────────────────────
    if df_principal.empty:
        st.error("❌ El archivo principal está vacío.")
        st.stop()

    if df_claves.empty:
        st.error("❌ El archivo de claves está vacío.")
        st.stop()

    # ── Filtrado ─────────────────────────────────────────────
    with st.spinner("Filtrando productos…"):
        lista_claves = df_claves["Clave"].dropna().unique().tolist()
        resultado = df_principal[df_principal["Clave"].isin(lista_claves)].copy()
        resultado = resultado[["Clave", "Producto", "Unidad de Medida", "Inventarios Teóricos"]]

    # ── Resultados ───────────────────────────────────────────
    total_principal = len(df_principal)
    total_claves = len(lista_claves)
    total_encontrados = len(resultado)
    no_encontrados = total_claves - total_encontrados

    # Métricas visuales
    st.markdown(
        f"""
        <div class="metric-row">
            <div class="metric-box">
                <div class="number">{total_principal:,}</div>
                <div class="label">Productos en archivo principal</div>
            </div>
            <div class="metric-box">
                <div class="number">{total_claves:,}</div>
                <div class="label">Claves a buscar</div>
            </div>
            <div class="metric-box">
                <div class="number">{total_encontrados:,}</div>
                <div class="label">Productos encontrados</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if total_encontrados == 0:
        st.warning("⚠️ No se encontraron coincidencias entre ambos archivos.")
        st.stop()

    st.success(
        f"✅ Se encontraron **{total_encontrados}** productos de "
        f"**{total_claves}** claves buscadas."
    )

    if no_encontrados > 0:
        # Mostrar claves no encontradas
        claves_encontradas = set(resultado["Clave"].unique())
        claves_no_encontradas = [c for c in lista_claves if c not in claves_encontradas]
        with st.expander(f"⚠️ {no_encontrados} claves no encontradas en el archivo principal"):
            st.dataframe(
                pd.DataFrame({"Clave no encontrada": claves_no_encontradas}),
                use_container_width=True,
            )

    # ── Vista previa ─────────────────────────────────────────
    st.subheader("Vista previa de resultados")
    st.dataframe(resultado, use_container_width=True, height=400)

    # ── Descarga ─────────────────────────────────────────────
    excel_bytes = generar_excel(resultado)

    st.download_button(
        label="📥 Descargar productos_filtrados.xlsx",
        data=excel_bytes,
        file_name="productos_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# ── Footer ──────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#aaa; font-size:0.85rem;">'
    "Filtro de Productos por Clave · Hecho con ❤️ y Streamlit"
    "</p>",
    unsafe_allow_html=True,
)


