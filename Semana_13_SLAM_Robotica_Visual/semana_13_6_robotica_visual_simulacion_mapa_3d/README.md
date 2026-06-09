# Taller Robotica Visual Simulacion Mapa 3D

## Nombre del estudiante

* Brayan Alejandro Muñoz Pérez bmunozp@unal.edu.co
* Álvaro Andrés Romero Castro alromeroca@unal.edu.co
* Juan Camilo Lopez Bustos juclopezbu@unal.edu.co
* Alejandro Ortiz Cortes alortizco@unal.edu.co

## Fecha de entrega
08 de junio de 2026

## Descripción breve

Este taller consistió en el desarrollo y simulación de un **robot móvil autónomo** capaz de desplazarse de manera inteligente dentro de un entorno tridimensional cerrado con forma de laberinto. El objetivo principal fue explorar e implementar principios fundamentales de **robótica visual y planificación reactiva local** mediante el uso de sensores de proximidad simulados a través de la técnica de *Raycasting* (lanzamiento de rayos).

Para comprobar la versatilidad de los algoritmos de control diseñados, se implementaron dos entornos paralelos con arquitecturas tecnológicas distintas: **Entorno A (Unity 3D)**, utilizando programación orientada a componentes en C#, y **Entorno B (React Three Fiber / Three.js)**, utilizando un enfoque declarativo web y renderizado acelerado por WebGL. En ambos casos, el chasis del agente ejecuta ciclos continuos de percepción-acción para evadir obstáculos dispuestos en zigzag, escapar de encajonamientos complejos y orientarse magnéticamente hacia una meta final.

---

## Implementaciones

### Unity

La implementación en el Entorno A se realizó sobre el motor Unity utilizando físicas cinemáticas y detección geométrica. El robot detecta el entorno mediante tres líneas de visión concurrentes (`Physics.Raycast`) configuradas en abanico frontal (frente, izquierda a $-45^\circ$ y derecha a $+45^\circ$). Cuando el frente está libre, el algoritmo ejecuta una rutina de atracción hacia el objetivo (*Goal Seeking*), calculando la dirección trigonométrica hacia la meta e interpolando suavemente la rotación del robot. Si el sensor frontal registra un obstáculo por debajo del umbral de seguridad, el robot entra en estado de evasión local, comparando las lecturas laterales para elegir la salida más despejada. Además, se utilizó un componente `LineRenderer` para persistir la posición histórica del chasis y trazar su trayectoria continua en color azul.

### Three.js / React Three Fiber

La implementación en el Entorno B trasladó la lógica al navegador web mediante React Three Fiber (R3F) y la librería de utilidades `@react-three/drei`. En lugar de recrear múltiples instancias físicas pesadas, se optimizó el bucle de renderizado interactivo dentro del gancho de alta frecuencia `useFrame`. El robot realiza proyecciones matemáticas vectoriales en el plano horizontal $XZ$ utilizando un único objeto de tipo `THREE.Raycaster`. El feedback visual de detección se realiza mutando directamente el color de las mallas que simulan los láseres de los sensores (cambiando instantáneamente a rojo o naranja al intersectar obstáculos) para evitar re-renders y caídas de frames. Se integró la librería `Leva` para proveer un panel de control interactivo en tiempo real y el componente `<Trail>` de Drei para el dibujo automatizado de la estela tridimensional.

---

## Resultados visuales

### Unity - Implementación

![Resultado Unity 1 (Animación GIF)](./media/unity_resultado_2.gif)

*Descripción: [Espacio reservado para el GIF de Unity] Animación en la que se aprecia al robot saliendo del bucle de atasco, evaluando esquinas y recorriendo la trayectoria de manera fluida.*

![Resultado Unity 2 (Captura de Pantalla)](./media/unity_resultado_1.png)

*Descripción: Captura de pantalla de la escena en Unity donde se visualiza la pista completa con los obstáculos de color rosa, la estela azul generada por el LineRenderer y las líneas de depuración de los rayos frontales.*

### Three.js - Implementación

![Resultado Three.js 1 (Animación GIF)](./media/three_resultado_2.gif)

*Descripción: [Espacio reservado para el GIF de Three.js] Demostración en el navegador del agente web sorteando el laberinto adaptativo de manera reactiva.*

![Resultado Three.js 2 (Captura de Pantalla)](./media/three_resultado_1.png)

*Descripción: Captura del lienzo WebGL en el navegador que muestra la geometría tridimensional de la pista, el objeto esférico dorado que representa la meta y el menú flotante de control Leva.*

---

## Código relevante

### Fragmento Crítico en Unity (C#)

A continuación se exponen las líneas más importantes del bucle de decisión del robot en Unity, encargadas de realizar el **Raycasting múltiple** y discriminar entre el estado de evasión adaptativa y la orientación suave hacia la meta:

```csharp
// --- PERCEPCIÓN: Lanzamiento de rayos en abanico frontal ---
Vector3 forwardDir = transform.forward;
Vector3 leftDir = Quaternion.Euler(0, -45, 0) * transform.forward;
Vector3 rightDir = Quaternion.Euler(0, 45, 0) * transform.forward;

bool hitForward = Physics.Raycast(transform.position, forwardDir, out RaycastHit forwardHit, rayLength, obstacleLayer);
bool hitLeft = Physics.Raycast(transform.position, leftDir, out RaycastHit leftHit, rayLength, obstacleLayer);
bool hitRight = Physics.Raycast(transform.position, rightDir, out RaycastHit rightHit, rayLength, obstacleLayer);

// --- TOMA DE DECISIONES Y CONTROL CINEMÁTICO ---
if (hitForward)
{
    // MÁQUINA DE ESTADOS: EVASIÓN DE OBSTÁCULOS
    // Si el frente está obstruido, analizamos los sensores laterales para decidir el giro óptimo
    if (hitRight && !hitLeft)        evasionDirection = -1; // Derecha bloqueada -> Girar a la Izquierda
    else if (hitLeft && !hitRight)   evasionDirection = 1;  // Izquierda bloqueada -> Girar a la Derecha
    else if (hitLeft && hitRight)
    {
        // Caso complejo (Pasillo cerrado/Esquina): Girar hacia donde el obstáculo esté más lejos
        evasionDirection = (leftHit.distance > rightHit.distance) ? -1 : 1;
    }
    
    // Aplicar velocidad de rotación sobre el eje vertical Y
    transform.Rotate(Vector3.up * evasionDirection * (rotationSpeed * 50.0f) * Time.deltaTime);
}
else
{
    // MÁQUINA DE ESTADOS: GOAL SEEKING (ATRACCIÓN A LA META)
    // El camino frontal está libre; orientamos activamente el rumbo hacia la meta dorada
    Vector3 directionToGoal = (goal.position - transform.position).normalized;
    float targetAngle = Mathf.Atan2(directionToGoal.x, directionToGoal.z) * Mathf.Rad2Deg;
    
    // Interpolación esférica suave (Slerp) para evitar giros instantáneos o poco naturales
    Quaternion targetRotation = Quaternion.Euler(0, targetAngle, 0);
    transform.rotation = Quaternion.Slerp(transform.rotation, targetRotation, rotationSpeed * Time.deltaTime);

    // Desplazamiento lineal constante hacia adelante
    transform.Translate(Vector3.forward * speed * Time.deltaTime);
}

```

### Fragmento Crítico en Three.js / React Three Fiber (JavaScript)
Este segmento del código dentro del hook recurrente useFrame ilustra cómo se gestiona de forma óptima el cálculo de distancias de colisión en WebGL y la normalización de la diferencia angular para evitar rotaciones infinitas del chasis:

```JavaScript
// --- EVALUACIÓN GEOMÉTRICA CON RAYCASTER OPTIMIZADO ---
// Se configuran las direcciones en el plano horizontal de Three.js (Avance estándar es el eje -Z)
const fDir = new THREE.Vector3(0, 0, -1).applyQuaternion(robot.quaternion);
const lDir = new THREE.Vector3(0, 0, -1).applyAxisAngle(new THREE.Vector3(0, 1, 0), Math.PI / 4).applyQuaternion(robot.quaternion);
const rDir = new THREE.Vector3(0, 0, -1).applyAxisAngle(new THREE.Vector3(0, 1, 0), -Math.PI / 4).applyQuaternion(robot.quaternion);

raycaster.set(robotPos, fDir);
const fHits = raycaster.intersectObjects(obstacles);
const hitForward = fHits.length > 0 && fHits[0].distance < rayLength;

// ... [Cálculo homólogo para lHits y rHits omitidos por brevedad] ...

if (hitForward) {
    // CONTROL REACTIVO DE EVASIÓN: Elección lateral dinámica basándose en la proximidad
    let turnDirection = evasionRef.current;
    if (hitRight && !hitLeft)        turnDirection = 1;   // Girar a la Izquierda (Y positivo)
    else if (hitLeft && !hitRight)   turnDirection = -1;  // Girar a la Derecha (Y negativo)
    else if (hitLeft && hitRight)    turnDirection = lHits[0].distance > rHits[0].distance ? 1 : -1;

    evasionRef.current = turnDirection;
    robot.rotation.y += turnDirection * rotationSpeed * delta; // Rotación incremental delta
} else {
    // PLANIFICACIÓN LOCAL (GOAL SEEKING): Alineación suave con el vector objetivo
    const toGoalVector = new THREE.Vector3().subVectors(goalPos, robotPos);
    const targetAngle = Math.atan2(-toGoalVector.x, -toGoalVector.z);
    
    // TRUCO MATEMÁTICO ESENCIAL: Normalizar la diferencia de ángulos entre [-PI, PI] 
    // Esto previene que el robot dé vueltas completas sobre su propio eje innecesariamente
    let angleDiff = targetAngle - robot.rotation.y;
    angleDiff = Math.atan2(Math.sin(angleDiff), Math.cos(angleDiff));
    
    // Rotar una fracción del ángulo restante amortiguado por el tiempo delta
    robot.rotation.y += angleDiff * (rotationSpeed * 0.6) * delta;
    robot.translateZ(-speed * delta); // Avanzar hacia su eje frontal local (-Z)
}
```
## Prompts utilizados
Durante las iteraciones de diseño de este software autónomo, se formularon los siguientes prompts de ingeniería:

* "Cómo puedo ajustar el script de un robot que busca la meta en Unity ya que solo gira a la derecha y se queda atrapado en una especie de loop al encontrarse con un pasillo en zigzag de paredes planas."

* "Escribe la sección de código reactivo en React Three Fiber para useFrame que tome un vector hacia una meta y oriente un mesh de manera suave utilizando atan2 y translateZ, asegurando que los rayos de visión cambien de color sin causar re-renders en React."

## Aprendizajes y dificultades
### Aprendizajes
- Navegación en Lazo Cerrado: Comprensión de las dinámicas de control basadas en ciclos de percepción-acción continua, donde el agente no planea de forma global, sino que reacciona adaptativamente a su entorno inmediato.

- Tratamiento Angular y Trigonometría: Dominio de las funciones de arcotangente generalizada (Math.atan2) y de los métodos de interpolación como Slerp o amortiguaciones angulares normalizadas para evitar singularidades geométricas u oscilaciones infinitas.

- Abstracción Multiplataforma: Capacidad de extrapolar una misma plantilla lógica y matemática desde un motor compilado y cerrado (Unity) hacia un ecosistema web declarativo guiado por estados (React Three Fiber) adaptando los sistemas de coordenadas locales.

### Dificultades
- El Problema del Mínimo Local: Al inicio, el robot poseía un solo sensor lineal y un giro estático por defecto. Esto causaba que al colisionar de frente contra paredes planas quedara atrapado en loops simétricos oscilatorios. La dificultad se resolvió expandiendo la percepción a un abanico de 3 sensores concurrentes y programando una memoria de decisión selectiva basada en la distancia de los flancos.

- Rendimiento e Hilos en WebGL: En Three.js, instanciar repetidamente objetos vectoriales en cada frame saturaba rápidamente el Garbage Collector, provocando saltos visibles en el movimiento. Se solucionó reciclando una única instancia global de Raycaster y manipulando los colores de los sensores directamente a nivel de propiedad de shader nativo.

### Mejoras futuras
- Campos Potenciales Virtuales: Cambiar la lógica discreta de if-else por fuerzas continuas donde los obstáculos repelan al robot de forma inversamente proporcional a la distancia y la meta lo atraiga.

- Controlador PID Integrado: Reemplazar las velocidades de traslación lineales fijas por un controlador Proporcional-Integral-Derivativo (PID) que desacelere el robot suavemente conforme se estrechan los pasillos o se aproxima a curvas cerradas.

## Referencias
Documentación de API Física de Unity: Physics.Raycast en Unity

Guía de optimización en bucles de animación WebGL: React Three Fiber Pitfalls and Performance (https://www.google.com/search?q=https://docs.pmnd.rs/react-three-fiber/advanced/pitfalls)

Conceptos de cinemática para robots móviles: Siegwart, R. - Introduction to Autonomous Mobile Robots (MIT Press).