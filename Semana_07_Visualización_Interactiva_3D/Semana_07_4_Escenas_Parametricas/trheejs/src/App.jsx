import React, { useMemo } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Stars } from '@react-three/drei'
import { useControls } from 'leva'

// 1. Datos Estructurados (simulando un JSON o CSV)
const rawData = [
  { id: 1, position: [0, 0, 0], value: 2, type: 'box' },
  { id: 2, position: [3, 1, -2], value: 1.5, type: 'sphere' },
  { id: 3, position: [-3, 2, 1], value: 3, type: 'box' },
  { id: 4, position: [0, 4, 2], value: 1, type: 'sphere' },
];

function DataObject({ data, globalScale, wireframe }) {
  const { position, value, type } = data;
  
  // Condicional para decidir qué geometría instanciar
  return (
    <mesh position={position} scale={value * globalScale}>
      {type === 'box' ? (
        <boxGeometry args={[1, 1, 1]} />
      ) : (
        <sphereGeometry args={[0.7, 32, 32]} />
      )}
      <meshStandardMaterial 
        color={type === 'box' ? "#4ade80" : "#60a5fa"} 
        wireframe={wireframe} 
      />
    </mesh>
  )
}

export default function Scene() {
  // 2. Controles Dinámicos con Leva
  const { scale, wireframe, background } = useControls({
    scale: { value: 1, min: 0.1, max: 5, step: 0.1 },
    wireframe: false,
    background: '#111111'
  })

  return (
    <div style={{ width: '100vw', height: '100vh', background: background }}>
      <Canvas camera={{ position: [10, 10, 10], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} />
        <Stars />
        
        {/* 3. Mapeo de datos para generar la escena */}
        {rawData.map((item) => (
          <DataObject 
            key={item.id} 
            data={item} 
            globalScale={scale} 
            wireframe={wireframe} 
          />
        ))}

        <OrbitControls />
      </Canvas>
    </div>
  )
}