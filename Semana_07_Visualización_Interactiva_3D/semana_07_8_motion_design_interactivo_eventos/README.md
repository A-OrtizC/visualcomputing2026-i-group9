# Taller Motion Design Interactivo Eventos

**Nombre de los estudiantes:**
* Brayan Alejandro Muñoz Pérez bmunozp@unal.edu.co
* Álvaro Andrés Romero Castro alromeroca@unal.edu.co
* Juan Camilo Lopez Bustos juclopezbu@unal.edu.co
* Alejandro Ortiz Cortes alortizco@unal.edu.co
**Fecha de entrega:** 2026-04-25

## Descripción breve
Este taller aborda la integración de modelos 3D con rigs esqueléticos (animaciones de Mixamo) controlados interactivamente por el usuario. Se implementó un sistema de Motion Design donde los inputs del DOM disparan transiciones fluidas de estados de animación (Crossfading) como Caminar, Saltar y Saludar usando React Three Fiber.

## Implementaciones

### Three.js / React Three Fiber
Se utilizaron 3 archivos `.FBX` exportados desde Mixamo de forma independiente. Utilizando el hook `useFBX` se cargaron individualmente y, mediante el hook `useAnimations` de Drei, se fusionaron sus animaciones en un solo mixer de animaciones. Las transiciones se programaron mediante eventos nativos de JavaScript (`keydown`) y eventos del canvas de R3F (`onClick`, `onPointerOver`). Las transiciones entre clips se suavizan utilizando los métodos `.fadeIn()` y `.fadeOut()` del action mixer de Three.js.

## Resultados visuales
A continuación se presenta un *overview* visual del funcionamiento del Motion Design interactivo desarrollado en Three.js:
- ![R3F Animation](./media/r3f_motion.gif)

## Prompts utilizados
Se usó la IA para generar el README.md.

## Aprendizajes y dificultades
- **Aprendizajes:** Entendí cómo funcionan las transiciones y el blending entre animaciones esqueléticas para evitar cortes abruptos (crossfade). En React, aprendí a mapear eventos del ciclo de vida y del DOM a las acciones del mixer 3D.
- **Dificultades:** Requirió programar una solución dinámica en React para juntar diferentes archivos de animación en un solo render, en lugar de combinarlos manualmente en un software externo como Blender.

## Referencias
- Mixamo: https://www.mixamo.com/
- Three.js Animation System: https://threejs.org/docs/#manual/en/introduction/Animation-system
- React Three Fiber `useAnimations`: https://github.com/pmndrs/drei#useanimations
