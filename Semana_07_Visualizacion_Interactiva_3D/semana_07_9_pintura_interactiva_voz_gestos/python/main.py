import cv2
import mediapipe as mp
import numpy as np
import speech_recognition as sr
import threading

# --- 1. CONFIGURACIÓN INICIAL ---
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Variables globales para el estado del dibujo
current_color = (255, 255, 255) # Blanco por defecto
brush_thickness = 5
prev_x, prev_y = 0, 0
canvas = None
clear_canvas = False
save_canvas = False
status_text = "Comandos: rojo, verde, azul, limpiar, guardar"

# --- 2. HILO DE RECONOCIMIENTO DE VOZ ---
def listen_commands():
    global current_color, clear_canvas, save_canvas, status_text
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    with microphone as source:
        # Ajustar ruido ambiental inicial
        recognizer.adjust_for_ambient_noise(source)
        
    while True:
        try:
            with microphone as source:
                print("Escuchando comando de voz...")
                audio = recognizer.listen(source, timeout=2, phrase_time_limit=3)
            
            # Reconocer voz en español
            command = recognizer.recognize_google(audio, language="es-ES").lower()
            print(f"Comando detectado: {command}")
            
            # Evaluar comandos
            if "rojo" in command:
                current_color = (0, 0, 255) # BGR
                status_text = "Color: ROJO"
            elif "verde" in command:
                current_color = (0, 255, 0)
                status_text = "Color: VERDE"
            elif "azul" in command:
                current_color = (255, 0, 0)
                status_text = "Color: AZUL"
            elif "pincel" in command:
                current_color = (255, 255, 255)
                status_text = "Color: BLANCO (Pincel)"
            elif "limpiar" in command:
                clear_canvas = True
                status_text = "Lienzo limpiado"
            elif "guardar" in command:
                save_canvas = True
                status_text = "Obra guardada!"
                
        except sr.WaitTimeoutError:
            pass # No se detectó voz en el tiempo límite, sigue escuchando
        except sr.UnknownValueError:
            pass # No se entendió el comando
        except Exception as e:
            print(f"Error de audio: {e}")

# Iniciar el hilo de voz en segundo plano (daemon=True permite cerrar el programa fácilmente)
voice_thread = threading.Thread(target=listen_commands, daemon=True)
voice_thread.start()

# --- 3. BUCLE PRINCIPAL DE VIDEO ---
cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=1) as hands:
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue

        # Voltear imagen y obtener dimensiones
        image = cv2.flip(image, 1)
        h, w, _ = image.shape
        
        # Inicializar el lienzo vacío la primera vez
        if canvas is None:
            canvas = np.zeros((h, w, 3), dtype=np.uint8)

        # Procesar banderas enviadas por la voz
        if clear_canvas:
            canvas = np.zeros((h, w, 3), dtype=np.uint8)
            clear_canvas = False
            
        if save_canvas:
            cv2.imwrite("mi_obra_maestra.png", canvas)
            save_canvas = False
            
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Dibujar esqueleto (opcional, para feedback visual)
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                lm = hand_landmarks.landmark
                index_tip = lm[8] # Punta del dedo índice
                
                # Coordenadas en píxeles del dedo índice
                cx, cy = int(index_tip.x * w), int(index_tip.y * h)
                
                # Para evitar saltos largos cuando la mano entra/sale de pantalla
                if prev_x == 0 and prev_y == 0:
                    prev_x, prev_y = cx, cy
                
                # Dibujar en el lienzo la línea desde el frame anterior hasta el actual
                cv2.line(canvas, (prev_x, prev_y), (cx, cy), current_color, brush_thickness)
                
                # Dibujar un círculo en vivo en la cámara para mostrar el "puntero"
                cv2.circle(image, (cx, cy), 10, current_color, cv2.FILLED)
                
                # Actualizar coordenadas previas
                prev_x, prev_y = cx, cy
        else:
            # Si no hay manos, reiniciar prev_x y prev_y para cortar el trazo
            prev_x, prev_y = 0, 0

        # Fusionar el lienzo sobre la cámara (donde el lienzo no es negro)
        # Esto permite ver tanto la cámara en vivo como la pintura flotando
        gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray_canvas, 1, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        
        image_bg = cv2.bitwise_and(image, image, mask=mask_inv)
        canvas_fg = cv2.bitwise_and(canvas, canvas, mask=mask)
        final_image = cv2.add(image_bg, canvas_fg)

        # Interfaz de texto
        cv2.putText(final_image, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(final_image, "Presiona ESC para salir", (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        cv2.imshow('Taller 7 - Pintura por Voz y Gestos', final_image)
        
        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()