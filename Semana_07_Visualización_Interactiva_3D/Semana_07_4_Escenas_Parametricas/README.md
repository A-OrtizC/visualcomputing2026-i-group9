# Taller Arquitectura Escenas Navegacion Unity Threejs

## Nombre del estudiante
* Brayan Alejandro Muñoz Pérez bmunozp@unal.edu.co
* Álvaro Andrés Romero Castro alromeroca@unal.edu.co
* Juan Camilo Lopez Bustos juclopezbu@unal.edu.co
* Alejandro Ortiz Cortes alortizco@unal.edu.co

## Fecha de entrega

25 de abril de 2026

## Descripción breve
Este taller explora la generación de geometría 3D programada a partir de datos estructurados en tres entornos diferentes. Se desarrollaron sistemas que interpretan listas de coordenadas y parámetros para crear escenas dinámicas, permitiendo la manipulación de formas, colores y escalas en tiempo real.

---

## Implementaciones

### Python (Google Colab)
Se utilizó la librería `vedo` para procesar una espiral de puntos generada matemáticamente.
* **Lógica Paramétrica:** Se implementó una condición donde los puntos con una altura $Z > 5$ se representan como esferas rojas, mientras que el resto son cubos azules cuya escala crece progresivamente.
* **Exportación:** El script genera un archivo `.obj` consolidando toda la geometría de la escena.

### Three.js (React Three Fiber)
Se creó una escena interactiva utilizando React para mapear un array de datos JSON.
* **Interfaz de Control:** Se integró la librería `Leva` para permitir al usuario controlar la escala global de los objetos y alternar el modo *wireframe* dinámicamente.
* **Componentización:** Cada objeto de datos se renderiza como un componente `DataObject` que decide su propia geometría (cubo o esfera) según sus propiedades internas.

### Unity (C#)
Se desarrolló un generador de primitivas en tiempo de ejecución.
* **Estructura de Datos:** Se empleó una clase serializable `DatosObjeto` para definir posiciones, escalas y tipos desde el inspector de Unity.
* **Sistema de Visualización:** Se añadió un botón en la interfaz de usuario para regenerar la escena y un script de cámara orbital que gira constantemente alrededor de los objetos para una visualización completa.

---

## Resultados visuales

### Python
![Resultado Python](media/python_resultado_1.gif)
*Muestra de la espiral generada y el cambio de geometría según la altura.*

### Three.js
| Captura 1 | Captura 2 |
| :---: | :---: |
| ![Threejs 1](media/threejs_resultado_1.png) | ![Threejs 2](media/threejs_resultado_2.png) |
*Uso de Leva para modificar parámetros de escala y visualización de mallas.*

### Unity
| Captura 1 | Captura 2 |
| :---: | :---: |
| ![Unity 1](media/unity_resultado_1.png) | ![Unity 2](media/unity_resultado_2.png) |
*Objetos generados en el espacio y configuración de la lista de datos en el Inspector.*

---

## Código relevante

### Lógica Condicional (Python)
```python
if pos[2] > 5:
    obj = vedo.Sphere(pos=pos, r=0.5, c="red", alpha=0.8)
else:
    size = 0.3 + (i * 0.05)
    obj = vedo.Cube(pos=pos, side=size, c="blue", alpha=0.8)

```
### Mapeo Adaptativo (Three.js)

```javaScript
{rawData.map((item) => (
  <DataObject 
    key={item.id} 
    data={item} 
    globalScale={scale} 
    wireframe={wireframe} 
  />
))}

```

### Generación de Primitivas (Unity)

```C#
if (dato.esEsfera) {
    nuevoObj = GameObject.CreatePrimitive(PrimitiveType.Sphere);
} else {
    nuevoObj = GameObject.CreatePrimitive(PrimitiveType.Cube);
}
nuevoObj.transform.position = dato.posicion;
nuevoObj.transform.localScale = Vector3.one * dato.escala;

```
## Prompts utilizados
- "Ayuda para generar una espiral de puntos en Python con vedo y exportarla a OBJ."

- "Cómo mapear un array de objetos en React Three Fiber usando Leva para controles."

- "Script en C# para Unity que cree cubos o esferas desde una lista y un botón para regenerar."

- "Crear un script de cámara que gire constantemente alrededor de un punto en Unity."

## Aprendizajes y dificultades

- Aprendizaje: La importancia de estandarizar los datos; una misma lista de coordenadas puede ser interpretada de forma idéntica en Python, WebGL o Unity.

- Dificultad: La gestión de materiales en Unity al usar CreatePrimitive, ya que requiere la creación de instancias de materiales para poder cambiar colores individualmente sin afectar el material global del motor.

## Referencias
* Vedo Documentation: https://vedo.embl.es/

* React Three Fiber Docs: https://docs.pmnd.rs/react-three-fiber/

* Unity Scripting API (GameObject.CreatePrimitive): https://docs.unity3d.com/ScriptReference/GameObject.CreatePrimitive.html

* Leva GUI Library: https://github.com/pmndrs/leva
