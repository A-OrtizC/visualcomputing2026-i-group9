import { useState } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";

import PanoramaViewer from "./PanoramaViewer";

const panoramas = [
  {
    name: "Museo",
    file: "/panoramaFoto1.png",
  },
  {
    name: "Edificio vacío",
    file: "/panoramaFoto2.png",
  },
  {
    name: "Cálido",
    file: "/panoramaFoto3.png",
  },
  {
    name: "Video atardecer",
    file: "/panoramaVideo1.mp4",
  },
  {
    name: "Calle Italia",
    file: "/panoramaVideo2.mp4",
  },
  {
    name: "Calle Florida",
    file: "/panoramaVideo3.mp4",
  },
];

export default function App() {
  const [selected, setSelected] = useState(
    panoramas[0].file
  );

  return (
    <>
      <div
        style={{
          position: "absolute",
          top: 15,
          left: 15,
          zIndex: 1000,
        }}
      >
        <select
          value={selected}
          onChange={(e) =>
            setSelected(e.target.value)
          }
        >
          {panoramas.map((p) => (
            <option
              key={p.file}
              value={p.file}
            >
              {p.name}
            </option>
          ))}
        </select>
      </div>

      <Canvas
        camera={{
          position: [0, 0, 0.1],
          fov: 75,
        }}
      >
        <PanoramaViewer item={selected} />

        <OrbitControls
          enableZoom={false}
          enablePan={false}
          rotateSpeed={-0.5}
        />
      </Canvas>
    </>
  );
}