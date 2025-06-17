import React, { useRef, useMemo, useEffect, useState } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Sphere, shaderMaterial } from '@react-three/drei';
import { extend } from '@react-three/fiber';
import * as THREE from 'three';

// Custom shader material for the energy ball effect
const EnergyBallMaterial = shaderMaterial(
  // Uniforms
  {
    time: 0,
    intensity: 1.0,
    pulseSpeed: 2.0,
    glowIntensity: 0.8,
    voiceActivity: 0.0,
    colorPrimary: new THREE.Color('#667eea'),
    colorSecondary: new THREE.Color('#764ba2'),
    colorAccent: new THREE.Color('#00d4ff'),
  },
  // Vertex shader
  `
    varying vec2 vUv;
    varying vec3 vPosition;
    varying vec3 vNormal;
    
    void main() {
      vUv = uv;
      vPosition = position;
      vNormal = normalize(normalMatrix * normal);
      
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  // Fragment shader
  `
    uniform float time;
    uniform float intensity;
    uniform float pulseSpeed;
    uniform float glowIntensity;
    uniform float voiceActivity;
    uniform vec3 colorPrimary;
    uniform vec3 colorSecondary;
    uniform vec3 colorAccent;
    
    varying vec2 vUv;
    varying vec3 vPosition;
    varying vec3 vNormal;
    
    // Noise function
    float noise(vec3 p) {
      return fract(sin(dot(p, vec3(12.9898, 78.233, 54.453))) * 43758.5453);
    }
    
    // Fractal noise
    float fbm(vec3 p) {
      float value = 0.0;
      float amplitude = 0.5;
      float frequency = 1.0;
      
      for(int i = 0; i < 4; i++) {
        value += amplitude * noise(p * frequency);
        amplitude *= 0.5;
        frequency *= 2.0;
      }
      return value;
    }
    
    void main() {
      vec3 pos = vPosition * 2.0;
      
      // Base energy field
      float energyField = fbm(pos + time * 0.5);
      
      // Pulse effect
      float pulse = sin(time * pulseSpeed) * 0.5 + 0.5;
      pulse = mix(0.7, 1.0, pulse);
      
      // Voice activity influence
      float voiceInfluence = voiceActivity * sin(time * 8.0) * 0.3;
      
      // Core energy pattern
      float coreEnergy = energyField + pulse + voiceInfluence;
      
      // Color mixing based on energy
      vec3 color = mix(colorPrimary, colorSecondary, coreEnergy);
      color = mix(color, colorAccent, voiceActivity * 0.6);
      
      // Fresnel effect for rim lighting
      float fresnel = 1.0 - abs(dot(vNormal, vec3(0.0, 0.0, 1.0)));
      fresnel = pow(fresnel, 2.0);
      
      // Final color with glow
      color += fresnel * glowIntensity * colorAccent;
      
      // Alpha for transparency effects
      float alpha = mix(0.8, 1.0, intensity);
      
      gl_FragColor = vec4(color, alpha);
    }
  `
);

// Extend the material to be usable in JSX
extend({ EnergyBallMaterial });

interface EnergyBallCoreProps {
  size: 'compact' | 'medium' | 'large';
  state: 'idle' | 'listening' | 'speaking' | 'thinking' | 'success';
  voiceActivity?: number;
  className?: string;
}

// Inner 3D component that uses the Three.js context
function EnergyBallCore({ size, state, voiceActivity = 0 }: EnergyBallCoreProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<any>(null);
  
  // Size mapping
  const sizeScale = useMemo(() => {
    switch (size) {
      case 'compact': return 0.8;
      case 'medium': return 1.2;
      case 'large': return 2.0;
      default: return 1.0;
    }
  }, [size]);

  // State-based properties
  const stateProperties = useMemo(() => {
    switch (state) {
      case 'idle':
        return {
          intensity: 0.7,
          pulseSpeed: 1.5,
          glowIntensity: 0.6,
          rotationSpeed: 0.005,
        };
      case 'listening':
        return {
          intensity: 1.0,
          pulseSpeed: 3.0,
          glowIntensity: 1.0,
          rotationSpeed: 0.01,
        };
      case 'speaking':
        return {
          intensity: 1.2,
          pulseSpeed: 4.0,
          glowIntensity: 1.2,
          rotationSpeed: 0.015,
        };
      case 'thinking':
        return {
          intensity: 0.9,
          pulseSpeed: 2.5,
          glowIntensity: 0.8,
          rotationSpeed: 0.008,
        };
      case 'success':
        return {
          intensity: 1.5,
          pulseSpeed: 2.0,
          glowIntensity: 1.5,
          rotationSpeed: 0.02,
        };
      default:
        return {
          intensity: 0.7,
          pulseSpeed: 1.5,
          glowIntensity: 0.6,
          rotationSpeed: 0.005,
        };
    }
  }, [state]);

  useFrame((state) => {
    if (materialRef.current) {
      materialRef.current.time = state.clock.elapsedTime;
      materialRef.current.intensity = stateProperties.intensity;
      materialRef.current.pulseSpeed = stateProperties.pulseSpeed;
      materialRef.current.glowIntensity = stateProperties.glowIntensity;
      materialRef.current.voiceActivity = voiceActivity;
    }
    
    if (meshRef.current) {
      meshRef.current.rotation.y += stateProperties.rotationSpeed;
      meshRef.current.rotation.x += stateProperties.rotationSpeed * 0.5;
    }
  });

  return (
    <mesh ref={meshRef} scale={sizeScale}>
      <sphereGeometry args={[1, 64, 64]} />
      <energyBallMaterial
        ref={materialRef}
        transparent
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}

// Particles system for additional effects
function Particles({ count = 50, state }: { count?: number; state: string }) {
  const points = useRef<THREE.Points>(null);
  
  const particlesPosition = useMemo(() => {
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 4;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 4;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 4;
    }
    return positions;
  }, [count]);

  useFrame((frameState) => {
    if (points.current) {
      points.current.rotation.y += 0.002;
      
      // Animate particles based on state
      const time = frameState.clock.elapsedTime;
      const positions = points.current.geometry.attributes.position.array as Float32Array;
      
      for (let i = 0; i < count; i++) {
        const offset = i * 3;
        const radius = 2 + Math.sin(time + i * 0.1) * 0.5;
        const angle = time * 0.5 + i * 0.1;
        
        positions[offset] = Math.cos(angle) * radius;
        positions[offset + 1] = Math.sin(time + i * 0.05) * 0.5;
        positions[offset + 2] = Math.sin(angle) * radius;
      }
      
      points.current.geometry.attributes.position.needsUpdate = true;
    }
  });

  return (
    <points ref={points}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          array={particlesPosition}
          count={particlesPosition.length / 3}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.05}
        color="#00d4ff"
        transparent
        opacity={state === 'speaking' ? 0.8 : 0.4}
        sizeAttenuation
      />
    </points>
  );
}

// Main EnergyBall component
export const EnergyBall: React.FC<EnergyBallCoreProps> = ({
  size = 'medium',
  state = 'idle',
  voiceActivity = 0,
  className = ''
}) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div 
        className={`energy-ball-placeholder ${className}`}
        style={{
          width: size === 'compact' ? '80px' : size === 'medium' ? '120px' : '200px',
          height: size === 'compact' ? '80px' : size === 'medium' ? '120px' : '200px',
          borderRadius: '50%',
          background: 'linear-gradient(45deg, #667eea, #764ba2)',
          animation: 'pulse 2s infinite'
        }}
      />
    );
  }

  return (
    <div 
      className={`energy-ball-container ${className}`}
      style={{
        width: size === 'compact' ? '80px' : size === 'medium' ? '120px' : '200px',
        height: size === 'compact' ? '80px' : size === 'medium' ? '120px' : '200px',
        position: 'relative'
      }}
    >
      <Canvas
        camera={{ position: [0, 0, 3], fov: 50 }}
        style={{ width: '100%', height: '100%' }}
      >
        <ambientLight intensity={0.2} />
        <pointLight position={[10, 10, 10]} intensity={0.5} />
        <pointLight position={[-10, -10, -10]} intensity={0.3} color="#764ba2" />
        
        <EnergyBallCore 
          size={size} 
          state={state} 
          voiceActivity={voiceActivity} 
        />
        
        <Particles count={30} state={state} />
      </Canvas>
      
      {/* Outer glow effect */}
      <div 
        className="energy-ball-glow"
        style={{
          position: 'absolute',
          inset: '-20px',
          borderRadius: '50%',
          background: `radial-gradient(circle, rgba(102, 126, 234, ${state === 'speaking' ? 0.4 : 0.2}) 0%, transparent 70%)`,
          filter: 'blur(15px)',
          pointerEvents: 'none',
          animation: state === 'speaking' ? 'glow-pulse 0.5s infinite alternate' : 'glow-pulse 3s infinite alternate'
        }}
      />
      
      <style jsx>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.8; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.05); }
        }
        
        @keyframes glow-pulse {
          0% { opacity: 0.6; transform: scale(1); }
          100% { opacity: 1; transform: scale(1.1); }
        }
      `}</style>
    </div>
  );
};

export default EnergyBall;