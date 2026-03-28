import React, { useRef, useMemo, useState } from 'react'
import ReactDOM from 'react-dom/client'
import { Canvas, useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { OrbitControls, ContactShadows } from '@react-three/drei';
import './style.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)

// 1. Recursive Fractal Component
const FractalTree = ({ position, scale, depth }) => {
  if (depth <= 0) return null;

  return (
    <group position={position} scale={scale}>
      <mesh>
        <sphereGeometry args={[1, 16, 16]} />
        <meshStandardMaterial color="hotpink" wireframe />
      </mesh>
      
      {/* Recursive branches */}
      <FractalTree position={[2, 2, 0]} scale={[0.5, 0.5, 0.5]} depth={depth - 1} />
      <FractalTree position={[-2, 2, 0]} scale={[0.5, 0.5, 0.5]} depth={depth - 1} />
    </group>
  );
};

const GridTile = ({ position, time, isPlaying }) => {
  const meshRef = useRef();

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    if (meshRef.current) {
      // Calculate a unique Y position based on X and Z coordinates + Time
      const wave = isPlaying?Math.sin(position[0] * 0.5 + t) * Math.cos(position[2] * 0.5 + t):0;
      meshRef.current.position.y = wave;
      
      // Optional: Make them rotate too
      meshRef.current.rotation.y = isPlaying? t * 0.5:0;
    }
  });

  return (
    <mesh ref={meshRef} position={position}>
      <boxGeometry args={[0.9, 0.1, 0.9]} />
      <meshStandardMaterial color="royalblue" />
    </mesh>
  );
};

// 2. Dynamic Vertex Grid
const AnimatedGrid = ({ count = 10, isPlaying }) => {
  const tiles = useMemo(() => {
    const temp = [];
    for (let x = 0; x < count; x++) {
      for (let z = 0; z < count; z++) {
        temp.push([x - count / 2, 0, z - count / 2]);
      }
    }
    return temp;
  }, [count]);

  return (
    <group>
      {tiles.map((pos, i) => (
        <GridTile key={i} position={pos} isPlaying={isPlaying}/>
      ))}
    </group>
  );
};

// 4. Main Scene
export default function App() {
  const [isPlaying, setIsPlaying] = useState(false)
  const [isVisible, setIsVisible] = useState(false)
  return (
    <div style={{width: "90vw", height: "90vh"}}>
      <div style={{ 
        position: 'absolute', 
        top: '20px', 
        left: '20px', 
        zIndex: 10, // Ensures buttons stay above the 3D canvas
        display: 'flex',
        gap: '10px'
      }}>
        <button 
          onClick={() => setIsPlaying(!isPlaying)}
          style={{ padding: '10px 20px', cursor: 'pointer' }}
        >Toggle animation
        </button>

        <button 
          onClick={() => setIsVisible(!isVisible)}
          style={{ padding: '10px 20px', cursor: 'pointer' }}
        >Toggle fractal
        </button>
      </div>
      <Canvas camera={{ position: [10, 10, 10] }}>
        <OrbitControls />
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} />
        
        {!isVisible && <AnimatedGrid count={8} isPlaying={isPlaying} />}
        {isVisible && <FractalTree position={[0, 2, 0]} scale={[1, 1, 1]} depth={4} />}
      </Canvas>
    </div>
  );
}