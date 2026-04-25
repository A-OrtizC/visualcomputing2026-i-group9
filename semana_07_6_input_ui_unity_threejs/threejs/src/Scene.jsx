import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import World from "./World";

export default function Scene() {
  return (
    <Canvas camera={{ position: [0, 3, 8], fov: 60 }}>
      <ambientLight intensity={1} />
      <directionalLight position={[5, 5, 5]} />

      <World />

      <OrbitControls />
    </Canvas>
  );
}