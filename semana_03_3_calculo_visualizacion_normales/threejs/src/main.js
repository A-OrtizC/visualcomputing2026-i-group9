import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { VertexNormalsHelper } from 'three/examples/jsm/helpers/VertexNormalsHelper';

// --- INICIALIZACIÓN ---
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
camera.position.set(2, 2, 2);
new OrbitControls(camera, renderer.domElement);

// --- 1. GEOMETRÍA PROCEDURAL ---
const geometry = new THREE.SphereGeometry(0.5, 4, 4); 

// --- 2. CÁLCULO DE NORMALES ---
// Para Smooth:
geometry.computeVertexNormals();

// Para Flat (Descomentar para ver el cambio):
// const flatGeo = geometry.toNonIndexed();
// flatGeo.computeVertexNormals();

// --- 3. SHADER DE VISUALIZACIÓN ---
const normalShaderMaterial = new THREE.ShaderMaterial({
  vertexShader: `
    varying vec3 vNormal;
    void main() {
      vNormal = normalize(normalMatrix * normal);
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    varying vec3 vNormal;
    void main() {
      gl_FragColor = vec4(vNormal * 0.5 + 0.5, 1.0);
    }
  `
});

const mesh = new THREE.Mesh(geometry, normalShaderMaterial);
scene.add(mesh);

// --- 4. HELPER DE NORMALES ---
const helper = new VertexNormalsHelper(mesh, 0.2, 0x00ff00);
scene.add(helper);

// --- LOOP ---
function animate() {
  requestAnimationFrame(animate);
  helper.update(); // Necesario si el mesh rota o cambia
  renderer.render(scene, camera);
}
animate();

// --- EJEMPLO DE ACCESO MANUAL ---
console.log("Normales del primer vértice:", 
  geometry.attributes.normal.getX(0),
  geometry.attributes.normal.getY(0),
  geometry.attributes.normal.getZ(0)
);