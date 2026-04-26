import React, { useRef, useEffect, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

function Agent() {
  const meshRef = useRef();
  
  // Estado objetivo recibido por WebSocket
  const [targetPosition, setTargetPosition] = useState(new THREE.Vector3(0, 0, 0));
  const [color, setColor] = useState('white');

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8765');

    socket.onopen = () => console.log('✅ Conectado al servidor WebSocket');
    
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        // El servidor envía: { x, y, color }
        // Actualizamos el objetivo. Mantenemos Z en 0 para visualización 2D en plano
        setTargetPosition(new THREE.Vector3(data.x, data.y, 0));
        setColor(data.color);
      } catch (error) {
        console.error("Error parseando el mensaje WebSocket:", error);
      }
    };

    socket.onclose = () => console.log('❌ Desconectado del servidor WebSocket');

    // Cleanup: cerrar la conexión cuando el componente se desmonte
    return () => socket.close();
  }, []);

  // Animación suave (Interpolación Lineal - LERP) hacia la posición objetivo
  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.position.lerp(targetPosition, delta * 5);
      
      // Añadimos una pequeña rotación decorativa
      meshRef.current.rotation.x += delta * 0.5;
      meshRef.current.rotation.y += delta * 0.5;
    }
  });

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[0.5, 32, 32]} />
      <meshStandardMaterial color={color} roughness={0.3} metalness={0.2} />
    </mesh>
  );
}

export default function App() {
  return (
    <div style={{ width: '100vw', height: '100vh', margin: 0, backgroundColor: '#1a1a1a' }}>
      <Canvas camera={{ position: [0, 0, 10], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[5, 5, 5]} intensity={1} />
        <gridHelper args={[20, 20]} rotation={[Math.PI / 2, 0, 0]} />
        <Agent />
        <OrbitControls />
      </Canvas>
    </div>
  );
}
