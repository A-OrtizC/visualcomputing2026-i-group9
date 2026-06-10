"""
VisioLab - Modulo de analisis y metricas (Dev 3)
Histogramas, estadisticas de imagen, comparacion y visualizaciones con Plotly.
"""

import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import Optional
import logging

logger = logging.getLogger("VisioLab.Analysis")

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    _plotly_available = True
except ImportError:
    _plotly_available = False
    logger.warning("plotly no instalado, graficos no disponibles")

try:
    from skimage.metrics import structural_similarity as ssim
    _skimage_available = True
except ImportError:
    _skimage_available = False


# Tema oscuro consistente con la UI
DARK_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,17,23,0.6)",
    font=dict(color="#9ca3af", size=11, family="Inter, sans-serif"),
    margin=dict(t=35, b=10, l=10, r=10),
)

# Colores para canales BGR
CHANNEL_COLORS = {
    "Blue":  {"line": "#60a5fa", "fill": "rgba(96,165,250,0.15)"},
    "Green": {"line": "#34d399", "fill": "rgba(52,211,153,0.15)"},
    "Red":   {"line": "#f87171", "fill": "rgba(248,113,113,0.15)"},
}


@dataclass
class ImageStats:
    """Estadisticas basicas de una imagen por canal."""
    mean: list[float] = field(default_factory=list)
    std: list[float] = field(default_factory=list)
    min_val: list[int] = field(default_factory=list)
    max_val: list[int] = field(default_factory=list)
    channels: int = 3
    height: int = 0
    width: int = 0
    total_pixels: int = 0


@dataclass
class ComparisonMetrics:
    """Metricas de comparacion entre dos imagenes."""
    mse: float = 0.0
    psnr: float = 0.0
    ssim_value: Optional[float] = None
    mean_diff: float = 0.0


class ImageAnalyzer:
    """Herramientas de analisis sobre imagenes individuales o pares."""

    @staticmethod
    def compute_stats(image: np.ndarray) -> ImageStats:
        """Calcula estadisticas por canal de la imagen."""
        h, w = image.shape[:2]
        channels = image.shape[2] if len(image.shape) == 3 else 1

        stats = ImageStats(
            height=h, width=w,
            channels=channels,
            total_pixels=h * w,
        )

        if channels == 1:
            stats.mean = [float(np.mean(image))]
            stats.std = [float(np.std(image))]
            stats.min_val = [int(np.min(image))]
            stats.max_val = [int(np.max(image))]
        else:
            for ch in range(channels):
                channel = image[:, :, ch]
                stats.mean.append(round(float(np.mean(channel)), 2))
                stats.std.append(round(float(np.std(channel)), 2))
                stats.min_val.append(int(np.min(channel)))
                stats.max_val.append(int(np.max(channel)))

        return stats

    @staticmethod
    def compare(original: np.ndarray, processed: np.ndarray) -> ComparisonMetrics:
        """Compara dos imagenes: MSE, PSNR y opcionalmente SSIM."""
        # Asegurar mismas dimensiones
        if original.shape != processed.shape:
            processed = cv2.resize(
                processed, (original.shape[1], original.shape[0])
            )

        orig_f = original.astype(np.float64)
        proc_f = processed.astype(np.float64)

        mse = float(np.mean((orig_f - proc_f) ** 2))
        psnr = 0.0
        if mse > 0:
            psnr = round(10 * np.log10(255.0 ** 2 / mse), 2)

        mean_diff = round(float(np.mean(np.abs(orig_f - proc_f))), 2)

        ssim_val = None
        if _skimage_available:
            try:
                gray_o = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
                gray_p = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
                ssim_val = round(float(ssim(gray_o, gray_p)), 4)
            except Exception:
                pass

        return ComparisonMetrics(
            mse=round(mse, 2),
            psnr=psnr,
            ssim_value=ssim_val,
            mean_diff=mean_diff,
        )

    @staticmethod
    def compute_difference_map(
        original: np.ndarray,
        processed: np.ndarray,
    ) -> np.ndarray:
        """Genera un mapa visual de diferencias entre dos imagenes."""
        if original.shape != processed.shape:
            processed = cv2.resize(
                processed, (original.shape[1], original.shape[0])
            )

        diff = cv2.absdiff(original, processed)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        # Amplificar diferencias para que sean visibles
        gray_diff = cv2.normalize(gray_diff, None, 0, 255, cv2.NORM_MINMAX)
        colored = cv2.applyColorMap(gray_diff, cv2.COLORMAP_MAGMA)
        return colored


class ChartBuilder:
    """Genera graficos Plotly con el tema de VisioLab."""

    @staticmethod
    def histogram_comparison(
        original: np.ndarray,
        processed: np.ndarray,
        height: int = 280,
    ) -> "go.Figure":
        """Histograma de canales BGR lado a lado: original vs procesada."""
        if not _plotly_available:
            return None

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=["Original", "Procesada"],
            horizontal_spacing=0.06,
        )

        labels = ["Blue", "Green", "Red"]
        for img, col_idx in [(original, 1), (processed, 2)]:
            for ch, label in enumerate(labels):
                style = CHANNEL_COLORS[label]
                hist = cv2.calcHist([img], [ch], None, [256], [0, 256])
                hist = hist.flatten()

                fig.add_trace(go.Scatter(
                    x=list(range(256)), y=hist,
                    mode="lines", fill="tozeroy",
                    line=dict(color=style["line"], width=1),
                    fillcolor=style["fill"],
                    name=label,
                    showlegend=(col_idx == 1),
                ), row=1, col=col_idx)

        fig.update_layout(
            **DARK_THEME,
            height=height,
            legend=dict(orientation="h", y=-0.15, bgcolor="rgba(0,0,0,0)"),
        )
        fig.update_xaxes(showgrid=False, color="#4b5563")
        fig.update_yaxes(showgrid=True, gridcolor="#1f2937", color="#4b5563")

        return fig

    @staticmethod
    def single_histogram(image: np.ndarray, height: int = 260) -> "go.Figure":
        """Histograma de una sola imagen."""
        if not _plotly_available:
            return None

        fig = go.Figure()
        labels = ["Blue", "Green", "Red"]

        for ch, label in enumerate(labels):
            style = CHANNEL_COLORS[label]
            hist = cv2.calcHist([image], [ch], None, [256], [0, 256])
            fig.add_trace(go.Scatter(
                x=list(range(256)), y=hist.flatten(),
                mode="lines", fill="tozeroy",
                line=dict(color=style["line"], width=1),
                fillcolor=style["fill"],
                name=label,
            ))

        fig.update_layout(**DARK_THEME, height=height)
        fig.update_xaxes(showgrid=False, color="#4b5563",
                         title_text="Intensidad")
        fig.update_yaxes(showgrid=True, gridcolor="#1f2937", color="#4b5563",
                         title_text="Frecuencia")
        return fig

    @staticmethod
    def detection_class_chart(
        class_counts: dict,
        height: int = 300,
    ) -> "go.Figure":
        """Grafico de barras horizontal con objetos detectados por clase."""
        if not _plotly_available or not class_counts:
            return None

        sorted_items = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)
        names = [item[0] for item in sorted_items]
        counts = [item[1] for item in sorted_items]

        # Asignar colores del gradiente
        n = len(names)
        colors = []
        for i in range(n):
            t = i / max(n - 1, 1)
            r = int(99 + (236 - 99) * t)
            g = int(102 + (72 - 102) * t)
            b = int(241 + (153 - 241) * t)
            colors.append(f"rgb({r},{g},{b})")

        fig = go.Figure(go.Bar(
            x=counts,
            y=names,
            orientation="h",
            marker_color=colors,
            text=counts,
            textposition="auto",
            textfont=dict(color="white", size=12),
        ))

        fig.update_layout(
            **DARK_THEME,
            height=height,
            yaxis=dict(autorange="reversed"),
            xaxis=dict(title_text="Cantidad"),
        )
        return fig

    @staticmethod
    def confidence_distribution(
        confidences: list[float],
        height: int = 260,
    ) -> "go.Figure":
        """Histograma de distribucion de confianzas de las detecciones."""
        if not _plotly_available or not confidences:
            return None

        fig = go.Figure(go.Histogram(
            x=confidences,
            nbinsx=20,
            marker_color="rgba(99, 102, 241, 0.7)",
            marker_line=dict(color="rgb(99, 102, 241)", width=1),
        ))

        fig.update_layout(
            **DARK_THEME,
            height=height,
            xaxis=dict(title_text="Confianza", range=[0, 1]),
            yaxis=dict(title_text="Frecuencia"),
        )
        return fig

    @staticmethod
    def color_scatter_3d(
        image: np.ndarray,
        sample_size: int = 2000,
        height: int = 400,
    ) -> "go.Figure":
        """Scatter 3D de la distribucion de color en espacio RGB."""
        if not _plotly_available:
            return None

        # Tomar una muestra aleatoria de pixeles
        pixels = image.reshape(-1, 3)
        if len(pixels) > sample_size:
            idx = np.random.choice(len(pixels), sample_size, replace=False)
            pixels = pixels[idx]

        # BGR a RGB para los ejes
        r, g, b = pixels[:, 2], pixels[:, 1], pixels[:, 0]

        # Color real de cada punto
        colors = [f"rgb({ri},{gi},{bi})" for ri, gi, bi in zip(r, g, b)]

        fig = go.Figure(go.Scatter3d(
            x=r, y=g, z=b,
            mode="markers",
            marker=dict(size=2, color=colors, opacity=0.6),
        ))

        fig.update_layout(
            **DARK_THEME,
            height=height,
            scene=dict(
                xaxis=dict(title="Red", range=[0, 255]),
                yaxis=dict(title="Green", range=[0, 255]),
                zaxis=dict(title="Blue", range=[0, 255]),
                bgcolor="rgba(15,17,23,0.8)",
            ),
        )
        return fig
