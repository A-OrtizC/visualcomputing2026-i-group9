import React, { useRef, useEffect, useState, useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useFBX, useAnimations, Environment } from '@react-three/drei';

function Character() {
  const group = useRef();
  
  // Cargar los 3 FBX individualmente
  const fbxWalk = useFBX('/walk.fbx');
  const fbxJump = useFBX('/Jump.fbx');
  const fbxWave = useFBX('/Standing Greeting.fbx');

  // Extraer y renombrar las animaciones de cada archivo para evitar conflictos (ya que todas suelen llamarse 'mixamo.com')
  const animations = useMemo(() => {
    const walkAnim = fbxWalk.animations[0]?.clone();
    if (walkAnim) walkAnim.name = 'Walk';

    const jumpAnim = fbxJump.animations[0]?.clone();
    if (jumpAnim) jumpAnim.name = 'Jump';

    const waveAnim = fbxWave.animations[0]?.clone();
    if (waveAnim) waveAnim.name = 'Wave';

    return [walkAnim, jumpAnim, waveAnim].filter(Boolean);
  }, [fbxWalk, fbxJump, fbxWave]);

  const { actions } = useAnimations(animations, group);
  
  // Estado actual de la animación
  const [action, setAction] = useState('Idle');

  // Lógica de transición de animaciones
  useEffect(() => {
    if (!actions[action]) return;

    // Transición suave (Crossfade)
    actions[action].reset().fadeIn(0.2).play();
    return () => actions[action].fadeOut(0.2);
  }, [action, actions]);

  // Eventos de teclado
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key.toLowerCase() === 'w') setAction('Walk');
      if (e.key === ' ') setAction('Jump');
    };
    const handleKeyUp = (e) => {
      if (e.key.toLowerCase() === 'w' || e.key === ' ') setAction('Idle');
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, []);

  return (
    <group 
      ref={group} 
      dispose={null}
      onClick={(e) => { e.stopPropagation(); setAction('Wave'); }}
      onPointerOver={(e) => { e.stopPropagation(); document.body.style.cursor = 'pointer'; }}
      onPointerOut={(e) => { e.stopPropagation(); document.body.style.cursor = 'default'; setAction('Idle'); }}
    >
      <primitive object={fbxWalk} scale={0.01} position={[0, -1, 0]} />
    </group>
  );
}

export default function App() {
  return (
    <div style={{ width: '100vw', height: '100vh', margin: 0, backgroundColor: '#202020' }}>
      <div style={{ position: 'absolute', top: 20, left: 20, color: 'white', zIndex: 1, fontFamily: 'sans-serif' }}>
        <h3>Controles:</h3>
        <p>W: Caminar</p>
        <p>Espacio: Saltar</p>
        <p>Clic en modelo: Saludar</p>
      </div>
      <Canvas camera={{ position: [0, 1.5, 4], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[2, 5, 2]} intensity={1} castShadow />
        <Environment preset="city" />
        <Character />
        <OrbitControls makeDefault target={[0, 1, 0]} />
      </Canvas>
    </div>
  );
}
