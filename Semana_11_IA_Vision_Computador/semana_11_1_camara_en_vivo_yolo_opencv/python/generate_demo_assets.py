#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utility to programmatically generate demo assets for the README.md documentation.
Runs the exact drawing, filtering, and HUD code from main.py on the synthetic generator
and saves the frames as high-fidelity PNG files in the media/ directory.
"""

import os
import cv2
import numpy as np

def generate():
    # Setup directories
    python_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(python_dir)
    media_dir = os.path.join(base_dir, "media")
    os.makedirs(media_dir, exist_ok=True)
    
    # Import components from main.py
    import sys
    sys.path.append(python_dir)
    from main import SyntheticVideoSource, draw_sci_fi_box
    
    # Initialize synthetic source
    # We tick it a few times to get objects in beautiful floating positions
    source = SyntheticVideoSource(width=640, height=480)
    for _ in range(35):
        source.read()
        
    width, height = 640, 480
    
    # -------------------------------------------------------------
    # 1. SCREENSHOT 1: YOLO HUD (Normal + YOLO boxes)
    # -------------------------------------------------------------
    _, raw_frame, detections = source.read()
    processed = raw_frame.copy()
    
    # Draw detections
    for det in detections:
        box = det["box"]
        cls_name = det["class_name"]
        conf = det["conf"]
        
        # Color coding
        if cls_name == "person":
            color = (0, 140, 255) # Orange
        elif cls_name == "dog":
            color = (255, 100, 100) # Blue
        elif cls_name in ["cell phone", "laptop"]:
            color = (255, 240, 0) # Cyan
        else:
            color = (0, 255, 100) # Green
            
        draw_sci_fi_box(processed, box, cls_name, conf, color)
        
    # Draw Top HUD Banner
    overlay = processed.copy()
    cv2.rectangle(overlay, (0, 0), (width, 38), (12, 12, 12), -1)
    cv2.addWeighted(overlay, 0.65, processed, 0.35, 0, processed)
    cv2.putText(processed, "ANTIGRAVITY TACTICAL HUD // YOLOv8", (12, 23), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 240), 1, cv2.LINE_AA)
    
    # Mode indicator
    cv2.rectangle(processed, (320, 10), (410, 28), (40, 40, 40), -1)
    cv2.rectangle(processed, (320, 10), (410, 28), (0, 255, 100), 1)
    cv2.putText(processed, "DEMO FEED", (328, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 100), 1, cv2.LINE_AA)
    
    # FPS and Filter indicators
    cv2.putText(processed, "FPS: 31.2", (430, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 100), 1, cv2.LINE_AA)
    cv2.putText(processed, "FILTRO: NORMAL+YOLO", (510, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1, cv2.LINE_AA)
    
    # Bottom Controls banner
    overlay_b = processed.copy()
    cv2.rectangle(overlay_b, (0, height - 30), (width, height), (15, 15, 15), -1)
    cv2.addWeighted(overlay_b, 0.75, processed, 0.25, 0, processed)
    controls_text = "[1-5] Filtros | [Space] Pausa | [S] Captura | [V] Video | [C] Condicional | [Q] Salir"
    cv2.putText(processed, controls_text, (12, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (190, 190, 190), 1, cv2.LINE_AA)
    
    # Left Tactical metadata
    tact_overlay = processed.copy()
    cv2.rectangle(tact_overlay, (10, 48), (200, 150), (10, 10, 10), -1)
    cv2.addWeighted(tact_overlay, 0.5, processed, 0.5, 0, processed)
    cv2.rectangle(processed, (10, 48), (200, 150), (60, 60, 60), 1)
    
    cv2.putText(processed, "METADATOS DE DETECCION", (18, 64), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (0, 255, 240), 1, cv2.LINE_AA)
    cv2.line(processed, (15, 70), (195, 70), (40, 40, 40), 1)
    cv2.putText(processed, f"Objetos Totales: {len(detections)}", (18, 88), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1, cv2.LINE_AA)
    person_cnt = sum(1 for d in detections if d["class_name"] == "person")
    cv2.putText(processed, f"Personas: {person_cnt}", (18, 106), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 140, 255) if person_cnt > 0 else (180, 180, 180), 1, cv2.LINE_AA)
    cv2.putText(processed, "Otros: dog:1, cup:1, phone:1", (18, 124), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (150, 150, 150), 1, cv2.LINE_AA)
    cv2.putText(processed, "COND_ACTION: ON", (18, 142), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (0, 255, 0), 1, cv2.LINE_AA)
    
    # Save YOLO HUD image
    cv2.imwrite(os.path.join(media_dir, "screenshot_yolo_hud.png"), processed)
    print("[ASSET] Saved screenshot_yolo_hud.png")

    # -------------------------------------------------------------
    # 2. SCREENSHOT 2: BINARIZATION (Thresholding at 127)
    # -------------------------------------------------------------
    # Tick source to change positions
    source.read()
    _, raw_frame, detections = source.read()
    
    # Process Binarization
    gray = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    processed = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    
    # Draw detections
    for det in detections:
        draw_sci_fi_box(processed, det["box"], det["class_name"], det["conf"], (200, 200, 200))
        
    # Overlays
    overlay = processed.copy()
    cv2.rectangle(overlay, (0, 0), (width, 38), (12, 12, 12), -1)
    cv2.addWeighted(overlay, 0.65, processed, 0.35, 0, processed)
    cv2.putText(processed, "ANTIGRAVITY TACTICAL HUD // YOLOv8", (12, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 240), 1, cv2.LINE_AA)
    
    cv2.rectangle(processed, (320, 10), (410, 28), (40, 40, 40), -1)
    cv2.rectangle(processed, (320, 10), (410, 28), (0, 255, 100), 1)
    cv2.putText(processed, "DEMO FEED", (328, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 100), 1, cv2.LINE_AA)
    cv2.putText(processed, "FPS: 29.8", (430, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 100), 1, cv2.LINE_AA)
    cv2.putText(processed, "FILTRO: BINARIZACION", (510, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1, cv2.LINE_AA)
    
    overlay_b = processed.copy()
    cv2.rectangle(overlay_b, (0, height - 30), (width, height), (15, 15, 15), -1)
    cv2.addWeighted(overlay_b, 0.75, processed, 0.25, 0, processed)
    cv2.putText(processed, controls_text, (12, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (190, 190, 190), 1, cv2.LINE_AA)
    
    # Save binarization image
    cv2.imwrite(os.path.join(media_dir, "screenshot_binarization.png"), processed)
    print("[ASSET] Saved screenshot_binarization.png")

    # -------------------------------------------------------------
    # 3. SCREENSHOT 3: CANNY (Edges min=50, max=150)
    # -------------------------------------------------------------
    # Tick source
    source.read()
    _, raw_frame, detections = source.read()
    
    # Process Canny Edges
    gray = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    processed = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    # Draw detections with highly visible lines
    for det in detections:
        draw_sci_fi_box(processed, det["box"], det["class_name"], det["conf"], (0, 255, 0))
        
    # Overlays
    overlay = processed.copy()
    cv2.rectangle(overlay, (0, 0), (width, 38), (12, 12, 12), -1)
    cv2.addWeighted(overlay, 0.65, processed, 0.35, 0, processed)
    cv2.putText(processed, "ANTIGRAVITY TACTICAL HUD // YOLOv8", (12, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 240), 1, cv2.LINE_AA)
    
    cv2.rectangle(processed, (320, 10), (410, 28), (40, 40, 40), -1)
    cv2.rectangle(processed, (320, 10), (410, 28), (0, 255, 100), 1)
    cv2.putText(processed, "DEMO FEED", (328, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 100), 1, cv2.LINE_AA)
    cv2.putText(processed, "FPS: 28.5", (430, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 100), 1, cv2.LINE_AA)
    cv2.putText(processed, "FILTRO: CANNY EDGES", (510, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1, cv2.LINE_AA)
    
    overlay_b = processed.copy()
    cv2.rectangle(overlay_b, (0, height - 30), (width, height), (15, 15, 15), -1)
    cv2.addWeighted(overlay_b, 0.75, processed, 0.25, 0, processed)
    cv2.putText(processed, controls_text, (12, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (190, 190, 190), 1, cv2.LINE_AA)
    
    # Save Canny Edges image
    cv2.imwrite(os.path.join(media_dir, "screenshot_canny.png"), processed)
    print("[ASSET] Saved screenshot_canny.png")

    # -------------------------------------------------------------
    # 4. SCREENSHOT 4: INTRUSION ALARM (Thermal filter + warning text + red borders)
    # -------------------------------------------------------------
    # Tick source
    source.read()
    _, raw_frame, detections = source.read()
    
    # Process Thermal Jet
    gray = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2GRAY)
    thermal = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
    processed = thermal.copy()
    
    # Draw detections
    for det in detections:
        box = det["box"]
        cls_name = det["class_name"]
        conf = det["conf"]
        # Flash alarm person is red, others are typical sci-fi
        color = (0, 0, 255) if cls_name == "person" else (255, 255, 255)
        draw_sci_fi_box(processed, box, cls_name, conf, color)
        
    # Draw Top HUD
    overlay = processed.copy()
    cv2.rectangle(overlay, (0, 0), (width, 38), (12, 12, 12), -1)
    cv2.addWeighted(overlay, 0.65, processed, 0.35, 0, processed)
    cv2.putText(processed, "ANTIGRAVITY TACTICAL HUD // YOLOv8", (12, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 240), 1, cv2.LINE_AA)
    
    cv2.rectangle(processed, (320, 10), (410, 28), (40, 40, 40), -1)
    cv2.rectangle(processed, (320, 10), (410, 28), (0, 255, 100), 1)
    cv2.putText(processed, "DEMO FEED", (328, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 100), 1, cv2.LINE_AA)
    cv2.putText(processed, "FPS: 30.5", (430, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1, cv2.LINE_AA) # Red FPS
    cv2.putText(processed, "FILTRO: CYBER_TERMAL", (510, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1, cv2.LINE_AA)
    
    # Flashing Alarm Border (Red border around frame)
    cv2.rectangle(processed, (0, 0), (width, height), (0, 0, 255), 4)
    # Warning box
    cv2.rectangle(processed, (width // 2 - 130, 48), (width // 2 + 130, 80), (0, 0, 255), -1)
    cv2.putText(processed, "ALERTA: INTRUSO DETECTADO", (width // 2 - 110, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 2, cv2.LINE_AA)
    
    # Left tactical metadata panel
    tact_overlay = processed.copy()
    cv2.rectangle(tact_overlay, (10, 48), (200, 150), (10, 10, 10), -1)
    cv2.addWeighted(tact_overlay, 0.5, processed, 0.5, 0, processed)
    cv2.rectangle(processed, (10, 48), (200, 150), (0, 0, 255), 1) # Red panel outline
    
    cv2.putText(processed, "METADATOS DE DETECCION", (18, 64), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (0, 0, 255), 1, cv2.LINE_AA)
    cv2.line(processed, (15, 70), (195, 70), (0, 0, 100), 1)
    cv2.putText(processed, f"Objetos Totales: {len(detections)}", (18, 88), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1, cv2.LINE_AA)
    person_cnt = sum(1 for d in detections if d["class_name"] == "person")
    cv2.putText(processed, f"Personas: {person_cnt}", (18, 106), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1, cv2.LINE_AA) # Red alerting text
    cv2.putText(processed, "Otros: dog:1, cup:1, phone:1", (18, 124), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (150, 150, 150), 1, cv2.LINE_AA)
    cv2.putText(processed, "COND_ACTION: ON", (18, 142), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (0, 255, 0), 1, cv2.LINE_AA)
    
    # Bottom Controls banner
    overlay_b = processed.copy()
    cv2.rectangle(overlay_b, (0, height - 30), (width, height), (15, 15, 15), -1)
    cv2.addWeighted(overlay_b, 0.75, processed, 0.25, 0, processed)
    cv2.putText(processed, controls_text, (12, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (190, 190, 190), 1, cv2.LINE_AA)
    
    # Save alarm image
    cv2.imwrite(os.path.join(media_dir, "screenshot_intrusion_alarm.png"), processed)
    print("[ASSET] Saved screenshot_intrusion_alarm.png")
    
    print("\n[OK] All high-quality README demo assets successfully generated!")

if __name__ == "__main__":
    generate()
