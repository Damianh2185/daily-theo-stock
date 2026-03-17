# ============================================================
# Filtro de Productos por Clave — Streamlit App
# ============================================================
# Aplicación web para filtrar productos de un archivo Excel
# usando claves manuales o una lista predeterminada de artículos.
#
# Ejecutar con:  streamlit run app.py
# ============================================================

import streamlit as st
import pandas as pd
from io import BytesIO
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers
from openpyxl.utils import get_column_letter

# ── Configuración de la página ──────────────────────────────
st.set_page_config(
    page_title="Filtro de Productos · Inventario Pro",
    page_icon="📦",
    layout="wide",
)

# ── Estilos personalizados ──────────────────────────────────
st.markdown(
    """
    <style>
    /* ═══ Tipografía y base ═══ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ═══ Ocultar decoración nativa de Streamlit ═══ */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.5rem; max-width: 960px; margin: auto; }

    /* ═══ Header ═══ */
    .app-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding-bottom: 1rem;
        margin-bottom: 1.2rem;
        border-bottom: 1px solid #e2e8f0;
    }
    .app-header-icon {
        width: 42px;
        height: 42px;
        background: linear-gradient(135deg, #1e3a5f, #4a90d9);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        flex-shrink: 0;
    }
    .app-header-text h1 {
        font-size: 1.35rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
        line-height: 1.3;
    }
    .app-header-text p {
        font-size: 0.82rem;
        color: #94a3b8;
        margin: 0;
        font-weight: 400;
    }

    /* ═══ Section titles ═══ */
    .section-title {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #8ca3bf;
        margin-bottom: 0.8rem;
        padding-left: 2px;
    }

    /* ═══ Mode selector pills ═══ */
    .mode-wrapper {
        background: #f8fafc;
        border-radius: 12px;
        padding: 0.6rem 1rem;
        margin-bottom: 1.2rem;
        border: 1px solid #e2e8f0;
    }
    div.stRadio > div { gap: 0.5rem; }
    div.stRadio > div > label {
        background: white;
        border: 1.5px solid #e2e8f0;
        border-radius: 12px;
        padding: 0.7rem 1.2rem !important;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    div.stRadio > div > label:hover {
        border-color: #4a90d9;
        background: #f0f7ff;
    }
    div.stRadio > div > label[data-checked="true"],
    div.stRadio > div > label[aria-checked="true"] {
        background: linear-gradient(135deg, #1e3a5f, #2c5364);
        color: white;
        border-color: #1e3a5f;
    }

    /* ═══ Upload cards ═══ */
    .upload-card {
        background: #ffffff;
        border: 1.5px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem 1.8rem;
        margin-bottom: 1.2rem;
        transition: all 0.25s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .upload-card:hover {
        border-color: #4a90d9;
        box-shadow: 0 4px 20px rgba(74,144,217,0.12);
        transform: translateY(-1px);
    }
    .upload-card .card-header {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        margin-bottom: 0.6rem;
    }
    .upload-card .card-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        flex-shrink: 0;
    }
    .upload-card .card-icon.blue { background: linear-gradient(135deg, #dbeafe, #bfdbfe); }
    .upload-card .card-icon.amber { background: linear-gradient(135deg, #fef3c7, #fde68a); }
    .upload-card .card-icon.green { background: linear-gradient(135deg, #d1fae5, #a7f3d0); }
    .upload-card h3 {
        margin: 0;
        font-size: 1.05rem;
        font-weight: 700;
        color: #1e293b;
    }
    .upload-card p {
        margin: 0;
        font-size: 0.85rem;
        color: #64748b;
        line-height: 1.4;
    }
    .upload-card .tag {
        display: inline-block;
        background: #f1f5f9;
        color: #475569;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 0.15rem 0.5rem;
        border-radius: 6px;
        margin-right: 0.3rem;
        margin-top: 0.4rem;
    }

    /* ═══ Process button ═══ */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #1e3a5f 0%, #2c5364 50%, #4a90d9 100%);
        background-size: 200% auto;
        color: white;
        font-weight: 700;
        font-size: 1.05rem;
        padding: 0.85rem 1.5rem;
        border: none;
        border-radius: 14px;
        cursor: pointer;
        letter-spacing: 0.3px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(30, 58, 95, 0.25);
    }
    div.stButton > button:hover {
        background-position: right center;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(30, 58, 95, 0.35);
    }
    div.stButton > button:active {
        transform: translateY(0);
    }

    /* ═══ Download button ═══ */
    div.stDownloadButton > button {
        width: 100%;
        background: linear-gradient(135deg, #059669, #10b981);
        color: white;
        font-weight: 700;
        font-size: 1.05rem;
        padding: 0.85rem 1.5rem;
        border: none;
        border-radius: 14px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(5, 150, 105, 0.25);
    }
    div.stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(5, 150, 105, 0.35);
    }

    /* ═══ Metrics ═══ */
    .metric-row {
        display: flex;
        gap: 1rem;
        margin: 1.2rem 0;
    }
    .metric-box {
        flex: 1;
        background: #ffffff;
        border: 1.5px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.2rem 1rem;
        text-align: center;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .metric-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    }
    .metric-box .icon {
        font-size: 1.5rem;
        margin-bottom: 0.3rem;
    }
    .metric-box .number {
        font-size: 2rem;
        font-weight: 800;
        color: #1e293b;
        letter-spacing: -1px;
    }
    .metric-box .label {
        font-size: 0.78rem;
        font-weight: 500;
        color: #94a3b8;
        margin-top: 0.15rem;
    }

    /* ═══ Divider ═══ */
    hr { border: none; border-top: 1px solid #e2e8f0; margin: 1.5rem 0; }

    /* ═══ Footer ═══ */
    .app-footer {
        text-align: center;
        padding: 1.5rem 0 1rem;
        color: #94a3b8;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .app-footer span { color: #ef4444; }

    /* ═══ Expander styling ═══ */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Encabezado ───────────────────────────────────────────────
st.markdown(
    """
    <div class="app-header">
        <div class="app-header-icon">📦</div>
        <div class="app-header-text">
            <h1>Filtro de Productos</h1>
            <p>Sube tu archivo principal y filtra con claves manuales o artículos predeterminados</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Artículos predeterminados ───────────────────────────────
# Extraídos de la imagen del formato de inventario proporcionada por el usuario
ARTICULOS_DEFAULT = [
    {"Almacen": "PTY GUY FIERI - COCINA", "Sub-Categoria": "Frutas y Verduras", "Código": "000235", "Descripción": "Papa Francesa 5/16 Sin Cascara y Con Cobertura"},
    {"Almacen": "PTY GUY FIERI - COCINA", "Sub-Categoria": "Frutas y Verduras", "Código": "001221", "Descripción": "Cebolla Blanca Jumbo"},
    {"Almacen": "PTY GUY FIERI - COCINA", "Sub-Categoria": "Frutas y Verduras", "Código": "016240", "Descripción": "Tomate 3x3"},
    {"Almacen": "PTY GUY FIERI - COCINA", "Sub-Categoria": "Carnes Frías", "Código": "002621", "Descripción": "Tocino De Cerdo Rebanado*"},
    {"Almacen": "PTY GUY FIERI - COCINA", "Sub-Categoria": "Abarrotes Secos", "Código": "001183", "Descripción": "Pepinillos Kosher Enteros"},
    {"Almacen": "PTY GUY FIERI - COCINA", "Sub-Categoria": "Derivados Lácteos", "Código": "001937", "Descripción": "Mantequilla Sin Sal"},
    {"Almacen": "PTY GUY FIERI - COCINA", "Sub-Categoria": "Abarrotes Secos", "Código": "001134", "Descripción": "Pimiento Morron Rojo Lata"},
    {"Almacen": "PTY GUY FIERI - COCINA", "Sub-Categoria": "Frutas y Verduras", "Código": "001093", "Descripción": "Cilantro"},
    {"Almacen": "PTY GUY FIERI - COCINA", "Sub-Categoria": "Derivados Lácteos", "Código": "001939", "Descripción": "Crema Agria"},
    {"Almacen": "PTY HOTDOG FLY - COCINA", "Sub-Categoria": "Panadería", "Código": "031757", "Descripción": "Hojaldre"},
    {"Almacen": "PTY HOTDOG FLY - COCINA", "Sub-Categoria": "Carnes Frías", "Código": "002621", "Descripción": "Tocino De Cerdo Rebanado*"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Aves", "Código": "016027", "Descripción": "Huevo AA"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Panadería", "Código": "040816", "Descripción": "Pan Molde Rebanado"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Panadería", "Código": "016147", "Descripción": "Tortilla Wraps"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Panadería", "Código": "010499", "Descripción": "Pan Frances (Michita)"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Panadería", "Código": "002373", "Descripción": "Pan De Hamburguesa HD"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Aves", "Código": "000809", "Descripción": "Pechuga De Pollo Entera Sin Hueso"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Carnes Rojas", "Código": "000890", "Descripción": "Falda de Res"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Carnes Frías", "Código": "002621", "Descripción": "Tocino De Cerdo Rebanado*"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Frutas y Verduras", "Código": "001313", "Descripción": "Zanahoria"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Frutas y Verduras", "Código": "001230", "Descripción": "Chayote"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Frutas y Verduras", "Código": "016092", "Descripción": "Platano Maduro"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Derivados Lácteos", "Código": "002019", "Descripción": "Queso Cheddar Rebanado"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Panadería", "Código": "039151", "Descripción": "Wafles"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Frutas y Verduras", "Código": "016152", "Descripción": "Uvas Rojas sin Semilla"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Frutas y Verduras", "Código": "001221", "Descripción": "Cebolla Blanca Jumbo"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Frutas y Verduras", "Código": "001052", "Descripción": "Melón"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Abarrotes Secos", "Código": "000541", "Descripción": "Pasta Fettuccine"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Frutas y Verduras", "Código": "001186", "Descripción": "Pulpa De Aguacate"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Frutas y Verduras", "Código": "015971", "Descripción": "Culantro"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Carnes Frías", "Código": "000711", "Descripción": "Jamón De Cerdo Americano"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Frutas y Verduras", "Código": "001110", "Descripción": "Perejil Chino"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Abarrotes Secos", "Código": "000413", "Descripción": "Sirope Para Pancake"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Derivados Lácteos", "Código": "002072", "Descripción": "Queso Prensado"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Derivados Lácteos", "Código": "008574", "Descripción": "Crema De Batir Para Pastelería"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Frutas y Verduras", "Código": "001026", "Descripción": "Fresa"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Aderezos y Condimentos", "Código": "040468", "Descripción": "Sazonador de Costilla de Res"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Frutas y Verduras", "Código": "001091", "Descripción": "Cebollín"},
    {"Almacen": "PTY PETIT GOURMET - COCINA", "Sub-Categoria": "Frutas y Verduras", "Código": "001270", "Descripción": "Jitomate Cherry"},
]

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


def generar_excel_inventario(df: pd.DataFrame) -> bytes:
    """Genera un archivo Excel de inventario con formato profesional."""
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Inventario")
        ws = writer.sheets["Inventario"]

        # ── Paleta de colores por Almacen ────────────────────
        # Colores de fondo (suaves) y texto para cada almacen
        ALMACEN_COLORS = {
            "PTY GUY FIERI - COCINA": {
                "fill": PatternFill(start_color="FCE4E4", end_color="FCE4E4", fill_type="solid"),  # Rojo suave
                "font_color": "8B0000",  # Rojo oscuro
            },
            "PTY HOTDOG FLY - COCINA": {
                "fill": PatternFill(start_color="E0F2F1", end_color="E0F2F1", fill_type="solid"),  # Verde teal suave
                "font_color": "004D40",  # Teal oscuro
            },
            "PTY PETIT GOURMET - COCINA": {
                "fill": PatternFill(start_color="E3F2FD", end_color="E3F2FD", fill_type="solid"),  # Azul suave
                "font_color": "0D47A1",  # Azul oscuro
            },
        }
        # Color por defecto para almacenes no mapeados
        DEFAULT_STYLE = {
            "fill": PatternFill(start_color="F5F5F5", end_color="F5F5F5", fill_type="solid"),
            "font_color": "333333",
        }

        # ── Estilos comunes ──────────────────────────────────
        header_fill = PatternFill(start_color="1E3A5F", end_color="1E3A5F", fill_type="solid")
        header_font = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        thin_border = Border(
            left=Side(style="thin", color="B0BEC5"),
            right=Side(style="thin", color="B0BEC5"),
            top=Side(style="thin", color="B0BEC5"),
            bottom=Side(style="thin", color="B0BEC5"),
        )
        header_border = Border(
            left=Side(style="thin", color="0D2137"),
            right=Side(style="thin", color="0D2137"),
            top=Side(style="medium", color="0D2137"),
            bottom=Side(style="medium", color="4A90D9"),
        )

        cell_alignment = Alignment(vertical="center", wrap_text=False)
        center_alignment = Alignment(horizontal="center", vertical="center")
        number_format_2dec = '#,##0.00'

        # ── Anchos de columna ────────────────────────────────
        column_widths = {
            1: 32,   # Almacen
            2: 26,   # Sub-Categoria
            3: 14,   # Código
            4: 45,   # Descripción
            5: 16,   # conteo fisico
            6: 22,   # inventario merawey
            7: 16,   # diferencia
            8: 28,   # Observaciones
            9: 28,   # responsable del conteo
        }
        for col_num, width in column_widths.items():
            ws.column_dimensions[get_column_letter(col_num)].width = width

        # ── Formato del encabezado (fila 1) ──────────────────
        ws.row_dimensions[1].height = 30
        for col_idx in range(1, 10):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment
            cell.border = header_border

        # ── Formato de las filas de datos ────────────────────
        for row_idx in range(2, ws.max_row + 1):
            almacen_value = str(ws.cell(row=row_idx, column=1).value or "")
            style = ALMACEN_COLORS.get(almacen_value, DEFAULT_STYLE)
            row_fill = style["fill"]
            row_font_color = style["font_color"]

            ws.row_dimensions[row_idx].height = 22

            for col_idx in range(1, 10):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.fill = row_fill
                cell.border = thin_border
                cell.alignment = cell_alignment

                # Fuente: negrita para Almacen, normal para el resto
                if col_idx == 1:
                    cell.font = Font(name="Calibri", bold=True, color=row_font_color, size=10)
                else:
                    cell.font = Font(name="Calibri", color="333333", size=10)

                # Centrar código
                if col_idx == 3:
                    cell.alignment = center_alignment
                    cell.font = Font(name="Calibri", bold=True, color="333333", size=10)

                # Formato numérico con 2 decimales para columnas numéricas
                if col_idx in (5, 6, 7):  # conteo fisico, inventario merawey, diferencia
                    cell.alignment = center_alignment
                    if cell.value is not None and cell.value != "":
                        try:
                            cell.value = round(float(cell.value), 2)
                        except (ValueError, TypeError):
                            pass
                    cell.number_format = number_format_2dec

        # ── Congelar panel del encabezado ────────────────────
        ws.freeze_panes = "A2"

        # ── Filtro automático ────────────────────────────────
        ws.auto_filter.ref = ws.dimensions

    return buffer.getvalue()


# ── Selector de modo ────────────────────────────────────────
st.markdown('<div class="mode-wrapper">', unsafe_allow_html=True)

modo = st.radio(
    "Selecciona el modo de operación:",
    options=["📂 Carga Manual (subir dos archivos)", "📋 Artículos Predeterminados (Inventario)"],
    index=0,
    horizontal=True,
    help="Carga Manual: sube ambos archivos. Predeterminados: solo sube el archivo principal y se filtran los artículos ya cargados.",
)

st.markdown('</div>', unsafe_allow_html=True)

es_modo_predeterminado = "Predeterminados" in modo

# ── Sección 1: Archivo principal ────────────────────────────
st.markdown(
    '<div class="upload-card">'
    '<div class="card-header">'
    '<div class="card-icon blue">📂</div>'
    '<div><h3>Archivo principal de productos</h3></div>'
    '</div>'
    '<p>Este archivo debe contener las columnas requeridas para el procesamiento.</p>'
    '<span class="tag">Clave</span>'
    '<span class="tag">Producto</span>'
    '<span class="tag">Unidad de Medida</span>'
    '<span class="tag">Inventarios Teóricos</span>'
    "</div>",
    unsafe_allow_html=True,
)
archivo_principal = st.file_uploader(
    "Subir archivo principal de productos (Excel)",
    type=["xlsx", "xls"],
    key="principal",
)

# ── Sección 2: Archivo de claves (solo en modo manual) ──────
if not es_modo_predeterminado:
    st.markdown(
        '<div class="upload-card">'
        '<div class="card-header">'
        '<div class="card-icon amber">🔑</div>'
        '<div><h3>Archivo con claves a buscar</h3></div>'
        '</div>'
        '<p>Este archivo debe contener al menos la columna Clave.</p>'
        '<span class="tag">Clave</span>'
        "</div>",
        unsafe_allow_html=True,
    )
    archivo_claves = st.file_uploader(
        "Subir archivo con claves a buscar",
        type=["xlsx", "xls"],
        key="claves",
    )
else:
    archivo_claves = None
    # Mostrar vista previa de los artículos predeterminados
    st.markdown(
        '<div class="upload-card">'
        '<div class="card-header">'
        '<div class="card-icon green">📋</div>'
        '<div><h3>' + str(len(ARTICULOS_DEFAULT)) + ' artículos predeterminados cargados</h3></div>'
        '</div>'
        '<p>Los artículos de inventario ya están configurados. Expande para ver el detalle.</p>'
        "</div>",
        unsafe_allow_html=True,
    )
    with st.expander("🔍 Ver detalle de artículos predeterminados"):
        df_preview = pd.DataFrame(ARTICULOS_DEFAULT)
        st.dataframe(df_preview, use_container_width=True, height=300)

# ── Separador visual ────────────────────────────────────────
st.markdown("---")

# ── Botón de procesamiento ──────────────────────────────────
if es_modo_predeterminado:
    procesar = st.button("🚀 Procesar con artículos predeterminados")
else:
    procesar = st.button("🚀 Procesar archivos")

if procesar:
    # ── Validación de carga ──────────────────────────────────
    if archivo_principal is None:
        st.warning("⚠️ Falta el archivo principal de productos.")
        st.stop()

    if not es_modo_predeterminado and archivo_claves is None:
        st.warning("⚠️ Falta el archivo con claves a buscar.")
        st.stop()

    # ── Lectura del archivo principal ────────────────────────
    with st.spinner("Leyendo archivo principal…"):
        try:
            df_principal = leer_excel(archivo_principal, "principal")
        except Exception as e:
            st.error(f"❌ Error al leer el archivo principal: {e}")
            st.stop()

    # ── Validación de columnas del archivo principal ─────────
    columnas_requeridas = {"Clave", "Producto", "Unidad de Medida", "Inventarios Teóricos"}
    columnas_faltantes = columnas_requeridas - set(df_principal.columns)

    if columnas_faltantes:
        st.error(
            f"❌ El archivo principal no contiene las columnas requeridas: "
            f"**{', '.join(sorted(columnas_faltantes))}**.\n\n"
            f"Columnas encontradas: {', '.join(df_principal.columns.tolist())}"
        )
        st.stop()

    if df_principal.empty:
        st.error("❌ El archivo principal está vacío.")
        st.stop()

    # ═══════════════════════════════════════════════════════════
    # MODO PREDETERMINADO (Inventario)
    # ═══════════════════════════════════════════════════════════
    if es_modo_predeterminado:
        with st.spinner("Filtrando artículos predeterminados…"):
            df_default = pd.DataFrame(ARTICULOS_DEFAULT)

            # Obtener códigos únicos de los artículos predeterminados
            codigos_default = df_default["Código"].unique().tolist()

            # Crear un diccionario para buscar inventarios teóricos por clave
            inventarios = df_principal.set_index("Clave")["Inventarios Teóricos"].to_dict()

            # Construir el DataFrame de resultado con el formato de inventario
            filas_resultado = []
            for _, art in df_default.iterrows():
                codigo = art["Código"]
                inv_teorico = inventarios.get(codigo, "")
                filas_resultado.append({
                    "Almacen": art["Almacen"],
                    "Sub-Categoria": art["Sub-Categoria"],
                    "Código": codigo,
                    "Descripción": art["Descripción"],
                    "conteo fisico": "",
                    "inventario merawey": inv_teorico,
                    "diferencia": "",
                    "Observaciones": "",
                    "responsable del conteo": "",
                })

            resultado = pd.DataFrame(filas_resultado)

        # Contar resultados
        total_principal = len(df_principal)
        total_predeterminados = len(ARTICULOS_DEFAULT)
        codigos_encontrados = [c for c in codigos_default if c in inventarios]
        total_encontrados_unicos = len(codigos_encontrados)

        # Métricas visuales
        st.markdown(
            f"""
            <div class="metric-row">
                <div class="metric-box">
                    <div class="icon">📊</div>
                    <div class="number">{total_principal:,}</div>
                    <div class="label">Productos en archivo</div>
                </div>
                <div class="metric-box">
                    <div class="icon">📋</div>
                    <div class="number">{total_predeterminados:,}</div>
                    <div class="label">Art. predeterminados</div>
                </div>
                <div class="metric-box">
                    <div class="icon">✅</div>
                    <div class="number">{total_encontrados_unicos:,}</div>
                    <div class="label">Códigos encontrados</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Advertencia de códigos no encontrados
        codigos_no_encontrados = [c for c in codigos_default if c not in inventarios]
        if codigos_no_encontrados:
            with st.expander(f"⚠️ {len(codigos_no_encontrados)} códigos no encontrados en el archivo principal"):
                st.dataframe(
                    pd.DataFrame({"Código no encontrado": codigos_no_encontrados}),
                    use_container_width=True,
                )

        st.success(
            f"✅ Se generó el formato de inventario con **{len(resultado)}** artículos."
        )

        # Vista previa
        st.subheader("Vista previa del formato de inventario")
        st.dataframe(resultado, use_container_width=True, height=400)

        # Descarga
        excel_bytes = generar_excel_inventario(resultado)
        st.download_button(
            label="📥 Descargar inventario.xlsx",
            data=excel_bytes,
            file_name="inventario.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    # ═══════════════════════════════════════════════════════════
    # MODO MANUAL (Original)
    # ═══════════════════════════════════════════════════════════
    else:
        with st.spinner("Leyendo archivo de claves…"):
            try:
                df_claves = leer_excel(archivo_claves, "claves")
            except Exception as e:
                st.error(f"❌ Error al leer el archivo de claves: {e}")
                st.stop()

        if "Clave" not in df_claves.columns:
            st.error(
                "❌ El archivo de claves no contiene la columna **Clave**.\n\n"
                f"Columnas encontradas: {', '.join(df_claves.columns.tolist())}"
            )
            st.stop()

        if df_claves.empty:
            st.error("❌ El archivo de claves está vacío.")
            st.stop()

        # Filtrado
        with st.spinner("Filtrando productos…"):
            lista_claves = df_claves["Clave"].dropna().unique().tolist()
            resultado = df_principal[df_principal["Clave"].isin(lista_claves)].copy()
            resultado = resultado[["Clave", "Producto", "Unidad de Medida", "Inventarios Teóricos"]]

        # Resultados
        total_principal = len(df_principal)
        total_claves = len(lista_claves)
        total_encontrados = len(resultado)
        no_encontrados = total_claves - total_encontrados

        # Métricas visuales
        st.markdown(
            f"""
            <div class="metric-row">
                <div class="metric-box">
                    <div class="icon">📊</div>
                    <div class="number">{total_principal:,}</div>
                    <div class="label">Productos en archivo</div>
                </div>
                <div class="metric-box">
                    <div class="icon">🔑</div>
                    <div class="number">{total_claves:,}</div>
                    <div class="label">Claves a buscar</div>
                </div>
                <div class="metric-box">
                    <div class="icon">✅</div>
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
            claves_encontradas = set(resultado["Clave"].unique())
            claves_no_encontradas = [c for c in lista_claves if c not in claves_encontradas]
            with st.expander(f"⚠️ {no_encontrados} claves no encontradas en el archivo principal"):
                st.dataframe(
                    pd.DataFrame({"Clave no encontrada": claves_no_encontradas}),
                    use_container_width=True,
                )

        # Vista previa
        st.subheader("Vista previa de resultados")
        st.dataframe(resultado, use_container_width=True, height=400)

        # Descarga
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
    '<div class="app-footer">'
    "Inventario Pro · Filtro de Productos por Clave<br>"
    "Hecho con <span>❤️</span> y Streamlit"
    "</div>",
    unsafe_allow_html=True,
)
