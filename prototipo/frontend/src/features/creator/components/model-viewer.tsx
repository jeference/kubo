"use client";

import { OrbitControls, Stage, useGLTF } from "@react-three/drei";
import { Canvas, useThree } from "@react-three/fiber";
import { Suspense, useEffect } from "react";
import { NeutralToneMapping, PMREMGenerator } from "three";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";

function Model({ url }: { url: string }) {
  const { scene } = useGLTF(url);
  return <primitive object={scene} />;
}

/** Soft studio light, generated locally, that keeps the colors close to the 2D image. */
function StudioLight() {
  const gl = useThree((state) => state.gl);
  const scene = useThree((state) => state.scene);

  useEffect(() => {
    const generator = new PMREMGenerator(gl);
    const { texture } = generator.fromScene(new RoomEnvironment(), 0.04);
    scene.environment = texture;
    return () => {
      scene.environment = null;
      texture.dispose();
      generator.dispose();
    };
  }, [gl, scene]);

  return null;
}

export function ModelViewer({ url, autoRotate }: { url: string; autoRotate: boolean }) {
  return (
    <Canvas
      camera={{ position: [0, 0.6, 3], fov: 35 }}
      dpr={[1, 2]}
      gl={{ toneMapping: NeutralToneMapping }}
      shadows
    >
      <color attach="background" args={["#f4f4f4"]} />
      <StudioLight />
      <Suspense fallback={null}>
        <Stage environment={null} intensity={0} shadows="contact" adjustCamera={1.2}>
          <Model url={url} />
        </Stage>
      </Suspense>
      <OrbitControls makeDefault autoRotate={autoRotate} autoRotateSpeed={1.5} enablePan={false} />
    </Canvas>
  );
}
