import React, { useState, useRef, useEffect } from 'react';
import { NGXAudio3DVisual } from './NGXAudio3DVisual';
import { NGXControls } from './NGXControls';
import '../styles/NGXDesignTokens.css';
import './NGXGeminiInterface.css';

interface NGXGeminiInterfaceProps {
  isOpen?: boolean;
  onClose?: () => void;
  onStartConversation?: () => void;
  onEndConversation?: () => void;
  context?: {
    touchpoint: string;
    userIntent?: string;
    pageContext?: string;
  };
}

type ConversationState = 'idle' | 'listening' | 'speaking' | 'thinking' | 'success';
type ConversationMode = 'voice' | 'text' | 'mixed';

export const NGXGeminiInterface: React.FC<NGXGeminiInterfaceProps> = ({
  isOpen = false,
  onClose,
  onStartConversation,
  onEndConversation,
  context
}) => {
  const [conversationState, setConversationState] = useState<ConversationState>('idle');
  const [conversationMode, setConversationMode] = useState<ConversationMode>('voice');
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(420); // 7 minutes
  const [currentMessage, setCurrentMessage] = useState('');
  
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const micStreamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize audio context for real-time visualization
  useEffect(() => {
    if (isOpen) {
      initializeAudio();
      startTimer();
    } else {
      cleanupAudio();
      stopTimer();
    }
    
    return () => {
      cleanupAudio();
      stopTimer();
    };
  }, [isOpen]);

  const initializeAudio = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      micStreamRef.current = stream;
      
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      analyserRef.current = audioContextRef.current.createAnalyser();
      
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      
      analyserRef.current.fftSize = 256;
      startAudioAnalysis();
    } catch (error) {
      console.warn('Could not initialize audio:', error);
    }
  };

  const startAudioAnalysis = () => {
    if (!analyserRef.current) return;

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    
    const analyze = () => {
      if (!analyserRef.current) return;
      
      analyserRef.current.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
      const normalizedLevel = Math.min(average / 128, 1);
      
      setAudioLevel(normalizedLevel);
      
      if (isRecording) {
        requestAnimationFrame(analyze);
      }
    };
    
    analyze();
  };

  const cleanupAudio = () => {
    if (micStreamRef.current) {
      micStreamRef.current.getTracks().forEach(track => track.stop());
      micStreamRef.current = null;
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    analyserRef.current = null;
  };

  const startTimer = () => {
    timerRef.current = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          handleEndConversation();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const stopTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleStartRecording = async () => {
    setIsRecording(true);
    setConversationState('listening');
    startAudioAnalysis();
    onStartConversation?.();
  };

  const handleStopRecording = () => {
    setIsRecording(false);
    setConversationState('thinking');
    
    // Simulate processing time
    setTimeout(() => {
      setConversationState('speaking');
      simulateResponse();
    }, 1500);
  };

  const simulateResponse = () => {
    // Simulate agent speaking with random duration
    const speakingDuration = Math.random() * 3000 + 2000; // 2-5 seconds
    
    setTimeout(() => {
      setConversationState('idle');
      setCurrentMessage('');
    }, speakingDuration);
  };

  const handleEndConversation = () => {
    setConversationState('success');
    setIsRecording(false);
    stopTimer();
    
    setTimeout(() => {
      onEndConversation?.();
      onClose?.();
    }, 2000);
  };

  const getWelcomeMessage = () => {
    const touchpoint = context?.touchpoint || 'default';
    
    switch (touchpoint) {
      case 'landing-page':
        return '¡Hola! Soy tu asistente experto NGX. Veo que estás interesado en transformar tu vida. ¿Tienes 7 minutos para que conversemos sobre tu situación específica?';
      case 'lead-magnet':
        return '¡Excelente! Descargaste nuestro recurso. Soy tu asistente personal NGX. ¿Qué tal si conversamos 7 minutos sobre cómo aplicar esto a tu caso particular?';
      default:
        return '¡Hola! Soy tu asistente experto NGX. ¿Tienes 7 minutos para una conversación personalizada que podría cambiar tu perspectiva?';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="ngx-gemini-interface">
      {/* Backdrop */}
      <div className="ngx-backdrop" onClick={onClose} />
      
      {/* Main Interface */}
      <div className="ngx-interface-container">
        {/* Header */}
        <div className="ngx-header">
          <div className="ngx-header-content">
            <div className="ngx-logo-section">
              <div className="ngx-logo">NGX</div>
              <div className="ngx-title">
                <h2>Expert Assistant</h2>
                <p>Conversación Inteligente</p>
              </div>
            </div>
            
            <div className="ngx-session-info">
              <div className="ngx-time-badge">
                <span className="time-icon">⏱️</span>
                <span>{formatTime(timeRemaining)}</span>
              </div>
              <button className="ngx-close-btn" onClick={onClose} aria-label="Cerrar">
                ✕
              </button>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="ngx-main-content">
          {/* 3D Audio Visualization */}
          <div className="ngx-visual-section">
            <NGXAudio3DVisual
              state={conversationState}
              audioLevel={audioLevel}
              isRecording={isRecording}
            />
          </div>

          {/* Status Display */}
          <div className="ngx-status-section">
            <div className="ngx-status-indicator">
              {conversationState === 'idle' && (
                <div className="status-message">
                  <h3>Listo para conversar</h3>
                  <p>{getWelcomeMessage()}</p>
                </div>
              )}
              
              {conversationState === 'listening' && (
                <div className="status-message listening">
                  <h3>Te escucho atentamente...</h3>
                  <p>Habla con naturalidad sobre tu situación</p>
                </div>
              )}
              
              {conversationState === 'thinking' && (
                <div className="status-message thinking">
                  <h3>Analizando tu situación...</h3>
                  <p>Procesando tu información para darte la mejor respuesta</p>
                </div>
              )}
              
              {conversationState === 'speaking' && (
                <div className="status-message speaking">
                  <h3>Compartiendo insights...</h3>
                  <p>Escucha mis recomendaciones personalizadas para ti</p>
                </div>
              )}
              
              {conversationState === 'success' && (
                <div className="status-message success">
                  <h3>¡Conversación completada!</h3>
                  <p>Fue un placer ayudarte. Revisa tu email para los próximos pasos</p>
                </div>
              )}
            </div>
          </div>

          {/* Controls */}
          <div className="ngx-controls-section">
            <NGXControls
              conversationState={conversationState}
              isRecording={isRecording}
              onStartRecording={handleStartRecording}
              onStopRecording={handleStopRecording}
              onEndConversation={handleEndConversation}
              conversationMode={conversationMode}
              onModeChange={setConversationMode}
            />
          </div>
        </div>

        {/* Footer */}
        <div className="ngx-footer">
          <div className="ngx-footer-content">
            <div className="security-badge">
              <span className="security-icon">🔒</span>
              <span>Conversación segura y confidencial</span>
            </div>
            
            {context?.touchpoint && (
              <div className="context-badge">
                <span className="context-icon">📍</span>
                <span>{context.touchpoint.replace('-', ' ').toUpperCase()}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default NGXGeminiInterface;