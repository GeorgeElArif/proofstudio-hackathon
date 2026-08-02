import { Canvas } from "@react-three/fiber";
import { RoundedBox } from "@react-three/drei";
import { PS039_PROOF_LAYERS } from "./ps039ProofLayers";

type HeroProceduralProps = {
  progress: number;
};

function clamp(value: number, min = 0, max = 1) {
  return Math.min(max, Math.max(min, value));
}

function smoothstep(edge0: number, edge1: number, value: number) {
  const x = clamp((value - edge0) / (edge1 - edge0));
  return x * x * (3 - 2 * x);
}

function EvidenceCore({ progress }: HeroProceduralProps) {
  const stabilize = smoothstep(0.08, 0.28, progress);
  const split = smoothstep(0.28, 0.58, progress) * (1 - smoothstep(0.72, 0.95, progress));
  const room = smoothstep(0.76, 1, progress);
  const rotationY = -0.45 + stabilize * 0.3 + room * 0.28;
  const rotationX = 0.12 - split * 0.08;

  return (
    <group rotation={[rotationX, rotationY, 0]} position={[0, -0.1 + room * 0.12, 0]}>
      <group scale={[1 + stabilize * 0.035, 1 + stabilize * 0.035, 1 + stabilize * 0.035]}>
        <RoundedBox args={[2.1, 2.9, 0.68]} radius={0.12} smoothness={6}>
          <meshStandardMaterial
            color="#101317"
            metalness={0.76}
            roughness={0.34}
            emissive="#030506"
            emissiveIntensity={0.25}
          />
        </RoundedBox>
        <RoundedBox args={[1.72, 2.46, 0.72]} radius={0.08} smoothness={5} position={[0, 0, 0.02]}>
          <meshStandardMaterial
            color="#070808"
            metalness={0.52}
            roughness={0.48}
            emissive="#071213"
            emissiveIntensity={0.34 + stabilize * 0.28}
          />
        </RoundedBox>
        <RoundedBox args={[1.84, 0.055, 0.76]} radius={0.02} smoothness={3} position={[0, 1.18, 0.06]}>
          <meshStandardMaterial
            color="#7fe9f2"
            emissive="#22d8e6"
            emissiveIntensity={0.9 + stabilize * 0.6}
            roughness={0.72}
            transparent
            opacity={0.58}
          />
        </RoundedBox>
        <RoundedBox args={[1.84, 0.055, 0.76]} radius={0.02} smoothness={3} position={[0, -1.18, 0.06]}>
          <meshStandardMaterial
            color="#7fe9f2"
            emissive="#22d8e6"
            emissiveIntensity={0.9 + stabilize * 0.6}
            roughness={0.72}
            transparent
            opacity={0.58}
          />
        </RoundedBox>
        <RoundedBox args={[0.052, 2.34, 0.76]} radius={0.02} smoothness={3} position={[-0.92, 0, 0.06]}>
          <meshStandardMaterial
            color="#7fe9f2"
            emissive="#22d8e6"
            emissiveIntensity={0.65 + stabilize * 0.45}
            roughness={0.72}
            transparent
            opacity={0.42}
          />
        </RoundedBox>
        <RoundedBox args={[0.052, 2.34, 0.76]} radius={0.02} smoothness={3} position={[0.92, 0, 0.06]}>
          <meshStandardMaterial
            color="#7fe9f2"
            emissive="#22d8e6"
            emissiveIntensity={0.65 + stabilize * 0.45}
            roughness={0.72}
            transparent
            opacity={0.42}
          />
        </RoundedBox>
      </group>

      <group rotation={[Math.PI / 2, 0, 0]} scale={[1 + stabilize * 0.08, 1 + stabilize * 0.08, 1]}>
        <mesh position={[0, 0, -0.42]}>
          <torusGeometry args={[1.42, 0.012, 12, 96]} />
          <meshStandardMaterial color="#27323a" metalness={0.84} roughness={0.3} />
        </mesh>
        <mesh position={[0, 0, -0.49]} scale={[1.14, 1.14, 1]}>
          <torusGeometry args={[1.42, 0.008, 12, 96]} />
          <meshStandardMaterial
            color="#7fe9f2"
            emissive="#21c7d6"
            emissiveIntensity={0.35 + stabilize * 0.65}
            transparent
            opacity={0.55}
          />
        </mesh>
      </group>

      {PS039_PROOF_LAYERS.map((layer, index) => {
        const row = index - (PS039_PROOF_LAYERS.length - 1) / 2;
        const side = index % 2 === 0 ? -1 : 1;
        const y = row * 0.26 * split;
        const x = side * split * (1.1 + Math.abs(row) * 0.08);
        const z = 0.48 + split * (0.28 + index * 0.055) - room * 0.36;
        const cyan = layer.accent === "cyan";

        return (
          <group key={layer.id} position={[x, y, z]} rotation={[0, side * split * 0.18, 0]}>
            <RoundedBox args={[1.56, 0.12, 0.04]} radius={0.015} smoothness={3}>
              <meshStandardMaterial
                color={cyan ? "#132a2d" : "#3c2413"}
                emissive={cyan ? "#1fcbd8" : "#f08a24"}
                emissiveIntensity={(cyan ? 0.12 : 0.22) + split * (cyan ? 0.28 : 0.48)}
                metalness={0.54}
                roughness={0.46}
                transparent
                opacity={0.14 + split * 0.72}
              />
            </RoundedBox>
          </group>
        );
      })}
    </group>
  );
}

export default function HeroProcedural({ progress }: HeroProceduralProps) {
  return (
    <Canvas
      camera={{ position: [0, 0.12, 6], fov: 38 }}
      dpr={[1, 1.6]}
      frameloop="demand"
      gl={{ alpha: true, antialias: true, powerPreference: "high-performance" }}
    >
      <color attach="background" args={["#050505"]} />
      <ambientLight intensity={0.34} />
      <directionalLight position={[3, 4, 5]} intensity={1.3} color="#d8f7ff" />
      <directionalLight position={[-4, -2, 3]} intensity={0.5} color="#66dce7" />
      <pointLight position={[0, 1.6, 2.4]} intensity={1.4} color="#8ef7ff" />
      <EvidenceCore progress={progress} />
    </Canvas>
  );
}
