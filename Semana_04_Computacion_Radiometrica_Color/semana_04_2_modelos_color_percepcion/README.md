# Taller - Explorando el Color: Percepción Humana y Modelos Computacionales

## Objetivo del taller

Investigar la percepción del color desde el punto de vista humano y computacional, y representar visualmente las diferencias entre modelos de color. El objetivo es comprender cómo los distintos espacios de color afectan la interpretación visual y cómo pueden aplicarse transformaciones para simular condiciones específicas.

---

## Actividades por entorno

Este taller se desarrolla en **Python** y puede complementarse con escenas en **Unity** o **Three.js** para explorar efectos visuales sobre materiales o texturas.

---

### Python (Colab o Jupyter Notebook)

**Herramientas:** `opencv-python`, `matplotlib`, `colorsys`, `skimage.color`, `numpy`

- Cargar una imagen y convertirla entre diferentes espacios de color:
 - De **RGB → HSV**
 - De **RGB → CIE Lab**
- Visualizar los canales individuales y su efecto en la percepción.
- Simular alteraciones de visión:
 - Daltonismo (protanopía, deuteranopía) con funciones de simulación o manipulación de matrices de color.
 - Reducción de brillo o contraste para simular entornos de baja luz.
- Aplicar transformaciones de color sobre imágenes o texturas para cambiar el aspecto visual según condiciones personalizadas (e.g., filtros de temperatura de color, inversión, monocromo).
- *Bonus:* Crear una función que permita alternar dinámicamente entre modelos o simulaciones.

---

### Unity o Three.js (Opcional)

**Escenario:**

- Crear una escena con materiales aplicados a objetos (cubos, esferas).
- Aplicar cambios de color programáticamente (por código) y observar su efecto visual.
- Simular filtros de visión o cambios de color al modificar shaders, materiales o texturas.
- *Bonus:* Agregar un UI slider o menú para seleccionar el modelo de color o simulación.

---

## Entrega

Crear carpeta con el nombre: `semana_4_2_modelos_color_percepcion` en tu repositorio de GitLab.

Dentro de la carpeta, crear la siguiente estructura:

```
semana_4_2_modelos_color_percepcion/
├── python/
├── unity/
├── threejs/
├── media/ # Imágenes, videos, GIFs de resultados
└── README.md
```

### Requisitos del README.md

El archivo `README.md` debe contener obligatoriamente:

1. **Título del taller**: Taller Modelos Color Percepcion
2. **Nombre del estudiante**
3. **Fecha de entrega**
4. **Descripción breve**: Explicación del objetivo y lo desarrollado
5. **Implementaciones**: Descripción de cada implementación realizada por entorno
6. **Resultados visuales**: 
 - **Imágenes, videos o GIFs** que muestren el funcionamiento
 - Deben estar en la carpeta `media/` y referenciados en el README
 - Mínimo 2 capturas/GIFs por implementación
7. **Código relevante**: Snippets importantes o enlaces al código
8. **Prompts utilizados**: Descripción de prompts usados (si aplicaron IA generativa)
9. **Aprendizajes y dificultades**: Reflexión personal sobre el proceso

### Estructura de carpetas

- Cada entorno de desarrollo debe tener su propia subcarpeta (`python/`, `unity/`, `threejs/`, etc.)
- La carpeta `media/` debe contener todos los recursos visuales (imágenes, GIFs, videos)
- Nombres de archivos en minúsculas, sin espacios (usar guiones bajos o guiones medios)

---

## Criterios de evaluación

- Cumplimiento de los objetivos del taller
- Código limpio, comentado y bien estructurado
- README.md completo con toda la información requerida
- Evidencias visuales claras (imágenes/GIFs/videos en carpeta `media/`)
- Repositorio organizado siguiendo la estructura especificada
- Commits descriptivos en inglés
- Nombre de carpeta correcto: `semana_4_2_modelos_color_percepcion`

