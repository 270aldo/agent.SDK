import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import './NGXAudio3DVisual.css';

interface NGXAudio3DVisualProps {
  state: 'idle' | 'listening' | 'speaking' | 'thinking' | 'success';
  audioLevel: number;
  isRecording: boolean;
}

export const NGXAudio3DVisual: React.FC<NGXAudio3DVisualProps> = ({
  state,
  audioLevel,
  isRecording
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const energyBallRef = useRef<THREE.Mesh | null>(null);
  const particlesRef = useRef<THREE.Points | null>(null);
  const frameRef = useRef<number>(0);
  
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize Three.js scene
  useEffect(() => {
    if (!containerRef.current) return;

    initializeScene();
    animate();
    setIsInitialized(true);

    return () => {
      cleanup();
    };
  }, []);

  // Update visual based on state and audio level
  useEffect(() => {
    if (!isInitialized) return;
    updateVisual();
  }, [state, audioLevel, isRecording, isInitialized]);

  const initializeScene = () => {
    if (!containerRef.current) return;

    const width = containerRef.current.offsetWidth;
    const height = containerRef.current.offsetHeight;

    // Scene
    sceneRef.current = new THREE.Scene();
    
    // Camera
    cameraRef.current = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    cameraRef.current.position.z = 5;

    // Renderer
    rendererRef.current = new THREE.WebGLRenderer({ 
      alpha: true, 
      antialias: true,
      powerPreference: "high-performance"
    });
    rendererRef.current.setSize(width, height);
    rendererRef.current.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    containerRef.current.appendChild(rendererRef.current.domElement);

    // Create main energy ball
    createEnergyBall();
    
    // Create particle system
    createParticleSystem();
  };

  const createEnergyBall = () => {
    if (!sceneRef.current) return;

    // Geometry
    const geometry = new THREE.SphereGeometry(1, 32, 32);
    
    // Material with NGX colors
    const material = new THREE.ShaderMaterial({
      uniforms: {
        time: { value: 0 },
        audioLevel: { value: 0 },
        state: { value: 0 }, // 0: idle, 1: listening, 2: speaking, 3: thinking, 4: success
        color1: { value: new THREE.Color(0x8B5CF6) }, // Electric Violet
        color2: { value: new THREE.Color(0x5B21B6) }, // Deep Purple
        color3: { value: new THREE.Color(0x000000) }  // Black Onyx
      },
      vertexShader: `
        uniform float time;
        uniform float audioLevel;
        uniform float state;
        varying vec2 vUv;
        varying vec3 vPosition;
        varying vec3 vNormal;
        
        void main() {
          vUv = uv;
          vNormal = normal;
          
          vec3 pos = position;
          
          // Dynamic morphing based on audio and state
          float morphFactor = 0.1 * audioLevel * sin(time * 2.0 + position.y * 5.0);
          
          // Different morphing patterns by state
          if (state == 1.0) { // listening
            morphFactor += 0.05 * sin(time * 3.0 + position.x * 8.0);
          } else if (state == 2.0) { // speaking
            morphFactor += 0.15 * audioLevel * sin(time * 4.0 + position.z * 6.0);
          } else if (state == 3.0) { // thinking
            morphFactor += 0.08 * sin(time * 1.5 + length(position) * 4.0);
          }
          
          pos += normal * morphFactor;
          vPosition = pos;
          
          gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
        }
      `,
      fragmentShader: `
        uniform float time;
        uniform float audioLevel;
        uniform float state;
        uniform vec3 color1;
        uniform vec3 color2;
        uniform vec3 color3;
        varying vec2 vUv;
        varying vec3 vPosition;
        varying vec3 vNormal;
        
        void main() {
          vec3 color = color1;
          
          // Base color mixing
          float mixFactor = sin(time * 0.5 + vUv.x * 3.14159) * 0.5 + 0.5;
          color = mix(color1, color2, mixFactor);
          
          // Audio reactive intensity
          float intensity = 0.5 + audioLevel * 0.8;
          
          // State-specific effects
          if (state == 1.0) { // listening - pulsing violet
            color = mix(color, color1, sin(time * 6.0) * 0.3 + 0.7);
            intensity *= 1.2;
          } else if (state == 2.0) { // speaking - dynamic gradient
            color = mix(color1, color2, sin(time * 4.0 + vUv.y * 6.28) * 0.5 + 0.5);
            intensity *= (1.0 + audioLevel);
          } else if (state == 3.0) { // thinking - slower pulse
            color = mix(color2, color3, sin(time * 2.0) * 0.4 + 0.6);
            intensity *= 0.9;
          } else if (state == 4.0) { // success - bright flash
            color = mix(color1, vec3(0.0, 1.0, 0.0), 0.3);
            intensity *= 1.5;
          }
          
          // Fresnel effect
          vec3 viewDirection = normalize(cameraPosition - vPosition);
          float fresnel = 1.0 - max(0.0, dot(viewDirection, vNormal));
          fresnel = pow(fresnel, 2.0);
          
          // Glow effect
          float glow = fresnel * intensity;
          color += glow * 0.3;
          
          // Final alpha with glow
          float alpha = 0.8 + fresnel * 0.4;
          
          gl_FragColor = vec4(color * intensity, alpha);
        }
      `,
      transparent: true,
      blending: THREE.AdditiveBlending
    });

    energyBallRef.current = new THREE.Mesh(geometry, material);
    sceneRef.current.add(energyBallRef.current);
  };

  const createParticleSystem = () => {
    if (!sceneRef.current) return;

    const particleCount = 200;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const velocities = new Float32Array(particleCount * 3);

    // Initialize particles in sphere
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3;
      const phi = Math.acos(-1 + (2 * i) / particleCount);
      const theta = Math.sqrt(particleCount * Math.PI) * phi;

      positions[i3] = Math.cos(theta) * Math.sin(phi) * 2;
      positions[i3 + 1] = Math.sin(theta) * Math.sin(phi) * 2;
      positions[i3 + 2] = Math.cos(phi) * 2;

      velocities[i3] = (Math.random() - 0.5) * 0.02;
      velocities[i3 + 1] = (Math.random() - 0.5) * 0.02;
      velocities[i3 + 2] = (Math.random() - 0.5) * 0.02;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('velocity', new THREE.BufferAttribute(velocities, 3));

    const material = new THREE.ShaderMaterial({
      uniforms: {
        time: { value: 0 },
        audioLevel: { value: 0 },
        state: { value: 0 },
        color: { value: new THREE.Color(0x8B5CF6) }
      },
      vertexShader: `
        uniform float time;
        uniform float audioLevel;
        uniform float state;
        attribute vec3 velocity;
        varying float vOpacity;
        
        void main() {
          vec3 pos = position;
          
          // Particle movement based on state
          if (state == 1.0) { // listening - inward flow
            pos += velocity * time * 0.5;
            pos *= 1.0 + sin(time * 2.0) * 0.1 * audioLevel;
          } else if (state == 2.0) { // speaking - outward burst
            pos += velocity * time * (1.0 + audioLevel * 2.0);
          } else if (state == 3.0) { // thinking - orbital motion
            float angle = time * 0.5 + length(position) * 0.1;
            pos.x += cos(angle) * 0.1;
            pos.z += sin(angle) * 0.1;
          }
          
          vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
          gl_Position = projectionMatrix * mvPosition;
          
          // Size based on distance and audio
          gl_PointSize = (20.0 / -mvPosition.z) * (1.0 + audioLevel);
          
          // Opacity based on state
          vOpacity = 0.3 + audioLevel * 0.7;
          if (state == 0.0) vOpacity *= 0.5; // idle - dimmer
        }
      `,
      fragmentShader: `
        uniform vec3 color;
        varying float vOpacity;
        
        void main() {
          float distanceToCenter = distance(gl_PointCoord, vec2(0.5, 0.5));
          float alpha = 1.0 - smoothstep(0.0, 0.5, distanceToCenter);
          
          gl_FragColor = vec4(color, alpha * vOpacity);
        }
      `,
      transparent: true,
      blending: THREE.AdditiveBlending
    });

    particlesRef.current = new THREE.Points(geometry, material);
    sceneRef.current.add(particlesRef.current);
  };

  const updateVisual = () => {
    if (!energyBallRef.current || !particlesRef.current) return;

    const energyMaterial = energyBallRef.current.material as THREE.ShaderMaterial;
    const particleMaterial = particlesRef.current.material as THREE.ShaderMaterial;

    // Update uniforms
    energyMaterial.uniforms.audioLevel.value = audioLevel;
    particleMaterial.uniforms.audioLevel.value = audioLevel;

    // Map state to number
    const stateMap = {
      idle: 0,
      listening: 1,
      speaking: 2,
      thinking: 3,
      success: 4
    };

    const stateValue = stateMap[state] || 0;
    energyMaterial.uniforms.state.value = stateValue;
    particleMaterial.uniforms.state.value = stateValue;
  };

  const animate = () => {
    frameRef.current = requestAnimationFrame(animate);

    if (!sceneRef.current || !rendererRef.current || !cameraRef.current) return;

    const time = Date.now() * 0.001;

    // Update shader uniforms
    if (energyBallRef.current) {
      const material = energyBallRef.current.material as THREE.ShaderMaterial;
      material.uniforms.time.value = time;
    }

    if (particlesRef.current) {
      const material = particlesRef.current.material as THREE.ShaderMaterial;
      material.uniforms.time.value = time;
    }

    // Rotate energy ball
    if (energyBallRef.current) {
      energyBallRef.current.rotation.y = time * 0.5;
      energyBallRef.current.rotation.x = Math.sin(time * 0.3) * 0.1;
    }

    // Rotate particles
    if (particlesRef.current) {
      particlesRef.current.rotation.y = time * 0.2;
    }

    rendererRef.current.render(sceneRef.current, cameraRef.current);
  };

  const cleanup = () => {
    if (frameRef.current) {
      cancelAnimationFrame(frameRef.current);
    }

    if (rendererRef.current && containerRef.current) {
      containerRef.current.removeChild(rendererRef.current.domElement);
      rendererRef.current.dispose();
    }

    // Dispose geometries and materials
    if (energyBallRef.current) {
      energyBallRef.current.geometry.dispose();
      (energyBallRef.current.material as THREE.Material).dispose();
    }

    if (particlesRef.current) {
      particlesRef.current.geometry.dispose();
      (particlesRef.current.material as THREE.Material).dispose();
    }
  };

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (!containerRef.current || !rendererRef.current || !cameraRef.current) return;

      const width = containerRef.current.offsetWidth;
      const height = containerRef.current.offsetHeight;

      cameraRef.current.aspect = width / height;
      cameraRef.current.updateProjectionMatrix();
      rendererRef.current.setSize(width, height);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className={`ngx-audio-3d-visual ${state}`}>
      <div ref={containerRef} className="three-container" />
      
      {/* Fallback 2D indicators for low-performance devices */}
      <div className="fallback-indicators">
        {state === 'listening' && (
          <div className="pulse-indicator">
            <div className="pulse-ring" />
            <div className="pulse-ring" />
            <div className="pulse-ring" />
          </div>
        )}
        
        {state === 'speaking' && (
          <div className="wave-indicator">
            <div className="wave" style={{ height: `${20 + audioLevel * 60}px` }} />
            <div className="wave" style={{ height: `${30 + audioLevel * 80}px` }} />
            <div className="wave" style={{ height: `${25 + audioLevel * 70}px` }} />
            <div className="wave" style={{ height: `${20 + audioLevel * 60}px` }} />
          </div>
        )}
        
        {state === 'thinking' && (
          <div className="thinking-indicator">
            <div className="thinking-dot" />
            <div className="thinking-dot" />
            <div className="thinking-dot" />
          </div>
        )}
      </div>
    </div>
  );
};

export default NGXAudio3DVisual;