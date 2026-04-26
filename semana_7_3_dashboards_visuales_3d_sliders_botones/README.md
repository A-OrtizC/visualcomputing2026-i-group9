# Taller Dashboards Visuales 3D Sliders Botones

**Nombre de los estudiantes:** 
* Brayan Alejandro Muñoz Pérez bmunozp@unal.edu.co
* Álvaro Andrés Romero Castro alromeroca@unal.edu.co
* Juan Camilo Lopez Bustos juclopezbu@unal.edu.co
* Alejandro Ortiz Cortes alortizco@unal.edu.co
**Fecha de entrega:** 2026-04-25

## Descripción breve
Este taller explora la creación de interfaces de usuario (Dashboards) para interactuar con entornos 3D en tiempo real. Se implementaron controladores de escala, color, rotación y luz paramétrica para modificar las propiedades espaciales y de renderizado de objetos en escena.

## Implementaciones

### Three.js / React Three Fiber
Se construyó una escena React utilizando `@react-three/fiber` y la librería `leva` para autogenerar un panel GUI. El panel actualiza el estado interno de React, el cual inyecta los valores paramétricos directamente a la geometría (escala), materiales (color) y luces (intensidad y color).

### Unity
Se implementó una escena interactiva usando el sistema de Canvas UI clásico. Se programó el script `DashboardController.cs` que realiza binding de eventos (`onValueChanged`, `onClick`) a funciones que alteran las propiedades del `transform`, `material.color` y la componente `Light` del motor.

## Resultados visuales
A continuación se presenta un *overview* visual del funcionamiento de los dashboards interactivos desarrollados en Three.js y Unity, respectivamente:
- ![React R3F Dashboard](./media/3f_dashboard.gif)
- ![Unity Dashboard](./media/unity_dashboard.gif)

## Prompts utilizados
Se usó para la creación/redacción del README.md

## Aprendizajes y dificultades
- **Aprendizajes:** Comprendí cómo mapear valores de un espacio bidimensional (UI Slider) a transformaciones afines en 3D (matriz de escala).
- **Dificultades:** Enlazar correctamente los eventos de Unity UI requirió asegurar que los objetos estuvieran correctamente referenciados en el Inspector.

## Referencias
- Documentación React Three Fiber: https://docs.pmnd.rs/react-three-fiber
- Librería Leva: https://github.com/pmndrs/leva
