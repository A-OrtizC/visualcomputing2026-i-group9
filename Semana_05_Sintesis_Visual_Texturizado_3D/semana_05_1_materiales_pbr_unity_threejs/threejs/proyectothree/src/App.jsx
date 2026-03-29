import { Canvas } from '@react-three/fiber'
import { useTexture, OrbitControls, Environment } from '@react-three/drei'
import { useControls } from 'leva' // Para el panel interactivo solicitado

function PBRSphere({ roughness, metalness }) {
  // 1. Cargar texturas desde /public/textures/
  const props = useTexture({
    map: 'textures/Color.jpg',
    normalMap: 'textures/NormalDX.jpg',
    roughnessMap: 'textures/Roughness.jpg',
    metalnessMap: 'textures/Metalness.jpg',
  })

  return (
    <mesh castShadow>
      <sphereGeometry args={[1, 64, 64]} />
      <meshStandardMaterial 
        {...props} 
        roughness={roughness} 
        metalness={metalness} 
        envMapIntensity={2}
      />
    </mesh>
  )
}

export default function App() {
  const { roughness, metalness, ambientIntensity, directionalIntensity } = useControls({
    roughness: { value: 0.2, min: 0, max: 1, step: 0.01 },
    metalness: { value: 0.6, min: 0, max: 1, step: 0.01 },
    ambientIntensity: { value: 1.1, min: 0, max: 3, step: 0.1 },
    directionalIntensity: { value: 2.2, min: 0, max: 5, step: 0.1 },
  })

  return (
    <Canvas shadows camera={{ position: [0, 1.5, 5], fov: 50 }}>
      <color attach="background" args={["#11131d"]} />
      <ambientLight intensity={ambientIntensity} />
      <directionalLight position={[5, 8, 5]} intensity={directionalIntensity} castShadow />
      <hemisphereLight skyColor="#f0f8ff" groundColor="#080820" intensity={0.5} />
      <Environment preset="sunset" />

      <group position={[0, 0.5, 0]}>
        <PBRSphere roughness={roughness} metalness={metalness} />
        <mesh position={[-2.5, 0, 0]}>
          <boxGeometry args={[1, 1, 1]} />
          <meshStandardMaterial color="red" roughness={0.7} metalness={0.0} />
        </mesh>
      </group>

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]} receiveShadow>
        <planeGeometry args={[20, 20]} />
        <meshStandardMaterial color="#222" roughness={0.8} metalness={0.05} />
      </mesh>

      <OrbitControls enableDamping />
    </Canvas>
  )
}