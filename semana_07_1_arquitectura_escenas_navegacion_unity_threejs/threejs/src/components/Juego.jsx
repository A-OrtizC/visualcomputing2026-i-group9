import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { Link } from "react-router-dom";

function Cubo() {
  return (
    <mesh rotation={[0.5, 0.5, 0]}>
      <boxGeometry args={[2, 2, 2]} />
      <meshStandardMaterial color="orange" />
    </mesh>
  );
}

function Juego() {
  return (
    <div className="pantalla">
      <h1>ESCENA DE JUEGO</h1>

      <div className="canvasBox">
        <Canvas camera={{ position: [4, 4, 4] }}>
          <ambientLight intensity={1} />
          <directionalLight position={[2, 2, 2]} />
          <Cubo />
          <OrbitControls />
        </Canvas>
      </div>

      <Link to="/">
        <button>Volver al menú</button>
      </Link>
    </div>
  );
}

export default Juego;