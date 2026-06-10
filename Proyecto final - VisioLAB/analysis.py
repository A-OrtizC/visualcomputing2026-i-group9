"""
VisioLab - Modulo de analisis y metricas (Dev 3)
Histogramas, estadisticas de imagen, comparacion y visualizaciones con Plotly.

Exporta:
  - ImageStats          : estadisticas por canal de una imagen
  - ExtendedStats       : estadisticas ampliadas (percentiles, entropía, balance)
  - ComparisonMetrics   : metricas MSE / PSNR / SSIM entre dos imagenes
  - ImageAnalyzer       : calculo de stats, comparacion y mapas de diferencias
  - MatrixExtractor     : extraccion de matrices de canal / region para inspeccion
  - ChartBuilder        : graficos Plotly con tema oscuro de VisioLab
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


# ──────────────────────────────────────────────────────────────
#  TEMA OSCURO  (consistente con la UI de VisioLab)
# ──────────────────────────────────────────────────────────────

DARK_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,17,23,0.6)",
    font=dict(color="#9ca3af", size=11, family="Inter, sans-serif"),
    margin=dict(t=35, b=10, l=10, r=10),
)

CHANNEL_COLORS = {
    "Blue":  {"line": "#60a5fa", "fill": "rgba(96,165,250,0.15)"},
    "Green": {"line": "#34d399", "fill": "rgba(52,211,153,0.15)"},
    "Red":   {"line": "#f87171", "fill": "rgba(248,113,113,0.15)"},
    "Gray":  {"line": "#d1d5db", "fill": "rgba(209,213,219,0.15)"},
}

CHANNEL_LABELS = ["Blue", "Green", "Red"]


# ──────────────────────────────────────────────────────────────
#  DATACLASSES
# ──────────────────────────────────────────────────────────────

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

    def to_dict(self) -> dict:
        """Serializa las estadisticas a dict (util para logs o exportacion)."""
        names = CHANNEL_LABELS[:self.channels] if self.channels <= 3 else [f"ch{i}" for i in range(self.channels)]
        return {
            "dimensions": f"{self.width}x{self.height}",
            "total_pixels": self.total_pixels,
            "channels": {
                name: {
                    "mean": self.mean[i],
                    "std": self.std[i],
                    "min": self.min_val[i],
                    "max": self.max_val[i],
                }
                for i, name in enumerate(names)
            }
        }


@dataclass
class ExtendedStats:
    """
    Estadisticas ampliadas por canal: percentiles, entropía y balance de color.
    Se generan a partir de ImageAnalyzer.compute_extended_stats().
    """
    p25: list[float] = field(default_factory=list)    # Percentil 25
    p50: list[float] = field(default_factory=list)    # Mediana
    p75: list[float] = field(default_factory=list)    # Percentil 75
    p95: list[float] = field(default_factory=list)    # Percentil 95
    entropy: list[float] = field(default_factory=list)  # Entropía por canal (bits)
    channel_dominance: str = "Balanced"  # Canal dominante o "Balanced"
    brightness: float = 0.0   # Brillo medio perceptual (0–255)
    contrast_rms: float = 0.0  # Contraste RMS (desv. estd. luminancia)

    def to_dict(self) -> dict:
        names = CHANNEL_LABELS[:len(self.p50)]
        return {
            "percentiles": {
                name: {"p25": self.p25[i], "p50": self.p50[i],
                        "p75": self.p75[i], "p95": self.p95[i]}
                for i, name in enumerate(names)
            },
            "entropy": {name: self.entropy[i] for i, name in enumerate(names)},
            "channel_dominance": self.channel_dominance,
            "brightness": self.brightness,
            "contrast_rms": self.contrast_rms,
        }


@dataclass
class ComparisonMetrics:
    """Metricas de comparacion entre dos imagenes."""
    mse: float = 0.0
    psnr: float = 0.0
    ssim_value: Optional[float] = None
    mean_diff: float = 0.0

    def quality_label(self) -> str:
        """Etiqueta de calidad basada en PSNR."""
        if self.psnr == 0:
            return "Identicas"
        elif self.psnr >= 40:
            return "Excelente"
        elif self.psnr >= 30:
            return "Buena"
        elif self.psnr >= 20:
            return "Aceptable"
        else:
            return "Degradada"


# ──────────────────────────────────────────────────────────────
#  IMAGE ANALYZER
# ──────────────────────────────────────────────────────────────

class ImageAnalyzer:
    """Herramientas de analisis sobre imagenes individuales o pares."""

    # ── Estadisticas basicas ─────────────────────────────────────

    @staticmethod
    def compute_stats(image: np.ndarray) -> ImageStats:
        """
        Calcula media, std, min y max por canal BGR.
        Funciona tanto para imagenes a color (3ch) como en escala de grises (1ch).
        """
        h, w = image.shape[:2]
        channels = image.shape[2] if len(image.shape) == 3 else 1

        stats = ImageStats(
            height=h, width=w,
            channels=channels,
            total_pixels=h * w,
        )

        if channels == 1:
            flat = image.ravel().astype(np.float64)
            stats.mean = [round(float(np.mean(flat)), 2)]
            stats.std = [round(float(np.std(flat)), 2)]
            stats.min_val = [int(np.min(flat))]
            stats.max_val = [int(np.max(flat))]
        else:
            for ch in range(channels):
                channel = image[:, :, ch].astype(np.float64)
                stats.mean.append(round(float(np.mean(channel)), 2))
                stats.std.append(round(float(np.std(channel)), 2))
                stats.min_val.append(int(np.min(channel)))
                stats.max_val.append(int(np.max(channel)))

        return stats

    # ── Estadisticas ampliadas ───────────────────────────────────

    @staticmethod
    def compute_extended_stats(image: np.ndarray) -> ExtendedStats:
        """
        Calcula percentiles, entropía de Shannon por canal y balance de color.

        La entropía mide la "cantidad de información" de cada canal:
          - Alta entropía → canal variado, muchos tonos distintos.
          - Baja entropía → canal uniforme o con pocas variaciones.
        """
        channels = image.shape[2] if len(image.shape) == 3 else 1
        stats = ExtendedStats()

        channel_means = []

        for ch in range(channels):
            arr = image[:, :, ch].ravel() if channels > 1 else image.ravel()
            arr_f = arr.astype(np.float64)

            stats.p25.append(round(float(np.percentile(arr_f, 25)), 2))
            stats.p50.append(round(float(np.percentile(arr_f, 50)), 2))
            stats.p75.append(round(float(np.percentile(arr_f, 75)), 2))
            stats.p95.append(round(float(np.percentile(arr_f, 95)), 2))
            channel_means.append(float(np.mean(arr_f)))

            # Entropía de Shannon a partir del histograma
            hist, _ = np.histogram(arr, bins=256, range=(0, 256))
            hist_norm = hist / (hist.sum() + 1e-9)
            nonzero = hist_norm[hist_norm > 0]
            entropy = float(-np.sum(nonzero * np.log2(nonzero)))
            stats.entropy.append(round(entropy, 3))

        # Brillo perceptual (luminancia BT.601 si es BGR a color)
        if channels == 3:
            b, g, r = channel_means[0], channel_means[1], channel_means[2]
            lum = 0.114 * b + 0.587 * g + 0.299 * r
            stats.brightness = round(lum, 2)

            # Contraste RMS sobre la luminancia
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float64)
            stats.contrast_rms = round(float(np.std(gray)), 2)

            # Canal dominante: diferencia significativa (>8 unidades)
            labels = CHANNEL_LABELS
            max_ch = int(np.argmax(channel_means))
            min_ch = int(np.argmin(channel_means))
            if channel_means[max_ch] - channel_means[min_ch] > 8:
                stats.channel_dominance = labels[max_ch]
            else:
                stats.channel_dominance = "Balanced"
        else:
            stats.brightness = round(channel_means[0], 2)
            stats.contrast_rms = round(float(np.std(image.astype(np.float64))), 2)
            stats.channel_dominance = "Gray"

        return stats

    # ── Comparacion entre imagenes ───────────────────────────────

    @staticmethod
    def compare(original: np.ndarray, processed: np.ndarray) -> ComparisonMetrics:
        """
        Compara dos imagenes calculando MSE, PSNR y opcionalmente SSIM.

        MSE  = Error cuadratico medio (0 = identicas).
        PSNR = Relacion señal-ruido de pico en dB (mayor = mas parecidas).
        SSIM = Indice de similitud estructural [0,1] (1 = identicas).
        """
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

    # ── Mapa de diferencias ──────────────────────────────────────

    @staticmethod
    def compute_difference_map(
        original: np.ndarray,
        processed: np.ndarray,
    ) -> np.ndarray:
        """
        Genera un mapa visual de diferencias amplificadas entre dos imagenes.
        Usa COLORMAP_MAGMA: negro = sin cambio, amarillo = mucho cambio.
        """
        if original.shape != processed.shape:
            processed = cv2.resize(
                processed, (original.shape[1], original.shape[0])
            )

        diff = cv2.absdiff(original, processed)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        gray_diff = cv2.normalize(gray_diff, None, 0, 255, cv2.NORM_MINMAX)
        colored = cv2.applyColorMap(gray_diff, cv2.COLORMAP_MAGMA)
        return colored

    # ── Mapa de diferencias por canal ─────────────────────────────

    @staticmethod
    def compute_channel_diff_map(
        original: np.ndarray,
        processed: np.ndarray,
        channel: int = 0,
    ) -> np.ndarray:
        """
        Diferencia amplificada de un canal individual (0=B, 1=G, 2=R).
        Util para identificar cuál canal cambia mas con un filtro de color.
        """
        if original.shape != processed.shape:
            processed = cv2.resize(
                processed, (original.shape[1], original.shape[0])
            )

        ch_orig = original[:, :, channel].astype(np.float32)
        ch_proc = processed[:, :, channel].astype(np.float32)
        diff = np.abs(ch_orig - ch_proc)
        diff = cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        cmaps = [cv2.COLORMAP_COOL, cv2.COLORMAP_SUMMER, cv2.COLORMAP_HOT]
        return cv2.applyColorMap(diff, cmaps[channel % 3])


# ──────────────────────────────────────────────────────────────
#  MATRIX EXTRACTOR  (nuevo en Dev 3)
# ──────────────────────────────────────────────────────────────

class MatrixExtractor:
    """
    Extrae y formatea matrices de píxeles de una imagen para inspeccion.

    Util para depuracion: permite ver los valores numericos exactos de
    regiones o canales especificos, tal como quedan en el array NumPy.
    """

    @staticmethod
    def extract_channel(image: np.ndarray, channel: int) -> np.ndarray:
        """
        Retorna la matriz 2D de un canal especifico (0=B, 1=G, 2=R).
        Si la imagen es en grises, ignora el parametro channel.
        """
        if len(image.shape) == 2:
            return image.copy()
        if image.shape[2] <= channel:
            raise ValueError(f"Canal {channel} no existe (imagen tiene {image.shape[2]} canales).")
        return image[:, :, channel].copy()

    @staticmethod
    def extract_roi(
        image: np.ndarray,
        x: int, y: int,
        width: int, height: int,
    ) -> np.ndarray:
        """
        Recorta una Region de Interes (ROI) del array.
        Retorna la sub-matriz (puede ser 2D o 3D segun la imagen).
        Recorta automaticamente si la ROI sale del borde.
        """
        h_img, w_img = image.shape[:2]
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(w_img, x + width)
        y2 = min(h_img, y + height)
        return image[y1:y2, x1:x2].copy()

    @staticmethod
    def channel_as_dataframe_dict(
        image: np.ndarray,
        channel: int,
        max_rows: int = 20,
        max_cols: int = 20,
    ) -> dict:
        """
        Devuelve un diccionario {col_index: [valores]} listo para
        construir un st.dataframe() en Streamlit, limitado a max_rows x max_cols.

        Ejemplo de uso en demo.py:
            import pandas as pd
            data = MatrixExtractor.channel_as_dataframe_dict(img, channel=2)
            st.dataframe(pd.DataFrame(data))
        """
        mat = MatrixExtractor.extract_channel(image, channel)
        mat_crop = mat[:max_rows, :max_cols]
        return {str(c): mat_crop[:, c].tolist() for c in range(mat_crop.shape[1])}

    @staticmethod
    def histogram_array(image: np.ndarray, channel: int) -> tuple[np.ndarray, np.ndarray]:
        """
        Calcula el histograma de un canal y retorna (bins, counts).
        bins: array de 256 valores [0..255]
        counts: frecuencia de cada intensidad
        """
        if len(image.shape) == 2:
            src = image
        else:
            src = image[:, :, channel]
        hist = cv2.calcHist([src], [0], None, [256], [0, 256]).flatten()
        bins = np.arange(256)
        return bins, hist

    @staticmethod
    def summary_table(image: np.ndarray) -> list[dict]:
        """
        Genera una lista de dicts con estadisticas por canal,
        directamente consumible por st.dataframe() o pd.DataFrame().

        Columnas: Canal | Media | Std | Min | Mediana | Max | Entropia
        """
        rows = []
        channels = image.shape[2] if len(image.shape) == 3 else 1
        labels = CHANNEL_LABELS[:channels] if channels <= 3 else [f"ch{i}" for i in range(channels)]

        for ch in range(channels):
            arr = image[:, :, ch].ravel() if channels > 1 else image.ravel()
            arr_f = arr.astype(np.float64)

            hist, _ = np.histogram(arr, bins=256, range=(0, 256))
            hist_norm = hist / (hist.sum() + 1e-9)
            nonzero = hist_norm[hist_norm > 0]
            entropy = float(-np.sum(nonzero * np.log2(nonzero)))

            rows.append({
                "Canal":    labels[ch],
                "Media":    round(float(np.mean(arr_f)), 2),
                "Std":      round(float(np.std(arr_f)), 2),
                "Min":      int(np.min(arr)),
                "Mediana":  round(float(np.median(arr_f)), 1),
                "Max":      int(np.max(arr)),
                "Entropia": round(entropy, 3),
            })

        return rows


# ──────────────────────────────────────────────────────────────
#  CHART BUILDER
# ──────────────────────────────────────────────────────────────

class ChartBuilder:
    """Genera graficos Plotly con el tema de VisioLab."""

    # ── Histogramas ───────────────────────────────────────────────

    @staticmethod
    def histogram_comparison(
        original: np.ndarray,
        processed: np.ndarray,
        height: int = 280,
        log_scale: bool = False,
    ) -> "go.Figure":
        """
        Histograma de canales BGR lado a lado: original vs procesada.
        log_scale: activa eje Y logaritmico (util para imagenes con picos altos).
        """
        if not _plotly_available:
            return None

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=["Original", "Procesada"],
            horizontal_spacing=0.06,
        )

        for img, col_idx in [(original, 1), (processed, 2)]:
            n_channels = img.shape[2] if len(img.shape) == 3 else 1
            labels = CHANNEL_LABELS[:n_channels] if n_channels <= 3 else ["Gray"]

            for ch, label in enumerate(labels):
                style = CHANNEL_COLORS.get(label, CHANNEL_COLORS["Gray"])
                src = img[:, :, ch] if n_channels > 1 else img
                hist = cv2.calcHist([src], [0], None, [256], [0, 256]).flatten()

                fig.add_trace(go.Scatter(
                    x=list(range(256)), y=hist,
                    mode="lines", fill="tozeroy",
                    line=dict(color=style["line"], width=1),
                    fillcolor=style["fill"],
                    name=label,
                    showlegend=(col_idx == 1),
                ), row=1, col=col_idx)

        y_type = "log" if log_scale else "linear"
        fig.update_layout(
            **DARK_THEME,
            height=height,
            legend=dict(orientation="h", y=-0.15, bgcolor="rgba(0,0,0,0)"),
        )
        fig.update_xaxes(showgrid=False, color="#4b5563")
        fig.update_yaxes(showgrid=True, gridcolor="#1f2937",
                         color="#4b5563", type=y_type)

        return fig

    @staticmethod
    def single_histogram(
        image: np.ndarray,
        height: int = 260,
        channels: Optional[list[int]] = None,
        log_scale: bool = False,
    ) -> "go.Figure":
        """
        Histograma de una sola imagen.
        channels: lista de indices a mostrar, p.ej. [0,2] para B y R.
                  None = todos los canales.
        log_scale: eje Y logaritmico.
        """
        if not _plotly_available:
            return None

        fig = go.Figure()
        n_channels = image.shape[2] if len(image.shape) == 3 else 1
        all_labels = CHANNEL_LABELS[:n_channels] if n_channels <= 3 else [f"ch{i}" for i in range(n_channels)]

        indices = channels if channels is not None else list(range(n_channels))

        for ch in indices:
            if ch >= n_channels:
                continue
            label = all_labels[ch]
            style = CHANNEL_COLORS.get(label, CHANNEL_COLORS["Gray"])
            src = image[:, :, ch] if n_channels > 1 else image
            hist = cv2.calcHist([src], [0], None, [256], [0, 256]).flatten()

            fig.add_trace(go.Scatter(
                x=list(range(256)), y=hist,
                mode="lines", fill="tozeroy",
                line=dict(color=style["line"], width=1),
                fillcolor=style["fill"],
                name=label,
            ))

        y_type = "log" if log_scale else "linear"
        fig.update_layout(**DARK_THEME, height=height)
        fig.update_xaxes(showgrid=False, color="#4b5563", title_text="Intensidad")
        fig.update_yaxes(showgrid=True, gridcolor="#1f2937", color="#4b5563",
                         title_text="Frecuencia", type=y_type)
        return fig

    # ── Estadisticas ampliadas ────────────────────────────────────

    @staticmethod
    def percentile_bar_chart(
        stats_orig: ExtendedStats,
        stats_proc: ExtendedStats,
        height: int = 300,
    ) -> "go.Figure":
        """
        Grafico de barras agrupadas: percentiles p25 / p50 / p75 por canal,
        comparando original vs procesada.
        """
        if not _plotly_available:
            return None

        n = len(stats_orig.p50)
        labels = CHANNEL_LABELS[:n]
        x = labels

        bar_colors_orig = ["#60a5fa", "#34d399", "#f87171"]
        bar_colors_proc = ["#3b82f6", "#10b981", "#ef4444"]

        fig = make_subplots(rows=1, cols=3,
                            subplot_titles=["P25", "Mediana (P50)", "P75"],
                            horizontal_spacing=0.07)

        for col_i, (attr, title) in enumerate([("p25", "P25"), ("p50", "P50"), ("p75", "P75")], start=1):
            orig_vals = getattr(stats_orig, attr)[:n]
            proc_vals = getattr(stats_proc, attr)[:n]

            fig.add_trace(go.Bar(
                x=x, y=orig_vals,
                name="Original" if col_i == 1 else None,
                showlegend=(col_i == 1),
                marker_color=bar_colors_orig[:n],
                opacity=0.85,
            ), row=1, col=col_i)

            fig.add_trace(go.Bar(
                x=x, y=proc_vals,
                name="Procesada" if col_i == 1 else None,
                showlegend=(col_i == 1),
                marker_color=bar_colors_proc[:n],
                opacity=0.55,
                marker_pattern_shape="/",
            ), row=1, col=col_i)

        fig.update_layout(
            **DARK_THEME,
            height=height,
            barmode="group",
            legend=dict(orientation="h", y=-0.18, bgcolor="rgba(0,0,0,0)"),
        )
        fig.update_yaxes(showgrid=True, gridcolor="#1f2937", range=[0, 255])
        return fig

    @staticmethod
    def entropy_comparison_chart(
        stats_orig: ExtendedStats,
        stats_proc: ExtendedStats,
        height: int = 260,
    ) -> "go.Figure":
        """
        Grafico radar / polar con la entropia de Shannon por canal,
        comparando original vs procesada.
        Alta entropia = mayor variedad tonal (generalmente mejor).
        """
        if not _plotly_available:
            return None

        n = len(stats_orig.entropy)
        labels = CHANNEL_LABELS[:n] + [CHANNEL_LABELS[0]]  # cerrar el poligono
        orig_vals = stats_orig.entropy[:n] + [stats_orig.entropy[0]]
        proc_vals = stats_proc.entropy[:n] + [stats_proc.entropy[0]]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=orig_vals, theta=labels,
            fill="toself",
            name="Original",
            line=dict(color="#6366f1", width=2),
            fillcolor="rgba(99,102,241,0.15)",
        ))
        fig.add_trace(go.Scatterpolar(
            r=proc_vals, theta=labels,
            fill="toself",
            name="Procesada",
            line=dict(color="#ec4899", width=2),
            fillcolor="rgba(236,72,153,0.15)",
        ))

        fig.update_layout(
            **DARK_THEME,
            height=height,
            polar=dict(
                bgcolor="rgba(15,17,23,0.6)",
                radialaxis=dict(
                    visible=True, range=[0, 8],
                    gridcolor="#1f2937", color="#4b5563",
                ),
                angularaxis=dict(color="#9ca3af"),
            ),
            legend=dict(orientation="h", y=-0.1, bgcolor="rgba(0,0,0,0)"),
        )
        return fig

    @staticmethod
    def channel_balance_chart(
        stats_orig: ExtendedStats,
        stats_proc: ExtendedStats,
        height: int = 260,
    ) -> "go.Figure":
        """
        Grafico de dona (pie) mostrando el peso relativo de cada canal
        en terminos de brillo medio (suma BGR = 100%).
        Dos donuts: original vs procesada.
        """
        if not _plotly_available:
            return None

        # Reconstruir medias desde percentil 50 (proxy) o stats basicas
        # Usamos p50 como representacion del "nivel tipico" del canal
        n = min(len(stats_orig.p50), 3)
        labels = CHANNEL_LABELS[:n]
        orig_vals = [max(v, 0.01) for v in stats_orig.p50[:n]]
        proc_vals = [max(v, 0.01) for v in stats_proc.p50[:n]]

        colors = ["#60a5fa", "#34d399", "#f87171"]

        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{"type": "pie"}, {"type": "pie"}]],
            subplot_titles=["Original", "Procesada"],
        )
        fig.add_trace(go.Pie(
            labels=labels, values=orig_vals,
            hole=0.5, marker_colors=colors[:n],
            textfont=dict(size=11, color="white"),
            showlegend=True,
        ), row=1, col=1)
        fig.add_trace(go.Pie(
            labels=labels, values=proc_vals,
            hole=0.5, marker_colors=colors[:n],
            textfont=dict(size=11, color="white"),
            showlegend=False,
        ), row=1, col=2)

        fig.update_layout(
            **DARK_THEME,
            height=height,
            legend=dict(orientation="h", y=-0.08, bgcolor="rgba(0,0,0,0)"),
        )
        return fig

    # ── Deteccion ─────────────────────────────────────────────────

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

        n = len(names)
        colors = []
        for i in range(n):
            t = i / max(n - 1, 1)
            r = int(99 + (236 - 99) * t)
            g = int(102 + (72 - 102) * t)
            b = int(241 + (153 - 241) * t)
            colors.append(f"rgb({r},{g},{b})")

        fig = go.Figure(go.Bar(
            x=counts, y=names,
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

    # ── Color 3D ──────────────────────────────────────────────────

    @staticmethod
    def color_scatter_3d(
        image: np.ndarray,
        sample_size: int = 2000,
        height: int = 400,
    ) -> "go.Figure":
        """Scatter 3D de la distribucion de color en espacio RGB."""
        if not _plotly_available:
            return None

        pixels = image.reshape(-1, 3)
        if len(pixels) > sample_size:
            idx = np.random.choice(len(pixels), sample_size, replace=False)
            pixels = pixels[idx]

        r, g, b = pixels[:, 2], pixels[:, 1], pixels[:, 0]
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

    # ── Intensidad media por fila/columna ─────────────────────────

    @staticmethod
    def spatial_intensity_profile(
        image: np.ndarray,
        axis: str = "horizontal",
        height: int = 240,
    ) -> "go.Figure":
        """
        Perfil de intensidad media a lo largo de filas (horizontal)
        o columnas (vertical).

        axis: 'horizontal' promedia cada fila → curva sobre eje Y (0..altura)
              'vertical'   promedia cada columna → curva sobre eje X (0..ancho)

        Util para detectar gradientes o iluminacion no uniforme.
        """
        if not _plotly_available:
            return None

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        gray_f = gray.astype(np.float64)

        if axis == "horizontal":
            profile = np.mean(gray_f, axis=1)   # media por fila
            x_label, y_label = "Intensidad media", "Fila (píxel)"
            x_data, y_data = profile, list(range(len(profile)))
        else:
            profile = np.mean(gray_f, axis=0)   # media por columna
            x_label, y_label = "Columna (píxel)", "Intensidad media"
            x_data, y_data = list(range(len(profile))), profile

        fig = go.Figure(go.Scatter(
            x=x_data, y=y_data,
            mode="lines",
            line=dict(color="#a78bfa", width=1.5),
            fill="tozeroy",
            fillcolor="rgba(167,139,250,0.12)",
            name="Intensidad",
        ))

        fig.update_layout(
            **DARK_THEME,
            height=height,
            title_text=f"Perfil de intensidad ({axis})",
            title_font=dict(size=12, color="#9ca3af"),
        )
        fig.update_xaxes(title_text=x_label, showgrid=False, color="#4b5563")
        fig.update_yaxes(title_text=y_label, showgrid=True,
                         gridcolor="#1f2937", color="#4b5563")
        return fig
