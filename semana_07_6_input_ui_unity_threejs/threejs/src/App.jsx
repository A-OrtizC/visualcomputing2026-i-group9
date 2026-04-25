import { Canvas } from "@react-three/fiber";
import { OrbitControls, Html } from "@react-three/drei";
import { useRef, useState, useEffect } from "react";
import { useFrame } from "@react-three/fiber";
import "./App.css";

function Cube() {
  const ref = useRef();
  const [active, setActive] = useState(false);

  const toggle = () => setActive((prev) => !prev);

  // Animación
  useFrame(() => {
    if (active && ref.current) {
      ref.current.rotation.y += 0.02;
    }
  });

  // Tecla R
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key.toLowerCase() === "r") {
        setActive(false);

        if (ref.current) {
          ref.current.rotation.set(0, 0, 0);
          ref.current.position.set(0, 1, 0);
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () =>
      window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <mesh ref={ref} onClick={toggle} position={[0, 1, 0]}>
      <boxGeometry />
      <meshStandardMaterial color={active ? "hotpink" : "orange"} />

      <Html position={[0, 1.3, 0]} center>
        <button className="btn3d" onClick={toggle}>
          {active ? "Detener" : "Activar"}
        </button>
      </Html>
    </mesh>
  );
}

export default function App() {
  const [mouse, setMouse] = useState("0 , 0");

  useEffect(() => {
    const move = (e) => {
      setMouse(`${e.clientX} , ${e.clientY}`);
    };

    window.addEventListener("mousemove", move);
    return () => window.removeEventListener("mousemove", move);
  }, []);

  return (
    <>
      {/* UI FIJA */}
      <div className="hud">
        <h2>Taller 61</h2>
        <p>Mouse: {mouse}</p>
        <p>Click cubo = activar giro</p>
        <p>R = reiniciar</p>
      </div>

      {/* ESCENA */}
      <Canvas camera={{ position: [0, 4, 8], fov: 60 }}>
        <color attach="background" args={["#0f172a"]} />

        <ambientLight intensity={2} />
        <directionalLight position={[5, 8, 5]} intensity={2} />

        <mesh rotation={[-Math.PI / 2, 0, 0]}>
          <planeGeometry args={[20, 20]} />
          <meshStandardMaterial color="#334155" />
        </mesh>

        <Cube />

        <OrbitControls />
      </Canvas>
    </>
  );
}