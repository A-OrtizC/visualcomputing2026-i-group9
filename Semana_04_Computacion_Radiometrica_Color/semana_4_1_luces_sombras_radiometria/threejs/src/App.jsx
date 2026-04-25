import React, { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, useHelper } from '@react-three/drei'
import * as THREE from 'three'
import { useControls } from 'leva'

// Componente para una esfera que gira levemente
const RotatingSphere = ({ position, materialArgs }) => {
  const meshRef = useRef()
  useFrame((state, delta) => {
    meshRef.current.rotation.y += delta * 0.5
  })
  return (
    <mesh ref={meshRef} position={position} castShadow receiveShadow>
      <sphereGeometry args={[1, 32, 32]} />
      <meshPhysicalMaterial {...materialArgs} />
    </mesh>
  )
}

const Scene = () => {
  // Controles UI con Leva
  const { dirInt, dirColor, pointInt, pointColor, ambientInt } = useControls({
    LuzDireccional: { folder: true },
    dirInt: { value: 2.5, min: 0, max: 5, step: 0.1, label: 'Intensidad' },
    dirColor: { value: '#ffffff', label: 'Color' },
    LuzPuntual: { folder: true },
    pointInt: { value: 5, min: 0, max: 20, step: 0.5, label: 'Intensidad' },
    pointColor: { value: '#ff0000', label: 'Color' },
    LuzAmbiental: { folder: true },
    ambientInt: { value: 0.3, min: 0, max: 2, step: 0.1, label: 'Intensidad' }
  })

  // Referencias para visualizar los helpers de las luces
  const dirLight = useRef()
  const pointLight = useRef()
  useHelper(dirLight, THREE.DirectionalLightHelper, 1, 'black')
  useHelper(pointLight, THREE.PointLightHelper, 0.5, 'white')

  return (
    <>
      <OrbitControls />
      
      {/* 1. Luz Ambiental */}
      <ambientLight intensity={ambientInt} />
      
      {/* 2. Luz Direccional (Sol) */}
      <directionalLight 
        ref={dirLight}
        position={[5, 5, 5]} 
        intensity={dirInt} 
        color={dirColor}
        castShadow 
        shadow-mapSize={[1024, 1024]}
      />
      
      {/* 3. Luz Puntual (Foco) */}
      <pointLight 
        ref={pointLight}
        position={[-3, 2, 2]} 
        intensity={pointInt} 
        color={pointColor}
        distance={10}
        castShadow 
      />

      {/* Objetos con diferentes materiales */}
      {/* Material Metálico */}
      <RotatingSphere position={[-2.5, 1, 0]} materialArgs={{ color: '#aaa', metalness: 1, roughness: 0.1 }} />
      
      {/* Material Mate (Standard) */}
      <RotatingSphere position={[0, 1, 0]} materialArgs={{ color: '#2194ce', metalness: 0, roughness: 0.9 }} />
      
      {/* Material Semitransparente (Physical) */}
      <RotatingSphere position={[2.5, 1, 0]} materialArgs={{ color: '#00ff00', transmission: 0.9, opacity: 1, transparent: true, roughness: 0.1 }} />

      {/* Plano base (Suelo) */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.5, 0]} receiveShadow>
        <planeGeometry args={[15, 15]} />
        <meshStandardMaterial color="#eeeeee" />
      </mesh>
    </>
  )
}

export default function App() {
  return (
    <div style={{ width: '100vw', height: '100vh', margin: 0, padding: 0, overflow: 'hidden' }}>
      <Canvas shadows camera={{ position: [0, 5, 8], fov: 50 }}>
        <color attach="background" args={['#202020']} />
        <Scene />
      </Canvas>
    </div>
  )
}