import React, { useState } from 'react';
import './NGXControls.css';

interface NGXControlsProps {
  conversationState: 'idle' | 'listening' | 'speaking' | 'thinking' | 'success';
  isRecording: boolean;
  onStartRecording: () => void;
  onStopRecording: () => void;
  onEndConversation: () => void;
  conversationMode: 'voice' | 'text' | 'mixed';
  onModeChange: (mode: 'voice' | 'text' | 'mixed') => void;
}

export const NGXControls: React.FC<NGXControlsProps> = ({
  conversationState,
  isRecording,
  onStartRecording,
  onStopRecording,
  onEndConversation,
  conversationMode,
  onModeChange
}) => {
  const [showModeSelector, setShowModeSelector] = useState(false);

  const handleMainButtonClick = () => {
    if (conversationState === 'speaking' || conversationState === 'thinking') {
      return; // Disabled during these states
    }
    
    if (isRecording) {
      onStopRecording();
    } else {
      onStartRecording();
    }
  };

  const getMainButtonText = () => {
    switch (conversationState) {
      case 'idle':
        return isRecording ? 'Detener grabación' : 'Iniciar conversación';
      case 'listening':
        return 'Pausar escucha';
      case 'speaking':
        return 'Hablando...';
      case 'thinking':
        return 'Procesando...';
      case 'success':
        return '¡Completado!';
      default:
        return 'Hablar';
    }
  };

  const getMainButtonIcon = () => {
    switch (conversationState) {
      case 'idle':
        return isRecording ? '⏹️' : '🎤';
      case 'listening':
        return '⏸️';
      case 'speaking':
        return '🗣️';
      case 'thinking':
        return '🧠';
      case 'success':
        return '✅';
      default:
        return '🎤';
    }
  };

  const isMainButtonDisabled = () => {
    return conversationState === 'speaking' || conversationState === 'thinking';
  };

  const getModeIcon = (mode: 'voice' | 'text' | 'mixed') => {
    switch (mode) {
      case 'voice':
        return '🎤';
      case 'text':
        return '💬';
      case 'mixed':
        return '🔄';
      default:
        return '🎤';
    }
  };

  return (
    <div className="ngx-controls">
      {/* Main Action Button */}
      <div className="main-control-group">
        <button
          className={`main-action-btn ${conversationState} ${isRecording ? 'recording' : ''}`}
          onClick={handleMainButtonClick}
          disabled={isMainButtonDisabled()}
          aria-label={getMainButtonText()}
        >
          <div className="btn-content">
            <span className="btn-icon">{getMainButtonIcon()}</span>
            <span className="btn-text">{getMainButtonText()}</span>
          </div>
          
          {isRecording && (
            <div className="recording-indicator">
              <div className="recording-pulse" />
            </div>
          )}
        </button>
      </div>

      {/* Secondary Controls */}
      <div className="secondary-controls">
        {/* Mode Selector */}
        <div className="mode-selector-group">
          <button
            className={`mode-toggle-btn ${showModeSelector ? 'active' : ''}`}
            onClick={() => setShowModeSelector(!showModeSelector)}
            aria-label="Cambiar modo de conversación"
          >
            <span className="mode-icon">{getModeIcon(conversationMode)}</span>
            <span className="mode-text">Modo</span>
            <span className="chevron">▼</span>
          </button>
          
          {showModeSelector && (
            <div className="mode-selector-dropdown">
              <button
                className={`mode-option ${conversationMode === 'voice' ? 'active' : ''}`}
                onClick={() => {
                  onModeChange('voice');
                  setShowModeSelector(false);
                }}
              >
                <span className="option-icon">🎤</span>
                <span className="option-text">Solo Voz</span>
                <span className="option-desc">Conversación por voz únicamente</span>
              </button>
              
              <button
                className={`mode-option ${conversationMode === 'text' ? 'active' : ''}`}
                onClick={() => {
                  onModeChange('text');
                  setShowModeSelector(false);
                }}
              >
                <span className="option-icon">💬</span>
                <span className="option-text">Solo Texto</span>
                <span className="option-desc">Conversación por texto únicamente</span>
              </button>
              
              <button
                className={`mode-option ${conversationMode === 'mixed' ? 'active' : ''}`}
                onClick={() => {
                  onModeChange('mixed');
                  setShowModeSelector(false);
                }}
              >
                <span className="option-icon">🔄</span>
                <span className="option-text">Mixto</span>
                <span className="option-desc">Voz y texto combinados</span>
              </button>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="action-buttons">
          <button
            className="action-btn secondary"
            onClick={onEndConversation}
            disabled={conversationState === 'thinking'}
            aria-label="Finalizar conversación"
          >
            <span className="btn-icon">🚪</span>
            <span className="btn-text">Finalizar</span>
          </button>
          
          <button
            className="action-btn utility"
            onClick={() => {/* Handle settings */}}
            aria-label="Configuración"
          >
            <span className="btn-icon">⚙️</span>
            <span className="btn-text">Config</span>
          </button>
        </div>
      </div>

      {/* Status Bar */}
      <div className="status-bar">
        <div className="status-indicators">
          <div className={`connection-status ${conversationState !== 'idle' ? 'connected' : 'disconnected'}`}>
            <div className="status-dot" />
            <span className="status-text">
              {conversationState !== 'idle' ? 'Conectado' : 'Desconectado'}
            </span>
          </div>
          
          <div className="mode-indicator">
            <span className="mode-badge">
              {getModeIcon(conversationMode)} {conversationMode.toUpperCase()}
            </span>
          </div>
        </div>
      </div>

      {/* Quick Actions (Touch Gestures) */}
      <div className="quick-actions">
        <div className="gesture-hint">
          <span className="hint-text">💡 Toca y mantén para hablar continuamente</span>
        </div>
      </div>
    </div>
  );
};

export default NGXControls;