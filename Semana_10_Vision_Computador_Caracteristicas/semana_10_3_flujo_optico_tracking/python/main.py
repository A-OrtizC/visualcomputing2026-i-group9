import cv2
import numpy as np
import time

def main():
    captura = cv2.VideoCapture(0)
    if not captura.isOpened():
        print("Error: No se pudo abrir la cámara.")
        return

    # Parámetros Lucas-Kanade y Shi-Tomasi
    params_esquinas = dict(maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)
    params_lk = dict(winSize=(15, 15), maxLevel=2,
                     criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    ret, frame_inicial = captura.read()
    if not ret:
        return
    frame_inicial = cv2.flip(frame_inicial, 1)
    gris_previo = cv2.cvtColor(frame_inicial, cv2.COLOR_BGR2GRAY)

    puntos_previos = None
    mascara_dibujo = np.zeros_like(frame_inicial)
    colores = np.random.randint(0, 255, (100, 3))

    hsv = np.zeros_like(frame_inicial)
    hsv[..., 1] = 255

    modo = 1 
    tiempo_previo = time.time()

    print("--- Controles ---")
    print("1: Flujo Disperso (Lucas-Kanade - Sin Fantasmas)")
    print("2: Flujo Denso (Farnebäck)")
    print("3: Detección de Movimiento (Tracking ROI)")
    print("r: Reiniciar puntos (Lucas-Kanade)")
    print("q: Salir")

    while True:
        ret, frame_actual = captura.read()
        if not ret:
            break
        frame_actual = cv2.flip(frame_actual, 1)
        gris_actual = cv2.cvtColor(frame_actual, cv2.COLOR_BGR2GRAY)
        resultado = frame_actual.copy()

        # Calcular FPS
        tiempo_actual = time.time()
        fps = 1.0 / (tiempo_actual - tiempo_previo)
        tiempo_previo = tiempo_actual

        if modo == 1:
            # FIX "FANTASMAS": Crear máscara basada en diferencia de frames (movimiento real)
            diferencia = cv2.absdiff(gris_previo, gris_actual)
            _, mascara_filtro_fondo = cv2.threshold(diferencia, 15, 255, cv2.THRESH_BINARY)
            # Limpiar ruido de la máscara con morfología
            kernel_ruido = np.ones((5,5), np.uint8)
            mascara_filtro_fondo = cv2.morphologyEx(mascara_filtro_fondo, cv2.MORPH_OPEN, kernel_ruido)

            # Re-detectar si se pierden puntos, aplicando la MÁSCARA DE MOVIMIENTO
            if puntos_previos is None or len(puntos_previos) < 10:
                puntos_previos = cv2.goodFeaturesToTrack(gris_previo, mask=mascara_filtro_fondo, **params_esquinas)
                mascara_dibujo = np.zeros_like(frame_actual)

            if puntos_previos is not None and len(puntos_previos) > 0:
                puntos_nuevos, estado, error = cv2.calcOpticalFlowPyrLK(gris_previo, gris_actual, puntos_previos, None, **params_lk)
                
                if puntos_nuevos is not None:
                    buenos_nuevos = puntos_nuevos[estado == 1]
                    buenos_viejos = puntos_previos[estado == 1]

                    for i, (nuevo, viejo) in enumerate(zip(buenos_nuevos, buenos_viejos)):
                        a, b = nuevo.ravel()
                        c, d = viejo.ravel()
                        # Dibujar solo si hay un movimiento notable (filtra micro-temblores)
                        if abs(a-c) > 0.5 or abs(b-d) > 0.5:
                            mascara_dibujo = cv2.line(mascara_dibujo, (int(a), int(b)), (int(c), int(d)), colores[i % 100].tolist(), 2)
                        resultado = cv2.circle(resultado, (int(a), int(b)), 5, colores[i % 100].tolist(), -1)
                    
                    resultado = cv2.add(resultado, mascara_dibujo)
                    puntos_previos = buenos_nuevos.reshape(-1, 1, 2)
            
            cv2.putText(resultado, "Modo: 1 - LK (Filtro Fondo Activo)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        elif modo in [2, 3]:
            flujo = cv2.calcOpticalFlowFarneback(gris_previo, gris_actual, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            magnitud, angulo = cv2.cartToPolar(flujo[..., 0], flujo[..., 1])

            if modo == 2:
                hsv[..., 0] = angulo * 180 / np.pi / 2
                hsv[..., 2] = cv2.normalize(magnitud, None, 0, 255, cv2.NORM_MINMAX)
                resultado = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
                cv2.putText(resultado, "Modo: 2 - Farneback Denso", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            elif modo == 3:
                _, mascara_movimiento = cv2.threshold(magnitud, 3.0, 255, cv2.THRESH_BINARY)
                mascara_movimiento = mascara_movimiento.astype(np.uint8)
                
                kernel = np.ones((5, 5), np.uint8)
                mascara_movimiento = cv2.morphologyEx(mascara_movimiento, cv2.MORPH_OPEN, kernel)
                mascara_movimiento = cv2.morphologyEx(mascara_movimiento, cv2.MORPH_CLOSE, kernel)

                contornos, _ = cv2.findContours(mascara_movimiento, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                objetos_movimiento = 0
                for contorno in contornos:
                    if cv2.contourArea(contorno) > 500:
                        x, y, w, h = cv2.boundingRect(contorno)
                        cv2.rectangle(resultado, (x, y), (x+w, y+h), (0, 0, 255), 2)
                        objetos_movimiento += 1

                cv2.putText(resultado, f"Modo: 3 - Tracking | Objetos: {objetos_movimiento}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.putText(resultado, f"FPS: {int(fps)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.imshow("Flujo Optico y Tracking", resultado)

        gris_previo = gris_actual.copy()

        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord('q'):
            break
        elif tecla == ord('1'):
            modo = 1
            puntos_previos = None # Fuerza re-detección limpia
            mascara_dibujo = np.zeros_like(frame_actual)
        elif tecla == ord('2'):
            modo = 2
        elif tecla == ord('3'):
            modo = 3
        elif tecla == ord('r') and modo == 1:
            puntos_previos = None # Fuerza re-detección limpia
            mascara_dibujo = np.zeros_like(frame_actual)

    captura.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()