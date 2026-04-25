import { useRef, useEffect, useState } from "react";
import { useGLTF, useAnimations } from "@react-three/drei";

export default function Character({ currentAnimation }) {
  const group = useRef();

  const { scene, animations } = useGLTF("/model.glb");
  const { actions, names } = useAnimations(animations, group);

  const [activeAction, setActiveAction] = useState(null);

  // 🎬 cambiar animaciones
  useEffect(() => {
    if (!actions || !currentAnimation) return;

    const nextAction = actions[currentAnimation];

    if (!nextAction) return;

    // fade entre animaciones
    if (activeAction && activeAction !== nextAction) {
      activeAction.fadeOut(0.3);
    }

    nextAction.reset().fadeIn(0.3).play();
    setActiveAction(nextAction);

  }, [currentAnimation, actions]);

  return (
    <primitive ref={group} object={scene} scale={1.5} />
  );
}