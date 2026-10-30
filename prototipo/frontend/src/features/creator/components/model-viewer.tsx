"use client";

import { OrbitControls, Stage, useGLTF } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { Suspense } from "react";

function Model({ url }: { url: string }) {
  const { scene } = useGLTF(url);
  return <primitive object={scene} />;
}

export function ModelViewer({ url, autoRotate }: { url: string; autoRotate: boolean }) {
  return (
    <Canvas camera={{ position: [0, 0.6, 3], fov: 35 }} dpr={[1, 2]} shadows>
      <color attach="background" args={["#f1efea"]} />
      <Suspense fallback={null}>
        <Stage environment="city" intensity={0.5} shadows="contact" adjustCamera={1.2}>
          <Model url={url} />
        </Stage>
      </Suspense>
      <OrbitControls makeDefault autoRotate={autoRotate} autoRotateSpeed={1.5} enablePan={false} />
    </Canvas>
  );
}
