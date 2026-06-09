"""
╔══════════════════════════════════════════════════════════════════╗
║         VISIOLAB: Pipeline de Procesamiento Espacial             ║
║         Módulo de Filtros y Transformaciones con OpenCV          ║
╚══════════════════════════════════════════════════════════════════╝

Responsabilidades:
  - Implementar filtros espaciales: Blur, Nitidez, Bordes, Contraste
  - Ajustes de color: Brillo, Saturación, Balance de Blancos
  - Conversiones de espacio de color (BGR, HSV, LAB, Grises)
  - Exposición de una API limpia para que Dev 4 (UX) pueda invocar filtros
  - Compatibilidad con imágenes NumPy (frame de OpenCV o Streamlit)

Uso desde Dev 4:
  from filters import FilterPipeline
  pipeline = FilterPipeline()
  pipeline.add("blur", kernel_size=15)
  pipeline.add("contraste", alpha=1.5, beta=30)
  frame_procesado = pipeline.apply(frame_original)

Dependencias:
  pip install opencv-python numpy
"""

import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VisioLab.Filters")


# ─────────────────────────────────────────────
#  TIPOS Y ESTRUCTURAS DE DATOS
# ─────────────────────────────────────────────

@dataclass
class FilterConfig:
    """Configuración de un filtro individual."""
    name: str
    params: dict = field(default_factory=dict)
    enabled: bool = True


@dataclass
class ProcessingResult:
    """Resultado devuelto tras aplicar el pipeline."""
    image: np.ndarray                 # Imagen procesada (BGR)
    filters_applied: list[str]        # Nombres de filtros aplicados
    metadata: dict = field(default_factory=dict)  # Info extra para Dev 3


# ─────────────────────────────────────────────
#  FILTROS INDIVIDUALES
# ─────────────────────────────────────────────

class SpatialFilters:
    """
    Colección de filtros espaciales.
    Cada método recibe una imagen BGR (np.ndarray) y devuelve otra.
    """

    # ── SUAVIZADO / BLUR ──────────────────────────────────────────

    @staticmethod
    def gaussian_blur(image: np.ndarray, kernel_size: int = 15) -> np.ndarray:
        """
        Desenfoque Gaussiano: reduce ruido y detalles finos.
        kernel_size: impar, mayor = más desenfoque (rango recomendado: 3–51)
        """
        k = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
        return cv2.GaussianBlur(image, (k, k), 0)

    @staticmethod
    def median_blur(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
        """
        Desenfoque Mediana: efectivo contra ruido impulsivo (sal y pimienta).
        kernel_size: impar (rango: 3–21)
        """
        k = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
        return cv2.medianBlur(image, k)

    @staticmethod
    def bilateral_filter(image: np.ndarray,
                         diameter: int = 9,
                         sigma_color: float = 75,
                         sigma_space: float = 75) -> np.ndarray:
        """
        Filtro Bilateral: suaviza preservando bordes.
        diameter: tamaño del vecindario de píxeles
        sigma_color: rango de color permitido
        sigma_space: influencia espacial
        """
        return cv2.bilateralFilter(image, diameter, sigma_color, sigma_space)

    @staticmethod
    def box_blur(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
        """Blur de caja simple (promedio). Rápido pero menos natural."""
        k = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
        return cv2.blur(image, (k, k))

    # ── NITIDEZ / SHARPENING ──────────────────────────────────────

    @staticmethod
    def sharpen(image: np.ndarray, intensity: float = 1.0) -> np.ndarray:
        """
        Realza bordes y detalles mediante un kernel laplaciano.
        intensity: 0.5 = suave, 1.0 = estándar, 2.0 = agresivo
        """
        kernel = np.array([
            [ 0, -1,  0],
            [-1,  5, -1],
            [ 0, -1,  0]
        ], dtype=np.float32)
        # Aumentar intensidad escalando el centro
        kernel[1, 1] = 1 + 4 * intensity
        kernel[0, 1] = kernel[1, 0] = kernel[1, 2] = kernel[2, 1] = -intensity
        sharpened = cv2.filter2D(image, -1, kernel)
        return np.clip(sharpened, 0, 255).astype(np.uint8)

    @staticmethod
    def unsharp_mask(image: np.ndarray,
                     kernel_size: int = 5,
                     sigma: float = 1.0,
                     amount: float = 1.5,
                     threshold: int = 0) -> np.ndarray:
        """
        Máscara de desenfoque invertida (Unsharp Mask).
        Más natural que el kernel laplaciano simple.
        amount: cuánto realce aplicar (0.5–3.0)
        threshold: diferencia mínima para aplicar el efecto
        """
        k = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
        blurred = cv2.GaussianBlur(image, (k, k), sigma)
        sharpened = cv2.addWeighted(image, 1.0 + amount, blurred, -amount, 0)
        if threshold > 0:
            low_contrast_mask = np.absolute(image.astype(int) - blurred.astype(int)) < threshold
            sharpened[low_contrast_mask] = image[low_contrast_mask]
        return np.clip(sharpened, 0, 255).astype(np.uint8)

    # ── DETECCIÓN DE BORDES ───────────────────────────────────────

    @staticmethod
    def canny_edges(image: np.ndarray,
                    threshold1: float = 100,
                    threshold2: float = 200) -> np.ndarray:
        """
        Detección de bordes Canny. Devuelve imagen BGR con bordes blancos.
        threshold1: umbral inferior (ruido)
        threshold2: umbral superior (bordes fuertes)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, threshold1, threshold2)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def sobel_edges(image: np.ndarray, ksize: int = 3) -> np.ndarray:
        """
        Bordes con gradiente Sobel (suaviza antes de detectar).
        ksize: tamaño del kernel (1, 3, 5, 7)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=ksize)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=ksize)
        magnitude = np.sqrt(sobelx**2 + sobely**2)
        magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
        edges = magnitude.astype(np.uint8)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def laplacian_edges(image: np.ndarray, ksize: int = 3) -> np.ndarray:
        """
        Bordes con operador Laplaciano. Más sensible al ruido que Canny.
        ksize: tamaño del kernel (1, 3, 5, 7)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        lap = cv2.Laplacian(gray, cv2.CV_64F, ksize=ksize)
        lap = np.absolute(lap)
        lap = cv2.normalize(lap, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        return cv2.cvtColor(lap, cv2.COLOR_GRAY2BGR)

    # ── MORFOLOGÍA ────────────────────────────────────────────────

    @staticmethod
    def morphology(image: np.ndarray,
                   operation: str = "erode",
                   kernel_size: int = 5,
                   iterations: int = 1) -> np.ndarray:
        """
        Operaciones morfológicas.
        operation: 'erode', 'dilate', 'open', 'close', 'gradient', 'tophat', 'blackhat'
        """
        k = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
        ops = {
            "erode":    lambda img: cv2.erode(img, kernel, iterations=iterations),
            "dilate":   lambda img: cv2.dilate(img, kernel, iterations=iterations),
            "open":     lambda img: cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel),
            "close":    lambda img: cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel),
            "gradient": lambda img: cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel),
            "tophat":   lambda img: cv2.morphologyEx(img, cv2.MORPH_TOPHAT, kernel),
            "blackhat": lambda img: cv2.morphologyEx(img, cv2.MORPH_BLACKHAT, kernel),
        }
        if operation not in ops:
            logger.warning(f"Operación morfológica '{operation}' desconocida. Usando 'erode'.")
            operation = "erode"
        return ops[operation](image)


# ─────────────────────────────────────────────
#  AJUSTES DE COLOR Y BRILLO
# ─────────────────────────────────────────────

class ColorAdjustments:
    """Ajustes de brillo, contraste, color y espacio de color."""

    @staticmethod
    def brightness_contrast(image: np.ndarray,
                            alpha: float = 1.0,
                            beta: float = 0) -> np.ndarray:
        """
        Ajuste lineal: pixel_nuevo = alpha * pixel + beta
        alpha: contraste  (0.5 = bajo, 1.0 = sin cambio, 2.5 = alto)
        beta:  brillo     (-100 a +100)
        """
        result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        return result

    @staticmethod
    def gamma_correction(image: np.ndarray, gamma: float = 1.0) -> np.ndarray:
        """
        Corrección gamma no lineal (útil para compensar pantallas).
        gamma < 1 → más brillante | gamma > 1 → más oscuro
        """
        inv_gamma = 1.0 / max(gamma, 0.01)
        table = np.array([
            ((i / 255.0) ** inv_gamma) * 255
            for i in range(256)
        ]).astype(np.uint8)
        return cv2.LUT(image, table)

    @staticmethod
    def saturation(image: np.ndarray, factor: float = 1.0) -> np.ndarray:
        """
        Ajuste de saturación en espacio HSV.
        factor: 0.0 = escala de grises, 1.0 = sin cambio, 2.0 = muy saturado
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * factor, 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    @staticmethod
    def hue_shift(image: np.ndarray, shift: int = 0) -> np.ndarray:
        """
        Rota el matiz (Hue) en espacio HSV.
        shift: -180 a +180 grados
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.int32)
        hsv[:, :, 0] = (hsv[:, :, 0] + shift) % 180
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    @staticmethod
    def white_balance(image: np.ndarray,
                      r_gain: float = 1.0,
                      g_gain: float = 1.0,
                      b_gain: float = 1.0) -> np.ndarray:
        """
        Balance de blancos manual por canal (BGR).
        gains: 0.5 = atenuar, 1.0 = sin cambio, 2.0 = realzar
        """
        result = image.astype(np.float32)
        result[:, :, 0] = np.clip(result[:, :, 0] * b_gain, 0, 255)
        result[:, :, 1] = np.clip(result[:, :, 1] * g_gain, 0, 255)
        result[:, :, 2] = np.clip(result[:, :, 2] * r_gain, 0, 255)
        return result.astype(np.uint8)

    @staticmethod
    def histogram_equalization(image: np.ndarray,
                               method: str = "clahe") -> np.ndarray:
        """
        Ecualización de histograma para mejorar contraste global.
        method: 'global' (básico) | 'clahe' (adaptativo, recomendado)
        """
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        if method == "clahe":
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
        else:
            l = cv2.equalizeHist(l)
        merged = cv2.merge([l, a, b])
        return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)

    @staticmethod
    def color_temperature(image: np.ndarray, temperature: int = 6500) -> np.ndarray:
        """
        Simula temperatura de color (Kelvin) ajustando canales R/B.
        temperatura < 5000K → calidez (más rojo/amarillo)
        temperatura > 6500K → frialdad (más azul)
        """
        # Mapeo simplificado de temperatura a gains R y B
        if temperature < 5000:
            r_gain = 1.0 + (5000 - temperature) / 5000 * 0.5
            b_gain = max(0.5, 1.0 - (5000 - temperature) / 5000 * 0.5)
        elif temperature > 6500:
            r_gain = max(0.5, 1.0 - (temperature - 6500) / 4500 * 0.5)
            b_gain = 1.0 + (temperature - 6500) / 4500 * 0.5
        else:
            r_gain = b_gain = 1.0
        return ColorAdjustments.white_balance(image, r_gain=r_gain, b_gain=b_gain)


# ─────────────────────────────────────────────
#  CONVERSIONES DE ESPACIO DE COLOR
# ─────────────────────────────────────────────

class ColorSpaceConverter:
    """Convierte la imagen a distintos espacios de color para visualización."""

    CONVERSIONS = {
        "original": None,
        "grises":   cv2.COLOR_BGR2GRAY,
        "hsv":      cv2.COLOR_BGR2HSV,
        "lab":      cv2.COLOR_BGR2LAB,
        "rgb":      cv2.COLOR_BGR2RGB,
        "ycrcb":    cv2.COLOR_BGR2YCrCb,
        "hls":      cv2.COLOR_BGR2HLS,
        "xyz":      cv2.COLOR_BGR2XYZ,
    }

    @classmethod
    def convert(cls, image: np.ndarray, target: str = "original") -> np.ndarray:
        """
        Convierte la imagen al espacio de color indicado.
        Devuelve siempre una imagen BGR de 3 canales (compatible con Streamlit).
        """
        target = target.lower()
        if target == "original" or target not in cls.CONVERSIONS:
            return image

        code = cls.CONVERSIONS[target]
        converted = cv2.cvtColor(image, code)

        # Si el resultado es de 1 canal (grises), reconvertir a 3 canales
        if len(converted.shape) == 2:
            converted = cv2.cvtColor(converted, cv2.COLOR_GRAY2BGR)
        elif target == "rgb":
            # Mantener como BGR para OpenCV pero los valores ya están en RGB
            # Revertir para que Streamlit lo muestre bien
            converted = cv2.cvtColor(converted, cv2.COLOR_RGB2BGR)

        return converted

    @classmethod
    def available_spaces(cls) -> list[str]:
        return list(cls.CONVERSIONS.keys())


# ─────────────────────────────────────────────
#  EFECTOS ESPECIALES / ARTÍSTICOS
# ─────────────────────────────────────────────

class SpecialEffects:
    """Efectos adicionales útiles para demostración pedagógica."""

    @staticmethod
    def cartoon(image: np.ndarray,
                blur_ksize: int = 7,
                line_size: int = 7,
                color_reduce: int = 9) -> np.ndarray:
        """
        Efecto caricatura: bordes fuertes + colores suavizados.
        """
        # Reducir colores
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(gray, blur_ksize if blur_ksize % 2 == 1 else blur_ksize + 1)
        edges = cv2.adaptiveThreshold(
            gray_blur, 255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            blockSize=line_size if line_size % 2 == 1 else line_size + 1,
            C=9
        )
        # Suavizar colores
        color = image.copy()
        for _ in range(color_reduce):
            color = cv2.bilateralFilter(color, 9, 300, 300)
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        return cartoon

    @staticmethod
    def emboss(image: np.ndarray) -> np.ndarray:
        """Efecto relieve / emboss."""
        kernel = np.array([
            [-2, -1,  0],
            [-1,  1,  1],
            [ 0,  1,  2]
        ], dtype=np.float32)
        embossed = cv2.filter2D(image, -1, kernel) + 128
        return np.clip(embossed, 0, 255).astype(np.uint8)

    @staticmethod
    def sepia(image: np.ndarray, intensity: float = 1.0) -> np.ndarray:
        """Filtro sepia (efecto fotografía antigua)."""
        kernel = np.array([
            [0.272, 0.534, 0.131],
            [0.349, 0.686, 0.168],
            [0.393, 0.769, 0.189]
        ], dtype=np.float32) * intensity
        sepia_img = cv2.transform(image.astype(np.float32), kernel)
        # Mezclar con original según intensidad
        result = np.clip(sepia_img * intensity + image * (1 - intensity), 0, 255)
        return result.astype(np.uint8)

    @staticmethod
    def night_vision(image: np.ndarray) -> np.ndarray:
        """Simula visión nocturna verde."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        green = np.zeros_like(image)
        green[:, :, 1] = enhanced  # Solo canal verde
        return green

    @staticmethod
    def vignette(image: np.ndarray, strength: float = 0.5) -> np.ndarray:
        """Oscurece los bordes de la imagen (efecto viñeta)."""
        h, w = image.shape[:2]
        # Crear máscara gaussiana centrada
        sigma = max(h, w) * (1 - strength)
        kernel_x = cv2.getGaussianKernel(w, sigma)
        kernel_y = cv2.getGaussianKernel(h, sigma)
        kernel = kernel_y * kernel_x.T
        mask = kernel / kernel.max()
        mask = mask[:, :, np.newaxis]
        result = (image.astype(np.float32) * mask).astype(np.uint8)
        return result

    @staticmethod
    def pixelate(image: np.ndarray, block_size: int = 10) -> np.ndarray:
        """Efecto pixelado (mosaico)."""
        h, w = image.shape[:2]
        temp = cv2.resize(image, (w // block_size, h // block_size),
                          interpolation=cv2.INTER_LINEAR)
        return cv2.resize(temp, (w, h), interpolation=cv2.INTER_NEAREST)


# ─────────────────────────────────────────────
#  PIPELINE PRINCIPAL — API PÚBLICA
# ─────────────────────────────────────────────

class FilterPipeline:
    """
    Clase principal del módulo Filters.
    Gestiona una lista ordenada de filtros y los aplica en secuencia.

    Uso:
        pipeline = FilterPipeline()
        pipeline.add("blur", kernel_size=15)
        pipeline.add("contraste", alpha=1.5, beta=10)
        resultado = pipeline.apply(frame)
    """

    # Mapa de nombres amigables → función interna
    FILTER_MAP = {
        # Suavizado
        "blur":             SpatialFilters.gaussian_blur,
        "gaussian_blur":    SpatialFilters.gaussian_blur,
        "median_blur":      SpatialFilters.median_blur,
        "bilateral":        SpatialFilters.bilateral_filter,
        "box_blur":         SpatialFilters.box_blur,
        # Nitidez
        "sharpen":          SpatialFilters.sharpen,
        "nitidez":          SpatialFilters.sharpen,
        "unsharp_mask":     SpatialFilters.unsharp_mask,
        # Bordes
        "canny":            SpatialFilters.canny_edges,
        "bordes_canny":     SpatialFilters.canny_edges,
        "sobel":            SpatialFilters.sobel_edges,
        "bordes_sobel":     SpatialFilters.sobel_edges,
        "laplacian":        SpatialFilters.laplacian_edges,
        "bordes_laplacian": SpatialFilters.laplacian_edges,
        # Morfología
        "morfologia":       SpatialFilters.morphology,
        "morphology":       SpatialFilters.morphology,
        # Color y brillo
        "contraste":        ColorAdjustments.brightness_contrast,
        "brillo_contraste": ColorAdjustments.brightness_contrast,
        "gamma":            ColorAdjustments.gamma_correction,
        "saturacion":       ColorAdjustments.saturation,
        "saturación":       ColorAdjustments.saturation,
        "hue":              ColorAdjustments.hue_shift,
        "matiz":            ColorAdjustments.hue_shift,
        "balance_blancos":  ColorAdjustments.white_balance,
        "temperatura":      ColorAdjustments.color_temperature,
        "ecualizar":        ColorAdjustments.histogram_equalization,
        # Efectos especiales
        "cartoon":          SpecialEffects.cartoon,
        "caricatura":       SpecialEffects.cartoon,
        "emboss":           SpecialEffects.emboss,
        "relieve":          SpecialEffects.emboss,
        "sepia":            SpecialEffects.sepia,
        "noche":            SpecialEffects.night_vision,
        "night_vision":     SpecialEffects.night_vision,
        "vignette":         SpecialEffects.vignette,
        "viñeta":           SpecialEffects.vignette,
        "pixelate":         SpecialEffects.pixelate,
        "pixelar":          SpecialEffects.pixelate,
    }

    def __init__(self):
        self._filters: list[FilterConfig] = []

    # ── Gestión del pipeline ──────────────────────────────────────

    def add(self, filter_name: str, **params) -> "FilterPipeline":
        """
        Agrega un filtro al final del pipeline.
        Retorna self para permitir encadenamiento: pipeline.add(...).add(...)
        """
        name = filter_name.lower()
        if name not in self.FILTER_MAP:
            logger.warning(f"Filtro '{filter_name}' no reconocido. Ignorado.")
            return self
        self._filters.append(FilterConfig(name=name, params=params))
        logger.info(f"Filtro añadido: {name} | params: {params}")
        return self

    def remove(self, index: int) -> "FilterPipeline":
        """Elimina el filtro en la posición indicada."""
        if 0 <= index < len(self._filters):
            removed = self._filters.pop(index)
            logger.info(f"Filtro eliminado: {removed.name}")
        return self

    def toggle(self, index: int) -> "FilterPipeline":
        """Activa/desactiva un filtro sin eliminarlo."""
        if 0 <= index < len(self._filters):
            self._filters[index].enabled = not self._filters[index].enabled
        return self

    def clear(self) -> "FilterPipeline":
        """Limpia todos los filtros del pipeline."""
        self._filters.clear()
        return self

    def list_filters(self) -> list[dict]:
        """Devuelve el estado actual del pipeline (útil para Dev 4)."""
        return [
            {
                "index": i,
                "name": f.name,
                "params": f.params,
                "enabled": f.enabled,
            }
            for i, f in enumerate(self._filters)
        ]

    @classmethod
    def available_filters(cls) -> list[str]:
        """Lista todos los nombres de filtros disponibles."""
        return sorted(cls.FILTER_MAP.keys())

    # ── Aplicación ────────────────────────────────────────────────

    def apply(self, image: np.ndarray,
              color_space: str = "original") -> ProcessingResult:
        """
        Aplica todos los filtros activos en orden secuencial.

        Args:
            image:       Frame BGR (de OpenCV o Streamlit).
            color_space: Espacio de color de salida (ver ColorSpaceConverter).

        Returns:
            ProcessingResult con imagen procesada y metadata.
        """
        if image is None or image.size == 0:
            raise ValueError("La imagen de entrada es inválida o está vacía.")

        result = image.copy()
        applied = []

        for fc in self._filters:
            if not fc.enabled:
                continue
            fn = self.FILTER_MAP.get(fc.name)
            if fn is None:
                continue
            try:
                result = fn(result, **fc.params)
                applied.append(fc.name)
            except TypeError as e:
                logger.error(f"Parámetros inválidos para '{fc.name}': {e}")
            except cv2.error as e:
                logger.error(f"Error de OpenCV en '{fc.name}': {e}")

        # Conversión de espacio de color al final
        if color_space != "original":
            result = ColorSpaceConverter.convert(result, color_space)

        metadata = {
            "height": result.shape[0],
            "width":  result.shape[1],
            "channels": result.shape[2] if len(result.shape) == 3 else 1,
            "dtype":  str(result.dtype),
            "filters_count": len(applied),
            "color_space": color_space,
        }

        return ProcessingResult(
            image=result,
            filters_applied=applied,
            metadata=metadata,
        )

    def apply_single(self, image: np.ndarray,
                     filter_name: str, **params) -> np.ndarray:
        """
        Aplica un único filtro sin modificar el pipeline (útil para preview).
        """
        name = filter_name.lower()
        fn = self.FILTER_MAP.get(name)
        if fn is None:
            logger.warning(f"Filtro '{filter_name}' no encontrado.")
            return image
        return fn(image, **params)


# ─────────────────────────────────────────────
#  UTILIDADES PARA INTEGRACIÓN CON STREAMLIT
# ─────────────────────────────────────────────

class StreamlitBridge:
    """
    Funciones de conversión entre formatos de OpenCV y Streamlit.
    Dev 4 (UX) puede importar estas utilidades directamente.
    """

    @staticmethod
    def bgr_to_rgb(image: np.ndarray) -> np.ndarray:
        """
        OpenCV usa BGR; Streamlit/PIL esperan RGB.
        Llamar antes de st.image(frame).
        """
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    @staticmethod
    def rgb_to_bgr(image: np.ndarray) -> np.ndarray:
        """
        Convierte de vuelta a BGR para procesamiento con OpenCV.
        Llamar cuando Streamlit entregue un frame RGB.
        """
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    @staticmethod
    def bytes_to_bgr(file_bytes: bytes) -> Optional[np.ndarray]:
        """
        Convierte bytes de un archivo subido en Streamlit a numpy BGR.
        Uso: frame = StreamlitBridge.bytes_to_bgr(uploaded_file.read())
        """
        arr = np.frombuffer(file_bytes, np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)

    @staticmethod
    def resize_for_display(image: np.ndarray,
                           max_width: int = 800) -> np.ndarray:
        """Redimensiona la imagen para visualización sin distorsión."""
        h, w = image.shape[:2]
        if w <= max_width:
            return image
        scale = max_width / w
        new_w, new_h = int(w * scale), int(h * scale)
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)