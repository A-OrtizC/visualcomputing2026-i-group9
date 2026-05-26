#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Taller 11-5: Detección de Objetos en Tiempo Real con YOLO y Webcam (Medición de Métricas)
Autor: Estudiante de Computación Visual
Fecha: Mayo 2026
Descripción:
    Aplicación interactiva que captura video en tiempo real de la webcam, realiza detección
    de objetos con YOLOv8, mide métricas de desempeño avanzadas (FPS, Inferencia, Latencia de Ciclo),
    permite cambiar de modelo en caliente (Nano, Small, Medium), controlar la confianza mediante
    un trackbar, filtrar clases y graficar el rendimiento en tiempo real a través de un HUD.
"""

import os
import cv2
import numpy as np
import time
from datetime import datetime

# Directorios de salida
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_DIR = os.path.join(BASE_DIR, "media")
os.makedirs(MEDIA_DIR, exist_ok=True)

# Intentar importar ultralytics para YOLOv8
try:
    # pyrefly: ignore [missing-import]
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("\n" + "="*80)
    print(" ADVERTENCIA: La librería 'ultralytics' no está instalada.")
    print(" La aplicación se ejecutará en 'MODO DEMOSTRACIÓN' con señal de video sintética")
    print(" y simulación de latencias y conteos de YOLOv8.")
    print(" Para ejecutar de forma real, instale los requisitos: pip install -r requirements.txt")
    print("="*80 + "\n")


class SyntheticVideoSource:
    """
    Clase de fallback que simula una señal de video en tiempo real con formas en movimiento
    y metadatos de detección simulados para cuando no hay cámara web física disponible.
    """
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        self.frame_count = 0
        # Objetos rebotando: [x, y, vx, vy, radio, etiqueta, confianza, color]
        self.objects = [
            {"x": 120, "y": 150, "vx": 4, "vy": 3, "r": 35, "label": "person", "conf": 0.88, "color": (0, 140, 255)},
            {"x": 350, "y": 220, "vx": -3, "vy": 5, "r": 30, "label": "dog", "conf": 0.91, "color": (255, 100, 100)},
            {"x": 500, "y": 120, "vx": 5, "vy": -4, "r": 20, "label": "bottle", "conf": 0.76, "color": (100, 255, 100)},
            {"x": 220, "y": 320, "vx": -4, "vy": -3, "r": 25, "label": "cell phone", "conf": 0.84, "color": (255, 240, 0)},
            {"x": 450, "y": 280, "vx": 3, "vy": -4, "r": 32, "label": "laptop", "conf": 0.79, "color": (200, 0, 255)}
        ]

    def read(self):
        self.frame_count += 1
        # Generar fondo estilo radar militar / cuadrícula cyberpunk
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Dibujar cuadrícula dinámica
        grid_size = 40
        offset_x = (self.frame_count * 2) % grid_size
        offset_y = (self.frame_count * 1) % grid_size
        
        for x in range(offset_x, self.width, grid_size):
            cv2.line(frame, (x, 0), (x, self.height), (20, 20, 20), 1)
        for y in range(offset_y, self.height, grid_size):
            cv2.line(frame, (0, y), (self.width, y), (20, 20, 20), 1)

        # Círculos concéntricos de fondo táctico
        cx, cy = self.width // 2, self.height // 2
        cv2.circle(frame, (cx, cy), 150, (28, 22, 22), 1)
        cv2.circle(frame, (cx, cy), 80, (24, 22, 22), 1)
        cv2.drawMarker(frame, (cx, cy), (40, 40, 40), cv2.MARKER_CROSS, 20, 1)

        # Mover objetos y construir detecciones
        detections = []
        for obj in self.objects:
            obj["x"] += obj["vx"]
            obj["y"] += obj["vy"]
            
            # Rebote en bordes
            margin = obj["r"] + 15
            if obj["x"] - margin < 0 or obj["x"] + margin > self.width:
                obj["vx"] *= -1
                obj["x"] = np.clip(obj["x"], margin, self.width - margin)
            if obj["y"] - margin < 40 or obj["y"] + margin > self.height - 40:
                obj["vy"] *= -1
                obj["y"] = np.clip(obj["y"], margin + 40, self.height - margin - 40)
                
            # Renderizar la forma del objeto simulado
            color = obj["color"]
            x, y, r = int(obj["x"]), int(obj["y"]), obj["r"]
            
            if obj["label"] == "person":
                cv2.circle(frame, (x, y - int(r * 0.6)), int(r * 0.4), color, -1)
                cv2.ellipse(frame, (x, y + int(r * 0.5)), (int(r * 0.75), int(r * 0.55)), 0, 180, 360, color, -1)
            elif obj["label"] == "dog":
                cv2.ellipse(frame, (x, y), (int(r), int(r * 0.6)), 0, 0, 360, color, -1)
                cv2.circle(frame, (x + int(r * 0.7), y - int(r * 0.35)), int(r * 0.3), color, -1)
            elif obj["label"] == "cell phone":
                cv2.rectangle(frame, (x - int(r * 0.5), y - r), (x + int(r * 0.5), y + r), color, -1)
            elif obj["label"] == "laptop":
                cv2.rectangle(frame, (x - r, y - int(r * 0.4)), (x + r, y + int(r * 0.4)), color, -1)
                cv2.line(frame, (x - r, y + int(r * 0.4)), (x - r - 10, y + int(r * 0.8)), color, 2)
                cv2.line(frame, (x + r, y + int(r * 0.4)), (x + r + 10, y + int(r * 0.8)), color, 2)
            else:
                # botella
                cv2.rectangle(frame, (x - int(r * 0.5), y - int(r * 0.4)), (x + int(r * 0.5), y + r), color, -1)
                cv2.rectangle(frame, (x - int(r * 0.2), y - r), (x + int(r * 0.2), y - int(r * 0.4)), color, -1)
            
            # Etiqueta
            cv2.putText(frame, f"RAW_FEED: {obj['label'].upper()}", (x - r, y - r - 8), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.32, (100, 100, 100), 1, cv2.LINE_AA)

            # Bounding box
            x1 = max(0, int(obj["x"] - r * 1.2))
            y1 = max(0, int(obj["y"] - r * 1.4))
            x2 = min(self.width, int(obj["x"] + r * 1.2))
            y2 = min(self.height, int(obj["y"] + r * 1.2))
            
            detections.append({
                "box": [x1, y1, x2, y2],
                "conf": min(1.0, max(0.2, obj["conf"] + 0.05 * np.sin(self.frame_count * 0.1))),
                "class_name": obj["label"],
                "class_id": 0
            })

        return True, frame, detections


def draw_sci_fi_box(img, box, label, conf, color):
    """
    Dibuja corchetes angulares futuristas (brackets) y etiquetas opacas elegantes sobre el frame.
    """
    x1, y1, x2, y2 = box
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 1, lineType=cv2.LINE_AA)
    
    corner_len = min(15, int((x2 - x1) * 0.22))
    thick = 3
    
    # Top-Left
    cv2.line(img, (x1, y1), (x1 + corner_len, y1), color, thick, lineType=cv2.LINE_AA)
    cv2.line(img, (x1, y1), (x1, y1 + corner_len), color, thick, lineType=cv2.LINE_AA)
    # Top-Right
    cv2.line(img, (x2, y1), (x2 - corner_len, y1), color, thick, lineType=cv2.LINE_AA)
    cv2.line(img, (x2, y1), (x2, y1 + corner_len), color, thick, lineType=cv2.LINE_AA)
    # Bottom-Left
    cv2.line(img, (x1, y2), (x1 + corner_len, y2), color, thick, lineType=cv2.LINE_AA)
    cv2.line(img, (x1, y2), (x1, y2 - corner_len), color, thick, lineType=cv2.LINE_AA)
    # Bottom-Right
    cv2.line(img, (x2, y2), (x2 - corner_len, y2), color, thick, lineType=cv2.LINE_AA)
    cv2.line(img, (x2, y2), (x2, y2 - corner_len), color, thick, lineType=cv2.LINE_AA)
    
    # Etiqueta
    text = f"{label.upper()} {conf:.0%}"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.35
    thickness = 1
    (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)
    
    cv2.rectangle(img, (x1, max(0, y1 - text_h - 8)), (x1 + text_w + 10, y1), color, -1)
    cv2.putText(img, text, (x1 + 5, y1 - 4), font, font_scale, (255, 255, 255) if color != (255, 255, 255) else (0, 0, 0), thickness, lineType=cv2.LINE_AA)


def draw_performance_graph(img, fps_history, inf_history, x_pos, y_pos, width=200, height=90):
    """
    Dibuja un osciloscopio vectorial dinámico en tiempo real que traza las curvas de FPS e Inferencia.
    """
    # 1. Fondo semitransparente
    overlay = img.copy()
    cv2.rectangle(overlay, (x_pos, y_pos), (x_pos + width, y_pos + height), (10, 10, 10), -1)
    cv2.addWeighted(overlay, 0.65, img, 0.35, 0, img)
    cv2.rectangle(img, (x_pos, y_pos), (x_pos + width, y_pos + height), (60, 60, 60), 1, lineType=cv2.LINE_AA)
    
    # Título y división
    cv2.putText(img, "HISTORICO DE RENDIMIENTO", (x_pos + 8, y_pos + 13), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 240), 1, cv2.LINE_AA)
    cv2.line(img, (x_pos + 5, y_pos + 18), (x_pos + width - 5, y_pos + 18), (40, 40, 40), 1)
    
    # Leyenda pequeña
    cv2.putText(img, "■ FPS (Max 60)", (x_pos + 8, y_pos + 84), cv2.FONT_HERSHEY_SIMPLEX, 0.28, (0, 255, 100), 1, cv2.LINE_AA)
    cv2.putText(img, "■ Inf (Max 80ms)", (x_pos + 110, y_pos + 84), cv2.FONT_HERSHEY_SIMPLEX, 0.28, (0, 255, 240), 1, cv2.LINE_AA)
    
    # 2. Dibujar líneas de referencia (Línea de 30 FPS / 40ms)
    # y = y_pos + 18 (arriba), y = y_pos + height - 12 (abajo, donde empieza la leyenda)
    graph_h = height - 30
    y_zero = y_pos + height - 12
    
    # Línea horizontal del medio (equivalente a 30 FPS / 40ms)
    cv2.line(img, (x_pos + 5, y_zero - graph_h // 2), (x_pos + width - 5, y_zero - graph_h // 2), (30, 30, 30), 1)
    
    # 3. Trazar las curvas si hay suficientes datos
    max_points = min(len(fps_history), width - 10)
    if max_points < 2:
        return
        
    step = (width - 10) / (max_points - 1) if max_points > 1 else 1.0
    
    pts_fps = []
    pts_inf = []
    
    for i in range(max_points):
        x = int(x_pos + 5 + i * step)
        
        # Curva de FPS: normalizada de 0 a 60 FPS
        fps_val = np.clip(fps_history[-(max_points - i)], 0, 60)
        y_fps = int(y_zero - (fps_val / 60.0) * graph_h)
        pts_fps.append((x, y_fps))
        
        # Curva de Inferencia: normalizada de 0 a 80 ms
        inf_val = np.clip(inf_history[-(max_points - i)], 0, 80)
        y_inf = int(y_zero - (inf_val / 80.0) * graph_h)
        pts_inf.append((x, y_inf))
        
    # Dibujar líneas del gráfico
    for i in range(len(pts_fps) - 1):
        cv2.line(img, pts_fps[i], pts_fps[i+1], (0, 255, 100), 1, lineType=cv2.LINE_AA)
        cv2.line(img, pts_inf[i], pts_inf[i+1], (0, 255, 240), 1, lineType=cv2.LINE_AA)


def main():
    print("="*70)
    print(" PIPELINE DE DETECCIÓN YOLOv8 CON MÉTRICAS DE RENDIMIENTO")
    print("="*70)
    
    # 1. Conexión de hardware (Cámara DirectShow para evitar cuelgues)
    cap = None
    demo_mode = False
    
    print("[INFO] Intentando conectar con la Webcam (ID 0)...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print("[AVISO] No se pudo acceder a una cámara física.")
        print("[INFO] Activando el Generador de Video Sintético de Fallback...")
        demo_mode = True
        cap = SyntheticVideoSource(width=640, height=480)
    else:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        print("[OK] Cámara web real conectada e inicializada a 640x480.")

    # 2. Carga inicial del modelo YOLOv8 Nano
    model_sizes = {
        "n": {"file": "yolov8n.pt", "name": "YOLOv8 Nano (Ultra-Fast)", "sim_inf": 6.5},
        "s": {"file": "yolov8s.pt", "name": "YOLOv8 Small (Equilibrado)", "sim_inf": 18.0},
        "m": {"file": "yolov8m.pt", "name": "YOLOv8 Medium (Alta Precision)", "sim_inf": 46.5}
    }
    
    active_size = "n"
    model = None
    active_model_name = "Simulado (YOLOv8 Nano)"
    
    if YOLO_AVAILABLE and not demo_mode:
        print(f"[INFO] Cargando modelo inicial: {model_sizes[active_size]['file']}...")
        try:
            model = YOLO(model_sizes[active_size]["file"])
            active_model_name = model_sizes[active_size]["name"]
            print("[OK] Modelo YOLOv8 cargado con éxito.")
        except Exception as e:
            print(f"[ERROR] No se pudo cargar YOLOv8: {e}")
            print("[INFO] Activando Modo Demo de simulación de IA.")
            if cap is not None and not isinstance(cap, SyntheticVideoSource):
                cap.release()
            demo_mode = True
            cap = SyntheticVideoSource(width=640, height=480)
    else:
        demo_mode = True
        cap = SyntheticVideoSource(width=640, height=480)
        active_model_name = "Simulacion (YOLOv8 Nano)"

    # 3. Inicializar ventana e interfaz
    window_name = "Deteccion Terapeutica YOLO - Metricas de Rendimiento"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    
    # Trackbar de confianza: rango 30 a 80 (mapeado de 0.3 a 0.8 en inferencia)
    cv2.createTrackbar("Confianza (x100)", window_name, 50, 80, lambda x: None)
    # Establecer mínimo implícito de 30 para evitar detecciones fantasma
    cv2.setTrackbarMin("Confianza (x100)", window_name, 30)

    # 4. Variables analíticas y de control
    class_filtering_mode = False  # Filtrar solo personas y tecnología
    target_classes = ["person", "cell phone", "laptop", "bottle"]
    
    # Históricos de métricas para el gráfico
    fps_history = []
    inference_history = []
    
    # Histórico acumulado de objetos
    cumulative_counts = {}
    prev_active_counts = {}
    
    # Medidores temporales y de transición
    prev_time = time.perf_counter()
    loading_status = None
    loading_timer = 0
    hud_notification = "SISTEMA TACTICO ONLINE"
    hud_notification_time = time.time()
    
    print("\n[CONTROLES DISPONIBLES]:")
    print("  [N] - Cambiar a modelo YOLOv8 Nano (Inferencia rápida)")
    print("  [S] - Cambiar a modelo YOLOv8 Small (Equilibrado)")
    print("  [M] - Cambiar a modelo YOLOv8 Medium (Mayor precisión)")
    print("  [F] - Alternar Filtro de Clases (Solo: person, cell phone, laptop, bottle)")
    print("  [C] - Resetear historial de objetos acumulativos")
    print("  [Q o ESC] - Salir de la aplicación")
    print("\nIniciando bucle de análisis en tiempo real...\n")

    while True:
        # Cronometrar el ciclo completo (Latencia de Ciclo)
        cycle_start = time.perf_counter()
        
        # 1. Leer Frame del dispositivo
        detections = []
        if demo_mode:
            ret, raw_frame, raw_detections = cap.read()
        else:
            ret, raw_frame = cap.read()
            
        if not ret:
            print("[ERROR] Fallo al capturar fotograma de la cámara.")
            break
            
        height, width = raw_frame.shape[:2]
        processed_frame = raw_frame.copy()
        
        # Leer valor de la confianza desde la barra deslizante
        conf_slider = cv2.getTrackbarPos("Confianza (x100)", window_name)
        min_confidence = conf_slider / 100.0
        
        # 2. Ejecutar Inferencia de YOLOv8
        inference_time_ms = 0.0
        
        if not demo_mode and model is not None:
            # Medir estrictamente el tiempo de ejecución de la red neuronal
            t_inf_start = time.perf_counter()
            results = model.predict(raw_frame, conf=min_confidence, verbose=False)
            t_inf_end = time.perf_counter()
            inference_time_ms = (t_inf_end - t_inf_start) * 1000.0
            
            # Extraer cajas de inferencia real
            if len(results) > 0:
                for box in results[0].boxes:
                    xyxy = box.xyxy[0].tolist()
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    cls_name = model.names[cls_id]
                    
                    detections.append({
                        "box": list(map(int, xyxy)),
                        "conf": conf,
                        "class_name": cls_name,
                        "class_id": cls_id
                    })
        else:
            # Modo Demostración Sintético
            # Mapear tiempo de inferencia simulado según el tamaño del modelo seleccionado
            base_sim = model_sizes[active_size]["sim_inf"]
            noise = np.random.normal(0, base_sim * 0.08) # ruido gaussiano
            inference_time_ms = max(1.5, base_sim + noise)
            
            # Filtrar detecciones sintéticas por confianza del slider
            detections = [d for d in raw_detections if d["conf"] >= min_confidence]

        # 3. Aplicar Filtro de Clases Seleccionadas (Modo Especializado)
        if class_filtering_mode:
            detections = [d for d in detections if d["class_name"] in target_classes]

        # 4. Conteo de Objetos en Frame y Actualización de Historial
        active_counts = {}
        for d in detections:
            cls_name = d["class_name"]
            active_counts[cls_name] = active_counts.get(cls_name, 0) + 1
            
        # Algoritmo de tracking de historial acumulado basado en deltas
        # Si la cantidad de un objeto en el frame actual supera la del frame anterior, sumamos la diferencia
        for cls, count in active_counts.items():
            prev_cnt = prev_active_counts.get(cls, 0)
            if count > prev_cnt:
                cumulative_counts[cls] = cumulative_counts.get(cls, 0) + (count - prev_cnt)
                
        prev_active_counts = active_counts.copy()

        # 5. Dibujar cajas delimitadoras Tácticas
        for d in detections:
            box = d["box"]
            cls_name = d["class_name"]
            conf = d["conf"]
            
            # Color del objeto
            if cls_name == "person":
                color = (0, 140, 255) # Naranja neon
            elif cls_name in ["cell phone", "laptop"]:
                color = (255, 240, 0) # Celeste/Amarillo
            elif cls_name == "bottle":
                color = (0, 255, 100) # Verde neon
            else:
                color = (200, 0, 255) # Morado neon
                
            draw_sci_fi_box(processed_frame, box, cls_name, conf, color)

        # 6. Calcular FPS y Latencia de Ciclo
        current_perf_time = time.perf_counter()
        frame_delta = current_perf_time - prev_time
        prev_time = current_perf_time
        
        # FPS mediante promedio móvil
        current_fps = 1.0 / frame_delta if frame_delta > 0 else 30.0
        fps_history.append(current_fps)
        if len(fps_history) > 100:
            fps_history.pop(0)
        smooth_fps = sum(fps_history) / len(fps_history)
        
        # Histórico de Inferencia para la gráfica
        inference_history.append(inference_time_ms)
        if len(inference_history) > 100:
            inference_history.pop(0)
            
        # Calcular Latencia de Ciclo total (Captura + Inferencia + Dibujado completo)
        cycle_latency_ms = (time.perf_counter() - cycle_start) * 1000.0

        # 7. Renderizar HUD e Interfaces Semitransparentes
        
        # A. Banner Superior de Estado
        overlay_top = processed_frame.copy()
        cv2.rectangle(overlay_top, (0, 0), (width, 42), (12, 12, 12), -1)
        cv2.addWeighted(overlay_top, 0.7, processed_frame, 0.3, 0, processed_frame)
        cv2.rectangle(processed_frame, (0, 0), (width, 42), (40, 40, 40), 1)
        
        # Título y Estado
        cv2.putText(processed_frame, "YOLOv8 REALTIME DIAGNOSTIC TOOL", (12, 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 240), 1, cv2.LINE_AA)
        
        # B. Panel de Métricas HUD (En esquina superior derecha)
        metrics_x = width - 290
        cv2.putText(processed_frame, f"FPS: {smooth_fps:.1f}", (metrics_x, 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 100) if smooth_fps >= 22 else (0, 0, 255), 1, cv2.LINE_AA)
        cv2.putText(processed_frame, f"Inf: {inference_time_ms:.1f}ms", (metrics_x + 85, 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 240), 1, cv2.LINE_AA)
        cv2.putText(processed_frame, f"Lat: {cycle_latency_ms:.1f}ms", (metrics_x + 190, 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1, cv2.LINE_AA)

        # C. Panel Lateral Izquierdo (Métricas de Cuentas)
        overlay_side = processed_frame.copy()
        cv2.rectangle(overlay_side, (10, 52), (210, 235), (10, 10, 10), -1)
        cv2.addWeighted(overlay_side, 0.6, processed_frame, 0.4, 0, processed_frame)
        cv2.rectangle(processed_frame, (10, 52), (210, 235), (55, 55, 55), 1, lineType=cv2.LINE_AA)
        
        # Título del panel
        cv2.putText(processed_frame, "ANALYTICS PANEL", (18, 68), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 240), 1, cv2.LINE_AA)
        cv2.line(processed_frame, (15, 73), (205, 73), (45, 45, 45), 1)
        
        # Modelo Activo
        cv2.putText(processed_frame, "MODELO SELECCIONADO:", (18, 88), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (150, 150, 150), 1, cv2.LINE_AA)
        cv2.putText(processed_frame, active_model_name, (18, 102), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (255, 255, 255), 1, cv2.LINE_AA)
        
        # Conteo Instantáneo
        cv2.putText(processed_frame, "ACTIVO EN PANTALLA:", (18, 122), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (150, 150, 150), 1, cv2.LINE_AA)
        y_offset = 136
        if not active_counts:
            cv2.putText(processed_frame, "Ninguno", (18, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (110, 110, 110), 1, cv2.LINE_AA)
            y_offset += 14
        else:
            for cls, count in list(active_counts.items())[:3]: # mostrar máximo 3 clases para evitar desborde
                cv2.putText(processed_frame, f"  {cls.capitalize()}: {count}", (18, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (0, 255, 100), 1, cv2.LINE_AA)
                y_offset += 14
                
        # Historial acumulado desde inicio
        cv2.line(processed_frame, (15, 180), (205, 180), (45, 45, 45), 1)
        cv2.putText(processed_frame, "HISTORICO ACUMULATIVO:", (18, 195), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (150, 150, 150), 1, cv2.LINE_AA)
        hist_str = ", ".join([f"{k}:{v}" for k, v in cumulative_counts.items()])
        if not hist_str:
            hist_str = "Vacio. Detectando..."
        if len(hist_str) > 28:
            hist_str = hist_str[:26] + "..."
        cv2.putText(processed_frame, hist_str, (18, 212), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (0, 255, 240), 1, cv2.LINE_AA)

        # D. Estado del Filtro de Clases (HUD Indicator)
        filter_color = (0, 255, 100) if class_filtering_mode else (180, 180, 180)
        filter_str = "FILTRO CLASES: SOLO DETECTA TECTONICOS" if class_filtering_mode else "FILTRO CLASES: TODAS LAS 80 CLASES COCO"
        cv2.putText(processed_frame, filter_str, (18, 227), cv2.FONT_HERSHEY_SIMPLEX, 0.28, filter_color, 1, cv2.LINE_AA)

        # E. Dibujar el Osciloscopio Vectorial de Rendimiento (Bonus de Gráfico en esquina)
        draw_performance_graph(processed_frame, fps_history, inference_history, 
                               x_pos=width - 215, y_pos=height - 128, width=205, height=90)

        # F. Notificaciones de Toast temporales
        if time.time() - hud_notification_time < 2.0:
            notif_w = 260
            cv2.rectangle(processed_frame, (10, height - 70), (10 + notif_w, height - 42), (20, 20, 20), -1)
            cv2.rectangle(processed_frame, (10, height - 70), (10 + notif_w, height - 42), (0, 255, 240), 1)
            cv2.putText(processed_frame, f">> {hud_notification}", (20, height - 52), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 240), 1, cv2.LINE_AA)

        # G. Leyenda de Controles Inferiores
        overlay_bottom = processed_frame.copy()
        cv2.rectangle(overlay_bottom, (0, height - 30), (width, height), (15, 15, 15), -1)
        cv2.addWeighted(overlay_bottom, 0.75, processed_frame, 0.25, 0, processed_frame)
        
        legend_str = "[N,S,M] Cambiar Modelo | [F] Filtrar Clases | [C] Limpiar Historial | [Q] Salir"
        cv2.putText(processed_frame, legend_str, (12, height - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (190, 190, 190), 1, cv2.LINE_AA)

        # H. Visualizar aviso de carga si se está cambiando de modelo en caliente
        if loading_status is not None:
            # Dibujar caja de carga en el centro de la pantalla
            box_w, box_h = 320, 80
            bx, by = (width - box_w) // 2, (height - box_h) // 2
            cv2.rectangle(processed_frame, (bx, by), (bx + box_w, by + box_h), (10, 10, 10), -1)
            cv2.rectangle(processed_frame, (bx, by), (bx + box_w, by + box_h), (0, 255, 240), 2)
            cv2.putText(processed_frame, "CARGANDO MODELO NEURONAL...", (bx + 20, by + 35), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 240), 1, cv2.LINE_AA)
            cv2.putText(processed_frame, f"Cargando {loading_status}...", (bx + 20, by + 58), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1, cv2.LINE_AA)
            
            # Dibujar barra de carga dinámica parpadeante
            bar_len = int((time.time() * 200) % 280)
            cv2.rectangle(processed_frame, (bx + 20, by + 68), (bx + 20 + bar_len, by + 72), (0, 255, 100), -1)

        # 8. Renderizar en la Ventana de OpenCV
        cv2.imshow(window_name, processed_frame)

        # Si se activó aviso de carga de modelo en el frame anterior, lo cargamos en este frame
        if loading_status is not None:
            t_load_start = time.time()
            try:
                if not demo_mode:
                    model = YOLO(model_sizes[active_size]["file"])
                    active_model_name = model_sizes[active_size]["name"]
                else:
                    active_model_name = f"Simulacion ({model_sizes[active_size]['file'][:-3].capitalize()})"
                
                # Simular tiempo de carga de medio segundo en modo demo para efectos visuales elegantes
                if demo_mode:
                    time.sleep(0.5)
                    
                hud_notification = f"MODELO CARGADO: {model_sizes[active_size]['file'].upper()}"
                print(f"[OK] Modelo cambiado a {model_sizes[active_size]['file']} en {time.time() - t_load_start:.2f}s")
            except Exception as e:
                print(f"[ERROR] No se pudo cambiar el modelo: {e}")
                hud_notification = "ERROR AL CARGAR MODELO"
            
            loading_status = None
            hud_notification_time = time.time()
            prev_time = time.perf_counter()  # resetear timer de FPS para evitar brincos
            continue

        # 9. Capturar Teclado
        key = cv2.waitKey(1) & 0xFF
        
        if key in [ord('q'), 27]: # 'q' o ESC
            break
        elif key == ord('f'):
            # Alternar filtrado selectivo de clases
            class_filtering_mode = not class_filtering_mode
            hud_notification = f"FILTRO CLASES: {'ON' if class_filtering_mode else 'OFF'}"
            hud_notification_time = time.time()
            print(f"[INFO] Filtro de clases especiales: {'ACTIVADO' if class_filtering_mode else 'DESACTIVADO'}")
        elif key == ord('c'):
            # Limpiar historial de conteos acumulativos
            cumulative_counts.clear()
            hud_notification = "HISTORIAL RESETEADO"
            hud_notification_time = time.time()
            print("[INFO] Historial acumulativo de detecciones borrado.")
        elif chr(key).lower() in ['n', 's', 'm'] and loading_status is None:
            # Mapear tecla pulsada al tamaño del modelo
            selected_size = chr(key).lower()
            if selected_size != active_size:
                active_size = selected_size
                loading_status = model_sizes[active_size]["file"]
                loading_timer = time.time()
                
    # 10. Cerrar recursos de hardware
    print("\nLiberando recursos de video...")
    if not demo_mode and cap is not None:
        cap.release()
    cv2.destroyAllWindows()
    print("[OK] Recursos liberados. ¡Aplicación finalizada correctamente!")


if __name__ == "__main__":
    main()
