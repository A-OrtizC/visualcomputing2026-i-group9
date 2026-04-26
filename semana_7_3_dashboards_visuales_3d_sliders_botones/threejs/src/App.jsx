import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { useControls } from 'leva';

function InteractiveScene() {
  const meshRef = useRef();

  // Configuración del panel de control Leva
  const { boxScale, boxColor, autoRotate, lightIntensity, lightColor } = useControls('Controles 3D', {
    boxScale: { value: 1.5, min: 0.5, max: 5, step: 0.1, label: 'Escala' },
    boxColor: { value: '#ff4081', label: 'Color Cubo' },
    autoRotate: { value: false, label: 'Rotar Automático' },
    lightIntensity: { value: 2, min: 0, max: 10, step: 0.1, label: 'Intensidad Luz' },
    lightColor: { value: '#ffffff', label: 'Color Luz' }
  });

  // Animación condicional
  useFrame((state, delta) => {
    if (autoRotate && meshRef.current) {
      meshRef.current.rotation.x += delta;
      meshRef.current.rotation.y += delta;
    }
  });

  return (
    <>
      <ambientLight intensity={0.3} />
      <directionalLight position={[5, 5, 5]} intensity={lightIntensity} color={lightColor} />
      
      <mesh ref={meshRef} scale={boxScale}>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial color={boxColor} roughness={0.3} metalness={0.7} />
      </mesh>
      
      <OrbitControls makeDefault />
    </>
  );
}

export default function App() {
  return (
    <div style={{ width: '100vw', height: '100vh', margin: 0, overflow: 'hidden', backgroundColor: '#1a1a1a' }}>
      <Canvas camera={{ position: [0, 2, 5], fov: 50 }}>
        <InteractiveScene />
      </Canvas>
    </div>
  );
}
