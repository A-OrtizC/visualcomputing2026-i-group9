"""
╔══════════════════════════════════════════════════════════════════╗
║         VISIOLAB — Demo interactivo del módulo                   ║
║         Prueba todos los filtros con imagen o cámara             ║
╚══════════════════════════════════════════════════════════════════╝

Ejecución:
    streamlit run demo.py

Dependencias:
    pip install streamlit opencv-python numpy plotly Pillow
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

# ── Importar el módulo Dev 1 (debe estar en el mismo directorio) ──────────────
from filters import (
    FilterPipeline,
    ColorSpaceConverter,
    StreamlitBridge,
)

# ─────────────────────────────────────────────
#  CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="VisioLab · Demo",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS personalizado ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Fondo y tipografía general */
    .stApp { background-color: #0f1117; }
    .main .block-container { padding-top: 1.5rem; max-width: 1400px; }

    /* Header principal */
    .vl-header {
        background: linear-gradient(135deg, #1a1d2e 0%, #0f1117 100%);
        border: 1px solid #2a2d3e;
        border-radius: 12px;
        padding: 1.2rem 1.8rem;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .vl-header h1 {
        font-size: 1.6rem;
        font-weight: 700;
        color: #e8e8f0;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .vl-header .badge {
        background: #7c3aed22;
        border: 1px solid #7c3aed55;
        color: #a78bfa;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 2px 10px;
        border-radius: 20px;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    /* Panel de filtros aplicados */
    .filter-tag {
        display: inline-block;
        background: #1e1b4b;
        border: 1px solid #4338ca44;
        color: #818cf8;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        margin: 2px 3px;
        letter-spacing: 0.03em;
    }

    /* Métricas */
    .metric-box {
        background: #1a1d2e;
        border: 1px solid #2a2d3e;
        border-radius: 10px;
        padding: 0.9rem 1rem;
        text-align: center;
    }
    .metric-val {
        font-size: 1.4rem;
        font-weight: 700;
        color: #a78bfa;
        line-height: 1;
    }
    .metric-lbl {
        font-size: 0.72rem;
        color: #6b7280;
        margin-top: 4px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    /* Sección colapsable sidebar */
    .stExpander { border: 1px solid #2a2d3e !important; border-radius: 8px !important; }

    /* Botones */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────

st.markdown("""
<div class="vl-header">
    <span style="font-size:2rem">🔬</span>
    <div>
        <h1>VisioLab</h1>
        <span style="color:#6b7280; font-size:0.82rem">Pipeline de Procesamiento Espacial — módulo de filtros OpenCV</span>
    </div>
    <div style="margin-left:auto"><span class="badge">MVP Demo</span></div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  ESTADO DE SESIÓN
# ─────────────────────────────────────────────

if "pipeline" not in st.session_state:
    st.session_state.pipeline = FilterPipeline()

if "filter_list" not in st.session_state:
    st.session_state.filter_list = []   # lista de dicts {name, params}


# ─────────────────────────────────────────────
#  SIDEBAR — CONFIGURACIÓN DE FILTROS
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🎛️ Configurar filtros")
    st.markdown("---")

    # ── Fuente de imagen ──────────────────────────────────────────
    st.markdown("#### 📷 Fuente de imagen")
    source = st.radio("", ["Subir imagen", "Imagen de prueba sintética"], label_visibility="collapsed")

    uploaded = None
    if source == "Subir imagen":
        uploaded = st.file_uploader("Arrastra tu imagen aquí", type=["jpg", "jpeg", "png", "bmp", "webp"])

    st.markdown("---")

    # ── Selector de espacio de color ──────────────────────────────
    st.markdown("#### 🎨 Espacio de color de salida")
    color_space = st.selectbox(
        "",
        ColorSpaceConverter.available_spaces(),
        label_visibility="collapsed"
    )

    st.markdown("---")

    # ── Agregar filtros al pipeline ───────────────────────────────
    st.markdown("#### ➕ Agregar filtro")

    categoria = st.selectbox("Categoría", [
        "Suavizado (Blur)",
        "Nitidez",
        "Detección de bordes",
        "Morfología",
        "Color y brillo",
        "Efectos especiales",
    ])

    # ── Parámetros según categoría ────────────────────────────────
    params = {}

    if categoria == "Suavizado (Blur)":
        tipo = st.selectbox("Tipo", ["gaussian_blur", "median_blur", "bilateral", "box_blur"])
        if tipo in ["gaussian_blur", "median_blur", "box_blur"]:
            params["kernel_size"] = st.slider("Tamaño del kernel", 3, 51, 15, step=2)
        elif tipo == "bilateral":
            params["diameter"]    = st.slider("Diámetro", 3, 25, 9)
            params["sigma_color"] = st.slider("Sigma color", 10, 200, 75)
            params["sigma_space"] = st.slider("Sigma espacio", 10, 200, 75)

    elif categoria == "Nitidez":
        tipo = st.selectbox("Tipo", ["sharpen", "unsharp_mask"])
        if tipo == "sharpen":
            params["intensity"] = st.slider("Intensidad", 0.1, 3.0, 1.0, step=0.1)
        else:
            params["kernel_size"] = st.slider("Kernel", 3, 21, 5, step=2)
            params["amount"]      = st.slider("Cantidad", 0.5, 3.0, 1.5, step=0.1)

    elif categoria == "Detección de bordes":
        tipo = st.selectbox("Tipo", ["canny", "sobel", "laplacian"])
        if tipo == "canny":
            params["threshold1"] = st.slider("Umbral bajo", 10, 200, 100)
            params["threshold2"] = st.slider("Umbral alto", 50, 400, 200)
        elif tipo == "sobel":
            params["ksize"] = st.select_slider("Kernel", [1, 3, 5, 7], value=3)
        elif tipo == "laplacian":
            params["ksize"] = st.select_slider("Kernel", [1, 3, 5, 7], value=3)

    elif categoria == "Morfología":
        tipo = "morfologia"
        params["operation"]   = st.selectbox("Operación", ["erode", "dilate", "open", "close", "gradient", "tophat", "blackhat"])
        params["kernel_size"] = st.slider("Tamaño kernel", 3, 21, 5, step=2)
        params["iterations"]  = st.slider("Iteraciones", 1, 5, 1)

    elif categoria == "Color y brillo":
        tipo = st.selectbox("Tipo", ["contraste", "gamma", "saturacion", "hue", "temperatura", "ecualizar"])
        if tipo == "contraste":
            params["alpha"] = st.slider("Contraste (alpha)", 0.1, 3.0, 1.0, step=0.05)
            params["beta"]  = st.slider("Brillo (beta)", -100, 100, 0)
        elif tipo == "gamma":
            params["gamma"] = st.slider("Gamma", 0.1, 3.0, 1.0, step=0.05)
        elif tipo == "saturacion":
            params["factor"] = st.slider("Factor saturación", 0.0, 3.0, 1.0, step=0.1)
        elif tipo == "hue":
            params["shift"] = st.slider("Rotación de matiz (°)", -180, 180, 0)
        elif tipo == "temperatura":
            params["temperature"] = st.slider("Temperatura (K)", 2000, 10000, 6500, step=100)
        elif tipo == "ecualizar":
            params["method"] = st.selectbox("Método", ["clahe", "global"])

    elif categoria == "Efectos especiales":
        tipo = st.selectbox("Tipo", ["cartoon", "emboss", "sepia", "night_vision", "vignette", "pixelate"])
        if tipo == "cartoon":
            params["blur_ksize"]    = st.slider("Blur base", 3, 21, 7, step=2)
            params["color_reduce"]  = st.slider("Reducción color", 1, 15, 9)
        elif tipo == "sepia":
            params["intensity"] = st.slider("Intensidad", 0.1, 1.0, 0.8, step=0.05)
        elif tipo == "vignette":
            params["strength"] = st.slider("Intensidad viñeta", 0.1, 0.95, 0.5, step=0.05)
        elif tipo == "pixelate":
            params["block_size"] = st.slider("Tamaño bloque", 3, 40, 10)

    # ── Botón agregar ─────────────────────────────────────────────
    col_add, col_clear = st.columns(2)
    with col_add:
        if st.button("＋ Agregar", use_container_width=True, type="primary"):
            st.session_state.filter_list.append({"name": tipo, "params": params})
            st.success(f"Filtro **{tipo}** añadido")

    with col_clear:
        if st.button("🗑 Limpiar todo", use_container_width=True):
            st.session_state.filter_list = []
            st.info("Pipeline limpiado")

    st.markdown("---")

    # ── Pipeline actual ───────────────────────────────────────────
    st.markdown("#### 🔗 Pipeline actual")

    if not st.session_state.filter_list:
        st.caption("Sin filtros — se mostrará la imagen original")
    else:
        for i, f in enumerate(st.session_state.filter_list):
            col_tag, col_del = st.columns([5, 1])
            with col_tag:
                st.markdown(f'<span class="filter-tag">{i+1}. {f["name"]}</span>', unsafe_allow_html=True)
            with col_del:
                if st.button("✕", key=f"del_{i}", help="Eliminar este filtro"):
                    st.session_state.filter_list.pop(i)
                    st.rerun()

    # ── Presets rápidos ───────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### ⚡ Presets rápidos")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("📸 Retrato", use_container_width=True, help="Bilateral + Nitidez suave"):
            st.session_state.filter_list = [
                {"name": "bilateral",  "params": {"diameter": 9, "sigma_color": 80, "sigma_space": 80}},
                {"name": "contraste",  "params": {"alpha": 1.15, "beta": 10}},
                {"name": "sharpen",    "params": {"intensity": 0.6}},
            ]
            st.rerun()

    with col_p2:
        if st.button("🌃 Noche", use_container_width=True, help="Night vision + CLAHE"):
            st.session_state.filter_list = [
                {"name": "night_vision", "params": {}},
                {"name": "ecualizar",    "params": {"method": "clahe"}},
            ]
            st.rerun()

    col_p3, col_p4 = st.columns(2)
    with col_p3:
        if st.button("🖼 Artístico", use_container_width=True, help="Sepia + Viñeta"):
            st.session_state.filter_list = [
                {"name": "sepia",    "params": {"intensity": 0.85}},
                {"name": "vignette", "params": {"strength": 0.55}},
                {"name": "contraste","params": {"alpha": 1.1, "beta": -5}},
            ]
            st.rerun()

    with col_p4:
        if st.button("🔍 Bordes", use_container_width=True, help="Canny clásico"):
            st.session_state.filter_list = [
                {"name": "gaussian_blur", "params": {"kernel_size": 5}},
                {"name": "canny",         "params": {"threshold1": 80, "threshold2": 160}},
            ]
            st.rerun()


# ─────────────────────────────────────────────
#  CARGAR IMAGEN
# ─────────────────────────────────────────────

def load_image(uploaded_file) -> np.ndarray:
    """Convierte el archivo subido a numpy BGR."""
    if uploaded_file is not None:
        return StreamlitBridge.bytes_to_bgr(uploaded_file.read())
    return None


def synthetic_image(size=(480, 640)) -> np.ndarray:
    """Genera una imagen de prueba colorida con formas geométricas."""
    h, w = size
    img = np.zeros((h, w, 3), dtype=np.uint8)

    # Gradiente de fondo
    for i in range(h):
        t = i / h
        img[i, :, 0] = int(20 + 180 * t)       # B
        img[i, :, 1] = int(80 * (1 - t))        # G
        img[i, :, 2] = int(200 * (1 - t) + 20)  # R

    # Formas
    cv2.circle(img, (w // 2, h // 2), 120, (255, 200, 50), -1)
    cv2.circle(img, (w // 2, h // 2), 80,  (30, 30, 200), -1)
    cv2.circle(img, (w // 2, h // 2), 30,  (240, 240, 240), -1)

    cv2.rectangle(img, (30, 30),   (180, 130), (50, 200, 100), -1)
    cv2.rectangle(img, (460, 30),  (610, 130), (200, 50, 150), -1)
    cv2.rectangle(img, (30, 350),  (180, 450), (100, 150, 230), -1)
    cv2.rectangle(img, (460, 350), (610, 450), (230, 180, 30), -1)

    pts = np.array([[w//2, 30], [w//2-80, 160], [w//2+80, 160]], np.int32)
    cv2.fillPoly(img, [pts], (220, 80, 80))

    cv2.putText(img, "VisioLab", (120, 420),
                cv2.FONT_HERSHEY_DUPLEX, 1.3, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(img, "Test image", (200, 460),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1, cv2.LINE_AA)

    # Ruido leve
    noise = np.random.randint(0, 18, img.shape, dtype=np.uint8)
    img = cv2.add(img, noise)
    return img


# ─────────────────────────────────────────────
#  CONSTRUIR PIPELINE Y APLICAR FILTROS
# ─────────────────────────────────────────────

img_bgr: np.ndarray | None = None

if source == "Subir imagen" and uploaded is not None:
    img_bgr = load_image(uploaded)
elif source == "Imagen de prueba sintética":
    img_bgr = synthetic_image()

if img_bgr is None:
    st.info("👆 Sube una imagen o selecciona **'Imagen de prueba sintética'** en la barra lateral para comenzar.")
    st.stop()

# Construir el pipeline desde el estado de sesión
pipeline = FilterPipeline()
for f in st.session_state.filter_list:
    pipeline.add(f["name"], **f["params"])

# Aplicar
result = pipeline.apply(img_bgr, color_space=color_space)
img_out = result.image


# ─────────────────────────────────────────────
#  COLUMNAS PRINCIPALES: Original vs Procesada
# ─────────────────────────────────────────────

col_orig, col_proc = st.columns(2, gap="medium")

with col_orig:
    st.markdown("##### 📥 Imagen original")
    st.image(StreamlitBridge.bgr_to_rgb(img_bgr), use_container_width=True)

with col_proc:
    st.markdown("##### 📤 Imagen procesada")
    st.image(StreamlitBridge.bgr_to_rgb(img_out), use_container_width=True)


# ─────────────────────────────────────────────
#  MÉTRICAS RÁPIDAS
# ─────────────────────────────────────────────

st.markdown("---")
m1, m2, m3, m4, m5 = st.columns(5)

h_o, w_o = img_bgr.shape[:2]
h_p, w_p = img_out.shape[:2]
n_filters = len(result.filters_applied)
mean_orig = int(img_bgr.mean())
mean_proc = int(img_out.mean())

for col, val, lbl in [
    (m1, f"{w_o}×{h_o}", "Resolución"),
    (m2, n_filters,       "Filtros aplicados"),
    (m3, mean_orig,       "Brillo medio (orig)"),
    (m4, mean_proc,       "Brillo medio (proc)"),
    (m5, result.metadata.get("dtype", "uint8"), "Dtype"),
]:
    with col:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-val">{val}</div>
            <div class="metric-lbl">{lbl}</div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HISTOGRAMAS (para Dev 3 — vista previa)
# ─────────────────────────────────────────────

st.markdown("---")
st.markdown("##### 📊 Histogramas de canales (B / G / R)")

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["Original", "Procesada"],
                        horizontal_spacing=0.08)

    colors      = ["#60a5fa", "#34d399", "#f87171"]          # B, G, R (línea)
    fill_colors = ["rgba(96,165,250,0.2)", "rgba(52,211,153,0.2)", "rgba(248,113,113,0.2)"]
    labels      = ["Blue", "Green", "Red"]

    for img, col_idx in [(img_bgr, 1), (img_out, 2)]:
        for ch, (color, fill, label) in enumerate(zip(colors, fill_colors, labels)):
            hist = cv2.calcHist([img], [ch], None, [256], [0, 256]).flatten()
            fig.add_trace(go.Scatter(
                x=list(range(256)), y=hist,
                mode="lines", fill="tozeroy",
                line=dict(color=color, width=1.2),
                fillcolor=fill,
                name=label,
                showlegend=(col_idx == 1),
            ), row=1, col=col_idx)

    fig.update_layout(
        paper_bgcolor="#0f1117",
        plot_bgcolor="#1a1d2e",
        font=dict(color="#9ca3af", size=11),
        height=260,
        margin=dict(t=30, b=10, l=10, r=10),
        legend=dict(orientation="h", y=-0.15, bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(showgrid=False, color="#4b5563")
    fig.update_yaxes(showgrid=True, gridcolor="#2a2d3e", color="#4b5563")

    st.plotly_chart(fig, use_container_width=True)

except ImportError:
    st.caption("Instala `plotly` para ver los histogramas: `pip install plotly`")


# ─────────────────────────────────────────────
#  PANEL DE FILTROS APLICADOS + METADATA
# ─────────────────────────────────────────────

with st.expander("🔎 Detalle del pipeline (útil para Dev 3 y Dev 4)", expanded=False):

    st.markdown("**Filtros aplicados en este frame:**")
    if result.filters_applied:
        tags = " ".join([f'<span class="filter-tag">{f}</span>' for f in result.filters_applied])
        st.markdown(tags, unsafe_allow_html=True)
    else:
        st.caption("Ninguno — imagen sin procesar")

    st.markdown("**Metadata del resultado (ProcessingResult.metadata):**")
    st.json(result.metadata)

    st.markdown("**Código equivalente para Dev 4:**")
    code_lines = ["pipeline = FilterPipeline()"]
    for f in st.session_state.filter_list:
        p_str = ", ".join(f"{k}={v}" for k, v in f["params"].items())
        code_lines.append(f'pipeline.add("{f["name"]}", {p_str})')
    code_lines.append(f'resultado = pipeline.apply(frame, color_space="{color_space}")')
    code_lines.append('st.image(StreamlitBridge.bgr_to_rgb(resultado.image))')
    st.code("\n".join(code_lines), language="python")


# ─────────────────────────────────────────────
#  DESCARGAR IMAGEN PROCESADA
# ─────────────────────────────────────────────

st.markdown("---")
dl_col, _ = st.columns([2, 5])
with dl_col:
    img_pil = Image.fromarray(StreamlitBridge.bgr_to_rgb(img_out))
    buf = io.BytesIO()
    img_pil.save(buf, format="PNG")
    st.download_button(
        label="⬇️ Descargar imagen procesada",
        data=buf.getvalue(),
        file_name="visiolab_output.png",
        mime="image/png",
        use_container_width=True,
    )


# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────

st.markdown("""
<div style="text-align:center; color:#374151; font-size:0.72rem; margin-top:2rem; padding-top:1rem; border-top:1px solid #1f2937">
    VisioLab — Pipeline de Procesamiento Espacial · OpenCV + Streamlit
</div>
""", unsafe_allow_html=True)