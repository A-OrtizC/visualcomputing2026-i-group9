import { Canvas } from "@react-three/fiber";
import { OrbitControls, Text } from "@react-three/drei";
import { useState, useEffect } from "react";
import Character from "./Character";

export default function App() {
  const [animation, setAnimation] = useState("Armature.447|[n_40] idle");
  const [message, setMessage] = useState("");

  // ⌨️ control por teclado
  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === "w") {
        setAnimation("Armature.447|[n_40] walk_1");
        setMessage("Caminando...");
      }
      if (e.key === "Shift") {
        setAnimation("Armature.447|[n_40] run_1");
        setMessage("Corriendo!");
      }
      if (e.key === " ") {
        setAnimation("Armature.447|[n_40] greeting_1");
        setMessage("Saludando");
      }
      if (e.key === "q") {
        setAnimation("Armature.447|[n_40] idle");
        setMessage("");
      }
    };

    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, []);

  return (
    <>
      {/* 🎮 UI HTML */}
      <div style={{ position: "absolute", top: 20, left: 20 }}>
        <button onClick={() => {
          setAnimation("Armature.447|[n_40] idle");
          setMessage("");
        }}>
          Idle
        </button>

        <button onClick={() => {
          setAnimation("Armature.447|[n_40] walk_1");
          setMessage("Caminando...");
        }}>
          Walk
        </button>

        <button onClick={() => {
          setAnimation("Armature.447|[n_40] run_1");
          setMessage("Corriendo!");
        }}>
          Run
        </button>

        <button onClick={() => {
          setAnimation("Armature.447|[n_40] greeting_1");
          setMessage("Saludando 👋");
        }}>
          Wave
        </button>
      </div>

      {/* 🎥 Escena 3D */}
      <Canvas style={{height: "100vh"}} camera={{ position: [0, 2, 5] }} >
        <ambientLight intensity={1} />
        <directionalLight position={[5, 5, 5]} />

        <Character currentAnimation={animation} />

        {/* 🔥 BONUS: texto sincronizado */}
        {message && (
          <Text position={[0, 3, 0]} fontSize={0.3} color="white">
            {message}
          </Text>
        )}

        <OrbitControls />
      </Canvas>
    </>
  );
}