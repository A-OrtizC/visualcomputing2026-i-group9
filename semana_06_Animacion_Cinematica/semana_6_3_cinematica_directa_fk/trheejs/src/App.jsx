import React, { useRef, forwardRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Grid, Trail } from '@react-three/drei'
import { useControls } from 'leva'

// --- 1. Definición del Componente ArmSegment ---
// Se usa forwardRef para que useFrame pueda rotar los grupos directamente
const ArmSegment = forwardRef(({ length, rotationZ, children, color }, ref) => {
  return (
    <group ref={ref} rotation={[0, 0, rotationZ]}>
      {/* Parte visual del eslabón */}
      <mesh position={[0, length / 2, 0]}>
        <boxGeometry args={[0.2, length, 0.2]} />
        <meshStandardMaterial color={color} />
      </mesh>
      
      {/* Punto de articulación para el siguiente hijo al final del eslabón */}
      <group position={[0, length, 0]}>
        {children}
      </group>
    </group>
  )
})

// --- 2. Componente de la Estructura Robótica ---
// Contiene la lógica de frames y la jerarquía de cinemática directa
const RoboticArm = () => {
  const arm1Ref = useRef()
  const arm2Ref = useRef()
  const arm3Ref = useRef()

  // Panel de control con Leva
  const [{ autoAnimate, speed, angle1, angle2, angle3 }] = useControls(() => ({
    autoAnimate: { value: false, label: 'Modo Automático' },
    speed: { value: 1, min: 0.1, max: 5, label: 'Velocidad' },
    angle1: { value: 0, min: -1.5, max: 1.5, label: 'Hombro' },
    angle2: { value: 0, min: -2, max: 2, label: 'Codo' },
    angle3: { value: 0, min: -2, max: 2, label: 'Muñeca' },
  }))

  // Bucle de animación para cinemática directa
  useFrame((state) => {
    if (autoAnimate) {
      const t = state.clock.getElapsedTime() * speed
      // Movimiento sinusoidal encadenado
      if (arm1Ref.current) arm1Ref.current.rotation.z = Math.sin(t) * 0.5
      if (arm2Ref.current) arm2Ref.current.rotation.z = Math.sin(t * 1.2) * 1.0
      if (arm3Ref.current) arm3Ref.current.rotation.z = Math.cos(t * 2) * 0.8
    } else {
      // Control manual mediante sliders
      if (arm1Ref.current) arm1Ref.current.rotation.z = angle1
      if (arm2Ref.current) arm2Ref.current.rotation.z = angle2
      if (arm3Ref.current) arm3Ref.current.rotation.z = angle3
    }
  })

  return (
    <group position={[0, -1, 0]}>
      {/* Base del Robot */}
      <mesh>
        <cylinderGeometry args={[0.5, 0.5, 0.2, 32]} />
        <meshStandardMaterial color="#333" />
      </mesh>

      {/* Cadena de articulaciones (Cinemática Directa) */}
      <ArmSegment ref={arm1Ref} length={1} rotationZ={0} color="royalblue">
        <ArmSegment ref={arm2Ref} length={0.8} rotationZ={0} color="indianred">
          <ArmSegment ref={arm3Ref} length={0.5} rotationZ={0} color="goldenrod">
            
            {/* Visualización de la trayectoria del extremo (Trail) */}
            <Trail
              width={1.5}           // Ancho de la línea de rastro
              length={10}           // Cantidad de puntos en el historial
              color={'#ffcc00'}     // Color del trazo
              attenuation={(t) => t * t} // Desvanecimiento progresivo
            >
              {/* Actuador Final (Mano/Pinza) */}
              <mesh>
                <sphereGeometry args={[0.15, 16, 16]} />
                <meshStandardMaterial color="white" emissive="white" emissiveIntensity={0.5} />
              </mesh>
            </Trail>

          </ArmSegment>
        </ArmSegment>
      </ArmSegment>
    </group>
  )
}

// --- 3. Componente Principal de la Aplicación ---
export default function App() {
  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <Canvas camera={{ position: [4, 4, 6], fov: 50 }}>
        {/* Configuración del Entorno */}
        <color attach="background" args={['#1a1a1a']} />
        <ambientLight intensity={1.5} /> 
        <pointLight position={[10, 10, 10]} intensity={2.5} /> 

        {/* Rejilla de referencia */}
        <Grid infiniteGrid fadeDistance={12} cellColor="#444" sectionColor="#666" />

        {/* Instancia del Brazo */}
        <RoboticArm />

        {/* Controles de cámara */}
        <OrbitControls />
      </Canvas>
    </div>
  )
}