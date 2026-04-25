import React, { useRef, useMemo, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'

// --- SHADERS ---
const vertexShader = `
  varying vec2 vUv;
  uniform float uTime;
  void main() {
    vUv = uv;
    // Desplazamiento de vértices basado en el tiempo y posición (simula pulsación)
    vec3 pos = position;
    float displacement = sin(pos.y * 5.0 + uTime * 2.0) * 0.1;
    pos += normal * displacement;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
  }
`

const fragmentShader = `
  varying vec2 vUv;
  uniform float uTime;
  uniform vec3 uColor1;
  uniform vec3 uColor2;
  void main() {
    // Mezcla de colores dinámica simulando energía/plasma
    float mixValue = (sin(vUv.y * 10.0 + uTime * 3.0) + 1.0) * 0.5;
    vec3 finalColor = mix(uColor1, uColor2, mixValue);
    gl_FragColor = vec4(finalColor, 1.0);
  }
`

// --- COMPONENTES ---
const DynamicSphere = ({ onClick }) => {
  const materialRef = useRef()

  // Uniforms para el Shader
  const uniforms = useMemo(() => ({
    uTime: { value: 0 },
    uColor1: { value: new THREE.Color('#ff0055') },
    uColor2: { value: new THREE.Color('#00ffff') }
  }), [])

  useFrame((state) => {
    if (materialRef.current) {
      materialRef.current.uniforms.uTime.value = state.clock.elapsedTime
    }
  })

  return (
    <mesh onClick={onClick}>
      <sphereGeometry args={[1.5, 64, 64]} />
      <shaderMaterial 
        ref={materialRef}
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms}
        wireframe={false}
      />
    </mesh>
  )
}

const ParticleSystem = ({ isExploding }) => {
  const pointsRef = useRef()
  const count = 2000

  // Generar posiciones aleatorias iniciales
  const [positions, initialPositions] = useMemo(() => {
    const pos = new Float32Array(count * 3)
    const initPos = new Float32Array(count * 3)
    for (let i = 0; i < count; i++) {
      const theta = Math.random() * Math.PI * 2
      const phi = Math.acos((Math.random() * 2) - 1)
      const r = 1.6 + Math.random() * 0.5
      
      const x = r * Math.sin(phi) * Math.cos(theta)
      const y = r * Math.sin(phi) * Math.sin(theta)
      const z = r * Math.cos(phi)

      pos[i*3] = x; pos[i*3+1] = y; pos[i*3+2] = z;
      initPos[i*3] = x; initPos[i*3+1] = y; initPos[i*3+2] = z;
    }
    return [pos, initPos]
  }, [count])

  useFrame((state, delta) => {
    if (!pointsRef.current) return
    const positionsAttr = pointsRef.current.geometry.attributes.position
    const posArray = positionsAttr.array

    for (let i = 0; i < count; i++) {
      const idx = i * 3
      if (isExploding) {
        // Expansión (explosión)
        posArray[idx] *= 1.05
        posArray[idx+1] *= 1.05
        posArray[idx+2] *= 1.05
      } else {
        // Rotación y flotación suave
        posArray[idx] = initialPositions[idx] + Math.sin(state.clock.elapsedTime + i) * 0.1
        posArray[idx+1] = initialPositions[idx+1] + Math.cos(state.clock.elapsedTime + i) * 0.1
      }
    }
    positionsAttr.needsUpdate = true
  })

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.03} color="#ffffff" transparent opacity={0.6} blending={THREE.AdditiveBlending} />
    </points>
  )
}

export default function App() {
  const [isExploding, setIsExploding] = useState(false)

  const handleExplosion = () => {
    setIsExploding(true)
    setTimeout(() => setIsExploding(false), 500) // Vuelve a la normalidad en 0.5s
  }

  return (
    <div style={{ width: '100vw', height: '100vh', backgroundColor: '#111' }}>
      <Canvas camera={{ position: [0, 0, 6] }}>
        <ambientLight intensity={0.5} />
        <DynamicSphere onClick={handleExplosion} />
        <ParticleSystem isExploding={isExploding} />
        <OrbitControls />
      </Canvas>
      <div style={{ position: 'absolute', top: 20, left: 20, color: 'white', fontFamily: 'sans-serif' }}>
        <h2>Texturizado y Partículas</h2>
        <p>Haz clic en la esfera para activar la explosión de partículas.</p>
      </div>
    </div>
  )
}