import { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Sphere, Torus } from '@react-three/drei'

function Logo() {
  const groupRef = useRef()
  const torusRef = useRef()

  useFrame((state) => {
    groupRef.current.rotation.y = state.clock.elapsedTime * 0.5
    torusRef.current.rotation.x = state.clock.elapsedTime * 0.7
  })

  return (
    <group ref={groupRef}>
      {/* Central sphere */}
      <Sphere args={[0.6, 32, 32]}>
        <meshStandardMaterial 
          color="#4f9eff" 
          metalness={0.8}
          roughness={0.2}
        />
      </Sphere>
      
      {/* Orbiting torus */}
      <group ref={torusRef}>
        <Torus args={[1.2, 0.15, 16, 32]}>
          <meshStandardMaterial 
            color="#00d9ff" 
            metalness={0.6}
            roughness={0.3}
          />
        </Torus>
      </group>

      {/* Small orbiting spheres */}
      <Sphere args={[0.15, 16, 16]} position={[1.2, 0, 0]}>
        <meshStandardMaterial color="#a78bfa" emissive="#a78bfa" emissiveIntensity={0.3} />
      </Sphere>
      <Sphere args={[0.15, 16, 16]} position={[-1.2, 0, 0]}>
        <meshStandardMaterial color="#f472b6" emissive="#f472b6" emissiveIntensity={0.3} />
      </Sphere>
    </group>
  )
}

export function Logo3D({ size = 40 }) {
  return (
    <div style={{ width: size, height: size }}>
      <Canvas camera={{ position: [0, 0, 5], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} color="#ffffff" />
        <pointLight position={[-10, -10, -10]} intensity={0.5} color="#4f9eff" />
        <spotLight position={[0, 10, 0]} intensity={0.5} color="#00d9ff" />
        <Logo />
      </Canvas>
    </div>
  )
}
