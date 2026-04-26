# Taller Websockets Interaccion Visual

**Nombre del estudiante:**
* Brayan Alejandro Muñoz Pérez bmunozp@unal.edu.co
* Álvaro Andrés Romero Castro alromeroca@unal.edu.co
* Juan Camilo Lopez Bustos juclopezbu@unal.edu.co
* Alejandro Ortiz Cortes alortizco@unal.edu.co
**Fecha de entrega:** 2026-04-25

## Descripción breve
Este taller explora la implementación de WebSockets para lograr comunicación bidireccional en tiempo real entre un servidor (escrito en Python) y una aplicación cliente (Three.js/React). A diferencia de HTTP tradicional, los WebSockets mantienen una conexión TCP abierta, lo cual permite transmitir un flujo de datos constante con latencia mínima, ideal para telemetría, dashboards en vivo o control remoto.

## Implementaciones

### Python (Servidor WebSocket)
Se implementó un script utilizando `asyncio` y la librería `websockets`. El servidor emite un JSON estructurado (`{"x", "y", "color"}`) cada 0.5 segundos con coordenadas espaciales aleatorias y colores elegidos al azar. Esta arquitectura simula una transmisión continua de señales de posicionamiento.

### Three.js / React Three Fiber (Cliente)
Se construyó un cliente React que instancia la conexión al WebSocket de Python. A través de manejadores de eventos asíncronos (`socket.onmessage`), los datos se desempaquetan y se inyectan en el estado de React. Posteriormente, el hook `useFrame` intercepta estos estados y realiza una interpolación lineal suave (`lerp`) para reposicionar una geometría y actualizar su material sin saltos abruptos.

## Resultados visuales*
- ![R3F Client Reacting](./media/r3f_client.gif)

## Código relevante

**Servidor Python (`python/server.py`):**
```python
async def handler(websocket):
    while True:
        data = { "x": random.uniform(-5, 5), "y": random.uniform(-5, 5), "color": random.choice(["red", "green", "blue"]) }
        await websocket.send(json.dumps(data))
        await asyncio.sleep(0.5)
```

**Cliente Three.js (`threejs/src/App.jsx`):**
```jsx
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    setTargetPosition(new THREE.Vector3(data.x, data.y, 0));
    setColor(data.color);
  };
  
  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.position.lerp(targetPosition, delta * 5);
    }
  });
```

## Prompts utilizados
No se usaron prompts de IA generativa para la lógica base, el código se adaptó del material provisto.

## Aprendizajes y dificultades
- **Aprendizajes:** Comprendí cómo gestionar la asincronía de la conexión WebSocket dentro del ciclo de vida de React (`useEffect` con cleanup para cerrar sockets) y usar la interpolación matemática para suavizar datos discretos entrantes.
- **Dificultades:** Sincronizar el reloj del servidor (envíos cada 0.5s) con los 60 cuadros por segundo de Three.js requirió usar `lerp` para que el movimiento no se viera entrecortado ("stuttering").
