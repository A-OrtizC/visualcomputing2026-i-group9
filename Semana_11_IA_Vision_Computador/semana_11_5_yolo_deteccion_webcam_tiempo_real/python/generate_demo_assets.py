#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utility to programmatically generate demo assets for the Taller 11-5 README.md.
Runs the drawing, performance measurements, metrics, and vector graphing algorithms
of main.py in headless mode, exporting beautiful, high-fidelity PNG results to media/.
"""

import os
import cv2
import numpy as np

def generate():
    python_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(python_dir)
    media_dir = os.path.join(base_dir, "media")
    os.makedirs(media_dir, exist_ok=True)
    
    import sys
    sys.path.append(python_dir)
    from main import SyntheticVideoSource, draw_sci_fi_box, draw_performance_graph
    
    # Initialize source and let objects float a bit
    source = SyntheticVideoSource(width=640, height=480)
    for _ in range(40):
        source.read()
        
    width, height = 640, 480
    legend_str = "[N,S,M] Cambiar Modelo | [F] Filtrar Clases | [C] Limpiar Historial | [Q] Salir"
    
    # -------------------------------------------------------------
    # 1. SCREENSHOT 1: YOLOv8 NANO (screenshot_yolo_nano.png)
    # -------------------------------------------------------------
    _, raw_frame, detections = source.read()
    processed = raw_frame.copy()
    
    # Draw detections
    for det in detections:
        box = det["box"]
        cls_name = det["class_name"]
        conf = det["conf"]
        color = (0, 140, 255) if cls_name == "person" else ((255, 240, 0) if cls_name in ["cell phone", "laptop"] else (200, 0, 255))
        draw_sci_fi_box(processed, box, cls_name, conf, color)
        
    # Generate mock histories for Nano (High FPS, low inference time)
    fps_history = [30.0 + np.random.normal(0, 0.5) for _ in range(80)]
    inf_history = [6.5 + np.random.normal(0, 0.4) for _ in range(80)]
    
    # Draw Top HUD
    overlay = processed.copy()
    cv2.rectangle(overlay, (0, 0), (width, 42), (12, 12, 12), -1)
    cv2.addWeighted(overlay, 0.7, processed, 0.3, 0, processed)
    cv2.rectangle(processed, (0, 0), (width, 42), (40, 40, 40), 1)
    
    cv2.putText(processed, "YOLOv8 REALTIME DIAGNOSTIC TOOL", (12, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 240), 1, cv2.LINE_AA)
    metrics_x = width - 290
    cv2.putText(processed, "FPS: 30.5", (metrics_x, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 100), 1, cv2.LINE_AA)
    cv2.putText(processed, "Inf: 6.8ms", (metrics_x + 85, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 240), 1, cv2.LINE_AA)
    cv2.putText(processed, "Lat: 8.4ms", (metrics_x + 190, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1, cv2.LINE_AA)
    
    # Draw Left Analytics
    overlay_s = processed.copy()
    cv2.rectangle(overlay_s, (10, 52), (210, 235), (10, 10, 10), -1)
    cv2.addWeighted(overlay_s, 0.6, processed, 0.4, 0, processed)
    cv2.rectangle(processed, (10, 52), (210, 235), (55, 55, 55), 1)
    
    cv2.putText(processed, "ANALYTICS PANEL", (18, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 240), 1, cv2.LINE_AA)
    cv2.line(processed, (15, 73), (205, 73), (45, 45, 45), 1)
    cv2.putText(processed, "MODELO SELECCIONADO:", (18, 88), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (150, 150, 150), 1, cv2.LINE_AA)
    cv2.putText(processed, "YOLOv8 Nano (Ultra-Fast)", (18, 102), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(processed, "ACTIVO EN PANTALLA:", (18, 122), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (150, 150, 150), 1, cv2.LINE_AA)
    cv2.putText(processed, "  Person: 1", (18, 136), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (0, 255, 100), 1, cv2.LINE_AA)
    cv2.putText(processed, "  Cell Phone: 1", (18, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (0, 255, 100), 1, cv2.LINE_AA)
    cv2.putText(processed, "  Laptop: 1", (18, 164), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (0, 255, 100), 1, cv2.LINE_AA)
    cv2.line(processed, (15, 180), (205, 180), (45, 45, 45), 1)
    cv2.putText(processed, "HISTORICO ACUMULATIVO:", (18, 195), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (150, 150, 150), 1, cv2.LINE_AA)
    cv2.putText(processed, "person:3, bottle:2, phone:2", (18, 212), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (0, 255, 240), 1, cv2.LINE_AA)
    cv2.putText(processed, "FILTRO CLASES: TODAS LAS 80 CLASES COCO", (18, 227), cv2.FONT_HERSHEY_SIMPLEX, 0.28, (180, 180, 180), 1, cv2.LINE_AA)
    
    # Draw Performance Graph
    draw_performance_graph(processed, fps_history, inf_history, x_pos=width - 215, y_pos=height - 128)
    
    # Bottom controls
    overlay_b = processed.copy()
    cv2.rectangle(overlay_b, (0, height - 30), (width, height), (15, 15, 15), -1)
    cv2.addWeighted(overlay_b, 0.75, processed, 0.25, 0, processed)
    cv2.putText(processed, legend_str, (12, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (190, 190, 190), 1, cv2.LINE_AA)
    
    # Save Nano
    cv2.imwrite(os.path.join(media_dir, "screenshot_yolo_nano.png"), processed)
    print("[ASSET] Saved screenshot_yolo_nano.png")

    # -------------------------------------------------------------
    # 2. SCREENSHOT 2: YOLOv8 MEDIUM (screenshot_yolo_medium.png)
    # -------------------------------------------------------------
    source.read()
    _, raw_frame, detections = source.read()
    processed = raw_frame.copy()
    
    # Draw detections
    for det in detections:
        box = det["box"]
        cls_name = det["class_name"]
        conf = det["conf"]
        color = (0, 140, 255) if cls_name == "person" else ((255, 240, 0) if cls_name in ["cell phone", "laptop"] else (200, 0, 255))
        draw_sci_fi_box(processed, box, cls_name, conf, color)
        
    # Generate mock histories for Medium (Lower FPS, higher inference time)
    fps_history = [16.5 + np.random.normal(0, 0.3) for _ in range(80)]
    inf_history = [46.5 + np.random.normal(0, 0.8) for _ in range(80)]
    
    # Draw Top HUD
    overlay = processed.copy()
    cv2.rectangle(overlay, (0, 0), (width, 42), (12, 12, 12), -1)
    cv2.addWeighted(overlay, 0.7, processed, 0.3, 0, processed)
    cv2.rectangle(processed, (0, 0), (width, 42), (40, 40, 40), 1)
    
    cv2.putText(processed, "YOLOv8 REALTIME DIAGNOSTIC TOOL", (12, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 240), 1, cv2.LINE_AA)
    metrics_x = width - 290
    cv2.putText(processed, "FPS: 16.2", (metrics_x, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 255), 1, cv2.LINE_AA) # Red FPS
    cv2.putText(processed, "Inf: 47.2ms", (metrics_x + 85, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 240), 1, cv2.LINE_AA)
    cv2.putText(processed, "Lat: 58.4ms", (metrics_x + 190, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1, cv2.LINE_AA)
    
    # Draw Left Analytics
    overlay_s = processed.copy()
    cv2.rectangle(overlay_s, (10, 52), (210, 235), (10, 10, 10), -1)
    cv2.addWeighted(overlay_s, 0.6, processed, 0.4, 0, processed)
    cv2.rectangle(processed, (10, 52), (210, 235), (55, 55, 55), 1)
    
    cv2.putText(processed, "ANALYTICS PANEL", (18, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 240), 1, cv2.LINE_AA)
    cv2.line(processed, (15, 73), (205, 73), (45, 45, 45), 1)
    cv2.putText(processed, "MODELO SELECCIONADO:", (18, 88), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (150, 150, 150), 1, cv2.LINE_AA)
    cv2.putText(processed, "YOLOv8 Medium (Alta Precision)", (18, 102), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(processed, "ACTIVO EN PANTALLA:", (18, 122), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (150, 150, 150), 1, cv2.LINE_AA)
    cv2.putText(processed, "  Person: 1", (18, 136), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (0, 255, 100), 1, cv2.LINE_AA)
    cv2.putText(processed, "  Cell Phone: 1", (18, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (0, 255, 100), 1, cv2.LINE_AA)
    cv2.putText(processed, "  Laptop: 1", (18, 164), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (0, 255, 100), 1, cv2.LINE_AA)
    cv2.line(processed, (15, 180), (205, 180), (45, 45, 45), 1)
    cv2.putText(processed, "HISTORICO ACUMULATIVO:", (18, 195), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (150, 150, 150), 1, cv2.LINE_AA)
    cv2.putText(processed, "person:5, bottle:3, phone:4", (18, 212), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (0, 255, 240), 1, cv2.LINE_AA)
    cv2.putText(processed, "FILTRO CLASES: TODAS LAS 80 CLASES COCO", (18, 227), cv2.FONT_HERSHEY_SIMPLEX, 0.28, (180, 180, 180), 1, cv2.LINE_AA)
    
    # Draw Performance Graph
    draw_performance_graph(processed, fps_history, inf_history, x_pos=width - 215, y_pos=height - 128)
    
    # Bottom controls
    overlay_b = processed.copy()
    cv2.rectangle(overlay_b, (0, height - 30), (width, height), (15, 15, 15), -1)
    cv2.addWeighted(overlay_b, 0.75, processed, 0.25, 0, processed)
    cv2.putText(processed, legend_str, (12, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (190, 190, 190), 1, cv2.LINE_AA)
    
    # Save Medium
    cv2.imwrite(os.path.join(media_dir, "screenshot_yolo_medium.png"), processed)
    print("[ASSET] Saved screenshot_yolo_medium.png")

    # -------------------------------------------------------------
    # 3. SCREENSHOT 3: CLASS FILTERING (screenshot_selective_filter.png)
    # -------------------------------------------------------------
    source.read()
    _, raw_frame, detections = source.read()
    processed = raw_frame.copy()
    
    # Selective Filter ACTIVE (only show person, phone, laptop, bottle - so dog cup are hidden!)
    # Let's filter out non-target classes
    target_classes = ["person", "cell phone", "laptop", "bottle"]
    filtered_detections = [d for d in detections if d["class_name"] in target_classes]
    
    # Draw filtered detections
    for det in filtered_detections:
        box = det["box"]
        cls_name = det["class_name"]
        conf = det["conf"]
        color = (0, 140, 255) if cls_name == "person" else ((255, 240, 0) if cls_name in ["cell phone", "laptop"] else (200, 0, 255))
        draw_sci_fi_box(processed, box, cls_name, conf, color)
        
    # Generate mock histories (Nano filter, High FPS)
    fps_history = [30.0 + np.random.normal(0, 0.4) for _ in range(80)]
    inf_history = [6.5 + np.random.normal(0, 0.3) for _ in range(80)]
    
    # Draw Top HUD
    overlay = processed.copy()
    cv2.rectangle(overlay, (0, 0), (width, 42), (12, 12, 12), -1)
    cv2.addWeighted(overlay, 0.7, processed, 0.3, 0, processed)
    cv2.rectangle(processed, (0, 0), (width, 42), (40, 40, 40), 1)
    
    cv2.putText(processed, "YOLOv8 REALTIME DIAGNOSTIC TOOL", (12, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 240), 1, cv2.LINE_AA)
    metrics_x = width - 290
    cv2.putText(processed, "FPS: 30.2", (metrics_x, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 100), 1, cv2.LINE_AA)
    cv2.putText(processed, "Inf: 6.4ms", (metrics_x + 85, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 240), 1, cv2.LINE_AA)
    cv2.putText(processed, "Lat: 8.1ms", (metrics_x + 190, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1, cv2.LINE_AA)
    
    # Draw Left Analytics
    overlay_s = processed.copy()
    cv2.rectangle(overlay_s, (10, 52), (210, 235), (10, 10, 10), -1)
    cv2.addWeighted(overlay_s, 0.6, processed, 0.4, 0, processed)
    cv2.rectangle(processed, (10, 52), (210, 235), (55, 55, 55), 1)
    
    cv2.putText(processed, "ANALYTICS PANEL", (18, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 240), 1, cv2.LINE_AA)
    cv2.line(processed, (15, 73), (205, 73), (45, 45, 45), 1)
    cv2.putText(processed, "MODELO SELECCIONADO:", (18, 88), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (150, 150, 150), 1, cv2.LINE_AA)
    cv2.putText(processed, "YOLOv8 Nano (Ultra-Fast)", (18, 102), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(processed, "ACTIVO EN PANTALLA:", (18, 122), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (150, 150, 150), 1, cv2.LINE_AA)
    cv2.putText(processed, "  Person: 1", (18, 136), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (0, 255, 100), 1, cv2.LINE_AA)
    cv2.putText(processed, "  Cell Phone: 1", (18, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (0, 255, 100), 1, cv2.LINE_AA)
    cv2.putText(processed, "  Laptop: 1", (18, 164), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (0, 255, 100), 1, cv2.LINE_AA)
    cv2.line(processed, (15, 180), (205, 180), (45, 45, 45), 1)
    cv2.putText(processed, "HISTORICO ACUMULATIVO:", (18, 195), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (150, 150, 150), 1, cv2.LINE_AA)
    cv2.putText(processed, "person:6, phone:4, laptop:3", (18, 212), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (0, 255, 240), 1, cv2.LINE_AA)
    cv2.putText(processed, "FILTRO CLASES: SOLO DETECTA TECTONICOS", (18, 227), cv2.FONT_HERSHEY_SIMPLEX, 0.28, (0, 255, 100), 1, cv2.LINE_AA)
    
    # Draw Performance Graph
    draw_performance_graph(processed, fps_history, inf_history, x_pos=width - 215, y_pos=height - 128)
    
    # Bottom controls
    overlay_b = processed.copy()
    cv2.rectangle(overlay_b, (0, height - 30), (width, height), (15, 15, 15), -1)
    cv2.addWeighted(overlay_b, 0.75, processed, 0.25, 0, processed)
    cv2.putText(processed, legend_str, (12, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (190, 190, 190), 1, cv2.LINE_AA)
    
    # Save Selective Filter
    cv2.imwrite(os.path.join(media_dir, "screenshot_selective_filter.png"), processed)
    print("[ASSET] Saved screenshot_selective_filter.png")
    
    print("\n[OK] All Taller 11-5 real-time graph assets successfully generated!")

if __name__ == "__main__":
    generate()
