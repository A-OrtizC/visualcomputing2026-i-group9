# Taller Gestos Webcam Mediapipe

## Nombre del estudiante

* Brayan Alejandro Muñoz Pérez bmunozp@unal.edu.co
* Álvaro Andrés Romero Castro alromeroca@unal.edu.co
* Juan Camilo Lopez Bustos juclopezbu@unal.edu.co
* Alejandro Ortiz Cortes alortizco@unal.edu.co

## Fecha de entrega

2026-04-25

---

## Descripción breve

El objetivo de este taller es utilizar la cámara web junto con la biblioteca MediaPipe para detectar gestos de las manos y ejecutar acciones visuales en tiempo real. 

Durante el desarrollo, se exploró cómo las interfaces naturales pueden emplearse para interactuar con la pantalla de forma intuitiva y sin necesidad de hardware adicional (como mouse o teclado), basando las interacciones en el conteo de dedos y la distancia entre las articulaciones clave.

---

## Implementaciones

### Python

Para este taller se desarrolló un script en Python utilizando `opencv-python` para la captura y renderizado de video, `mediapipe` para el seguimiento de los puntos de referencia de la mano (Hand Landmarks) y `numpy` para operaciones de matrices.

**Funcionalidades logradas:**
1. **Conteo de dedos:** Se implementó una lógica heurística que evalúa la posición de las puntas de los dedos (tips) respecto a sus articulaciones inferiores (pips) para determinar cuántos dedos están extendidos.
2. **Distancia de pinza:** Se calcula la distancia euclidiana entre la punta del pulgar (Landmark 4) y el índice (Landmark 8) para escalar el tamaño de un objeto interactivo en pantalla.
3. **Acciones Visuales Interactivas:**
   - **Cambio de fondo:** El color de la interfaz cambia dinámicamente si el usuario muestra de 1 a 4 dedos.
   - **Seguimiento de objeto:** Un elemento gráfico (círculo/cuadrado) sigue las coordenadas en tiempo real del dedo índice.
   - **Cambio de Escena:** Mostrar la palma abierta completa (5 dedos) y separados activa un "Modo Juego" que cambia de la captura de video en vivo a una interfaz opaca interactiva.

---

## Resultados visuales

*(Nota: Asegúrate de guardar tus capturas o GIFs en la carpeta `media/`)*

### Python - Implementación

![Detección y seguimiento de dedos](./media/python_resultado_1.gif)

*Escena 0: Cámara en vivo detectando los dedos de la mano y calculando la distancia (pinza) entre el pulgar y el índice, modificando el radio del círculo de seguimiento.*

![Cambio de escena y color](./media/python_resultado_2.gif)

*Escena 1: Interfaz opaca ("Modo Juego") activada al mostrar 5 dedos, interactuando con el objeto (cuadrado) en un lienzo virtual limpio.*

---

## Código relevante

A continuación, se presentan los fragmentos clave del archivo `main.py` que controlan el núcleo de la aplicación:

### 1. Medición de distancia (Pinza Pulgar-Índice)
Utilizando la librería `math`, calculamos la hipotenusa (distancia euclidiana) entre el punto del pulgar y el índice para modificar el tamaño de objetos:

```python
# --- MEDICIÓN 1: Distancia entre pulgar e índice ---
cx1, cy1 = int(thumb_tip.x * w), int(thumb_tip.y * h)
cx2, cy2 = int(index_tip.x * w), int(index_tip.y * h)
distance = math.hypot(cx2 - cx1, cy2 - cy1)
```

### 2. Conteo de dedos extendidos
A través de heurísticas espaciales comparamos la posición de las puntas de los dedos (tips) con sus articulaciones (pips):

```python
# --- MEDICIÓN 2: Contar dedos extendidos ---
# Pulgar (heurística básica basada en X, asumiendo mano derecha)
if lm[4].x < lm[3].x: fingers_count += 1
# Resto de dedos (basado en Y)
if index_tip.y < index_pip.y: fingers_count += 1
if middle_tip.y < middle_pip.y: fingers_count += 1
if ring_tip.y < ring_pip.y: fingers_count += 1
if pinky_tip.y < pinky_pip.y: fingers_count += 1

```

### 3. Acciones visuales y cambio de escena
Dependiendo del número de dedos, se cambia el color de fondo. Si hay 5 dedos y están separados (distancia > 50), se alterna entre la escena de cámara (0) y el modo juego (1):

```python
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

```

### 4. Interacción del objeto en pantalla
El objeto en la pantalla usa el radio basado en la distancia calculada previamente y sigue al índice:

```python
# Tamaño del objeto cambia según la distancia (pinza)
radius = max(10, int(distance / 2))
cv2.circle(image, tuple(object_pos), radius, (255, 0, 255), -1)

```

## Prompts utilizados
Durante el desarrollo de este taller se utilizó IA generativa (Gemini) para la configuración inicial del entorno, escritura del código base y resolución de errores. Los prompts principales fueron:

* "Explícame la estructura de los multi_hand_landmarks que devuelve MediaPipe. ¿Qué significan exactamente los valores x, y y z de cada punto y por qué es necesario multiplicarlos por el ancho (w) y alto (h) de la imagen para dibujar en OpenCV?"

* "En el script usamos una comparación entre las puntas de los dedos (Tips) y sus articulaciones medias (PIPs). Explícame detalladamente por qué esta lógica funciona para contar dedos y por qué el pulgar requiere una lógica diferente basada en el eje X en lugar del eje Y."

* "Deseo profundizar en la interacción por proximidad. ¿Cómo funciona la función math.hypot para calcular la distancia entre el pulgar y el índice? Además, explícame cómo puedo normalizar esa distancia para que el tamaño del objeto en pantalla no dependa de qué tan cerca o lejos esté mi mano de la cámara."
## Aprendizajes y dificultades
### Aprendizajes
Aprendí a utilizar las Solutions de MediaPipe para obtener las coordenadas espaciales (Landmarks) de las manos en tiempo real. También reforcé mis conocimientos sobre entornos virtuales en Python y cómo manipular capas superpuestas (overlays) con OpenCV combinando matrices de NumPy con los frames de la cámara de video para crear interfaces en tiempo real.

### Dificultades
1. Compatibilidad de versiones de Python: Encontré dificultades al intentar ejecutar MediaPipe con Python 3.14, lo que requirió la creación de un entorno virtual forzado con Python 3.10 usando el comando py -3.10 -m venv venv desde Git Bash en Windows.
2. Error de caracteres especiales en rutas (Windows): MediaPipe arrojaba un FileNotFoundError al intentar cargar el archivo de modelo C++ hand_landmark_tracking_cpu.binarypb. Descubrí que el motor de MediaPipe en Windows no soporta rutas con tildes (como "Ingeniería" o "Computación"), lo que se solucionó migrando el proyecto a una ruta limpia sin caracteres especiales.

##Mejoras futuras
Para futuros proyectos, me gustaría implementar un reconocedor de gestos más robusto utilizando Machine Learning (como un clasificador KNN o SVM sobre los landmarks) en lugar de depender únicamente de condicionales (if/else) y coordenadas X/Y, lo cual haría la detección completamente independiente del ángulo y la rotación de la mano.

## Referencias
- Documentación oficial de OpenCV: https://docs.opencv.org/

- Documentación de MediaPipe Hands: https://developers.google.com/mediapipe/solutions/vision/hand_landmarker

