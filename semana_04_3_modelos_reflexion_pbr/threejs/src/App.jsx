import React, { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import * as THREE from "three";
import { Leva, useControls } from "leva";

// =============================
// SHADERS
// =============================
const vertexShader = `
  varying vec3 vNormal;
  varying vec3 vPosition;

  void main() {
    vNormal = normalize(normalMatrix * normal);
    vec4 worldPos = modelMatrix * vec4(position, 1.0);
    vPosition = worldPos.xyz;
    gl_Position = projectionMatrix * viewMatrix * worldPos;
  }
`;

const fragmentShader = `
  uniform vec3 lightDir;
  uniform vec3 viewPos;
  uniform vec3 color;
  uniform float shininess;
  uniform int modelType;

  varying vec3 vNormal;
  varying vec3 vPosition;

  void main() {
    vec3 N = normalize(vNormal);
    vec3 L = normalize(lightDir);

    float diff = max(dot(N, L), 0.0);
    vec3 diffuse = diff * color;

    vec3 specular = vec3(0.0);
    vec3 V = normalize(viewPos - vPosition);

    if (modelType == 1) {
      vec3 R = reflect(-L, N);
      float spec = pow(max(dot(R, V), 0.0), shininess);
      specular = vec3(spec);
    }

    if (modelType == 2) {
      vec3 H = normalize(L + V);
      float spec = pow(max(dot(N, H), 0.0), shininess);
      specular = vec3(spec);
    }

    gl_FragColor = vec4(diffuse + specular, 1.0);
  }
`;

// =============================
// ESFERA CUSTOM SHADER
// =============================
function Sphere({ modelType }) {
  const meshRef = useRef();

  const { shininess, color } = useControls({
    shininess: { value: 32, min: 1, max: 128 },
    color: "#ff8844",
  });

  // 🔥 IMPORTANTE: uniforms con useMemo (CLAVE)
  const uniforms = useMemo(
    () => ({
      lightDir: { value: new THREE.Vector3(1, 1, 1) },
      viewPos: { value: new THREE.Vector3() },
      color: { value: new THREE.Color(color) },
      shininess: { value: shininess },
      modelType: { value: modelType },
    }),
    []
  );

  useFrame(({ camera, clock }) => {
    if (!meshRef.current) return;

    const mat = meshRef.current.material;

    // cámara
    mat.uniforms.viewPos.value.copy(camera.position);

    // 🔥 actualizar uniforms correctamente
    mat.uniforms.shininess.value = shininess;
    mat.uniforms.color.value.set(color);
    mat.uniforms.modelType.value = modelType;

    // luz dinámica
    const t = clock.getElapsedTime();
    mat.uniforms.lightDir.value.set(Math.sin(t), 1, Math.cos(t));
  });

  return (
    <mesh ref={meshRef} position={[-1.5, 0, 0]}>
      <sphereGeometry args={[1, 64, 64]} />
      <shaderMaterial
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms}
      />
    </mesh>
  );
}

// =============================
// BUILT-IN COMPARACIÓN
// =============================
function BuiltInSphere({ modelType }) {
  let material;

  if (modelType === 0) {
    material = <meshLambertMaterial color="orange" />;
  } else if (modelType === 1) {
    material = <meshPhongMaterial color="orange" shininess={100} />;
  } else {
    material = (
      <meshStandardMaterial color="orange" metalness={1} roughness={0.2} />
    );
  }

  return (
    <mesh position={[1.5, 0, 0]}>
      <sphereGeometry args={[1, 64, 64]} />
      {material}
    </mesh>
  );
}

// =============================
// APP
// =============================
export default function App() {
  const { model } = useControls({
    model: {
      options: {
        Lambert: 0,
        Phong: 1,
        Blinn: 2,
      },
    },
  });

  return (
    <>
      <Leva collapsed oneLineLabels />

      <Canvas style={{width: "60vw", height: "60vh"}} camera={{ position: [0, 0, 5] }}>
        <ambientLight intensity={0.2} />

        <Sphere modelType={model} />
        <BuiltInSphere modelType={model} />

        <OrbitControls />
      </Canvas>
    </>
  );
}