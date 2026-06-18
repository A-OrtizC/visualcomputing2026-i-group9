// DronExplorador.jsx
// Dron explorador autónomo con persistencia Firebase.
// Vuela en un patrón de exploración ondulante sobre un arrecife bioluminiscente,
// guardando su posición + altitud + rotación cada 3 segundos en Firebase Realtime DB.
//
// Objeto COMPLETAMENTE DISTINTO al rover terrestre usado anteriormente:
// - Se desplaza en 3 ejes (X, Y, Z) en vez de solo sobre el plano del suelo.
// - Navega por waypoints en el aire, no evita obstáculos por raycast.
// - Tiene hélices que giran, luces de navegación parpadeantes y un haz de escaneo.

import React, { useRef, useEffect, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import { Trail } from "@react-three/drei";
import * as THREE from "three";
import { useControls } from "leva";

// ─── Límites del área de vuelo ────────────────────────────────────────────────
const FLIGHT_MIN_Y = 2.5;
const FLIGHT_MAX_Y = 9;
const AREA_RADIUS  = 13;

// Waypoints de exploración: el dron los visita en bucle
const WAYPOINTS = [
  new THREE.Vector3(  8,  4, -8),
  new THREE.Vector3( -9,  6, -10),
  new THREE.Vector3( -10, 3,  6),
  new THREE.Vector3(  6,  7,  9),
  new THREE.Vector3(  0,  5,  0),
];

// ─── Hélice individual con giro continuo ──────────────────────────────────────
const Helice = ({ position }) => {
  const ref = useRef();
  useFrame((_, delta) => {
    if (ref.current) ref.current.rotation.y += delta * 28; // giro rápido
  });
  return (
    <group position={position}>
      <mesh position={[0, 0.04, 0]}>
        <cylinderGeometry args={[0.05, 0.05, 0.08, 8]} />
        <meshStandardMaterial color="#222" metalness={0.8} />
      </mesh>
      <mesh ref={ref} position={[0, 0.08, 0]}>
        <boxGeometry args={[0.55, 0.015, 0.06]} />
        <meshStandardMaterial color="#1a1a1a" roughness={0.4} transparent opacity={0.85} />
      </mesh>
    </group>
  );
};

// ─── Dron explorador ───────────────────────────────────────────────────────────
/**
 * Props:
 *  savedPos      – { x, y, z, rotY } leído de Firebase (puede ser null)
 *  savePosition  – función que guarda posición en Firebase
 */
const DronExplorador = ({ savedPos, savePosition }) => {
  const droneRef     = useRef();
  const scanLightRef = useRef();
  const navLightRef  = useRef();
  const waypointIdx   = useRef(0);
  const saveTimerRef  = useRef(0);
  const blinkTimerRef = useRef(0);
  const bobOffset      = useRef(Math.random() * Math.PI * 2);

  const [{ velocidad, altitudOscilacion, alcanceEscaneo }] = useControls(() => ({
    velocidad:          { value: 2.2, min: 0.5, max: 5,  label: "Velocidad Dron"     },
    altitudOscilacion:  { value: 0.4, min: 0,   max: 1.2, label: "Oscilación Vuelo"  },
    alcanceEscaneo:      { value: 3.5, min: 1,   max: 6,  label: "Alcance Escáner"    },
  }));

  // ── Restaurar posición desde Firebase al montar ───────────────────────────
  useEffect(() => {
    if (savedPos && droneRef.current) {
      droneRef.current.position.set(savedPos.x, savedPos.y, savedPos.z);
      droneRef.current.rotation.y = savedPos.rotY ?? 0;
      console.log("[Firebase] Posición del dron restaurada:", savedPos);
    }
  }, [savedPos]);

  useFrame((state, delta) => {
    if (!droneRef.current) return;
    const drone = droneRef.current;
    const t = state.clock.elapsedTime;

    // ── Guardar posición cada 3 segundos ─────────────────────────────────
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

    // ── Navegación autónoma por waypoints (vuelo libre en 3D) ─────────────
    const target = WAYPOINTS[waypointIdx.current];
    const toTarget = new THREE.Vector3().subVectors(target, drone.position);
    const dist = toTarget.length();

    if (dist < 0.6) {
      waypointIdx.current = (waypointIdx.current + 1) % WAYPOINTS.length;
    } else {
      toTarget.normalize();
      drone.position.addScaledVector(toTarget, velocidad * delta);

      // Orientar el dron hacia la dirección de vuelo (yaw)
      const targetYaw = Math.atan2(toTarget.x, toTarget.z);
      let diff = targetYaw - drone.rotation.y;
      diff = Math.atan2(Math.sin(diff), Math.cos(diff));
      drone.rotation.y += diff * 3 * delta;

      // Inclinación de "pitch" sutil hacia adelante al volar
      drone.rotation.x = THREE.MathUtils.lerp(drone.rotation.x, -toTarget.y * 0.4, 4 * delta);
    }

    // Oscilación de vuelo (efecto "hover" natural) + límites de altitud
    const bob = Math.sin(t * 1.6 + bobOffset.current) * altitudOscilacion * 0.3;
    drone.position.y = THREE.MathUtils.clamp(drone.position.y + bob * delta, FLIGHT_MIN_Y, FLIGHT_MAX_Y);

    // Mantenerse dentro del área circular de vuelo
    const radial = Math.sqrt(drone.position.x ** 2 + drone.position.z ** 2);
    if (radial > AREA_RADIUS) {
      const scale = AREA_RADIUS / radial;
      drone.position.x *= scale;
      drone.position.z *= scale;
    }

    // ── Luces de navegación parpadeantes ───────────────────────────────────
    blinkTimerRef.current += delta;
    if (navLightRef.current) {
      const blink = (Math.sin(blinkTimerRef.current * 6) + 1) / 2;
      navLightRef.current.intensity = 0.4 + blink * 1.6;
    }

    // Haz de escáner apuntando hacia abajo
    if (scanLightRef.current) {
      scanLightRef.current.intensity = 2 + Math.sin(t * 3) * 0.6;
      scanLightRef.current.distance = alcanceEscaneo;
    }
  });

  return (
    <group ref={droneRef} position={[0, 5, 0]}>
      {/* Estela de vuelo */}
      <Trail width={0.5} length={28} color="#22e0ff" attenuation={(tt) => tt * tt}>
        {/* ── Cuerpo central del dron (forma aerodinámica, no caja como el rover) ── */}
        <mesh castShadow>
          <octahedronGeometry args={[0.32, 1]} />
          <meshStandardMaterial color="#0d1f2e" roughness={0.25} metalness={0.85} />
        </mesh>
      </Trail>

      {/* Núcleo emisivo central */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[0.14, 16, 16]} />
        <meshStandardMaterial color="#00e5ff" emissive="#00e5ff" emissiveIntensity={1.4} />
      </mesh>

      {/* Brazos en X con hélices en las puntas */}
      {[
        { ang: Math.PI / 4,      },
        { ang: -Math.PI / 4,     },
        { ang: (3 * Math.PI) / 4 },
        { ang: -(3 * Math.PI) / 4 },
      ].map(({ ang }, i) => {
        const armLen = 0.55;
        const x = Math.cos(ang) * armLen;
        const z = Math.sin(ang) * armLen;
        return (
          <group key={i}>
            <mesh position={[x / 2, 0, z / 2]} rotation={[0, -ang, 0]}>
              <boxGeometry args={[armLen, 0.05, 0.07]} />
              <meshStandardMaterial color="#1c2733" metalness={0.7} roughness={0.4} />
            </mesh>
            <Helice position={[x, 0.05, z]} />
          </group>
        );
      })}

      {/* Luz de navegación intermitente (roja, en la cola) */}
      <pointLight ref={navLightRef} position={[0, 0.1, 0.4]} color="#ff2244" intensity={1} distance={2.5} />
      <mesh position={[0, 0.1, 0.4]}>
        <sphereGeometry args={[0.05, 8, 8]} />
        <meshStandardMaterial color="#ff2244" emissive="#ff2244" emissiveIntensity={1.5} />
      </mesh>

      {/* Haz de escáner hacia el terreno */}
      <pointLight ref={scanLightRef} position={[0, -0.3, 0]} color="#22e0ff" intensity={2} distance={3.5} />
      <mesh position={[0, -0.2, 0]} rotation={[Math.PI, 0, 0]}>
        <coneGeometry args={[0.18, 0.4, 12, 1, true]} />
        <meshBasicMaterial color="#22e0ff" transparent opacity={0.18} side={THREE.DoubleSide} />
      </mesh>

      {/* Cámara de sensores frontal */}
      <mesh position={[0, -0.05, 0.25]}>
        <sphereGeometry args={[0.08, 12, 12]} />
        <meshStandardMaterial color="#111" emissive="#00ffaa" emissiveIntensity={0.6} roughness={0.1} />
      </mesh>
    </group>
  );
};

export default DronExplorador;
