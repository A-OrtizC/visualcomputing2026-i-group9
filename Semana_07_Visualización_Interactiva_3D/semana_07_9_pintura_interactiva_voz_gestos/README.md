# Taller Pintura Interactiva Voz Gestos

## Nombre del estudiante

* Brayan Alejandro Muñoz Pérez bmunozp@unal.edu.co
* Álvaro Andrés Romero Castro alromeroca@unal.edu.co
* Juan Camilo Lopez Bustos juclopezbu@unal.edu.co
* Alejandro Ortiz Cortes alortizco@unal.edu.co

## Fecha de entrega

2026-04-25

---

## Descripción breve

Este taller consistió en la creación de una obra artística digital interactiva controlada mediante una interfaz natural de usuario (NUI). El sistema integra la detección de gestos manuales para el control del "pincel" y el reconocimiento de voz para la ejecución de comandos lógicos.

Se desarrolló una aplicación en Python que utiliza la cámara para rastrear la punta del dedo índice y un lienzo virtual donde se generan trazos en tiempo real. Mediante comandos de voz, el usuario puede cambiar los colores (rojo, verde, azul), limpiar el lienzo o guardar su creación como un archivo de imagen, eliminando por completo la necesidad de periféricos tradicionales como el mouse o teclado.

---

## Implementaciones

### Python

La implementación se realizó utilizando un enfoque de **multihilo (threading)** para evitar que la interfaz de video se bloquee mientras el sistema espera la entrada de audio.

**Funcionalidades logradas:**
1. **Seguimiento con MediaPipe:** Se aisló el Landmark 8 (punta del índice) para mapear las coordenadas de la mano al lienzo digital.
2. **Lienzo Digital Dinámico:** Uso de máscaras bit a bit de OpenCV para superponer el dibujo sobre el video de la cámara en tiempo real.
3. **Procesamiento de Lenguaje Natural (NLP):** Integración de `speech_recognition` con el motor de Google para interpretar comandos en español.
4. **Persistencia de Datos:** Implementación de la función de guardado local de la obra maestra en formato `.png`.

---

## Resultados visuales

*(Nota: Asegúrate de que tus archivos en la carpeta `media/` tengan estos nombres exactos o actualízalos aquí)*

### Python - Implementación

![Funcionamiento de pintura y gestos](./media/python_resultado_1.gif)

*Demostración del trazo siguiendo el dedo índice y la respuesta visual del puntero en pantalla.*

![Comandos de voz y guardado](./media/python_resultado_2.webm)

*Captura del sistema reconociendo comandos de voz para cambiar de color y el resultado del lienzo guardado localmente.*

---

## Código relevante

A continuación, los fragmentos más importantes de la lógica implementada:

### 1. Control de voz con Hilos (Threading)
Para que la cámara no se detenga al hablar, el reconocimiento de voz corre en un hilo independiente:

```python
def listen_commands():
    global current_color, clear_canvas, status_text
    # ... configuración del micrófono ...
    command = recognizer.recognize_google(audio, language="es-ES").lower()
    
    if "rojo" in command:
        current_color = (0, 0, 255)
    elif "limpiar" in command:
        clear_canvas = True

```

### 2. Dibujo fluido sobre el lienzo
Se calcula la línea entre la posición anterior y la actual del dedo índice para crear un trazo continuo:
```
Python
# Mapeo de coordenadas del dedo índice (Landmark 8)
cx, cy = int(index_tip.x * w), int(index_tip.y * h)

# Dibujar en el lienzo virtual
if prev_x != 0:
    cv2.line(canvas, (prev_x, prev_y), (cx, cy), current_color, brush_thickness)
prev_x, prev_y = cx, cy

```
### 3. Fusión de Cámara y Lienzo (Masking)
Uso de operaciones bitwise para mostrar la pintura sobre el video:

```
Python
gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
_, mask = cv2.threshold(gray_canvas, 1, 255, cv2.THRESH_BINARY)
mask_inv = cv2.bitwise_not(mask)

image_bg = cv2.bitwise_and(image, image, mask=mask_inv)
canvas_fg = cv2.bitwise_and(canvas, canvas, mask=mask)
final_image = cv2.add(image_bg, canvas_fg)

```
## Prompts utilizados
Durante el desarrollo se utilizaron los siguientes prompts para optimizar el código y resolver errores de entorno:

* "¿Cómo puedo hacer para que el reconocimiento de voz no congele el video de la cámara?"

* "Explícame cómo funciona cv2.addWeighted y las máscaras para pintar sobre el video"

## Aprendizajes y dificultades
### Aprendizajes
Este taller me permitió entender la importancia de la concurrencia en Python. Aprendí que las tareas pesadas como el reconocimiento de voz deben ir en hilos separados para mantener una experiencia de usuario fluida (60 FPS en cámara). También profundicé en el uso de máscaras de imagen, una técnica fundamental en efectos visuales para combinar capas de video.

### Dificultades
1. Latencia de Voz: El reconocimiento de voz basado en la nube (Google API) presenta un pequeño retraso. Esto se mitigó ajustando el phrase_time_limit para capturar comandos cortos de forma más eficiente.
2. Incompatibilidad de MediaPipe: Al recrear el entorno para el Taller 7, volví a enfrentar el error de módulos faltantes en MediaPipe. La solución definitiva fue forzar la instalación de la versión estable 0.10.14 dentro del entorno virtual.

### Mejoras futuras
Me gustaría implementar el reconocimiento de voz de forma local (offline) utilizando librerías como Vosk para eliminar la dependencia de internet y reducir la latencia de los comandos. Además, podría añadir gestos para cambiar el grosor del pincel (por ejemplo, con la distancia entre dedos).

## Referencias
- MediaPipe Hands Documentation: https://developers.google.com/mediapipe/solutions/vision/hand_landmarker

- Python SpeechRecognition Library: https://pypi.org/project/SpeechRecognition/

- OpenCV Masking Tutorials: https://docs.opencv.org/
