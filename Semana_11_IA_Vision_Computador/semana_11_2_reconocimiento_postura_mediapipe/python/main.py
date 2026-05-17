import cv2
import mediapipe as mp
import numpy as np
import math
import time

# ==========================================
# CONFIGURACIÓN MEDIAPIPE
# ==========================================

print(mp)
print(mp.__file__)

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ==========================================
# VARIABLES GLOBALES
# ==========================================

ultima_accion = "Ninguna"
ultimo_cambio = time.time()

# Variables para detectar caminata
historial_pie_izq = []
historial_pie_der = []

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

def calcular_distancia(p1, p2):
    return math.sqrt(
        (p2[0] - p1[0])**2 +
        (p2[1] - p1[1])**2
    )


def calcular_angulo(a, b, c):
    """
    Calcula el ángulo entre 3 puntos.
    """
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - \
              np.arctan2(a[1] - b[1], a[0] - b[0])

    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle


def detectar_sentado(
    left_shoulder,
    right_shoulder,
    left_hip,
    right_hip,
    left_knee,
    right_knee,
    left_ankle,
    right_ankle
):

    # =========================
    # ÁNGULOS DE RODILLAS
    # =========================

    angulo_rodilla_izq = calcular_angulo(
        [left_hip.x, left_hip.y],
        [left_knee.x, left_knee.y],
        [left_ankle.x, left_ankle.y]
    )

    angulo_rodilla_der = calcular_angulo(
        [right_hip.x, right_hip.y],
        [right_knee.x, right_knee.y],
        [right_ankle.x, right_ankle.y]
    )

    # =========================
    # ÁNGULO DEL TORSO
    # =========================

    shoulder_center = [
        (left_shoulder.x + right_shoulder.x) / 2,
        (left_shoulder.y + right_shoulder.y) / 2
    ]

    hip_center = [
        (left_hip.x + right_hip.x) / 2,
        (left_hip.y + right_hip.y) / 2
    ]

    # Línea vertical artificial
    punto_vertical = [
        hip_center[0],
        hip_center[1] - 0.3
    ]

    angulo_torso = calcular_angulo(
        shoulder_center,
        hip_center,
        punto_vertical
    )

    # =========================
    # CONDICIÓN DE SENTADO
    # =========================

    rodillas_dobladas = (
        angulo_rodilla_izq < 160 and
        angulo_rodilla_der < 160
    )

    torso_recto = angulo_torso < 35

    return rodillas_dobladas and torso_recto

def detectar_brazos_arriba(left_wrist_y, right_wrist_y, nose_y):
    """
    Brazos levantados:
    Las muñecas están arriba de la cabeza.
    """
    return left_wrist_y < nose_y and right_wrist_y < nose_y


historial_distancias = []

def detectar_caminando(left_ankle, right_ankle):

    global historial_distancias

    # Distancia horizontal entre pies
    distancia = abs(left_ankle.x - right_ankle.x)

    historial_distancias.append(distancia)

    if len(historial_distancias) > 20:
        historial_distancias.pop(0)

    if len(historial_distancias) < 20:
        return False

    variacion = max(historial_distancias) - min(historial_distancias)

    # Detecta alternancia incluso en pasos pequeños
    return variacion > 0.03

# ==========================================
# CAPTURA DE VIDEO
# ==========================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("No se pudo abrir la cámara")
    exit()

print("Presiona Q para salir")

# ==========================================
# BUCLE PRINCIPAL
# ==========================================

while True:

    ret, frame = cap.read()

    if not ret:
        break

    # Voltear imagen horizontalmente
    frame = cv2.flip(frame, 1)

    # Convertir BGR -> RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Procesar pose
    results = pose.process(rgb_frame)

    accion_detectada = "Sin detectar"

    if results.pose_landmarks:

        # Dibujar esqueleto
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

        landmarks = results.pose_landmarks.landmark

        # ==========================================
        # OBTENER LANDMARKS IMPORTANTES
        # ==========================================

        nose = landmarks[mp_pose.PoseLandmark.NOSE]

        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]

        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]

        left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
        right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE]

        left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
        right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]

        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

        # ==========================================
        # DETECCIÓN DE ACCIONES
        # ==========================================

        # Brazos arriba
        if detectar_brazos_arriba(
            left_wrist.y,
            right_wrist.y,
            nose.y
        ):
            accion_detectada = "Brazos Arriba"

        # Sentado
        elif detectar_sentado(
            left_shoulder,
            right_shoulder,
            left_hip,
            right_hip,
            left_knee,
            right_knee,
            left_ankle,
            right_ankle
        ):
            accion_detectada = "Sentado"

        # Caminando
        elif detectar_caminando(
            left_ankle,
            right_ankle
        ):
            accion_detectada = "Caminando"

        else:
            accion_detectada = "De Pie"

        # ==========================================
        # CÁLCULO DE ÁNGULOS
        # ==========================================

        angulo_rodilla_izq = calcular_angulo(
            [left_hip.x, left_hip.y],
            [left_knee.x, left_knee.y],
            [left_ankle.x, left_ankle.y]
        )

        angulo_rodilla_der = calcular_angulo(
            [right_hip.x, right_hip.y],
            [right_knee.x, right_knee.y],
            [right_ankle.x, right_ankle.y]
        )

        # Mostrar ángulos
        cv2.putText(
            frame,
            f"Rodilla Izq: {int(angulo_rodilla_izq)}",
            (10, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Rodilla Der: {int(angulo_rodilla_der)}",
            (10, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )

        # ==========================================
        # RETROALIMENTACIÓN VISUAL
        # ==========================================

        if accion_detectada == "Brazos Arriba":
            color = (0, 255, 0)

        elif accion_detectada == "Sentado":
            color = (0, 0, 255)

        elif accion_detectada == "Caminando":
            color = (255, 0, 0)

        else:
            color = (255, 255, 255)

        # Mostrar acción
        cv2.putText(
            frame,
            f"Accion: {accion_detectada}",
            (10, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            3
        )

        # Mostrar cantidad de landmarks
        cv2.putText(
            frame,
            "Landmarks detectados: 33",
            (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

    # ==========================================
    # MOSTRAR VIDEO
    # ==========================================

    cv2.imshow("Reconocimiento de Acciones", frame)

    # Salir con Q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ==========================================
# LIBERAR RECURSOS
# ==========================================

cap.release()
cv2.destroyAllWindows()