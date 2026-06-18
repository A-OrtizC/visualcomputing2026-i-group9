# Taller Guardado Persistencia Firebase Unity Threejs

**Nombre del estudiante:** [Tu nombre aquí]
**Fecha de entrega:** [Fecha de entrega aquí]
**Carpeta del taller:** `semana_15_4_guardado_persistencia_firebase_unity_threejs`

---

## Descripción breve

Este taller implementa un sistema de persistencia de datos en la nube usando **Firebase Realtime Database**, integrado en una escena interactiva de **Three.js + React (react-three-fiber)**.

El escenario es un **arrecife bioluminiscente nocturno** explorado por un **dron autónomo volador**. El dron navega en 3D visitando puntos de interés (waypoints), y cada 3 segundos guarda su posición (x, y, z) y rotación en Firebase. Al recargar la página, el dron recupera automáticamente la última posición guardada y continúa la exploración desde ahí, en lugar de reiniciar siempre en el punto de partida.

---

## Implementaciones

### Three.js + Firebase Realtime Database

**Flujo de persistencia:**

```
[Dron vuela en 3D] → cada 3 s → savePosition() → Firebase Realtime DB
                                                          │
[Recarga de página] → useDronePersistence() → get() de Firebase → dron se reposiciona
```

**Estructura de datos guardada en Firebase (`dron/posicion`):**
```json
{
  "x": 5.214,
  "y": 6.087,
  "z": -3.402,
  "rotY": 0.7854
}
```

**Archivos principales del proyecto:**

| Archivo | Rol |
|---|---|
| `src/firebase/firebaseConfig.js` | Inicialización del SDK de Firebase (modular v11) |
| `src/firebase/useDronePersistence.js` | Hook: lee la posición al montar, expone `savePosition()` |
| `src/components/DronExplorador.jsx` | Dron autónomo: vuelo por waypoints, hélices, luces, guardado cada 3 s |
| `src/App.jsx` | Escena del arrecife bioluminiscente + HUD de estado de Firebase |

**Por qué se cambió el objeto de la entrega anterior:**

La versión anterior usaba un rover terrestre que se desplazaba solo sobre el plano XZ evitando obstáculos por raycast. En esta versión se reemplazó por un **dron volador** que:
- Se mueve libremente en los 3 ejes (X, Y, Z), por lo que la persistencia ahora también debe capturar la altitud (Y), no solo una posición sobre el suelo.
- Navega por waypoints en lugar de evitar obstáculos por sensores láser.
- Vive en un escenario completamente distinto (arrecife submarino nocturno en vez de desierto marciano).

---

## Resultados visuales

> Las capturas y GIFs deben colocarse en la carpeta `media/` (al nivel de la carpeta `threejs/`) y referenciarse aquí. Mínimo 2 capturas/GIFs para esta implementación:

```
![Vista general del arrecife bioluminiscente](../media/escena_general.png)
![Dron explorador con HUD de Firebase activo](../media/firebase_hud.png)
![Posición restaurada al recargar la página](../media/restauracion_posicion.gif)
![Datos guardados en Firebase Console](../media/firebase_console.png)
```

---

## Código relevante

### Hook de persistencia (`useDronePersistence.js`)

```js
// Lee la última posición al montar el componente
useEffect(() => {
  get(ref(db, "dron/posicion")).then((snapshot) => {
    if (snapshot.exists()) setSavedPos(snapshot.val());
    setStatus("ready");
  });
}, []);

// Guarda la posición actual bajo demanda
const savePosition = useCallback((pos) => {
  set(ref(db, "dron/posicion"), pos);
}, []);
```

### Guardado automático cada 3 s (`DronExplorador.jsx`)

```js
saveTimerRef.current += delta;
if (saveTimerRef.current >= 3) {
  saveTimerRef.current = 0;
  savePosition({
    x:    parseFloat(drone.position.x.toFixed(3)),
    y:    parseFloat(drone.position.y.toFixed(3)),
    z:    parseFloat(drone.position.z.toFixed(3)),
    rotY: parseFloat(drone.rotation.y.toFixed(4)),
  });
}
```

### Restauración de posición al montar (`DronExplorador.jsx`)

```js
useEffect(() => {
  if (savedPos && droneRef.current) {
    droneRef.current.position.set(savedPos.x, savedPos.y, savedPos.z);
    droneRef.current.rotation.y = savedPos.rotY ?? 0;
  }
}, [savedPos]);
```

---

## Prompts utilizados

- Se utilizó IA generativa para diseñar el nuevo objeto (dron explorador) y el nuevo escenario (arrecife bioluminiscente), reemplazando completamente el rover y el desierto marciano de la entrega previa, manteniendo la misma arquitectura de persistencia Firebase.
- Prompt base: *"Reemplaza el objeto del rover por un dron volador completamente distinto, con su propio escenario, e integra el guardado/lectura de posición en Firebase cada 3 segundos."*

---

## Aprendizajes y dificultades

**Aprendizajes:**
- Firebase Realtime Database con el SDK modular (`firebase/app`, `firebase/database`) usa funciones puras (`ref`, `get`, `set`) en lugar de métodos encadenados como en versiones antiguas del SDK.
- Separar la lógica de Firebase en un hook personalizado (`useDronePersistence`) mantiene el componente 3D limpio y reutilizable.
- Para un objeto que se mueve en 3 ejes (a diferencia de un objeto terrestre que solo usa X y Z), es importante persistir también la altitud (Y), ya que de lo contrario el objeto "caería" o "flotaría" de forma incorrecta al restaurar la escena.
- `useEffect` con dependencia en `savedPos` es la forma correcta de aplicar la posición restaurada, porque la lectura de Firebase es asíncrona y llega después del primer render.

**Dificultades:**
- Es necesario asegurarse de que las **reglas de Realtime Database** permitan lectura y escritura (en desarrollo se usa modo abierto; en producción se deben restringir con autenticación).
- Al cambiar de un objeto que se mueve en el plano (rover) a uno que vuela en 3D (dron), hubo que ajustar la estructura del JSON guardado para incluir la altitud, y validar los límites de vuelo para que el dron no se "pierda" fuera del área visible tras restaurar una posición antigua.

---

## Configuración de Firebase

1. Crear un proyecto en [Firebase Console](https://console.firebase.google.com/)
2. Habilitar **Realtime Database** (modo de prueba para desarrollo)
3. Copiar las credenciales del proyecto en `src/firebase/firebaseConfig.js`
4. Instalar dependencias y correr el proyecto:

```bash
npm install
npm run dev
```

### Reglas de Realtime Database (entorno de desarrollo)
```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

> ⚠️ Estas reglas son solo para desarrollo. En producción se deben restringir con autenticación de usuarios.

---

## Estructura del repositorio

```
semana_15_4_guardado_persistencia_firebase_unity_threejs/
├── python/
├── unity/
│   └── Assets/Scripts/FirebaseManager.cs
├── threejs/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── index.css
│       ├── App.jsx
│       ├── App.css
│       ├── firebase/
│       │   ├── firebaseConfig.js
│       │   └── useDronePersistence.js
│       └── components/
│           └── DronExplorador.jsx
├── media/
│   ├── escena_general.png
│   ├── firebase_hud.png
│   ├── restauracion_posicion.gif
│   └── firebase_console.png
└── README.md
```
