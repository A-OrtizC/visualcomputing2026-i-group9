import { useMemo } from "react";
import * as THREE from "three";
import { useTexture } from "@react-three/drei";

function ImageSphere({ src }) {
  const texture = useTexture(src);

  return (
    <mesh scale={[-1, 1, 1]}>
      <sphereGeometry args={[50, 64, 64]} />
      <meshBasicMaterial
        map={texture}
        side={THREE.BackSide}
      />
    </mesh>
  );
}

function VideoSphere({ src }) {
  const texture = useMemo(() => {
    const video = document.createElement("video");

    video.src = src;
    video.crossOrigin = "anonymous";
    video.loop = true;
    video.muted = true;
    video.playsInline = true;

    video.play();

    return new THREE.VideoTexture(video);
  }, [src]);

  return (
    <mesh scale={[-1, 1, 1]}>
      <sphereGeometry args={[50, 64, 64]} />
      <meshBasicMaterial
        map={texture}
        side={THREE.BackSide}
      />
    </mesh>
  );
}

export default function PanoramaViewer({ item }) {
  const isVideo =
    item.endsWith(".mp4")

  return isVideo ? (
    <VideoSphere src={item} />
  ) : (
    <ImageSphere src={item} />
  );
}