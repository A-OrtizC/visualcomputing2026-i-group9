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
    print(" y detección de objetos simulada.")
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
            {"x": 120, "y": 150, "vx": 4, "vy": 3, "r": 35, "label": "person", "conf": 0.89, "color": (0, 140, 255)},
            {"x": 350, "y": 220, "vx": -3, "vy": 5, "r": 30, "label": "dog", "conf": 0.94, "color": (255, 100, 100)},
            {"x": 500, "y": 120, "vx": 5, "vy": -4, "r": 20, "label": "cup", "conf": 0.76, "color": (100, 255, 100)},
            {"x": 220, "y": 320, "vx": -4, "vy": -3, "r": 25, "label": "cell phone", "conf": 0.82, "color": (255, 240, 0)}
        ]

    def read(self):
        self.frame_count += 1
        # Generar fondo oscuro estilo Cyberpunk con cuadrícula
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Dibujar cuadrícula dinámica en movimiento
        grid_size = 40
        offset_x = (self.frame_count * 2) % grid_size
        offset_y = (self.frame_count * 1) % grid_size
        
        for x in range(offset_x, self.width, grid_size):
            cv2.line(frame, (x, 0), (x, self.height), (22, 22, 22), 1)
        for y in range(offset_y, self.height, grid_size):
            cv2.line(frame, (0, y), (self.width, y), (22, 22, 22), 1)

        # Círculo digital y punto de mira en el centro
        cx, cy = self.width // 2, self.height // 2
        pulse = int(12 * np.sin(self.frame_count * 0.08))
        cv2.circle(frame, (cx, cy), 120 + pulse, (30, 20, 20), 1)
        cv2.circle(frame, (cx, cy), 80, (25, 20, 20), 1)
        cv2.drawMarker(frame, (cx, cy), (45, 45, 45), cv2.MARKER_CROSS, 24, 1)
        
        # Efecto de texto flotante de fondo
        cv2.putText(frame, "VIRTUAL FEED - LAB ENVIRONMENT", (40, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (40, 40, 40), 1, cv2.LINE_AA)

        # Actualizar física de objetos rebotando y generar detecciones
        detections = []
        for obj in self.objects:
            obj["x"] += obj["vx"]
            obj["y"] += obj["vy"]
            
            # Rebote en bordes horizontales (dejando margen para que no se corten las formas)
            margin = obj["r"] + 10
            if obj["x"] - margin < 0 or obj["x"] + margin > self.width:
                obj["vx"] *= -1
                obj["x"] = np.clip(obj["x"], margin, self.width - margin)
            # Rebote en bordes verticales
            if obj["y"] - margin < 40 or obj["y"] + margin > self.height - 45: # margen para HUD
                obj["vy"] *= -1
                obj["y"] = np.clip(obj["y"], margin + 40, self.height - margin - 45)
                
            # Dibujar el objeto físico simulado en la pantalla
            color = obj["color"]
            x, y, r = int(obj["x"]), int(obj["y"]), obj["r"]
            
            if obj["label"] == "person":
                # Dibujar silueta simple (cabeza y hombros/cuerpo)
                cv2.circle(frame, (x, y - int(r * 0.6)), int(r * 0.4), color, -1)
                cv2.ellipse(frame, (x, y + int(r * 0.5)), (int(r * 0.8), int(r * 0.6)), 0, 180, 360, color, -1)
            elif obj["label"] == "dog":
                # Dibujar cuadrúpedo abstracto
                cv2.ellipse(frame, (x, y), (int(r), int(r * 0.6)), 0, 0, 360, color, -1)
                cv2.circle(frame, (x + int(r * 0.7), y - int(r * 0.4)), int(r * 0.35), color, -1)
            elif obj["label"] == "cell phone":
                # Dibujar rectángulo tipo smartphone
                cv2.rectangle(frame, (x - int(r * 0.6), y - r), (x + int(r * 0.6), y + r), color, -1)
                cv2.circle(frame, (x, y + int(r * 0.7)), 3, (0, 0, 0), -1)
            else:
                # Taza / Círculo genérico
                cv2.circle(frame, (x, y), r, color, -1)
                # asa
                cv2.ellipse(frame, (x + int(r * 0.8), y), (int(r * 0.4), int(r * 0.3)), 0, -90, 90, color, 2)
            
            # Etiqueta de la señal analógica
            cv2.putText(frame, f"RAW_OBJ: {obj['label'].upper()}", (x - r, y - r - 8), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (120, 120, 120), 1, cv2.LINE_AA)

            # Generar caja de detección YOLO simulada con ligera fluctuación en coordenadas
            fluct = int(3 * np.sin(self.frame_count * 0.2))
            x1 = max(0, int(obj["x"] - r * 1.25) + fluct)
            y1 = max(0, int(obj["y"] - r * 1.5) + fluct)
            x2 = min(self.width, int(obj["x"] + r * 1.25) - fluct)
            y2 = min(self.height, int(obj["y"] + r * 1.3) - fluct)
            
            detections.append({
                "box": [x1, y1, x2, y2],
                "conf": min(1.0, max(0.5, obj["conf"] + 0.04 * np.sin(self.frame_count * 0.15))),
                "class_name": obj["label"],
                "class_id": 0 if obj["label"] == "person" else (16 if obj["label"] == "dog" else (67 if obj["label"] == "cell phone" else 41))
            })

        return True, frame, detections


def draw_sci_fi_box(img, box, label, conf, color):
    """
    Dibuja cajas delimitadoras con estilo futurista de retícula sci-fi
    (esquinas gruesas y líneas finas con etiqueta flotante).
    """
    x1, y1, x2, y2 = box
    
    # 1. Dibujar rectángulo exterior muy fino
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 1, lineType=cv2.LINE_AA)
    
    # 2. Dibujar esquinas gruesas (Brackets)
    corner_len = min(15, int((x2 - x1) * 0.2))
    thick = 3
    
    # Top-Left Corner
    cv2.line(img, (x1, y1), (x1 + corner_len, y1), color, thick, lineType=cv2.LINE_AA)
    cv2.line(img, (x1, y1), (x1, y1 + corner_len), color, thick, lineType=cv2.LINE_AA)
    
    # Top-Right Corner
    cv2.line(img, (x2, y1), (x2 - corner_len, y1), color, thick, lineType=cv2.LINE_AA)
    cv2.line(img, (x2, y1), (x2, y1 + corner_len), color, thick, lineType=cv2.LINE_AA)
    
    # Bottom-Left Corner
    cv2.line(img, (x1, y2), (x1 + corner_len, y2), color, thick, lineType=cv2.LINE_AA)
    cv2.line(img, (x1, y2), (x1, y2 - corner_len), color, thick, lineType=cv2.LINE_AA)
    
    # Bottom-Right Corner
    cv2.line(img, (x2, y2), (x2 - corner_len, y2), color, thick, lineType=cv2.LINE_AA)
    cv2.line(img, (x2, y2), (x2, y2 - corner_len), color, thick, lineType=cv2.LINE_AA)
    
    # 3. Dibujar etiqueta interactiva
    text = f"{label.upper()} {conf:.0%}"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.35
    thickness = 1
    
    # Obtener dimensiones del texto
    (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
    # Fondo de etiqueta flotante semitransparente sobre la caja
    tag_y1 = max(0, y1 - text_h - 10)
    tag_y2 = y1
    cv2.rectangle(img, (x1, tag_y1), (x1 + text_w + 10, tag_y2), color, -1)
    
    # Texto de la etiqueta (en negro o blanco para contraste)
    cv2.putText(img, text, (x1 + 5, y1 - 5), font, font_scale, (255, 255, 255) if color != (255, 255, 255) else (0, 0, 0), thickness, lineType=cv2.LINE_AA)
    
    # Cruz pequeña en el centro del objeto detectado para aumentar la estética de mira militar
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    cv2.line(img, (cx - 4, cy), (cx + 4, cy), color, 1)
    cv2.line(img, (cx, cy - 4), (cx, cy + 4), color, 1)


def main():
    print("="*60)
    print(" SISTEMA DE DETECCIÓN Y PROCESAMIENTO EN TIEMPO REAL")
    print("="*60)
    
    # Intentar inicializar la cámara web
    cap = None
    demo_mode = False
    
    print("[INFO] Intentando conectar con la Webcam (ID 0)...")
    # En Windows, cv2.CAP_DSHOW acelera la conexión y evita que se congele si no hay cámara web física
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print("[AVISO] No se pudo acceder a una cámara física.")
        print("[INFO] Activando el Generador de Video Sintético de Fallback...")
        demo_mode = True
        cap = SyntheticVideoSource(width=640, height=480)
    else:
        # Configurar cámara web real a 640x480 para mantener una inferencia rápida y alta tasa de FPS
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        print("[OK] Cámara web real conectada e inicializada a 640x480.")
        
    # Inicializar YOLOv8 si está disponible
    model = None
    if YOLO_AVAILABLE and not demo_mode:
        print("[INFO] Cargando modelo YOLOv8n (preentrenado)...")
        try:
            model = YOLO("yolov8n.pt")
            print("[OK] Modelo YOLOv8n cargado exitosamente.")
        except Exception as e:
            print(f"[ERROR] Error al cargar YOLOv8: {e}")
            print("[INFO] Activando Modo de simulación de detección.")
            if cap is not None and not isinstance(cap, SyntheticVideoSource):
                cap.release()
            demo_mode = True
            cap = SyntheticVideoSource(width=640, height=480)
    elif not YOLO_AVAILABLE and not demo_mode:
        print("[AVISO] Al no tener 'ultralytics' instalado, se usará el Modo Demo sintético.")
        if cap is not None and not isinstance(cap, SyntheticVideoSource):
            cap.release()
        demo_mode = True
        cap = SyntheticVideoSource(width=640, height=480)

    # Crear ventana única para la interfaz
    window_name = "Taller YOLO - Procesamiento en Vivo"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    
    # Crear trackbars interactivos (se inicializan siempre y se usan según el filtro activo)
    cv2.createTrackbar("Umbral Binar", window_name, 127, 255, lambda x: None)
    cv2.createTrackbar("Canny Min", window_name, 50, 255, lambda x: None)
    cv2.createTrackbar("Canny Max", window_name, 150, 255, lambda x: None)
    
    # Variables de control de la aplicación
    active_filter = 0  # 0: YOLO + Normal, 1: Grises, 2: Binarizar, 3: Bordes (Canny), 4: Cyberpunk Termal
    paused = False
    conditional_action = True  # Acción condicional por defecto activada (alarma si hay personas)
    
    # Variables de grabación
    is_recording = False
    video_writer = None
    recording_start_time = 0
    max_record_duration = 5.0 # segundos
    
    # Medición de FPS con promedio móvil de 30 muestras
    fps_history = []
    prev_time = time.time()
    
    # Estado para el efecto de parpadeo visual (alerta de intrusión)
    flash_state = False
    flash_timer = time.time()
    
    # Mensaje de retroalimentación temporal en el HUD
    hud_notification = "SISTEMA INICIALIZADO"
    hud_notification_time = time.time()
    
    print("\n[CONTROLES DISPONIBLES]:")
    print("  [1] - Filtro 0: Imagen Original + Detección YOLOv8")
    print("  [2] - Filtro 1: Escala de Grises")
    print("  [3] - Filtro 2: Binarización (Control por barra 'Umbral Binar')")
    print("  [4] - Filtro 3: Detección de Bordes Canny (Control por barras 'Canny Min/Max')")
    print("  [5] - Filtro 4: Filtro Cyberpunk Termal (Mapa de calor)")
    print("  [P o Espacio] - Pausar / Reanudar flujo de video")
    print("  [C] - Activar / Desactivar Acción Condicional (Reacción ante personas)")
    print("  [S] - Capturar Pantalla (Guardar instantánea en carpeta 'media')")
    print("  [V] - Iniciar / Detener Grabación de Video de 5 segundos")
    print("  [Q o ESC] - Salir de la aplicación")
    print("\nIniciando bucle de procesamiento interactivo...\n")
    
    while True:
        current_time = time.time()
        
        # Si está pausado, simplemente espera entrada de teclado para no sobrecargar el procesador
        if paused:
            key = cv2.waitKey(30) & 0xFF
            if key in [ord('q'), 27]: # ESC o q
                break
            elif key in [ord('p'), ord(' ')]: # Reanudar
                paused = False
                hud_notification = "SISTEMA REANUDADO"
                hud_notification_time = time.time()
            continue

        # 1. Leer fotograma
        detections = []
        if demo_mode:
            ret, raw_frame, detections = cap.read()
        else:
            ret, raw_frame = cap.read()
            if ret and model is not None:
                # Correr inferencia real de YOLOv8
                detections = []
                # Inferencia con confianza mínima del 50%
                results = model.predict(raw_frame, conf=0.50, verbose=False)
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
                        
        if not ret:
            print("[ERROR] Error al leer el fotograma del dispositivo.")
            break
            
        height, width = raw_frame.shape[:2]
        
        # 2. Calcular FPS mediante promedio móvil
        delta = current_time - prev_time
        prev_time = current_time
        if delta > 0:
            fps_history.append(1.0 / delta)
            if len(fps_history) > 30:
                fps_history.pop(0)
        fps = sum(fps_history) / len(fps_history) if fps_history else 30.0
        
        # 3. Evaluar Acción Condicional (Si detecta una persona)
        person_detected = any(d["class_name"] == "person" for d in detections)
        active_filter_run = active_filter
        
        # Si está activada la acción condicional y se detecta una persona:
        # - Cambiamos automáticamente al Filtro 4 (Cyberpunk Termal) si el usuario está en el modo por defecto (0)
        # - Se generará una alerta de pantalla parpadeante roja.
        if conditional_action and person_detected:
            if active_filter == 0:
                active_filter_run = 4
            # Alternar el estado de flash cada 0.25 segundos para crear un efecto de alarma intermitente
            if current_time - flash_timer > 0.25:
                flash_state = not flash_state
                flash_timer = current_time
        else:
            flash_state = False

        # 4. Aplicar Filtro de Procesamiento de Imagen
        processed_frame = raw_frame.copy()
        
        if active_filter_run == 0:
            # Filtro 0: Imagen original con cajas de YOLO
            pass
        elif active_filter_run == 1:
            # Filtro 1: Escala de grises
            gray = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2GRAY)
            processed_frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        elif active_filter_run == 2:
            # Filtro 2: Binarización con umbral ajustable por trackbar
            threshold_val = cv2.getTrackbarPos("Umbral Binar", window_name)
            gray = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, threshold_val, 255, cv2.THRESH_BINARY)
            processed_frame = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        elif active_filter_run == 3:
            # Filtro 3: Canny con umbrales ajustables por trackbar
            canny_min = cv2.getTrackbarPos("Canny Min", window_name)
            canny_max = cv2.getTrackbarPos("Canny Max", window_name)
            gray = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, canny_min, canny_max)
            processed_frame = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        elif active_filter_run == 4:
            # Filtro 4: Mapa térmico Cyberpunk
            gray = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2GRAY)
            # Aplicar color map térmico
            thermal = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
            processed_frame = thermal

        # 5. Dibujar detecciones YOLO sobre el frame procesado (Solo si el filtro es normal, termal o grises para mantener coherencia visual)
        # En binarización o bordes puros a veces se prefiere no dibujar o usar colores planos. Lo dibujaremos en todos los filtros excepto binarización para no tapar, o en todos con colores de alto contraste.
        for det in detections:
            box = det["box"]
            cls_name = det["class_name"]
            conf = det["conf"]
            
            # Definir color de caja según la clase
            if cls_name == "person":
                color = (0, 0, 255) if flash_state else (0, 140, 255) # Parpadea rojo o naranja neon
            elif cls_name == "dog":
                color = (255, 100, 100) # Azul neon
            elif cls_name in ["cell phone", "laptop"]:
                color = (255, 240, 0) # Amarillo/Cyan
            else:
                color = (0, 255, 100) # Verde neon
                
            draw_sci_fi_box(processed_frame, box, cls_name, conf, color)

        # 6. Construir e Inyectar la interfaz de usuario HUD (Heads-Up Display)
        
        # A. Banner Superior de Estado (Semitransparente)
        overlay = processed_frame.copy()
        cv2.rectangle(overlay, (0, 0), (width, 38), (12, 12, 12), -1)
        cv2.addWeighted(overlay, 0.65, processed_frame, 0.35, 0, processed_frame)
        
        # B. Título de la Aplicación
        cv2.putText(processed_frame, "ANTIGRAVITY TACTICAL HUD // YOLOv8", (12, 23), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 240), 1, cv2.LINE_AA)
        
        # C. Indicadores de Estado en Banner Superior
        # Indicador de Modo
        mode_str = "DEMO FEED" if demo_mode else "WEBCAM LIVE"
        mode_color = (0, 200, 255) if demo_mode else (0, 255, 100)
        cv2.rectangle(processed_frame, (320, 10), (410, 28), (40, 40, 40), -1)
        cv2.rectangle(processed_frame, (320, 10), (410, 28), mode_color, 1)
        cv2.putText(processed_frame, mode_str, (328, 22), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, mode_color, 1, cv2.LINE_AA)
        
        # Indicador de FPS
        fps_color = (0, 255, 100) if fps >= 25 else ((0, 255, 255) if fps >= 15 else (0, 0, 255))
        cv2.putText(processed_frame, f"FPS: {fps:.1f}", (430, 23), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, fps_color, 1, cv2.LINE_AA)
        
        # Indicador de Filtro Activo
        filter_names = ["NORMAL+YOLO", "GRISES", "BINARIZACION", "CANNY EDGES", "CYBER_TERMAL"]
        cv2.putText(processed_frame, f"FILTRO: {filter_names[active_filter_run]}", (510, 23), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1, cv2.LINE_AA)

        # D. Banner Inferior de Controles (Sugerencias de Teclado)
        overlay_bottom = processed_frame.copy()
        cv2.rectangle(overlay_bottom, (0, height - 30), (width, height), (15, 15, 15), -1)
        cv2.addWeighted(overlay_bottom, 0.75, processed_frame, 0.25, 0, processed_frame)
        
        controls_text = "[1-5] Filtros | [Space] Pausa | [S] Captura | [V] Video | [C] Condicional | [Q] Salir"
        cv2.putText(processed_frame, controls_text, (12, height - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (190, 190, 190), 1, cv2.LINE_AA)
        
        # E. Panel Izquierdo / Panel de Datos Tácticos
        # Contadores de detección en tiempo real
        person_count = sum(1 for d in detections if d["class_name"] == "person")
        total_objects = len(detections)
        
        tactical_overlay = processed_frame.copy()
        cv2.rectangle(tactical_overlay, (10, 48), (200, 150), (10, 10, 10), -1)
        cv2.addWeighted(tactical_overlay, 0.5, processed_frame, 0.5, 0, processed_frame)
        cv2.rectangle(processed_frame, (10, 48), (200, 150), (60, 60, 60), 1)
        
        cv2.putText(processed_frame, "METADATOS DE DETECCION", (18, 64), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.33, (0, 255, 240), 1, cv2.LINE_AA)
        cv2.line(processed_frame, (15, 70), (195, 70), (40, 40, 40), 1)
        
        cv2.putText(processed_frame, f"Objetos Totales: {total_objects}", (18, 88), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(processed_frame, f"Personas: {person_count}", (18, 106), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 140, 255) if person_count > 0 else (180, 180, 180), 1, cv2.LINE_AA)
        
        # Mostrar desglose rápido de otros objetos
        other_objects = [d["class_name"] for d in detections if d["class_name"] != "person"]
        other_counts = {x: other_objects.count(x) for x in set(other_objects)}
        other_str = ", ".join([f"{k}:{v}" for k, v in other_counts.items()])
        if len(other_str) > 22:
            other_str = other_str[:20] + "..."
        cv2.putText(processed_frame, f"Otros: {other_str if other_str else 'Ninguno'}", (18, 124), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.33, (150, 150, 150), 1, cv2.LINE_AA)
        
        # Estado de la Acción Condicional
        cond_status = "COND_ACTION: ON" if conditional_action else "COND_ACTION: OFF"
        cond_color = (0, 255, 0) if conditional_action else (150, 150, 150)
        cv2.putText(processed_frame, cond_status, (18, 142), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.33, cond_color, 1, cv2.LINE_AA)

        # F. Notificaciones del Sistema Temporal (HUD Toast)
        if current_time - hud_notification_time < 2.0:
            # Panel de notificación
            notif_w = 260
            cv2.rectangle(processed_frame, (width - notif_w - 10, height - 70), (width - 10, height - 42), (20, 20, 20), -1)
            cv2.rectangle(processed_frame, (width - notif_w - 10, height - 70), (width - 10, height - 42), (0, 255, 240), 1)
            cv2.putText(processed_frame, f">> {hud_notification}", (width - notif_w, height - 52), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 240), 1, cv2.LINE_AA)

        # G. Alerta Visual de Intrusión (Si Acción Condicional está activa y se detecta persona)
        if conditional_action and person_detected:
            # Dibujar un marco exterior parpadeante de color rojo
            if flash_state:
                cv2.rectangle(processed_frame, (0, 0), (width, height), (0, 0, 255), 4)
                # Letrero de Advertencia
                cv2.rectangle(processed_frame, (width // 2 - 130, 48), (width // 2 + 130, 80), (0, 0, 255), -1)
                cv2.putText(processed_frame, "ALERTA: INTRUSO DETECTADO", (width // 2 - 110, 68), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 2, cv2.LINE_AA)

        # H. Lógica y Visualización de Grabación de Video
        if is_recording:
            # Dibujar círculo de grabación parpadeante
            recorded_duration = current_time - recording_start_time
            rec_flash = int(current_time * 4) % 2
            
            rec_color = (0, 0, 255) if rec_flash else (0, 0, 100)
            cv2.circle(processed_frame, (width - 110, height - 15), 5, rec_color, -1)
            cv2.putText(processed_frame, f"REC {recorded_duration:.1f}s / {max_record_duration:.0f}s", (width - 98, height - 11), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1, cv2.LINE_AA)
            
            # Escribir frame en el archivo de video (guardamos lo que ve el usuario, HUD incluido)
            if video_writer is not None:
                video_writer.write(processed_frame)
                
            # Parada automática si se supera el tiempo límite
            if recorded_duration >= max_record_duration:
                is_recording = False
                if video_writer is not None:
                    video_writer.release()
                    video_writer = None
                hud_notification = "GRABACION FINALIZADA (AUTO)"
                hud_notification_time = time.time()
                print(f"[OK] Grabación automática finalizada y guardada en {MEDIA_DIR}")

        # 7. Renderizar la Imagen Final en la Ventana Interactiva
        cv2.imshow(window_name, processed_frame)

        # 8. Lectura de Eventos de Teclado
        key = cv2.waitKey(1) & 0xFF
        
        if key in [ord('q'), 27]: # Tecla 'q' o ESC para salir
            break
        elif key == ord('p') or key == 32: # Tecla 'p' o barra espaciadora para pausar
            paused = True
            hud_notification = "SISTEMA PAUSADO"
            hud_notification_time = time.time()
            print("[INFO] Flujo de video pausado. Presione Espacio o 'p' para reanudar.")
        elif key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5')]:
            # Cambiar filtro activo
            active_filter = int(chr(key)) - 1
            hud_notification = f"FILTRO CAMBIADO A {filter_names[active_filter]}"
            hud_notification_time = time.time()
            print(f"[INFO] Filtro cambiado a: {filter_names[active_filter]}")
        elif key == ord('c'):
            # Conmutar acción condicional
            conditional_action = not conditional_action
            hud_notification = f"ACCION CONDICIONAL: {'ON' if conditional_action else 'OFF'}"
            hud_notification_time = time.time()
            print(f"[INFO] Reacción condicional ante personas: {'ACTIVADA' if conditional_action else 'DESACTIVADA'}")
        elif key == ord('s'):
            # Guardar captura de pantalla
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(MEDIA_DIR, filename)
            
            # Guardar tanto el fotograma procesado como el original para comparar si el usuario lo requiere
            cv2.imwrite(filepath, processed_frame)
            
            hud_notification = f"CAPTURA GUARDADA: {filename}"
            hud_notification_time = time.time()
            print(f"[OK] Captura de pantalla guardada: {filepath}")
        elif key == ord('v'):
            # Iniciar/Detener grabación de video manualmente
            if not is_recording:
                # Iniciar grabación
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"video_{timestamp}.avi"
                filepath = os.path.join(MEDIA_DIR, filename)
                
                # Codec MJPG (muy compatible y estándar en Windows sin software adicional)
                fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                video_writer = cv2.VideoWriter(filepath, fourcc, 20.0, (width, height))
                
                if video_writer.isOpened():
                    is_recording = True
                    recording_start_time = time.time()
                    hud_notification = "GRABACION INICIADA"
                    hud_notification_time = time.time()
                    print(f"[INFO] Iniciando grabación de video: {filepath}")
                else:
                    video_writer = None
                    hud_notification = "ERROR: NO SE PUDO GRABAR"
                    hud_notification_time = time.time()
                    print("[ERROR] No se pudo abrir el VideoWriter de OpenCV.")
            else:
                # Detener grabación manualmente
                is_recording = False
                if video_writer is not None:
                    video_writer.release()
                    video_writer = None
                hud_notification = "GRABACION DETENIDA Y GUARDADA"
                hud_notification_time = time.time()
                print(f"[OK] Grabación detenida manualmente y guardada en {MEDIA_DIR}")

    # 9. Liberar recursos y cerrar
    print("\nCerrando aplicación y liberando hardware...")
    if not demo_mode and cap is not None:
        cap.release()
    if video_writer is not None:
        video_writer.release()
    cv2.destroyAllWindows()
    print("[OK] Recursos liberados con éxito. ¡Gracias por usar la aplicación!")


if __name__ == "__main__":
    main()
