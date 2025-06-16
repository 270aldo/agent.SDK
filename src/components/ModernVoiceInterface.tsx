import React, { useState, useRef, useEffect } from 'react';
import { EnergyBall } from './EnergyBall';
import './ModernVoiceInterface.css';

interface VoiceInterfaceProps {
  size?: 'compact' | 'medium' | 'large' | 'fullscreen';
  position?: 'bottom-right' | 'bottom-left' | 'center' | 'top-right' | 'top-left';
  isOpen?: boolean;
  onToggle?: () => void;
  onStartConversation?: () => void;
  onEndConversation?: () => void;
  context?: {
    touchpoint: string;
    userIntent?: string;
    pageContext?: string;
    previousInteractions?: number;
  };
  branding?: {
    primaryColor?: string;
    secondaryColor?: string;
    logo?: string;
    companyName?: string;
  };
}

type ConversationState = 'idle' | 'listening' | 'speaking' | 'thinking' | 'success' | 'ended';

export const ModernVoiceInterface: React.FC<VoiceInterfaceProps> = ({
  size = 'medium',
  position = 'bottom-right',
  isOpen = false,
  onToggle,
  onStartConversation,
  onEndConversation,
  context,
  branding
}) => {
  const [conversationState, setConversationState] = useState<ConversationState>('idle');
  const [isExpanded, setIsExpanded] = useState(false);
  const [voiceActivity, setVoiceActivity] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(420); // 7 minutes in seconds
  const [messages, setMessages] = useState<Array<{
    id: string;
    text: string;
    sender: 'user' | 'agent';
    timestamp: Date;
  }>>([]);

  const audioRef = useRef<HTMLAudioElement>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Get contextual welcome message based on touchpoint
  const getWelcomeMessage = () => {
    const touchpoint = context?.touchpoint || 'default';
    const companyName = branding?.companyName || 'NGX';
    
    switch (touchpoint) {
      case 'landing-page':
        return `¡Hola! Soy el asistente experto de ${companyName}. Veo que estás interesado en transformar tu vida. ¿Tienes 7 minutos para que conversemos sobre tu situación específica?`;
      case 'lead-magnet':
        return `¡Excelente! Descargaste nuestro recurso. Soy tu asistente personal de ${companyName}. ¿Qué tal si conversamos 7 minutos sobre cómo aplicar esto a tu caso particular?`;
      case 'webinar-end':
        return `¡Increíble sesión! Soy el asistente de ${companyName}. Tengo 7 minutos para ayudarte con preguntas específicas sobre tu transformación. ¿Empezamos?`;
      case 'exit-intent':
        return `¡Espera un momento! Antes de irte, soy el asistente de ${companyName}. ¿Puedo hacerte 2 preguntas rápidas para enviarte algo personalizado?`;
      case 'email-campaign':
        return `¡Hola! Veo que interactuaste con nuestro email. Soy tu asistente personal de ${companyName}. ¿Hablamos 7 minutos sobre tu situación específica?`;
      default:
        return `¡Hola! Soy tu asistente experto de ${companyName}. ¿Tienes 7 minutos para una conversación personalizada que podría cambiar tu perspectiva?`;
    }
  };

  // Format time remaining
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Handle conversation start
  const handleStartConversation = async () => {
    setConversationState('listening');
    setIsExpanded(true);
    
    // Add welcome message
    const welcomeMessage = {
      id: Date.now().toString(),
      text: getWelcomeMessage(),
      sender: 'agent' as const,
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
    
    // Start 7-minute timer
    timerRef.current = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          handleEndConversation();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    
    onStartConversation?.();
  };

  // Handle conversation end
  const handleEndConversation = () => {
    setConversationState('ended');
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    
    setTimeout(() => {
      setConversationState('idle');
      setIsExpanded(false);
      setTimeRemaining(420);
      setMessages([]);
    }, 3000);
    
    onEndConversation?.();
  };

  // Handle voice activity simulation (would connect to real voice detection)
  useEffect(() => {
    if (conversationState === 'speaking') {
      const interval = setInterval(() => {
        setVoiceActivity(Math.random() * 0.8 + 0.2);
      }, 100);
      
      return () => clearInterval(interval);
    } else {
      setVoiceActivity(0);
    }
  }, [conversationState]);

  // Get container classes based on props
  const getContainerClasses = () => {
    const baseClasses = ['modern-voice-interface'];
    
    if (size) baseClasses.push(`size-${size}`);
    if (position) baseClasses.push(`position-${position}`);
    if (isExpanded) baseClasses.push('expanded');
    if (conversationState !== 'idle') baseClasses.push('active');
    
    return baseClasses.join(' ');
  };

  return (
    <div className={getContainerClasses()}>
      {/* Backdrop */}
      {isExpanded && (
        <div 
          className="interface-backdrop" 
          onClick={() => size !== 'fullscreen' && setIsExpanded(false)}
        />
      )}
      
      {/* Main interface container */}
      <div className="interface-container">
        {/* Compact trigger when collapsed */}
        {!isExpanded && (
          <div 
            className="interface-trigger"
            onClick={handleStartConversation}
            role="button"
            tabIndex={0}
            aria-label="Iniciar conversación con asistente experto"
          >
            <EnergyBall 
              size={size === 'fullscreen' ? 'large' : size} 
              state={conversationState}
              voiceActivity={voiceActivity}
            />
            
            {/* Floating hint */}
            <div className="trigger-hint">
              <div className="hint-bubble">
                <span>💬 ¿7 minutos para cambiar tu perspectiva?</span>
              </div>
            </div>
          </div>
        )}
        
        {/* Expanded conversation interface */}
        {isExpanded && (
          <div className="conversation-interface">
            {/* Header */}
            <div className="interface-header">
              <div className="header-content">
                <div className="header-info">
                  <h3>{branding?.companyName || 'NGX'} Expert Assistant</h3>
                  <div className="session-info">
                    <span className="time-badge">⏱️ {formatTime(timeRemaining)}</span>
                    <span className="status-badge">{conversationState}</span>
                  </div>
                </div>
                
                {size !== 'fullscreen' && (
                  <button 
                    className="close-button"
                    onClick={handleEndConversation}
                    aria-label="Cerrar conversación"
                  >
                    ✕
                  </button>
                )}
              </div>
            </div>
            
            {/* Energy Ball in conversation mode */}
            <div className="conversation-avatar">
              <EnergyBall 
                size={size === 'fullscreen' ? 'large' : 'medium'} 
                state={conversationState}
                voiceActivity={voiceActivity}
              />
            </div>
            
            {/* Conversation status */}
            <div className="conversation-status">
              {conversationState === 'listening' && (
                <div className="status-indicator listening">
                  <div className="pulse-rings">
                    <div className="pulse-ring"></div>
                    <div className="pulse-ring"></div>
                    <div className="pulse-ring"></div>
                  </div>
                  <span>Te escucho...</span>
                </div>
              )}
              
              {conversationState === 'speaking' && (
                <div className="status-indicator speaking">
                  <div className="sound-waves">
                    <div className="wave"></div>
                    <div className="wave"></div>
                    <div className="wave"></div>
                    <div className="wave"></div>
                  </div>
                  <span>Hablando...</span>
                </div>
              )}
              
              {conversationState === 'thinking' && (
                <div className="status-indicator thinking">
                  <div className="thinking-dots">
                    <div className="dot"></div>
                    <div className="dot"></div>
                    <div className="dot"></div>
                  </div>
                  <span>Analizando...</span>
                </div>
              )}
            </div>
            
            {/* Voice controls */}
            <div className="voice-controls">
              <button 
                className={`voice-button ${conversationState === 'listening' ? 'active' : ''}`}
                onClick={() => setConversationState(
                  conversationState === 'listening' ? 'idle' : 'listening'
                )}
                disabled={conversationState === 'speaking' || conversationState === 'thinking'}
              >
                {conversationState === 'listening' ? '🛑 Pausar' : '🎤 Hablar'}
              </button>
              
              <button 
                className="action-button secondary"
                onClick={handleEndConversation}
              >
                Finalizar conversación
              </button>
            </div>
            
            {/* Footer with context info */}
            <div className="interface-footer">
              <div className="footer-info">
                <span>🔒 Conversación segura y personalizada</span>
                {context?.touchpoint && (
                  <span className="context-tag">
                    📍 {context.touchpoint.replace('-', ' ').toUpperCase()}
                  </span>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Audio element for voice playback */}
      <audio ref={audioRef} style={{ display: 'none' }} />
    </div>
  );
};

export default ModernVoiceInterface;