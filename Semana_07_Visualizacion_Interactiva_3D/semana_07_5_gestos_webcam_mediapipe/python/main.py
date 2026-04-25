import cv2
import mediapipe as mp
import numpy as np
import math

# Inicializar MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Variables de estado iniciales
bg_color = (0, 0, 0)
object_pos = [320, 240]
scene = 0
scene_changed = False 

# Iniciar captura de video
cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=1) as hands:
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignorando frame vacío de la cámara.")
            continue

        # Voltear la imagen (efecto espejo) y convertir a RGB
        image = cv2.flip(image, 1)
        h, w, _ = image.shape
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Procesar con MediaPipe
        results = hands.process(image_rgb)

        # Capa superpuesta para efectos visuales
        overlay = np.zeros((h, w, 3), dtype=np.uint8)
        fingers_count = 0
        distance = 0

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Dibujar conexiones de la mano
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                lm = hand_landmarks.landmark
                
                # Obtener puntos clave (pulgar e índice)
                thumb_tip = lm[4]
                index_tip = lm[8]
                middle_tip = lm[12]
                ring_tip = lm[16]
                pinky_tip = lm[20]
                
                # Articulaciones para calcular si el dedo está extendido
                index_pip = lm[6]
                middle_pip = lm[10]
                ring_pip = lm[14]
                pinky_pip = lm[18]
                
                # --- MEDICIÓN 1: Distancia entre pulgar e índice ---
                cx1, cy1 = int(thumb_tip.x * w), int(thumb_tip.y * h)
                cx2, cy2 = int(index_tip.x * w), int(index_tip.y * h)
                distance = math.hypot(cx2 - cx1, cy2 - cy1)
                
                # --- MEDICIÓN 2: Contar dedos extendidos ---
                # Pulgar (heurística básica basada en X, asumiendo mano derecha)
                if lm[4].x < lm[3].x: fingers_count += 1
                # Resto de dedos (basado en Y)
                if index_tip.y < index_pip.y: fingers_count += 1
                if middle_tip.y < middle_pip.y: fingers_count += 1
                if ring_tip.y < ring_pip.y: fingers_count += 1
                if pinky_tip.y < pinky_pip.y: fingers_count += 1

                # --- ACCIONES VISUALES ---
                # Acción 1: Mover objeto en pantalla (sigue al índice)
                object_pos = [cx2, cy2]
                
                # Acción 2: Cambiar color de fondo según número de dedos
                if fingers_count == 1: bg_color = (0, 0, 255)       # Rojo
                elif fingers_count == 2: bg_color = (0, 255, 0)     # Verde
                elif fingers_count == 3: bg_color = (255, 0, 0)     # Azul
                elif fingers_count == 4: bg_color = (0, 255, 255)   # Amarillo
                elif fingers_count == 0: bg_color = (0, 0, 0)       # Normal
                
                # Acción 3: Cambiar de escena con palma abierta (5 dedos) y separados
                if fingers_count == 5 and distance > 50:
                    if not scene_changed:
                        scene = 1 if scene == 0 else 0
                        scene_changed = True
                else:
                    scene_changed = False

        # --- RENDERIZADO DE ESCENAS ---
        if scene == 0:
            # ESCENA 0: Cámara en vivo con tinte de color y objeto escalable
            overlay[:] = bg_color
            image = cv2.addWeighted(image, 0.8, overlay, 0.2, 0)
            
            # Dibujar línea e info si hay manos
            if results.multi_hand_landmarks:
                cv2.line(image, (cx1, cy1), (cx2, cy2), (255, 255, 255), 2)
                
                # Tamaño del objeto cambia según la distancia (pinza)
                radius = max(10, int(distance / 2))
                cv2.circle(image, tuple(object_pos), radius, (255, 0, 255), -1)
            
            cv2.putText(image, f"Dedos: {fingers_count} - Escena 0 (Camara)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(image, "Muestra 5 dedos para cambiar de escena", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        elif scene == 1:
            # ESCENA 1: "Modo Juego" - Fondo opaco, solo interfaz
            image[:] = bg_color # Rellenar todo el fondo
            
            # Dibujar el "jugador" (cuadrado) en la posición del dedo
            cv2.rectangle(image, (object_pos[0]-30, object_pos[1]-30), (object_pos[0]+30, object_pos[1]+30), (255, 255, 255), -1)
            
            cv2.putText(image, "ESCENA 1 - MODO JUEGO", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(image, f"Mueve el cuadro con el indice. Dedos: {fingers_count}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Mostrar FPS e imagen
        cv2.imshow('Taller Gestos Webcam - ESC para salir', image)
        
        # Salir con la tecla ESC
        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
