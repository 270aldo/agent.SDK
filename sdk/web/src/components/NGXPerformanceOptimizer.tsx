/**
 * NGX Performance Optimizer
 * Advanced performance optimization for 3D components and heavy assets
 * Includes lazy loading, caching, device adaptation, and intelligent rendering
 */

import React, { 
  useState, 
  useEffect, 
  useRef, 
  useMemo, 
  useCallback,
  Suspense,
  lazy
} from 'react';
import { Canvas } from '@react-three/fiber';
import { Preload, useProgress } from '@react-three/drei';

interface PerformanceConfig {
  enableLazyLoading: boolean;
  enableCaching: boolean;
  adaptToDevice: boolean;
  maxTextureSize: number;
  shadowQuality: 'low' | 'medium' | 'high';
  antialias: boolean;
  powerPreference: 'default' | 'high-performance' | 'low-power';
  pixelRatio: number;
}

interface DeviceCapabilities {
  gpu: 'low' | 'medium' | 'high';
  memory: number;
  cores: number;
  mobile: boolean;
  webgl2: boolean;
  maxTextureSize: number;
  hardwareConcurrency: number;
}

interface AssetCache {
  textures: Map<string, any>;
  models: Map<string, any>;
  audio: Map<string, any>;
  shaders: Map<string, any>;
  lastAccessed: Map<string, number>;
  maxSize: number;
  currentSize: number;
}

// Lazy loaded components
const NGXAudio3DVisual = lazy(() => import('./NGXAudio3DVisual'));
const NGXGeminiInterface = lazy(() => import('./NGXGeminiInterface'));

// Component loader with fallback
const ComponentLoader: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { progress } = useProgress();
  
  return (
    <Suspense fallback={
      <div className="ngx-loading-container">
        <div className="ngx-loading-progress">
          <div 
            className="ngx-loading-bar"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p>Loading HIE Experience... {Math.round(progress)}%</p>
      </div>
    }>
      {children}
    </Suspense>
  );
};

class PerformanceOptimizer {
  private static instance: PerformanceOptimizer;
  private deviceCapabilities: DeviceCapabilities;
  private performanceConfig: PerformanceConfig;
  private assetCache: AssetCache;
  private frameCounter: number = 0;
  private lastFrameTime: number = 0;
  private avgFrameTime: number = 16.67; // Target 60fps
  private frameHistory: number[] = [];
  
  constructor() {
    this.deviceCapabilities = this.detectDeviceCapabilities();
    this.performanceConfig = this.generateOptimalConfig();
    this.assetCache = this.initializeCache();
    this.startPerformanceMonitoring();
  }
  
  static getInstance(): PerformanceOptimizer {
    if (!PerformanceOptimizer.instance) {
      PerformanceOptimizer.instance = new PerformanceOptimizer();
    }
    return PerformanceOptimizer.instance;
  }
  
  private detectDeviceCapabilities(): DeviceCapabilities {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
    
    let gpuTier: 'low' | 'medium' | 'high' = 'medium';
    let maxTextureSize = 2048;
    
    if (gl) {
      const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
      const renderer = debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : '';
      maxTextureSize = gl.getParameter(gl.MAX_TEXTURE_SIZE);
      
      // GPU tier detection based on renderer string
      if (renderer.includes('Intel') || renderer.includes('PowerVR')) {
        gpuTier = 'low';
      } else if (renderer.includes('GeForce') || renderer.includes('Radeon') || renderer.includes('Mali')) {
        gpuTier = 'high';
      }
    }
    
    // Memory estimation (rough)
    const memory = (navigator as any).deviceMemory || 4;
    
    return {
      gpu: gpuTier,
      memory,
      cores: navigator.hardwareConcurrency || 4,
      mobile: /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent),
      webgl2: !!canvas.getContext('webgl2'),
      maxTextureSize,
      hardwareConcurrency: navigator.hardwareConcurrency || 4
    };
  }
  
  private generateOptimalConfig(): PerformanceConfig {
    const device = this.deviceCapabilities;
    
    return {
      enableLazyLoading: true,
      enableCaching: device.memory >= 4,
      adaptToDevice: true,
      maxTextureSize: Math.min(device.maxTextureSize, device.mobile ? 1024 : 2048),
      shadowQuality: device.gpu === 'high' ? 'high' : device.gpu === 'medium' ? 'medium' : 'low',
      antialias: device.gpu !== 'low' && !device.mobile,
      powerPreference: device.mobile ? 'low-power' : 'high-performance',
      pixelRatio: Math.min(window.devicePixelRatio, device.mobile ? 2 : 3)
    };
  }
  
  private initializeCache(): AssetCache {
    const maxSize = this.deviceCapabilities.memory * 1024 * 1024 * 0.1; // 10% of device memory
    
    return {
      textures: new Map(),
      models: new Map(),
      audio: new Map(),
      shaders: new Map(),
      lastAccessed: new Map(),
      maxSize,
      currentSize: 0
    };
  }
  
  private startPerformanceMonitoring(): void {
    const monitor = () => {
      const now = performance.now();
      if (this.lastFrameTime > 0) {
        const frameTime = now - this.lastFrameTime;
        this.frameHistory.push(frameTime);
        
        // Keep only last 60 frames
        if (this.frameHistory.length > 60) {
          this.frameHistory.shift();
        }
        
        // Calculate average
        this.avgFrameTime = this.frameHistory.reduce((a, b) => a + b, 0) / this.frameHistory.length;
        
        // Auto-adjust quality if performance drops
        if (this.avgFrameTime > 20 && this.frameCounter % 60 === 0) {
          this.adaptPerformanceConfig();
        }
      }
      
      this.lastFrameTime = now;
      this.frameCounter++;
      requestAnimationFrame(monitor);
    };
    
    requestAnimationFrame(monitor);
  }
  
  private adaptPerformanceConfig(): void {
    if (this.avgFrameTime > 25) { // Below 40fps
      // Reduce quality
      if (this.performanceConfig.shadowQuality === 'high') {
        this.performanceConfig.shadowQuality = 'medium';
      } else if (this.performanceConfig.shadowQuality === 'medium') {
        this.performanceConfig.shadowQuality = 'low';
      }
      
      if (this.performanceConfig.antialias) {
        this.performanceConfig.antialias = false;
      }
      
      if (this.performanceConfig.pixelRatio > 1) {
        this.performanceConfig.pixelRatio = Math.max(1, this.performanceConfig.pixelRatio - 0.5);
      }
    } else if (this.avgFrameTime < 15) { // Above 65fps, can increase quality
      if (this.performanceConfig.shadowQuality === 'low' && this.deviceCapabilities.gpu !== 'low') {
        this.performanceConfig.shadowQuality = 'medium';
      } else if (this.performanceConfig.shadowQuality === 'medium' && this.deviceCapabilities.gpu === 'high') {
        this.performanceConfig.shadowQuality = 'high';
      }
    }
  }
  
  cacheAsset(key: string, asset: any, type: keyof AssetCache): void {
    if (!this.performanceConfig.enableCaching) return;
    
    const cache = this.assetCache[type] as Map<string, any>;
    const estimatedSize = this.estimateAssetSize(asset);
    
    // Clean cache if necessary
    if (this.assetCache.currentSize + estimatedSize > this.assetCache.maxSize) {
      this.cleanCache();
    }
    
    cache.set(key, asset);
    this.assetCache.lastAccessed.set(key, Date.now());
    this.assetCache.currentSize += estimatedSize;
  }
  
  getCachedAsset(key: string, type: keyof AssetCache): any {
    if (!this.performanceConfig.enableCaching) return null;
    
    const cache = this.assetCache[type] as Map<string, any>;
    const asset = cache.get(key);
    
    if (asset) {
      this.assetCache.lastAccessed.set(key, Date.now());
      return asset;
    }
    
    return null;
  }
  
  private cleanCache(): void {
    // Remove least recently used assets
    const sortedEntries = Array.from(this.assetCache.lastAccessed.entries())
      .sort((a, b) => a[1] - b[1]);
    
    const toRemove = sortedEntries.slice(0, Math.floor(sortedEntries.length * 0.3));
    
    for (const [key] of toRemove) {
      // Remove from all cache types
      Object.keys(this.assetCache).forEach(cacheType => {
        if (cacheType !== 'lastAccessed' && cacheType !== 'maxSize' && cacheType !== 'currentSize') {
          const cache = this.assetCache[cacheType as keyof AssetCache] as Map<string, any>;
          cache.delete(key);
        }
      });
      this.assetCache.lastAccessed.delete(key);
    }
    
    // Recalculate cache size
    this.assetCache.currentSize = this.assetCache.currentSize * 0.7; // Approximate
  }
  
  private estimateAssetSize(asset: any): number {
    // Rough estimation of asset size in bytes
    if (asset instanceof HTMLImageElement) {
      return asset.width * asset.height * 4; // RGBA
    } else if (asset instanceof ArrayBuffer) {
      return asset.byteLength;
    } else if (typeof asset === 'string') {
      return asset.length * 2; // Unicode characters
    }
    return 1024; // Default 1KB
  }
  
  getConfig(): PerformanceConfig {
    return { ...this.performanceConfig };
  }
  
  getCapabilities(): DeviceCapabilities {
    return { ...this.deviceCapabilities };
  }
  
  getCurrentFPS(): number {
    return 1000 / this.avgFrameTime;
  }
}

// React Hook for performance optimization
export const usePerformanceOptimizer = () => {
  const optimizer = useMemo(() => PerformanceOptimizer.getInstance(), []);
  const [config, setConfig] = useState(optimizer.getConfig());
  const [fps, setFPS] = useState(60);
  
  useEffect(() => {
    const interval = setInterval(() => {
      setConfig(optimizer.getConfig());
      setFPS(optimizer.getCurrentFPS());
    }, 1000);
    
    return () => clearInterval(interval);
  }, [optimizer]);
  
  return { optimizer, config, fps, capabilities: optimizer.getCapabilities() };
};

// Optimized Canvas Component
interface OptimizedCanvasProps {
  children: React.ReactNode;
  className?: string;
  fallback?: React.ReactNode;
}

export const OptimizedCanvas: React.FC<OptimizedCanvasProps> = ({ 
  children, 
  className,
  fallback 
}) => {
  const { config, capabilities } = usePerformanceOptimizer();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  const canvasProps = useMemo(() => ({
    gl: {
      powerPreference: config.powerPreference,
      antialias: config.antialias,
      alpha: true,
      premultipliedAlpha: false,
      preserveDrawingBuffer: false,
      failIfMajorPerformanceCaveat: capabilities.mobile
    },
    dpr: config.pixelRatio,
    performance: { min: 0.8 },
    frameloop: 'demand' as const,
    shadows: config.shadowQuality !== 'low'
  }), [config, capabilities]);
  
  // Fallback for low-end devices
  if (capabilities.gpu === 'low' && capabilities.mobile) {
    return (
      <div className={`ngx-canvas-fallback ${className || ''}`}>
        {fallback || (
          <div className="ngx-fallback-content">
            <div className="ngx-fallback-animation">
              <div className="ngx-energy-pulse"></div>
            </div>
            <p>Optimizing experience for your device...</p>
          </div>
        )}
      </div>
    );
  }
  
  return (
    <Canvas
      ref={canvasRef}
      className={className}
      {...canvasProps}
    >
      <ComponentLoader>
        {children}
        <Preload all />
      </ComponentLoader>
    </Canvas>
  );
};

// Lazy Loading Hook
export const useLazyLoad = <T extends any>(
  loader: () => Promise<T>,
  deps: React.DependencyList = []
) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const { optimizer } = usePerformanceOptimizer();
  
  const load = useCallback(async () => {
    const cacheKey = deps.join('-');
    const cached = optimizer.getCachedAsset(cacheKey, 'models');
    
    if (cached) {
      setData(cached);
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await loader();
      setData(result);
      optimizer.cacheAsset(cacheKey, result, 'models');
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Loading failed'));
    } finally {
      setLoading(false);
    }
  }, deps);
  
  useEffect(() => {
    load();
  }, [load]);
  
  return { data, loading, error, reload: load };
};

// Asset Preloader Component
interface AssetPreloaderProps {
  assets: Array<{
    type: 'texture' | 'model' | 'audio';
    url: string;
    key: string;
  }>;
  onProgress?: (progress: number) => void;
  onComplete?: () => void;
}

export const AssetPreloader: React.FC<AssetPreloaderProps> = ({
  assets,
  onProgress,
  onComplete
}) => {
  const { optimizer } = usePerformanceOptimizer();
  const [progress, setProgress] = useState(0);
  
  useEffect(() => {
    let loaded = 0;
    const total = assets.length;
    
    const updateProgress = () => {
      loaded++;
      const newProgress = (loaded / total) * 100;
      setProgress(newProgress);
      onProgress?.(newProgress);
      
      if (loaded === total) {
        onComplete?.();
      }
    };
    
    assets.forEach(async (asset) => {
      try {
        let loadedAsset;
        
        switch (asset.type) {
          case 'texture':
            loadedAsset = await loadTexture(asset.url);
            break;
          case 'model':
            loadedAsset = await loadModel(asset.url);
            break;
          case 'audio':
            loadedAsset = await loadAudio(asset.url);
            break;
        }
        
        optimizer.cacheAsset(asset.key, loadedAsset, asset.type === 'texture' ? 'textures' : 'models');
        updateProgress();
      } catch (error) {
        console.warn(`Failed to load asset: ${asset.url}`, error);
        updateProgress(); // Still count as "processed"
      }
    });
  }, [assets, optimizer, onProgress, onComplete]);
  
  return null; // This component doesn't render anything
};

// Asset loading utilities
const loadTexture = (url: string): Promise<HTMLImageElement> => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = url;
  });
};

const loadModel = async (url: string): Promise<any> => {
  try {
    const response = await fetch(url);
    return await response.arrayBuffer();
  } catch (error) {
    throw new Error(`Failed to load model: ${url}`);
  }
};

const loadAudio = (url: string): Promise<HTMLAudioElement> => {
  return new Promise((resolve, reject) => {
    const audio = new Audio();
    audio.oncanplaythrough = () => resolve(audio);
    audio.onerror = reject;
    audio.src = url;
  });
};

// Performance Monitor Component
export const PerformanceMonitor: React.FC = () => {
  const { fps, config, capabilities } = usePerformanceOptimizer();
  const [showDetails, setShowDetails] = useState(false);
  
  return (
    <div className="ngx-performance-monitor">
      <div 
        className="ngx-fps-display"
        onClick={() => setShowDetails(!showDetails)}
      >
        <span className={`ngx-fps-value ${fps < 30 ? 'warning' : fps < 50 ? 'caution' : 'good'}`}>
          {Math.round(fps)} FPS
        </span>
      </div>
      
      {showDetails && (
        <div className="ngx-performance-details">
          <h4>Performance Details</h4>
          <div className="ngx-detail-row">
            <span>GPU Tier:</span>
            <span>{capabilities.gpu}</span>
          </div>
          <div className="ngx-detail-row">
            <span>Shadow Quality:</span>
            <span>{config.shadowQuality}</span>
          </div>
          <div className="ngx-detail-row">
            <span>Pixel Ratio:</span>
            <span>{config.pixelRatio.toFixed(1)}</span>
          </div>
          <div className="ngx-detail-row">
            <span>Antialias:</span>
            <span>{config.antialias ? 'On' : 'Off'}</span>
          </div>
          <div className="ngx-detail-row">
            <span>Device:</span>
            <span>{capabilities.mobile ? 'Mobile' : 'Desktop'}</span>
          </div>
        </div>
      )}
      
      <style jsx>{`
        .ngx-performance-monitor {
          position: fixed;
          top: 20px;
          right: 20px;
          z-index: 1000;
          font-family: 'Segoe UI', sans-serif;
        }
        
        .ngx-fps-display {
          background: rgba(0, 0, 0, 0.8);
          color: white;
          padding: 8px 12px;
          border-radius: 4px;
          cursor: pointer;
          user-select: none;
        }
        
        .ngx-fps-value.good { color: #10B981; }
        .ngx-fps-value.caution { color: #F59E0B; }
        .ngx-fps-value.warning { color: #EF4444; }
        
        .ngx-performance-details {
          background: rgba(0, 0, 0, 0.9);
          color: white;
          padding: 12px;
          margin-top: 8px;
          border-radius: 4px;
          min-width: 200px;
        }
        
        .ngx-performance-details h4 {
          margin: 0 0 8px 0;
          font-size: 14px;
          color: #8B5CF6;
        }
        
        .ngx-detail-row {
          display: flex;
          justify-content: space-between;
          margin-bottom: 4px;
          font-size: 12px;
        }
        
        .ngx-canvas-fallback {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 400px;
          background: linear-gradient(135deg, #1F2937, #111827);
          border-radius: 12px;
          color: white;
        }
        
        .ngx-fallback-content {
          text-align: center;
        }
        
        .ngx-fallback-animation {
          margin-bottom: 20px;
        }
        
        .ngx-energy-pulse {
          width: 60px;
          height: 60px;
          background: radial-gradient(circle, #8B5CF6, #5B21B6);
          border-radius: 50%;
          animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
          0%, 100% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.2); opacity: 0.7; }
        }
        
        .ngx-loading-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 200px;
          color: white;
        }
        
        .ngx-loading-progress {
          width: 200px;
          height: 4px;
          background: rgba(255, 255, 255, 0.2);
          border-radius: 2px;
          margin-bottom: 16px;
          overflow: hidden;
        }
        
        .ngx-loading-bar {
          height: 100%;
          background: linear-gradient(90deg, #8B5CF6, #5B21B6);
          transition: width 0.3s ease;
        }
      `}</style>
    </div>
  );
};

export default PerformanceOptimizer;