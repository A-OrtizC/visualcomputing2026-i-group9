import React from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'

export default function App() {
  return (
    <div style={{ width: '100vw', height: '100vh', display: 'flex' }}>
      {/* Escena 1: Visualización de Z-Buffer con meshDepthMaterial */}
      <div style={{ flex: 1, borderRight: '2px solid white' }}>
        <h2 style={{ position: 'absolute', color: 'white', zIndex: 10, padding: '10px' }}>Depth Material</h2>
        <Canvas camera={{ position: [0, 0, 5], near: 1, far: 8 }}>
          <OrbitControls />
          <mesh position={[0, 0, 1]}>
            <boxGeometry args={[1, 1, 1]} />
            <meshDepthMaterial />
          </mesh>
          <mesh position={[0.5, 0.5, -1]}>
            <sphereGeometry args={[0.8, 32, 32]} />
            <meshDepthMaterial />
          </mesh>
        </Canvas>
      </div>

      {/* Escena 2: Simulación de Z-Fighting */}
      <div style={{ flex: 1 }}>
        <h2 style={{ position: 'absolute', color: 'white', zIndex: 10, padding: '10px' }}>Z-Fighting (Gira la cámara)</h2>
        <Canvas camera={{ position: [0, 2, 5], near: 0.1, far: 10000 }}>
          <OrbitControls />
          <ambientLight intensity={1} />
          {/* Plano 1 */}
          <mesh position={[0, 0, 0]} rotation={[-Math.PI / 2, 0, 0]}>
            <planeGeometry args={[5, 5]} />
            <meshBasicMaterial color="red" side={THREE.DoubleSide} depthTest={true} />
          </mesh>
          {/* Plano 2 coplanar para provocar el glitch */}
          <mesh position={[0, 0.00001, 0]} rotation={[-Math.PI / 2, 0, 0]}>
            <planeGeometry args={[5, 5]} />
            <meshBasicMaterial color="blue" side={THREE.DoubleSide} depthTest={true} />
          </mesh>
        </Canvas>
      </div>
    </div>
  )
}