import React, { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Grid, Trail } from '@react-three/drei'
import { useControls } from 'leva'
import * as THREE from 'three'

// --- 1. Componente del Robot Autónomo ---
const AutonomousRobot = ({ obstaclesGroupRef, goalRef }) => {
  const robotRef = useRef()
  const evasionRef = useRef(1) // 1 = Izquierda, -1 = Derecha

  // Refs para cambiar el color de los "Láseres de Visión" en tiempo real sin causar re-renders
  const laserForwardMat = useRef()
  const laserLeftMat = useRef()
  const laserRightMat = useRef()

  // Panel de control interactivo mediante Leva (Requisito del taller / Bonus)
  const [{ speed, rotationSpeed, rayLength }] = useControls(() => ({
    speed: { value: 4, min: 1, max: 10, label: 'Velocidad Avanzar' },
    rotationSpeed: { value: 3, min: 1, max: 6, label: 'Velocidad Giro' },
    rayLength: { value: 3.5, min: 2, max: 7, label: 'Distancia Sensores' },
  }))

  // Instanciamos un único Raycaster para optimizar memoria
  const raycaster = new THREE.Raycaster()

  useFrame((state, delta) => {
    if (!robotRef.current || !obstaclesGroupRef.current || !goalRef.current) return

    const robot = robotRef.current
    const obstacles = obstaclesGroupRef.current.children
    const goalPos = goalRef.current.position
    const robotPos = robot.position

    // 1. Condición de Parada (Meta Alcanzada)
    const distanceToGoal = robotPos.distanceTo(goalPos)
    if (distanceToGoal < 1.5) {
      // El robot se detiene e ilumina sus sensores en azul indicando éxito
      laserForwardMat.current.color.set('#00aaff')
      return
    }

    // 2. Definición de Vectores de Dirección del Sensor (Frente, Izquierda 45°, Derecha 45°)
    // Nota: En Three.js, la dirección frontal por defecto al avanzar es el eje -Z
    const fDir = new THREE.Vector3(0, 0, -1).applyQuaternion(robot.quaternion)
    const lDir = new THREE.Vector3(0, 0, -1).applyAxisAngle(new THREE.Vector3(0, 1, 0), Math.PI / 4).applyQuaternion(robot.quaternion)
    const rDir = new THREE.Vector3(0, 0, -1).applyAxisAngle(new THREE.Vector3(0, 1, 0), -Math.PI / 4).applyQuaternion(robot.quaternion)

    // 3. Ejecución de Raycasting para cada sensor
    raycaster.set(robotPos, fDir)
    const fHits = raycaster.intersectObjects(obstacles)
    const hitForward = fHits.length > 0 && fHits[0].distance < rayLength

    raycaster.set(robotPos, lDir)
    const lHits = raycaster.intersectObjects(obstacles)
    const hitLeft = lHits.length > 0 && lHits[0].distance < rayLength

    raycaster.set(robotPos, rDir)
    const rHits = raycaster.intersectObjects(obstacles)
    const hitRight = rHits.length > 0 && rHits[0].distance < rayLength

    // 4. Feedback Visual de los Sensores (Verde = Libre, Rojo = Obstáculo Detectado)
    laserForwardMat.current.color.set(hitForward ? '#ff0055' : '#00ff66')
    laserLeftMat.current.color.set(hitLeft ? '#ffaa00' : '#00ffff')
    laserRightMat.current.color.set(hitRight ? '#ffaa00' : '#00ffff')

    // 5. Máquina de Estados de Navegación Reactiva e Inteligente
    if (hitForward) {
      // Hay un obstáculo al frente. Decidir evasión analizando los sensores laterales
      let turnDirection = evasionRef.current

      if (hitRight && !hitLeft) {
        turnDirection = 1 // Derecha bloqueada, girar a la Izquierda (Y positivo)
      } else if (hitLeft && !hitRight) {
        turnDirection = -1 // Izquierda bloqueada, girar a la Derecha (Y negativo)
      } else if (hitLeft && hitRight) {
        // Encajonado en un pasillo: girar hacia el lado que tenga el obstáculo más lejano
        turnDirection = lHits[0].distance > rHits[0].distance ? 1 : -1
      }

      evasionRef.current = turnDirection
      robot.rotation.y += turnDirection * rotationSpeed * delta
    } else {
      // Camino libre al frente: Orientarse activamente hacia la meta (Goal Seeking)
      const toGoalVector = new THREE.Vector3().subVectors(goalPos, robotPos)
      
      // Calculamos el ángulo objetivo en el plano horizontal XZ respecto al frente (-Z)
      const targetAngle = Math.atan2(-toGoalVector.x, -toGoalVector.z)
      
      // Interpolación suave del ángulo (Evita saltos bruscos y giros infinitos)
      let angleDiff = targetAngle - robot.rotation.y
      angleDiff = Math.atan2(Math.sin(angleDiff), Math.cos(angleDiff)) // Normalizar entre -PI y PI
      
      robot.rotation.y += angleDiff * (rotationSpeed * 0.6) * delta

      // Avanzar de manera constante hacia su eje -Z local
      robot.translateZ(-speed * delta)
    }
  })

  // Matriz de conversión para la rotación de 45° en los sensores visuales
  const angle45 = Math.PI / 4

  return (
    <group ref={robotRef} position={[0, 0.5, 12]}>
      
      {/* Rastro de Movimiento automático provisto por Drei (Requisito de trayectoria) */}
      <Trail width={0.8} length={50} color="#00aaff" attenuation={(t) => t * t}>
        {/* Cuerpo del Robot */}
        <mesh castShadow>
          <boxGeometry args={[1.2, 0.8, 1.5]} />
          <meshStandardMaterial color="#333333" roughness={0.2} metalness={0.8} />
        </mesh>
      </Trail>

      {/* Indicador Frontal Visual (Cabina/Frente del Robot) */}
      <mesh position={[0, 0.2, -0.6]}>
        <boxGeometry args={[0.8, 0.3, 0.3]} />
        <meshStandardMaterial color="#222" emissive="#00aaff" emissiveIntensity={0.5} />
      </mesh>

      {/* --- Visualización de Rayos / Sensores Visuales Simulados --- */}
      {/* Sensor Central */}
      <mesh position={[0, 0, -rayLength / 2]}>
        <boxGeometry args={[0.02, 0.02, rayLength]} />
        <meshBasicMaterial ref={laserForwardMat} color="#00ff66" transparent opacity={0.6} />
      </mesh>

      {/* Sensor Izquierdo (Rotado 45° a la izquierda) */}
      <group rotation={[0, angle45, 0]}>
        <mesh position={[0, 0, -rayLength / 2]}>
          <boxGeometry args={[0.02, 0.02, rayLength]} />
          <meshBasicMaterial ref={laserLeftMat} color="#00ffff" transparent opacity={0.4} />
        </mesh>
      </group>

      {/* Sensor Derecho (Rotado 45° a la derecha) */}
      <group rotation={[0, -angle45, 0]}>
        <mesh position={[0, 0, -rayLength / 2]}>
          <boxGeometry args={[0.02, 0.02, rayLength]} />
          <meshBasicMaterial ref={laserRightMat} color="#00ffff" transparent opacity={0.4} />
        </mesh>
      </group>

    </group>
  )
}

// --- 2. Componente del Escenario (Paredes y Laberinto idéntico a Unity) ---
const MapEnvironment = React.forwardRef((props, ref) => {
  return (
    <group ref={ref}>
      {/* Suelo de la pista */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]} receiveShadow>
        <planeGeometry args={[30, 40]} />
        <meshStandardMaterial color="#b5835c" roughness={0.8} />
      </mesh>

      {/* Paredes Perimetrales (Color Rosa del Laboratorio de Unity) */}
      <mesh position={[0, 1, -20]}><boxGeometry args={[30, 2, 0.5]} /><meshStandardMaterial color="#db7b93" /></mesh> {/* Norte */}
      <mesh position={[0, 1, 20]}><boxGeometry args={[30, 2, 0.5]} /><meshStandardMaterial color="#db7b93" /></mesh> {/* Sur */}
      <mesh position={[-15, 1, 0]}><boxGeometry args={[0.5, 2, 40]} /><meshStandardMaterial color="#db7b93" /></mesh> {/* Oeste */}
      <mesh position={[15, 1, 0]}><boxGeometry args={[0.5, 2, 40]} /><meshStandardMaterial color="#db7b93" /></mesh>  {/* Este */}

      {/* Obstáculos de Pasillo / Deflectores en Zigzag */}
      <mesh position={[-4, 1, 5]}><boxGeometry args={[22, 2, 0.5]} /><meshStandardMaterial color="#db7b93" /></mesh>  {/* Muro Inferior */}
      <mesh position={[4, 1, -5]}><boxGeometry args={[22, 2, 0.5]} /><meshStandardMaterial color="#db7b93" /></mesh>  {/* Muro Intermedio */}
      
      {/* Obstáculo de Cápsula/Cilindro superior */}
      <mesh position={[0, 1, -12]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[1.2, 1.2, 10, 32]} />
        <meshStandardMaterial color="#db7b93" roughness={0.4} />
      </mesh>
    </group>
  )
})

// --- 3. Componente Raíz de la Aplicación ---
export default function App() {
  const obstaclesGroupRef = useRef()
  const goalRef = useRef()

  return (
    <div style={{ width: '100vw', height: '100vh', backgroundColor: '#1a1a1a' }}>
      <Canvas camera={{ position: [0, 25, 25], fov: 50 }} shadows>
        {/* Iluminación Realista */}
        <ambientLight intensity={0.7} />
        <directionalLight 
          position={[10, 20, 10]} 
          intensity={1.5} 
          castShadow 
          shadow-mapSize={[2048, 2048]} 
        />

        {/* Rejilla de Referencia Espacial */}
        <Grid infiniteGrid fadeDistance={30} cellColor="#333" sectionColor="#555" />

        {/* Objeto Meta (Cápsula dorada al fondo del escenario) */}
        <mesh ref={goalRef} position={[0, 0.5, -17]}>
          <sphereGeometry args={[0.8, 32, 32]} />
          <meshStandardMaterial color="#ffcc00" emissive="#ff9900" emissiveIntensity={0.6} />
        </mesh>

        {/* Grupo de Obstáculos mapeados para detección */}
        <MapEnvironment ref={obstaclesGroupRef} />

        {/* Instanciación del Robot con sus dependencias de navegación */}
        <AutonomousRobot obstaclesGroupRef={obstaclesGroupRef} goalRef={goalRef} />

        {/* Controles del Escenario */}
        <OrbitControls maxPolarAngle={Math.PI / 2.1} />
      </Canvas>
    </div>
  )
}