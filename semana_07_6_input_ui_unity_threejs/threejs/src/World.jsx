import { useRef, useState, useEffect } from "react";
import { useFrame } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import { useControls } from "leva";

export default function World() {
  const cube = useRef();

  const [active, setActive] = useState(false);
  const [position, setPosition] = useState([0, 0.5, 0]);
  const [mouseText, setMouseText] = useState("0 , 0");

  // Slider UI
  const { size } = useControls({
    size: { value: 1, min: 0.5, max: 3 }
  });

  // Tecla R
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "r") {
        setPosition([0, 0.5, 0]);
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () =>
      window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Movimiento mouse
  useEffect(() => {
    const move = (e) => {
      setMouseText(`${e.clientX} , ${e.clientY}`);
    };

    window.addEventListener("mousemove", move);

    return () =>
      window.removeEventListener("mousemove", move);
  }, []);

  // Animación
  useFrame(() => {
    if (cube.current && active) {
      cube.current.rotation.y += 0.02;
    }
  });

  return (
    <>
      {/* Piso */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.5, 0]}>
        <planeGeometry args={[20, 20]} />
        <meshStandardMaterial color="gray" />
      </mesh>

      {/* Cubo interactivo */}
      <mesh
        ref={cube}
        position={position}
        scale={size}
        onClick={() => setActive(!active)}
      >
        <boxGeometry />
        <meshStandardMaterial color={active ? "hotpink" : "orange"} />

        {/* HTML encima del cubo */}
        <Html position={[0, 1.5, 0]}>
          <button
            onClick={() => setActive(!active)}
            style={{
              padding: "8px",
              cursor: "pointer"
            }}
          >
            {active ? "Desactivar" : "Activar"}
          </button>
        </Html>
      </mesh>

      {/* UI superior */}
      <Html position={[-3, 3, 0]}>
        <div
          style={{
            background: "white",
            padding: "10px",
            borderRadius: "8px"
          }}
        >
          <p>Mouse: {mouseText}</p>
          <p>Tecla R reinicia cubo</p>
          <p>Estado: {active ? "Activo" : "Inactivo"}</p>
        </div>
      </Html>
    </>
  );
}