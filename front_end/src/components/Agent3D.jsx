import { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import * as THREE from 'three'

// Professional Agent - Businessman with glasses
function ProfessionalFace() {
  const groupRef = useRef()
  const glassesRef = useRef()

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.1
    }
    if (glassesRef.current) {
      glassesRef.current.position.y = 0.15 + Math.sin(state.clock.elapsedTime * 2) * 0.02
    }
  })

  return (
    <group ref={groupRef}>
      {/* Cara circular */}
      <mesh position={[0, 0, 0]}>
        <cylinderGeometry args={[0.65, 0.65, 0.2, 32]} />
        <meshStandardMaterial color="#ffcc99" flatShading={false} />
      </mesh>
      
      {/* Ojos */}
      <mesh position={[-0.22, 0.15, 0.11]}>
        <sphereGeometry args={[0.08, 16, 16]} />
        <meshStandardMaterial color="#000000" />
      </mesh>
      <mesh position={[0.22, 0.15, 0.11]}>
        <sphereGeometry args={[0.08, 16, 16]} />
        <meshStandardMaterial color="#000000" />
      </mesh>
      
      {/* Lentes */}
      <group ref={glassesRef}>
        {/* Lente izquierdo */}
        <mesh position={[-0.22, 0.15, 0.15]}>
          <torusGeometry args={[0.12, 0.02, 16, 32]} />
          <meshStandardMaterial color="#333333" metalness={0.8} roughness={0.2} />
        </mesh>
        {/* Lente derecho */}
        <mesh position={[0.22, 0.15, 0.15]}>
          <torusGeometry args={[0.12, 0.02, 16, 32]} />
          <meshStandardMaterial color="#333333" metalness={0.8} roughness={0.2} />
        </mesh>
        {/* Puente */}
        <mesh position={[0, 0.15, 0.15]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.015, 0.015, 0.08, 8]} />
          <meshStandardMaterial color="#333333" />
        </mesh>
      </group>
      
      {/* Boca seria */}
      <mesh position={[0, -0.15, 0.11]}>
        <boxGeometry args={[0.25, 0.03, 0.02]} />
        <meshStandardMaterial color="#cc6666" />
      </mesh>
      
      {/* Corbata */}
      <mesh position={[0, -0.5, 0.08]} rotation={[0, 0, 0]}>
        <coneGeometry args={[0.1, 0.3, 3]} />
        <meshStandardMaterial color="#4f9eff" />
      </mesh>
    </group>
  )
}

// Communication Agent - Happy with big smile
function CommunicationFace() {
  const groupRef = useRef()
  const eyesRef = useRef()

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.6) * 0.15
      groupRef.current.position.y = Math.sin(state.clock.elapsedTime * 2) * 0.08
    }
    
    // Parpadeo
    if (eyesRef.current) {
      const blink = Math.sin(state.clock.elapsedTime * 3) > 0.92
      eyesRef.current.scale.y = blink ? 0.1 : 1
    }
  })

  return (
    <group ref={groupRef}>
      {/* Cara circular */}
      <mesh position={[0, 0, 0]}>
        <cylinderGeometry args={[0.65, 0.65, 0.2, 32]} />
        <meshStandardMaterial color="#ffe4b5" />
      </mesh>
      
      {/* Ojos grandes */}
      <group ref={eyesRef}>
        {/* Ojo izquierdo */}
        <mesh position={[-0.22, 0.12, 0.11]}>
          <sphereGeometry args={[0.12, 16, 16]} />
          <meshStandardMaterial color="#ffffff" />
        </mesh>
        <mesh position={[-0.22, 0.12, 0.22]}>
          <sphereGeometry args={[0.06, 16, 16]} />
          <meshStandardMaterial color="#000000" />
        </mesh>
        
        {/* Ojo derecho */}
        <mesh position={[0.22, 0.12, 0.11]}>
          <sphereGeometry args={[0.12, 16, 16]} />
          <meshStandardMaterial color="#ffffff" />
        </mesh>
        <mesh position={[0.22, 0.12, 0.22]}>
          <sphereGeometry args={[0.06, 16, 16]} />
          <meshStandardMaterial color="#000000" />
        </mesh>
      </group>
      
      {/* Gran sonrisa */}
      <mesh position={[0, -0.15, 0.11]} rotation={[0, 0, Math.PI]}>
        <torusGeometry args={[0.28, 0.05, 16, 32, Math.PI]} />
        <meshStandardMaterial color="#ff6b9d" />
      </mesh>
      
      {/* Mejillas rosadas */}
      <mesh position={[-0.48, -0.05, 0.05]}>
        <sphereGeometry args={[0.12, 16, 16]} />
        <meshStandardMaterial color="#ffaacc" />
      </mesh>
      <mesh position={[0.48, -0.05, 0.05]}>
        <sphereGeometry args={[0.12, 16, 16]} />
        <meshStandardMaterial color="#ffaacc" />
      </mesh>
      
      {/* Lengua */}
      <mesh position={[0, -0.22, 0.13]} rotation={[Math.PI / 4, 0, 0]}>
        <boxGeometry args={[0.12, 0.08, 0.03]} />
        <meshStandardMaterial color="#ff6b9d" />
      </mesh>
    </group>
  )
}

// Knowledge Agent - Wise with book on head
function KnowledgeFace() {
  const groupRef = useRef()
  const bookRef = useRef()

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.3) * 0.1
    }
    
    if (bookRef.current) {
      bookRef.current.rotation.y = state.clock.elapsedTime * 0.5
      bookRef.current.position.y = 0.75 + Math.sin(state.clock.elapsedTime * 2) * 0.05
    }
  })

  return (
    <group ref={groupRef}>
      {/* Cara circular */}
      <mesh position={[0, 0, 0]}>
        <cylinderGeometry args={[0.65, 0.65, 0.2, 32]} />
        <meshStandardMaterial color="#f5deb3" />
      </mesh>
      
      {/* Ojos pensativos */}
      <mesh position={[-0.22, 0.12, 0.11]}>
        <boxGeometry args={[0.15, 0.08, 0.02]} />
        <meshStandardMaterial color="#000000" />
      </mesh>
      <mesh position={[0.22, 0.12, 0.11]}>
        <boxGeometry args={[0.15, 0.08, 0.02]} />
        <meshStandardMaterial color="#000000" />
      </mesh>
      
      {/* Cejas */}
      <mesh position={[-0.22, 0.25, 0.11]} rotation={[0, 0, 0.2]}>
        <boxGeometry args={[0.18, 0.03, 0.02]} />
        <meshStandardMaterial color="#8b7355" />
      </mesh>
      <mesh position={[0.22, 0.25, 0.11]} rotation={[0, 0, -0.2]}>
        <boxGeometry args={[0.18, 0.03, 0.02]} />
        <meshStandardMaterial color="#8b7355" />
      </mesh>
      
      {/* Boca pensativa */}
      <mesh position={[0, -0.18, 0.11]}>
        <boxGeometry args={[0.2, 0.03, 0.02]} />
        <meshStandardMaterial color="#996666" />
      </mesh>
      
      {/* Barba */}
      <mesh position={[0, -0.4, 0.08]}>
        <boxGeometry args={[0.3, 0.25, 0.15]} />
        <meshStandardMaterial color="#c8a882" />
      </mesh>
      
      {/* Libro flotante */}
      <group ref={bookRef} position={[0, 0.75, 0]}>
        <mesh>
          <boxGeometry args={[0.35, 0.45, 0.12]} />
          <meshStandardMaterial color="#a78bfa" />
        </mesh>
        <mesh position={[0, 0, 0.07]}>
          <boxGeometry args={[0.32, 0.42, 0.02]} />
          <meshStandardMaterial color="#ffffff" />
        </mesh>
        {/* Líneas del libro */}
        {[-0.1, -0.05, 0, 0.05, 0.1].map((y, i) => (
          <mesh key={i} position={[0, y, 0.08]}>
            <boxGeometry args={[0.25, 0.01, 0.01]} />
            <meshStandardMaterial color="#666666" />
          </mesh>
        ))}
      </group>
    </group>
  )
}

// Decision Agent - Two-faced (left/right thinking)
function DecisionFace() {
  const groupRef = useRef()
  const leftSideRef = useRef()
  const rightSideRef = useRef()

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.4) * 0.12
    }
    
    const balance = Math.sin(state.clock.elapsedTime * 1.5)
    
    // Lado izquierdo brilla cuando está activo
    if (leftSideRef.current) {
      leftSideRef.current.material.emissiveIntensity = balance > 0 ? balance * 0.5 : 0
    }
    
    // Lado derecho brilla cuando está activo
    if (rightSideRef.current) {
      rightSideRef.current.material.emissiveIntensity = balance < 0 ? -balance * 0.5 : 0
    }
  })

  return (
    <group ref={groupRef}>
      {/* Cara dividida */}
      {/* Lado izquierdo - Rosa */}
      <mesh position={[-0.33, 0, 0]} ref={leftSideRef}>
        <cylinderGeometry args={[0.33, 0.33, 0.2, 32, 1, false, 0, Math.PI]} />
        <meshStandardMaterial color="#ff99cc" emissive="#ff99cc" />
      </mesh>
      
      {/* Lado derecho - Púrpura */}
      <mesh position={[0.33, 0, 0]} rotation={[0, Math.PI, 0]} ref={rightSideRef}>
        <cylinderGeometry args={[0.33, 0.33, 0.2, 32, 1, false, 0, Math.PI]} />
        <meshStandardMaterial color="#bb99ff" emissive="#bb99ff" />
      </mesh>
      
      {/* Ojo izquierdo */}
      <mesh position={[-0.22, 0.12, 0.11]}>
        <sphereGeometry args={[0.09, 16, 16]} />
        <meshStandardMaterial color="#000000" />
      </mesh>
      
      {/* Ojo derecho */}
      <mesh position={[0.22, 0.12, 0.11]}>
        <sphereGeometry args={[0.09, 16, 16]} />
        <meshStandardMaterial color="#000000" />
      </mesh>
      
      {/* Boca neutral/pensativa */}
      <mesh position={[0, -0.15, 0.11]}>
        <boxGeometry args={[0.3, 0.04, 0.02]} />
        <meshStandardMaterial color="#8b4789" />
      </mesh>
      
      {/* Balanza en la cabeza */}
      <group position={[0, 0.7, 0]}>
        <mesh>
          <cylinderGeometry args={[0.02, 0.02, 0.25, 8]} />
          <meshStandardMaterial color="#ffd700" metalness={0.8} />
        </mesh>
        <mesh position={[0, 0.15, 0]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.02, 0.02, 0.6, 8]} />
          <meshStandardMaterial color="#ffd700" metalness={0.8} />
        </mesh>
        {/* Platos */}
        <mesh position={[-0.28, 0.1, 0]}>
          <cylinderGeometry args={[0.12, 0.12, 0.02, 16]} />
          <meshStandardMaterial color="#ffed4e" />
        </mesh>
        <mesh position={[0.28, 0.1, 0]}>
          <cylinderGeometry args={[0.12, 0.12, 0.02, 16]} />
          <meshStandardMaterial color="#ffed4e" />
        </mesh>
      </group>
    </group>
  )
}

// General Agent - Robot style
function GeneralFace() {
  const groupRef = useRef()
  const antennaRef = useRef()

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.group.rotation.y = Math.sin(state.clock.elapsedTime * 0.35) * 0.1
    }
    
    if (antennaRef.current) {
      antennaRef.current.material.emissiveIntensity = 0.7 + Math.sin(state.clock.elapsedTime * 4) * 0.3
    }
  })

  return (
    <group ref={groupRef}>
      {/* Cara cuadrada de robot */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[0.8, 0.9, 0.2]} />
        <meshStandardMaterial color="#9ab5d1" metalness={0.6} roughness={0.3} />
      </mesh>
      
      {/* Pantalla/visor */}
      <mesh position={[0, 0.1, 0.11]}>
        <boxGeometry args={[0.65, 0.35, 0.02]} />
        <meshStandardMaterial 
          color="#00ff88" 
          emissive="#00ff88"
          emissiveIntensity={0.6}
        />
      </mesh>
      
      {/* Ojos digitales */}
      <mesh position={[-0.15, 0.1, 0.12]}>
        <boxGeometry args={[0.12, 0.15, 0.01]} />
        <meshStandardMaterial color="#003322" />
      </mesh>
      <mesh position={[0.15, 0.1, 0.12]}>
        <boxGeometry args={[0.12, 0.15, 0.01]} />
        <meshStandardMaterial color="#003322" />
      </mesh>
      
      {/* Pupilas digitales */}
      <mesh position={[-0.15, 0.1, 0.13]}>
        <boxGeometry args={[0.05, 0.08, 0.01]} />
        <meshStandardMaterial 
          color="#00ffff" 
          emissive="#00ffff"
          emissiveIntensity={1}
        />
      </mesh>
      <mesh position={[0.15, 0.1, 0.13]}>
        <boxGeometry args={[0.05, 0.08, 0.01]} />
        <meshStandardMaterial 
          color="#00ffff" 
          emissive="#00ffff"
          emissiveIntensity={1}
        />
      </mesh>
      
      {/* Rejilla de voz */}
      <group position={[0, -0.25, 0.11]}>
        {[-0.2, -0.1, 0, 0.1, 0.2].map((x, i) => (
          <mesh key={i} position={[x, 0, 0]}>
            <boxGeometry args={[0.03, 0.2, 0.02]} />
            <meshStandardMaterial color="#556677" />
          </mesh>
        ))}
      </group>
      
      {/* Antena */}
      <group position={[0.3, 0.45, 0]}>
        <mesh>
          <cylinderGeometry args={[0.02, 0.02, 0.22, 8]} />
          <meshStandardMaterial color="#7a8ca0" />
        </mesh>
        <mesh position={[0, 0.12, 0]} ref={antennaRef}>
          <sphereGeometry args={[0.06, 8, 8]} />
          <meshStandardMaterial 
            color="#ff4444" 
            emissive="#ff0000"
            emissiveIntensity={0.8}
          />
        </mesh>
      </group>
      
      {/* Tornillos decorativos */}
      <mesh position={[-0.35, 0.4, 0.11]}>
        <cylinderGeometry args={[0.03, 0.03, 0.02, 8]} />
        <meshStandardMaterial color="#334455" />
      </mesh>
      <mesh position={[0.35, 0.4, 0.11]}>
        <cylinderGeometry args={[0.03, 0.03, 0.02, 8]} />
        <meshStandardMaterial color="#334455" />
      </mesh>
    </group>
  )
}

// Main component
export function Agent3D({ agentId, size = 100 }) {
  const getFaceComponent = () => {
    switch (agentId?.toLowerCase()) {
      case 'professional':
        return <ProfessionalFace />
      case 'communication':
        return <CommunicationFace />
      case 'knowledge':
        return <KnowledgeFace />
      case 'decision':
        return <DecisionFace />
      case 'general':
        return <GeneralFace />
      default:
        return <GeneralFace />
    }
  }

  return (
    <div style={{ width: size, height: size }}>
      <Canvas
        camera={{ position: [0, 0, 3.5], fov: 45 }}
        style={{ background: 'transparent' }}
      >
        <ambientLight intensity={1} />
        <directionalLight position={[5, 5, 5]} intensity={1} />
        <directionalLight position={[-3, -3, -3]} intensity={0.4} />
        <spotLight position={[0, 5, 3]} intensity={0.5} angle={0.3} />
        {getFaceComponent()}
      </Canvas>
    </div>
  )
}
