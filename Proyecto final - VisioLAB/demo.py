"""
VisioLab - Demo interactivo
Procesamiento de imagenes, deteccion de objetos y analisis visual.
Ejecutar con: streamlit run demo.py
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

# Modulos del proyecto
from filters import FilterPipeline, ColorSpaceConverter, StreamlitBridge
from analysis import ImageAnalyzer, ChartBuilder, ImageStats
from detection import ObjectDetector, DetectionAnalytics, DetectionResult


# --- Configuracion de pagina ---

st.set_page_config(
    page_title="VisioLab",
    page_icon="V",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- Estilos CSS ---

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {
        background: #0a0b10;
        font-family: 'Inter', sans-serif;
    }
    .main .block-container {
        padding-top: 1rem;
        max-width: 1440px;
    }

    .vl-header {
        background: linear-gradient(135deg, rgba(99,102,241,0.08) 0%, rgba(15,17,23,0.9) 50%, rgba(236,72,153,0.06) 100%);
        border: 1px solid rgba(99,102,241,0.15);
        border-radius: 16px;
        padding: 1.2rem 1.8rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        backdrop-filter: blur(20px);
    }
    .vl-logo {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #6366f1, #ec4899);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 1.1rem;
    }
    .vl-header h1 {
        font-size: 1.4rem;
        font-weight: 700;
        color: #e8e8f0;
        margin: 0;
        letter-spacing: -0.03em;
    }
    .vl-header .subtitle {
        color: #6b7280;
        font-size: 0.78rem;
        font-weight: 400;
    }
    .vl-badge {
        margin-left: auto;
        background: rgba(99,102,241,0.12);
        border: 1px solid rgba(99,102,241,0.3);
        color: #a5b4fc;
        font-size: 0.68rem;
        font-weight: 600;
        padding: 3px 12px;
        border-radius: 20px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    .glass-card {
        background: rgba(17,19,28,0.7);
        border: 1px solid rgba(99,102,241,0.1);
        border-radius: 14px;
        padding: 1.2rem;
        backdrop-filter: blur(12px);
        transition: border-color 0.2s ease;
    }
    .glass-card:hover {
        border-color: rgba(99,102,241,0.25);
    }

    .metric-card {
        background: rgba(17,19,28,0.6);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 0.9rem 1rem;
        text-align: center;
        transition: transform 0.15s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99,102,241,0.2);
    }
    .metric-val {
        font-size: 1.3rem;
        font-weight: 700;
        color: #a5b4fc;
        line-height: 1.2;
    }
    .metric-lbl {
        font-size: 0.68rem;
        color: #6b7280;
        margin-top: 3px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 500;
    }

    .filter-tag {
        display: inline-block;
        background: rgba(99,102,241,0.1);
        border: 1px solid rgba(99,102,241,0.2);
        color: #a5b4fc;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 6px;
        margin: 2px 3px;
        letter-spacing: 0.02em;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(17,19,28,0.5);
        border-radius: 12px;
        padding: 4px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.85rem;
        color: #6b7280;
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(99,102,241,0.15) !important;
        color: #a5b4fc !important;
    }

    [data-testid="stSidebar"] {
        background: #0d0e14;
        border-right: 1px solid rgba(255,255,255,0.04);
    }
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] .stMarkdown h4 {
        color: #d1d5db;
        font-weight: 600;
    }

    .stExpander {
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 10px !important;
        background: rgba(17,19,28,0.4);
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.82rem;
        transition: all 0.15s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
    }

    .section-label {
        color: #9ca3af;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.6rem;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .vl-divider {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.05);
        margin: 1rem 0;
    }

    .vl-footer {
        text-align: center;
        color: #374151;
        font-size: 0.7rem;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255,255,255,0.04);
    }

    .stDeployButton { display: none; }

    .status-online {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 0.72rem;
        font-weight: 500;
        color: #34d399;
    }
    .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #34d399;
        animation: pulse-dot 2s infinite;
    }
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }
</style>
""", unsafe_allow_html=True)


# --- Header ---

st.markdown("""
<div class="vl-header">
    <div class="vl-logo">V</div>
    <div>
        <h1>VisioLab</h1>
        <span class="subtitle">Pipeline de procesamiento visual</span>
    </div>
    <span class="vl-badge">Proyecto Final</span>
</div>
""", unsafe_allow_html=True)


# --- Estado de sesion ---

if "pipeline" not in st.session_state:
    st.session_state.pipeline = FilterPipeline()

if "filter_list" not in st.session_state:
    st.session_state.filter_list = []

if "detector" not in st.session_state:
    st.session_state.detector = None

if "det_result" not in st.session_state:
    st.session_state.det_result = None


# --- Sidebar: configuracion global ---

with st.sidebar:
    st.markdown("### Configuracion")
    st.markdown('<hr class="vl-divider">', unsafe_allow_html=True)

    # Fuente de imagen
    st.markdown('<div class="section-label">Fuente de imagen</div>',
                unsafe_allow_html=True)
    source = st.radio(
        "Fuente", ["Subir imagen", "Imagen sintetica"],
        label_visibility="collapsed",
    )

    uploaded = None
    if source == "Subir imagen":
        uploaded = st.file_uploader(
            "Selecciona una imagen",
            type=["jpg", "jpeg", "png", "bmp", "webp"],
        )

    st.markdown('<hr class="vl-divider">', unsafe_allow_html=True)

    # Espacio de color
    st.markdown('<div class="section-label">Espacio de color</div>',
                unsafe_allow_html=True)
    color_space = st.selectbox(
        "Espacio de color",
        ColorSpaceConverter.available_spaces(),
        label_visibility="collapsed",
    )

    st.markdown('<hr class="vl-divider">', unsafe_allow_html=True)

    # Agregar filtros al pipeline
    st.markdown('<div class="section-label">Agregar filtro</div>',
                unsafe_allow_html=True)

    categoria = st.selectbox("Categoria", [
        "Suavizado (Blur)",
        "Nitidez",
        "Deteccion de bordes",
        "Morfologia",
        "Color y brillo",
        "Efectos especiales",
    ])

    params = {}

    if categoria == "Suavizado (Blur)":
        tipo = st.selectbox("Tipo", [
            "gaussian_blur", "median_blur", "bilateral", "box_blur",
        ])
        if tipo in ("gaussian_blur", "median_blur", "box_blur"):
            params["kernel_size"] = st.slider("Kernel", 3, 51, 15, step=2)
        elif tipo == "bilateral":
            params["diameter"] = st.slider("Diametro", 3, 25, 9)
            params["sigma_color"] = st.slider("Sigma color", 10, 200, 75)
            params["sigma_space"] = st.slider("Sigma espacio", 10, 200, 75)

    elif categoria == "Nitidez":
        tipo = st.selectbox("Tipo", ["sharpen", "unsharp_mask"])
        if tipo == "sharpen":
            params["intensity"] = st.slider("Intensidad", 0.1, 3.0, 1.0, step=0.1)
        else:
            params["kernel_size"] = st.slider("Kernel", 3, 21, 5, step=2)
            params["amount"] = st.slider("Cantidad", 0.5, 3.0, 1.5, step=0.1)

    elif categoria == "Deteccion de bordes":
        tipo = st.selectbox("Tipo", ["canny", "sobel", "laplacian"])
        if tipo == "canny":
            params["threshold1"] = st.slider("Umbral bajo", 10, 200, 100)
            params["threshold2"] = st.slider("Umbral alto", 50, 400, 200)
        else:
            params["ksize"] = st.select_slider("Kernel", [1, 3, 5, 7], value=3)

    elif categoria == "Morfologia":
        tipo = "morfologia"
        params["operation"] = st.selectbox("Operacion", [
            "erode", "dilate", "open", "close",
            "gradient", "tophat", "blackhat",
        ])
        params["kernel_size"] = st.slider("Kernel", 3, 21, 5, step=2)
        params["iterations"] = st.slider("Iteraciones", 1, 5, 1)

    elif categoria == "Color y brillo":
        tipo = st.selectbox("Tipo", [
            "contraste", "gamma", "saturacion", "hue", "temperatura", "ecualizar",
        ])
        if tipo == "contraste":
            params["alpha"] = st.slider("Contraste", 0.1, 3.0, 1.0, step=0.05)
            params["beta"] = st.slider("Brillo", -100, 100, 0)
        elif tipo == "gamma":
            params["gamma"] = st.slider("Gamma", 0.1, 3.0, 1.0, step=0.05)
        elif tipo == "saturacion":
            params["factor"] = st.slider("Saturacion", 0.0, 3.0, 1.0, step=0.1)
        elif tipo == "hue":
            params["shift"] = st.slider("Rotacion matiz", -180, 180, 0)
        elif tipo == "temperatura":
            params["temperature"] = st.slider("Temperatura (K)", 2000, 10000, 6500, step=100)
        elif tipo == "ecualizar":
            params["method"] = st.selectbox("Metodo", ["clahe", "global"])

    elif categoria == "Efectos especiales":
        tipo = st.selectbox("Tipo", [
            "cartoon", "emboss", "sepia", "night_vision", "vignette", "pixelate",
        ])
        if tipo == "cartoon":
            params["blur_ksize"] = st.slider("Blur base", 3, 21, 7, step=2)
            params["color_reduce"] = st.slider("Reduccion color", 1, 15, 9)
        elif tipo == "sepia":
            params["intensity"] = st.slider("Intensidad", 0.1, 1.0, 0.8, step=0.05)
        elif tipo == "vignette":
            params["strength"] = st.slider("Fuerza", 0.1, 0.95, 0.5, step=0.05)
        elif tipo == "pixelate":
            params["block_size"] = st.slider("Tamano bloque", 3, 40, 10)

    # Botones de accion
    col_add, col_clear = st.columns(2)
    with col_add:
        if st.button("Agregar", use_container_width=True, type="primary"):
            st.session_state.filter_list.append({"name": tipo, "params": params})
            st.success(f"Filtro {tipo} agregado")
    with col_clear:
        if st.button("Limpiar", use_container_width=True):
            st.session_state.filter_list = []
            st.info("Pipeline limpiado")

    st.markdown('<hr class="vl-divider">', unsafe_allow_html=True)

    # Pipeline actual
    st.markdown('<div class="section-label">Pipeline actual</div>',
                unsafe_allow_html=True)

    if not st.session_state.filter_list:
        st.caption("Sin filtros aplicados")
    else:
        for i, f in enumerate(st.session_state.filter_list):
            col_tag, col_del = st.columns([5, 1])
            with col_tag:
                st.markdown(
                    f'<span class="filter-tag">{i+1}. {f["name"]}</span>',
                    unsafe_allow_html=True,
                )
            with col_del:
                if st.button("x", key=f"del_{i}", help="Eliminar"):
                    st.session_state.filter_list.pop(i)
                    st.rerun()

    # Presets rapidos
    st.markdown('<hr class="vl-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Presets</div>',
                unsafe_allow_html=True)

    p1, p2 = st.columns(2)
    with p1:
        if st.button("Retrato", use_container_width=True):
            st.session_state.filter_list = [
                {"name": "bilateral", "params": {"diameter": 9, "sigma_color": 80, "sigma_space": 80}},
                {"name": "contraste", "params": {"alpha": 1.15, "beta": 10}},
                {"name": "sharpen", "params": {"intensity": 0.6}},
            ]
            st.rerun()
    with p2:
        if st.button("Noche", use_container_width=True):
            st.session_state.filter_list = [
                {"name": "night_vision", "params": {}},
                {"name": "ecualizar", "params": {"method": "clahe"}},
            ]
            st.rerun()

    p3, p4 = st.columns(2)
    with p3:
        if st.button("Artistico", use_container_width=True):
            st.session_state.filter_list = [
                {"name": "sepia", "params": {"intensity": 0.85}},
                {"name": "vignette", "params": {"strength": 0.55}},
                {"name": "contraste", "params": {"alpha": 1.1, "beta": -5}},
            ]
            st.rerun()
    with p4:
        if st.button("Bordes", use_container_width=True):
            st.session_state.filter_list = [
                {"name": "gaussian_blur", "params": {"kernel_size": 5}},
                {"name": "canny", "params": {"threshold1": 80, "threshold2": 160}},
            ]
            st.rerun()


# --- Cargar imagen ---

def load_image(uploaded_file):
    """Convierte archivo subido a numpy BGR."""
    if uploaded_file is not None:
        return StreamlitBridge.bytes_to_bgr(uploaded_file.read())
    return None


def synthetic_image(size=(480, 640)):
    """Genera imagen de prueba con formas geometricas."""
    h, w = size
    img = np.zeros((h, w, 3), dtype=np.uint8)

    for i in range(h):
        t = i / h
        img[i, :, 0] = int(20 + 180 * t)
        img[i, :, 1] = int(80 * (1 - t))
        img[i, :, 2] = int(200 * (1 - t) + 20)

    cv2.circle(img, (w // 2, h // 2), 120, (255, 200, 50), -1)
    cv2.circle(img, (w // 2, h // 2), 80, (30, 30, 200), -1)
    cv2.circle(img, (w // 2, h // 2), 30, (240, 240, 240), -1)

    cv2.rectangle(img, (30, 30), (180, 130), (50, 200, 100), -1)
    cv2.rectangle(img, (460, 30), (610, 130), (200, 50, 150), -1)
    cv2.rectangle(img, (30, 350), (180, 450), (100, 150, 230), -1)
    cv2.rectangle(img, (460, 350), (610, 450), (230, 180, 30), -1)

    pts = np.array([[w//2, 30], [w//2-80, 160], [w//2+80, 160]], np.int32)
    cv2.fillPoly(img, [pts], (220, 80, 80))

    cv2.putText(img, "VisioLab", (120, 420),
                cv2.FONT_HERSHEY_DUPLEX, 1.3, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(img, "Test image", (200, 460),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1, cv2.LINE_AA)

    noise = np.random.randint(0, 18, img.shape, dtype=np.uint8)
    img = cv2.add(img, noise)
    return img


# --- Obtener imagen ---

img_bgr = None

if source == "Subir imagen" and uploaded is not None:
    img_bgr = load_image(uploaded)
elif source == "Imagen sintetica":
    img_bgr = synthetic_image()

if img_bgr is None:
    st.info("Sube una imagen o selecciona 'Imagen sintetica' en la barra lateral para empezar.")
    st.stop()


# --- Aplicar pipeline de filtros ---

pipeline = FilterPipeline()
for f in st.session_state.filter_list:
    pipeline.add(f["name"], **f["params"])

result = pipeline.apply(img_bgr, color_space=color_space)
img_out = result.image


# --- Tabs principales ---

tab_filters, tab_detection, tab_analysis, tab_full = st.tabs([
    "Filtros", "Deteccion IA", "Analisis", "Pipeline completo",
])


# ---- TAB 1: FILTROS ----

with tab_filters:
    col_orig, col_proc = st.columns(2, gap="medium")

    with col_orig:
        st.markdown('<div class="section-label">Imagen original</div>',
                    unsafe_allow_html=True)
        st.image(StreamlitBridge.bgr_to_rgb(img_bgr), use_container_width=True)

    with col_proc:
        st.markdown('<div class="section-label">Imagen procesada</div>',
                    unsafe_allow_html=True)
        st.image(StreamlitBridge.bgr_to_rgb(img_out), use_container_width=True)

    # Metricas rapidas
    st.markdown('<hr class="vl-divider">', unsafe_allow_html=True)

    h_o, w_o = img_bgr.shape[:2]
    n_filters = len(result.filters_applied)
    mean_orig = int(img_bgr.mean())
    mean_proc = int(img_out.mean())

    m1, m2, m3, m4, m5 = st.columns(5)
    metrics_data = [
        (m1, f"{w_o} x {h_o}", "Resolucion"),
        (m2, str(n_filters), "Filtros"),
        (m3, str(mean_orig), "Brillo (orig)"),
        (m4, str(mean_proc), "Brillo (proc)"),
        (m5, result.metadata.get("dtype", "uint8"), "Tipo dato"),
    ]

    for col, val, lbl in metrics_data:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val">{val}</div>
                <div class="metric-lbl">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    # Histogramas
    st.markdown('<hr class="vl-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Histogramas por canal</div>',
                unsafe_allow_html=True)

    hist_fig = ChartBuilder.histogram_comparison(img_bgr, img_out)
    if hist_fig:
        st.plotly_chart(hist_fig, use_container_width=True)

    # Detalle del pipeline
    with st.expander("Detalle del pipeline", expanded=False):
        st.markdown("**Filtros aplicados:**")
        if result.filters_applied:
            tags = " ".join(
                f'<span class="filter-tag">{f}</span>'
                for f in result.filters_applied
            )
            st.markdown(tags, unsafe_allow_html=True)
        else:
            st.caption("Ninguno")

        st.markdown("**Metadata:**")
        st.json(result.metadata)

    # Descargar imagen procesada
    st.markdown('<hr class="vl-divider">', unsafe_allow_html=True)
    dl_col, _ = st.columns([2, 5])
    with dl_col:
        img_pil = Image.fromarray(StreamlitBridge.bgr_to_rgb(img_out))
        buf = io.BytesIO()
        img_pil.save(buf, format="PNG")
        st.download_button(
            label="Descargar imagen procesada",
            data=buf.getvalue(),
            file_name="visiolab_output.png",
            mime="image/png",
            use_container_width=True,
        )


# ---- TAB 2: DETECCION IA ----

with tab_detection:
    st.markdown('<div class="section-label">Deteccion de objetos con YOLO</div>',
                unsafe_allow_html=True)

    det_col1, det_col2, det_col3 = st.columns([2, 1, 1])

    with det_col1:
        model_choice = st.selectbox(
            "Modelo",
            list(ObjectDetector.AVAILABLE_MODELS.keys()),
        )
    with det_col2:
        confidence_thresh = st.slider("Confianza minima", 0.1, 0.9, 0.25, step=0.05)
    with det_col3:
        use_filtered = st.checkbox("Usar imagen filtrada", value=False,
                                   help="Aplica deteccion sobre la imagen ya procesada por el pipeline")

    det_input = img_out if use_filtered else img_bgr

    run_detection = st.button("Ejecutar deteccion", type="primary")

    if run_detection:
        model_file = ObjectDetector.AVAILABLE_MODELS[model_choice]

        with st.spinner("Cargando modelo y ejecutando inferencia..."):
            try:
                detector = ObjectDetector(model_file)
                det_result = detector.detect(
                    det_input,
                    confidence=confidence_thresh,
                )
                st.session_state.det_result = det_result
                st.session_state.detector = detector
            except ImportError as e:
                st.error(f"Error: {e}. Instala con: pip install ultralytics")
            except Exception as e:
                st.error(f"Error durante la deteccion: {e}")

    det_result = st.session_state.get("det_result")

    if det_result is not None:
        st.markdown('<hr class="vl-divider">', unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:16px; margin-bottom:1rem;">
            <span class="status-online">
                <span class="status-dot"></span>
                Deteccion completada
            </span>
            <span style="color:#6b7280; font-size:0.75rem;">
                {det_result.inference_time_ms:.0f} ms
                &middot; {det_result.total_objects} objetos
                &middot; {det_result.model_name}
            </span>
        </div>
        """, unsafe_allow_html=True)

        res_col1, res_col2 = st.columns([3, 1])

        with res_col1:
            st.image(
                StreamlitBridge.bgr_to_rgb(det_result.annotated_image),
                use_container_width=True,
            )

        with res_col2:
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom:8px;">
                <div class="metric-val">{det_result.total_objects}</div>
                <div class="metric-lbl">Objetos detectados</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="metric-card" style="margin-bottom:8px;">
                <div class="metric-val">{det_result.inference_time_ms:.0f}ms</div>
                <div class="metric-lbl">Tiempo inferencia</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="metric-card" style="margin-bottom:8px;">
                <div class="metric-val">{len(det_result.class_counts)}</div>
                <div class="metric-lbl">Clases unicas</div>
            </div>
            """, unsafe_allow_html=True)

        if det_result.detections:
            st.markdown('<hr class="vl-divider">', unsafe_allow_html=True)

            chart_c1, chart_c2 = st.columns(2)

            with chart_c1:
                st.markdown('<div class="section-label">Distribucion por clase</div>',
                            unsafe_allow_html=True)
                class_fig = ChartBuilder.detection_class_chart(det_result.class_counts)
                if class_fig:
                    st.plotly_chart(class_fig, use_container_width=True)

            with chart_c2:
                st.markdown('<div class="section-label">Distribucion de confianza</div>',
                            unsafe_allow_html=True)
                confs = [d.confidence for d in det_result.detections]
                conf_fig = ChartBuilder.confidence_distribution(confs)
                if conf_fig:
                    st.plotly_chart(conf_fig, use_container_width=True)

            st.markdown('<div class="section-label">Mapa de calor de detecciones</div>',
                        unsafe_allow_html=True)
            heatmap_overlay = DetectionAnalytics.overlay_heatmap(
                det_input, det_result.detections, alpha=0.35,
            )
            st.image(
                StreamlitBridge.bgr_to_rgb(heatmap_overlay),
                use_container_width=True,
            )

            with st.expander("Lista de detecciones", expanded=False):
                for i, det in enumerate(det_result.detections):
                    x1, y1, x2, y2 = det.bbox
                    st.markdown(
                        f"**{i+1}.** {det.class_name} — "
                        f"{det.confidence:.1%} — "
                        f"bbox: ({x1}, {y1}, {x2}, {y2})"
                    )

    elif not run_detection:
        st.caption("Configura los parametros y presiona 'Ejecutar deteccion' para empezar.")


# ---- TAB 3: ANALISIS ----

with tab_analysis:
    st.markdown('<div class="section-label">Analisis de imagen</div>',
                unsafe_allow_html=True)

    stats_orig = ImageAnalyzer.compute_stats(img_bgr)
    stats_proc = ImageAnalyzer.compute_stats(img_out)
    comparison = ImageAnalyzer.compare(img_bgr, img_out)

    cmp_c1, cmp_c2, cmp_c3, cmp_c4 = st.columns(4)
    cmp_metrics = [
        (cmp_c1, f"{comparison.mse:.1f}", "MSE"),
        (cmp_c2, f"{comparison.psnr:.1f} dB" if comparison.psnr > 0 else "N/A", "PSNR"),
        (cmp_c3, f"{comparison.ssim_value:.3f}" if comparison.ssim_value else "N/A", "SSIM"),
        (cmp_c4, f"{comparison.mean_diff:.1f}", "Diferencia media"),
    ]

    for col, val, lbl in cmp_metrics:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val">{val}</div>
                <div class="metric-lbl">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<hr class="vl-divider">', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Histogramas comparativos</div>',
                unsafe_allow_html=True)
    hist_cmp = ChartBuilder.histogram_comparison(img_bgr, img_out, height=300)
    if hist_cmp:
        st.plotly_chart(hist_cmp, use_container_width=True)

    st.markdown('<hr class="vl-divider">', unsafe_allow_html=True)

    an_c1, an_c2 = st.columns(2)

    with an_c1:
        st.markdown('<div class="section-label">Mapa de diferencias</div>',
                    unsafe_allow_html=True)
        diff_map = ImageAnalyzer.compute_difference_map(img_bgr, img_out)
        st.image(StreamlitBridge.bgr_to_rgb(diff_map), use_container_width=True)

    with an_c2:
        st.markdown('<div class="section-label">Estadisticas por canal</div>',
                    unsafe_allow_html=True)

        channel_names = ["Blue", "Green", "Red"]
        for ch in range(min(3, stats_orig.channels)):
            st.markdown(f"**{channel_names[ch]}**")
            orig_str = (f"Media: {stats_orig.mean[ch]} | "
                       f"Std: {stats_orig.std[ch]} | "
                       f"Rango: [{stats_orig.min_val[ch]}, {stats_orig.max_val[ch]}]")
            proc_str = (f"Media: {stats_proc.mean[ch]} | "
                       f"Std: {stats_proc.std[ch]} | "
                       f"Rango: [{stats_proc.min_val[ch]}, {stats_proc.max_val[ch]}]")
            st.caption(f"Original: {orig_str}")
            st.caption(f"Procesada: {proc_str}")

    st.markdown('<hr class="vl-divider">', unsafe_allow_html=True)
    with st.expander("Distribucion de color 3D", expanded=False):
        scatter_c1, scatter_c2 = st.columns(2)
        with scatter_c1:
            st.markdown("**Original**")
            fig_3d_orig = ChartBuilder.color_scatter_3d(img_bgr)
            if fig_3d_orig:
                st.plotly_chart(fig_3d_orig, use_container_width=True)
        with scatter_c2:
            st.markdown("**Procesada**")
            fig_3d_proc = ChartBuilder.color_scatter_3d(img_out)
            if fig_3d_proc:
                st.plotly_chart(fig_3d_proc, use_container_width=True)


# ---- TAB 4: PIPELINE COMPLETO ----

with tab_full:
    st.markdown('<div class="section-label">Pipeline completo: filtros + deteccion + analisis</div>',
                unsafe_allow_html=True)

    st.markdown(
        "Este tab ejecuta el flujo completo: la imagen pasa por los filtros "
        "configurados, luego se ejecuta la deteccion de objetos, "
        "y finalmente se muestran las metricas de analisis."
    )

    full_model = st.selectbox(
        "Modelo YOLO",
        list(ObjectDetector.AVAILABLE_MODELS.keys()),
        key="full_model",
    )
    full_conf = st.slider("Confianza", 0.1, 0.9, 0.3, step=0.05, key="full_conf")

    if st.button("Ejecutar pipeline completo", type="primary", key="full_run"):
        model_file = ObjectDetector.AVAILABLE_MODELS[full_model]

        st.markdown("**Paso 1: Filtros aplicados**")
        if result.filters_applied:
            tags = " ".join(
                f'<span class="filter-tag">{f}</span>'
                for f in result.filters_applied
            )
            st.markdown(tags, unsafe_allow_html=True)
        else:
            st.caption("Sin filtros")

        st.markdown("**Paso 2: Deteccion de objetos**")
        with st.spinner("Ejecutando deteccion..."):
            try:
                detector = ObjectDetector(model_file)
                full_det = detector.detect(img_out, confidence=full_conf)

                full_c1, full_c2, full_c3 = st.columns(3)
                with full_c1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-val">{full_det.total_objects}</div>
                        <div class="metric-lbl">Objetos</div>
                    </div>
                    """, unsafe_allow_html=True)
                with full_c2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-val">{full_det.inference_time_ms:.0f}ms</div>
                        <div class="metric-lbl">Inferencia</div>
                    </div>
                    """, unsafe_allow_html=True)
                with full_c3:
                    comparison_full = ImageAnalyzer.compare(img_bgr, img_out)
                    psnr_str = f"{comparison_full.psnr:.1f}" if comparison_full.psnr > 0 else "N/A"
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-val">{psnr_str} dB</div>
                        <div class="metric-lbl">PSNR</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown('<hr class="vl-divider">', unsafe_allow_html=True)

                vis_c1, vis_c2, vis_c3 = st.columns(3)
                with vis_c1:
                    st.markdown('<div class="section-label">Original</div>',
                                unsafe_allow_html=True)
                    st.image(StreamlitBridge.bgr_to_rgb(img_bgr),
                             use_container_width=True)
                with vis_c2:
                    st.markdown('<div class="section-label">Filtrada</div>',
                                unsafe_allow_html=True)
                    st.image(StreamlitBridge.bgr_to_rgb(img_out),
                             use_container_width=True)
                with vis_c3:
                    st.markdown('<div class="section-label">Detecciones</div>',
                                unsafe_allow_html=True)
                    st.image(StreamlitBridge.bgr_to_rgb(full_det.annotated_image),
                             use_container_width=True)

                st.markdown('<hr class="vl-divider">', unsafe_allow_html=True)
                st.markdown("**Paso 3: Analisis**")

                full_hist = ChartBuilder.histogram_comparison(img_bgr, img_out)
                if full_hist:
                    st.plotly_chart(full_hist, use_container_width=True)

                if full_det.class_counts:
                    class_chart = ChartBuilder.detection_class_chart(full_det.class_counts)
                    if class_chart:
                        st.plotly_chart(class_chart, use_container_width=True)

            except ImportError as e:
                st.error(f"Error: {e}. Instala con: pip install ultralytics")
            except Exception as e:
                st.error(f"Error: {e}")

    else:
        st.caption("Presiona el boton para ejecutar el pipeline completo.")


# --- Footer ---

st.markdown("""
<div class="vl-footer">
    VisioLab &mdash; Pipeline de Procesamiento Visual &middot; UNAL 2026-I
</div>
""", unsafe_allow_html=True)