// App.jsx — Taller 63: Guardado y Persistencia con Firebase
// Escenario: arrecife bioluminiscente nocturno con un dron explorador autónomo.
// Integra Firebase Realtime Database para guardar/recuperar la posición del dron
// (x, y, z, rotación) cada 3 segundos.

import React, { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Stars, Sparkles } from "@react-three/drei";
import * as THREE from "three";

// Componentes propios
import DronExplorador from "./components/DronExplorador";
import { useDronePersistence } from "./firebase/useDronePersistence";

// ─────────────────────────────────────────────────────────────
// SUELO MARINO ONDULANTE
// ─────────────────────────────────────────────────────────────
const SeaFloor = () => {
  const meshRef = useRef();
  const geometry = useMemo(() => new THREE.PlaneGeometry(40, 40, 60, 60), []);

  useFrame(({ clock }) => {
    if (!meshRef.current) return;
    const pos = meshRef.current.geometry.attributes.position;
    const t = clock.elapsedTime;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const y = pos.getY(i);
      const wave =
        Math.sin(x * 0.3 + t * 0.4) * 0.25 +
        Math.cos(y * 0.25 + t * 0.3) * 0.25;
      pos.setZ(i, wave);
    }
    pos.needsUpdate = true;
    meshRef.current.geometry.computeVertexNormals();
  });

  return (
    <mesh
      ref={meshRef}
      geometry={geometry}
      rotation={[-Math.PI / 2, 0, 0]}
      position={[0, -0.4, 0]}
      receiveShadow
    >
      {/* Color de suelo más claro para que se aprecie el relieve ondulante */}
      <meshStandardMaterial color="#0a3a5c" roughness={0.6} metalness={0.25} />
    </mesh>
  );
};

// ─────────────────────────────────────────────────────────────
// CORALES BIOLUMINISCENTES
// ─────────────────────────────────────────────────────────────
const coralColors = ["#00e5ff", "#ff2fb0", "#7cff4d", "#ffd23f", "#9d4dff"];

const CoralCluster = ({ position, scale = 1, colorIdx = 0 }) => {
  const ref = useRef();
  useFrame(({ clock }) => {
    if (ref.current) {
      const pulse = 1.1 + Math.sin(clock.elapsedTime * 1.5 + position[0]) * 0.4;
      ref.current.children.forEach((c) => {
        if (c.material?.emissiveIntensity !== undefined) {
          c.material.emissiveIntensity = pulse;
        }
      });
    }
  });

  const color = coralColors[colorIdx % coralColors.length];
  const branches = useMemo(
    () =>
      Array.from({ length: 5 }, () => ({
        h: 0.6 + Math.random() * 1.4,
        x: (Math.random() - 0.5) * 0.6,
        z: (Math.random() - 0.5) * 0.6,
        r: Math.random() * Math.PI,
      })),
    []
  );

  return (
    <group ref={ref} position={position} scale={scale}>
      {branches.map((b, i) => (
        <mesh key={i} position={[b.x, b.h / 2, b.z]} rotation={[0, b.r, 0.15]}>
          <coneGeometry args={[0.12, b.h, 6]} />
          {/* Color base más claro + mayor emisión para que el coral se vea mejor */}
          <meshStandardMaterial
            color="#1a2a3a"
            emissive={color}
            emissiveIntensity={1.1}
            roughness={0.4}
          />
        </mesh>
      ))}
      {/* Luz puntual propia de cada coral para iluminar su entorno */}
      <pointLight color={color} intensity={1.2} distance={4} position={[0, 0.8, 0]} />
    </group>
  );
};

// ─────────────────────────────────────────────────────────────
// FORMACIONES ROCOSAS SUBMARINAS
// ─────────────────────────────────────────────────────────────
const RockFormation = ({ position, scale = 1 }) => (
  <group position={position} scale={scale}>
    <mesh castShadow receiveShadow>
      <icosahedronGeometry args={[1.2, 0]} />
      <meshStandardMaterial color="#33536a" roughness={0.85} />
    </mesh>
    <mesh position={[0.6, 0.6, 0.3]} scale={0.6}>
      <icosahedronGeometry args={[1, 0]} />
      <meshStandardMaterial color="#2c4a5e" roughness={0.85} />
    </mesh>
  </group>
);

// ─────────────────────────────────────────────────────────────
// MEDUSAS FLOTANTES
// ─────────────────────────────────────────────────────────────
const Jellyfish = ({ position }) => {
  const ref = useRef();
  const t0 = useRef(Math.random() * Math.PI * 2);
  useFrame(({ clock }) => {
    if (!ref.current) return;
    const t = clock.elapsedTime + t0.current;
    ref.current.position.y = position[1] + Math.sin(t * 0.6) * 0.6;
    ref.current.scale.setScalar(0.9 + Math.sin(t * 3) * 0.08);
  });
  return (
    <group ref={ref} position={position}>
      <mesh>
        <sphereGeometry args={[0.35, 16, 16, 0, Math.PI * 2, 0, Math.PI / 1.7]} />
        <meshStandardMaterial
          color="#ffb3ff"
          emissive="#ff5fe0"
          emissiveIntensity={1.2}
          transparent
          opacity={0.75}
        />
      </mesh>
      {[0, 1, 2, 3, 4].map((i) => (
        <mesh key={i} position={[Math.cos(i * 1.3) * 0.15, -0.4, Math.sin(i * 1.3) * 0.15]}>
          <cylinderGeometry args={[0.015, 0.01, 0.7, 4]} />
          <meshStandardMaterial color="#ff8fe8" transparent opacity={0.6} />
        </mesh>
      ))}
      {/* Pequeño resplandor propio para que destaque en la oscuridad */}
      <pointLight color="#ff5fe0" intensity={0.8} distance={3} />
    </group>
  );
};

// ─────────────────────────────────────────────────────────────
// ESTACIÓN DE INVESTIGACIÓN SUMERGIDA
// ─────────────────────────────────────────────────────────────
const ResearchStation = () => {
  const beaconRef = useRef();
  useFrame(({ clock }) => {
    if (beaconRef.current) {
      beaconRef.current.position.y = 2.4 + Math.sin(clock.elapsedTime * 2) * 0.1;
    }
  });
  return (
    <group position={[0, 0, -2]}>
      <mesh position={[0, 1, 0]} castShadow>
        <cylinderGeometry args={[1, 1.2, 1.6, 8]} />
        <meshStandardMaterial color="#7e8fa0" metalness={0.5} roughness={0.35} />
      </mesh>
      <mesh position={[0, 1.9, 0]}>
        <sphereGeometry args={[0.7, 16, 16]} />
        <meshStandardMaterial color="#cfe8ff" transparent opacity={0.4} roughness={0.1} />
      </mesh>
      <mesh ref={beaconRef} position={[0, 2.4, 0]}>
        <sphereGeometry args={[0.2, 12, 12]} />
        <meshStandardMaterial color="#fff7c0" emissive="#ffe680" emissiveIntensity={1.8} />
      </mesh>
      {/* Luz principal de la estación, más intensa y de mayor alcance */}
      <pointLight position={[0, 1.5, 0]} color="#9fdfff" intensity={5} distance={14} />
    </group>
  );
};

// ─────────────────────────────────────────────────────────────
// HUD de estado Firebase (overlay HTML)
// ─────────────────────────────────────────────────────────────
const FirebaseStatusHUD = ({ status, savedPos }) => {
  const statusColor =
    status === "ready" ? "#00ff88" : status === "error" ? "#ff4444" : "#ffcc00";
  const statusLabel =
    status === "ready" ? "CONECTADO" : status === "error" ? "ERROR" : "CARGANDO…";

  return (
    <div
      style={{
        position: "absolute",
        top: 16,
        left: 16,
        fontFamily: "monospace",
        fontSize: 11,
        color: "#cde6ff",
        background: "rgba(2,10,20,0.6)",
        border: "1px solid #22e0ff33",
        borderRadius: 6,
        padding: "10px 14px",
        lineHeight: 1.7,
        pointerEvents: "none",
        minWidth: 240,
        backdropFilter: "blur(2px)",
      }}
    >
      <div style={{ color: "#22e0ff", fontWeight: "bold", letterSpacing: 1, marginBottom: 4 }}>
        🔥 FIREBASE REALTIME DB — DRON
      </div>
      <div>
        Estado: <span style={{ color: statusColor, fontWeight: "bold" }}>● {statusLabel}</span>
      </div>
      {savedPos ? (
        <>
          <div style={{ color: "#8db3cc", marginTop: 4 }}>Última posición restaurada:</div>
          <div>X: <span style={{ color: "#7cffb2" }}>{savedPos.x.toFixed(2)}</span></div>
          <div>Y (altitud): <span style={{ color: "#7cffb2" }}>{savedPos.y.toFixed(2)}</span></div>
          <div>Z: <span style={{ color: "#7cffb2" }}>{savedPos.z.toFixed(2)}</span></div>
          <div>RotY: <span style={{ color: "#7cffb2" }}>{((savedPos.rotY ?? 0) * 57.29).toFixed(1)}°</span></div>
        </>
      ) : (
        <div style={{ color: "#5a7186" }}>Sin datos previos en DB</div>
      )}
      <div style={{ marginTop: 6, color: "#3d566b" }}>Guardado automático cada 3 s</div>
    </div>
  );
};

// ─────────────────────────────────────────────────────────────
// COMPONENTE RAÍZ
// ─────────────────────────────────────────────────────────────
export default function App() {
  // Hook de persistencia Firebase para el dron
  const { savedPos, savePosition, status } = useDronePersistence();

  // Posiciones fijas (memorizadas) para corales, rocas y medusas
  const corals = useMemo(
    () => [
      { p: [4, -0.3, 3], s: 1.1, c: 0 },
      { p: [-5, -0.35, 5], s: 0.9, c: 1 },
      { p: [6, -0.3, -6], s: 1.3, c: 2 },
      { p: [-7, -0.3, -4], s: 1, c: 3 },
      { p: [2, -0.35, -9], s: 0.8, c: 4 },
      { p: [-3, -0.3, 8], s: 1.2, c: 2 },
      { p: [9, -0.3, 1], s: 0.9, c: 0 },
    ],
    []
  );

  const rocks = useMemo(
    () => [
      { p: [7, 0.4, 7], s: 0.9 },
      { p: [-8, 0.3, -7], s: 1.2 },
      { p: [-4, 0.35, -10], s: 0.7 },
      { p: [8, 0.4, -3], s: 1 },
    ],
    []
  );

  const jellies = useMemo(
    () => [
      [3, 5, 2],
      [-4, 6.5, -3],
      [6, 7, -7],
      [-7, 5.5, 4],
    ],
    []
  );

  return (
    <div style={{ width: "100vw", height: "100vh", background: "#010810", position: "relative" }}>
      <Canvas camera={{ position: [0, 10, 16], fov: 55 }} shadows style={{ width: "100%", height: "100%" }}>
        {/* Ambiente nocturno submarino — fondo y niebla aclarados ligeramente */}
        <color attach="background" args={["#06203a"]} />
        <fog attach="fog" args={["#06203a", 14, 42]} />
        <Stars radius={80} depth={40} count={2500} factor={4} saturation={0} fade speed={0.3} />

        {/* Luces generales mucho más intensas para apreciar formas y materiales */}
        <ambientLight intensity={0.55} color="#2a5d85" />
        <directionalLight
          position={[6, 14, 6]}
          intensity={1.4}
          color="#aee2ff"
          castShadow
        />
        <hemisphereLight skyColor="#3a78a8" groundColor="#072233" intensity={0.7} />
        {/* Luz de relleno frontal para que la cámara orbital siempre vea algo iluminado */}
        <pointLight position={[0, 8, 14]} color="#bfe6ff" intensity={1.2} distance={30} />

        {/* Partículas suspendidas tipo plancton, más brillantes */}
        <Sparkles count={150} scale={[26, 8, 26]} size={3} speed={0.3} color="#bfeeff" opacity={0.85} />

        <SeaFloor />
        <ResearchStation />

        {corals.map((c, i) => (
          <CoralCluster key={i} position={c.p} scale={c.s} colorIdx={c.c} />
        ))}
        {rocks.map((r, i) => (
          <RockFormation key={i} position={r.p} scale={r.s} />
        ))}
        {jellies.map((p, i) => (
          <Jellyfish key={i} position={p} />
        ))}

        {/* Dron explorador con persistencia Firebase */}
        <DronExplorador savedPos={savedPos} savePosition={savePosition} />

        <OrbitControls maxPolarAngle={Math.PI / 1.9} minDistance={5} maxDistance={35} />
      </Canvas>

      {/* HUD de estado Firebase */}
      <FirebaseStatusHUD status={status} savedPos={savedPos} />
    </div>
  );
}