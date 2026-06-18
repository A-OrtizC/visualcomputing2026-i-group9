// useDronePersistence.js
// Hook que encapsula toda la lógica de lectura y escritura del dron en Firebase.
// - Lee la posición/altitud guardada al montar (para restaurar el dron).
// - Expone savePosition() para guardar bajo demanda (llamado cada 3 s desde App).

import { useEffect, useCallback, useState } from "react";
import { ref, set, get } from "firebase/database";
import { db } from "./firebaseConfig";

const DRONE_PATH = "dron/posicion"; // ruta en Realtime Database

/**
 * Retorna:
 *  savedPos  → { x, y, z, rotY } | null  (posición recuperada de Firebase)
 *  savePosition(pos) → guarda la posición actual en Firebase
 *  status    → 'loading' | 'ready' | 'error'
 */
export function useDronePersistence() {
  const [savedPos, setSavedPos] = useState(null);
  const [status, setStatus] = useState("loading");

  // Al montar: leer posición guardada
  useEffect(() => {
    get(ref(db, DRONE_PATH))
      .then((snapshot) => {
        if (snapshot.exists()) {
          setSavedPos(snapshot.val()); // { x, y, z, rotY }
        }
        setStatus("ready");
      })
      .catch((err) => {
        console.error("[Firebase] Error al leer posición del dron:", err);
        setStatus("error");
      });
  }, []);

  // Guardar posición en Firebase
  const savePosition = useCallback((pos) => {
    set(ref(db, DRONE_PATH), pos)
      .then(() => console.log("[Firebase] Posición del dron guardada:", pos))
      .catch((err) => console.error("[Firebase] Error al guardar:", err));
  }, []);

  return { savedPos, savePosition, status };
}
