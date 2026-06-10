"""
VisioLab - Modulo de deteccion de objetos (Dev 2)
Wrapper sobre ultralytics YOLO para inferencia y anotacion de imagenes.
"""

import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import Optional
import time
import logging

logger = logging.getLogger("VisioLab.Detection")

# Se importa bajo demanda para no bloquear si no esta instalado
_yolo_available = False
try:
    from ultralytics import YOLO
    _yolo_available = True
except ImportError:
    logger.warning("ultralytics no instalado, deteccion YOLO no disponible")


@dataclass
class Detection:
    """Una deteccion individual."""
    class_id: int
    class_name: str
    confidence: float
    bbox: tuple  # (x1, y1, x2, y2)
    center: tuple  # (cx, cy)


@dataclass
class DetectionResult:
    """Resultado completo de inferencia sobre una imagen."""
    detections: list[Detection] = field(default_factory=list)
    annotated_image: Optional[np.ndarray] = None
    inference_time_ms: float = 0.0
    model_name: str = ""
    class_counts: dict = field(default_factory=dict)

    @property
    def total_objects(self) -> int:
        return len(self.detections)


# Paleta de colores para dibujar bounding boxes (evita repetir colores)
_BOX_COLORS = [
    (99, 102, 241),   # indigo
    (236, 72, 153),   # pink
    (34, 197, 94),    # green
    (251, 146, 60),   # orange
    (14, 165, 233),   # sky
    (168, 85, 247),   # purple
    (234, 179, 8),    # yellow
    (239, 68, 68),    # red
    (45, 212, 191),   # teal
    (156, 163, 175),  # gray
]


class ObjectDetector:
    """
    Detector de objetos usando YOLOv8.
    El modelo se descarga automaticamente la primera vez.
    """

    AVAILABLE_MODELS = {
        "YOLOv8 Nano (rapido)": "yolov8n.pt",
        "YOLOv8 Small (balanceado)": "yolov8s.pt",
        "YOLOv8 Medium (preciso)": "yolov8m.pt",
    }

    def __init__(self, model_name: str = "yolov8n.pt"):
        if not _yolo_available:
            raise ImportError(
                "Instala ultralytics: pip install ultralytics"
            )
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        """Carga lazy del modelo para no bloquear el import."""
        if self._model is None:
            logger.info(f"Cargando modelo {self.model_name}...")
            self._model = YOLO(self.model_name)
        return self._model

    def detect(
        self,
        image: np.ndarray,
        confidence: float = 0.25,
        iou_threshold: float = 0.45,
        classes: Optional[list[int]] = None,
    ) -> DetectionResult:
        """
        Ejecuta deteccion sobre una imagen BGR.
        Retorna DetectionResult con las detecciones y metadata.
        """
        model = self._load_model()

        start = time.perf_counter()
        results = model.predict(
            image,
            conf=confidence,
            iou=iou_threshold,
            classes=classes,
            verbose=False,
        )
        elapsed = (time.perf_counter() - start) * 1000

        detections = []
        class_counts = {}

        if results and len(results) > 0:
            result = results[0]
            boxes = result.boxes

            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    cls_name = result.names.get(cls_id, f"clase_{cls_id}")

                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2

                    detections.append(Detection(
                        class_id=cls_id,
                        class_name=cls_name,
                        confidence=conf,
                        bbox=(x1, y1, x2, y2),
                        center=(cx, cy),
                    ))

                    class_counts[cls_name] = class_counts.get(cls_name, 0) + 1

        # Dibujar las anotaciones
        annotated = self.draw_detections(image, detections)

        return DetectionResult(
            detections=detections,
            annotated_image=annotated,
            inference_time_ms=elapsed,
            model_name=self.model_name,
            class_counts=class_counts,
        )

    def draw_detections(
        self,
        image: np.ndarray,
        detections: list[Detection],
    ) -> np.ndarray:
        """Dibuja bounding boxes con labels sobre la imagen."""
        img = image.copy()

        for det in detections:
            x1, y1, x2, y2 = det.bbox
            color = _BOX_COLORS[det.class_id % len(_BOX_COLORS)]
            label = f"{det.class_name} {det.confidence:.0%}"

            # Caja principal
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

            # Fondo del label
            (tw, th), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            cv2.rectangle(
                img, (x1, y1 - th - 8), (x1 + tw + 6, y1), color, -1
            )

            # Texto del label
            cv2.putText(
                img, label, (x1 + 3, y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1,
                cv2.LINE_AA,
            )

        return img

    def get_class_names(self) -> dict:
        """Retorna el diccionario de clases del modelo COCO."""
        model = self._load_model()
        return model.names


class DetectionAnalytics:
    """Utilidades de analisis sobre las detecciones para graficos."""

    @staticmethod
    def build_heatmap(
        detections: list[Detection],
        shape: tuple,
        radius: int = 40,
    ) -> np.ndarray:
        """
        Genera un heatmap basado en los centroides de las detecciones.
        Retorna una imagen BGR lista para mostrar.
        """
        h, w = shape[:2]
        heatmap = np.zeros((h, w), dtype=np.float32)

        for det in detections:
            cx, cy = det.center
            cv2.circle(heatmap, (cx, cy), radius, 1.0, -1)

        # Suavizar para que se vea como un heatmap real
        heatmap = cv2.GaussianBlur(heatmap, (0, 0), radius * 0.6)

        if heatmap.max() > 0:
            heatmap = (heatmap / heatmap.max() * 255).astype(np.uint8)
        else:
            heatmap = heatmap.astype(np.uint8)

        colored = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        return colored

    @staticmethod
    def overlay_heatmap(
        image: np.ndarray,
        detections: list[Detection],
        alpha: float = 0.4,
        radius: int = 40,
    ) -> np.ndarray:
        """Superpone el heatmap sobre la imagen original."""
        heatmap = DetectionAnalytics.build_heatmap(
            detections, image.shape, radius
        )
        return cv2.addWeighted(image, 1 - alpha, heatmap, alpha, 0)
