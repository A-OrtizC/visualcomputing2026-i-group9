import { Canvas, useFrame } from '@react-three/fiber'
import { useRef, useMemo } from 'react'
import * as THREE from 'three'
import { OrbitControls } from '@react-three/drei'

const CustomShaderMaterial = () => {
  const meshRef = useRef()

  // Definición de Uniforms (Datos que enviamos de CPU a GPU)
  const uniforms = useMemo(() => ({
    uTime: { value: 0 },
    uColor: { value: new THREE.Color('#00ffcc') }
  }), [])

  // Actualización por frame (Animación)
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.material.uniforms.uTime.value = state.clock.getElapsedTime()
    }
  })

  // VERTEX SHADER: Transformaciones y Deformación
  const vertexShader = `
    varying vec2 vUv;
    varying vec3 vNormal;
    uniform float uTime;

    void main() {
      vUv = uv;
      vNormal = normal; // Pasar normales al Fragment Shader

      vec3 pos = position;
      // Deformación senoidal (Punto 2 del taller de Three.js)
      pos.z += sin(pos.x * 4.0 + uTime) * 0.3;
      pos.z += cos(pos.y * 3.0 + uTime) * 0.2;

      // Transformación: Model -> View -> Projection
      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
    }
  `

  // FRAGMENT SHADER: Cálculo de Color e Iluminación
  const fragmentShader = `
    varying vec2 vUv;
    varying vec3 vNormal;
    uniform float uTime;
    uniform vec3 uColor;

    void main() {
      // Iluminación básica tipo Lambert
      vec3 lightDir = normalize(vec3(1.0, 1.0, 1.0));
      float intensity = max(0.0, dot(vNormal, lightDir));
      
      // Efecto procedural (Punto 3 del taller)
      vec3 finalColor = uColor * intensity;
      finalColor.r += vUv.x * 0.5; // Gradiente basado en UV
      
      gl_FragColor = vec4(finalColor, 1.0);
    }
  `

  return (
    <mesh ref={meshRef} rotation={[-Math.PI / 3, 0, 0]}>
      {/* Geometría con suficientes subdivisiones para la deformación */}
      <planeGeometry args={[5, 5, 64, 64]} />
      <shaderMaterial
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms}
        side={THREE.DoubleSide}
        wireframe={false}
      />
    </mesh>
  )
}

export default function App() {
  return (
    <div style={{ width: '100vw', height: '100vh', background: '#111' }}>
      <Canvas camera={{ position: [0, 0, 6] }}>
        <color attach="background" args={['#050505']} />
        <ambientLight intensity={0.5} />
        <CustomShaderMaterial />
        <OrbitControls />
      </Canvas>
    </div>
  )
}