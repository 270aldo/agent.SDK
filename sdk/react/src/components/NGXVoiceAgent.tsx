import React, { useEffect, useRef, useState, forwardRef, useImperativeHandle } from 'react';
import {
  NGXVoiceAgent as CoreAgent,
  NGXConfig,
  CustomerData,
  ConversationState,
  ConversationMessage,
  NGXEventMap
} from '@ngx/voice-agent-sdk';

export interface NGXVoiceAgentProps {
  config: NGXConfig;
  customerData?: CustomerData;
  autoStart?: boolean;
  onConversationStart?: (conversationId: string) => void;
  onConversationEnd?: (conversationId: string, reason: string) => void;
  onMessage?: (message: ConversationMessage, type: 'sent' | 'received') => void;
  onQualificationComplete?: (score: number, recommendation: string) => void;
  onError?: (error: Error, context?: string) => void;
  className?: string;
  style?: React.CSSProperties;
  children?: React.ReactNode;
}

export interface NGXVoiceAgentRef {
  start: (customerData?: CustomerData) => Promise<string>;
  sendMessage: (message: string) => Promise<ConversationMessage>;
  endConversation: () => Promise<void>;
  getState: () => ConversationState | null;
  isActive: () => boolean;
  playAudio: (audioUrl: string) => Promise<void>;
  stopAudio: () => void;
  setVoiceEnabled: (enabled: boolean) => void;
}

export const NGXVoiceAgent = forwardRef<NGXVoiceAgentRef, NGXVoiceAgentProps>(
  ({
    config,
    customerData,
    autoStart = false,
    onConversationStart,
    onConversationEnd,
    onMessage,
    onQualificationComplete,
    onError,
    className,
    style,
    children
  }, ref) => {
    const agentRef = useRef<CoreAgent | null>(null);
    const [isInitialized, setIsInitialized] = useState(false);
    const [conversationState, setConversationState] = useState<ConversationState | null>(null);
    const [error, setError] = useState<string | null>(null);

    // Initialize agent
    useEffect(() => {
      const initAgent = async () => {
        try {
          const agent = new CoreAgent();
          await agent.init(config);
          
          // Set up event listeners
          agent.on('conversation.started', ({ conversationId }) => {
            onConversationStart?.(conversationId);
          });

          agent.on('conversation.ended', ({ conversationId, reason }) => {
            setConversationState(null);
            onConversationEnd?.(conversationId, reason);
          });

          agent.on('message.sent', ({ message }) => {
            setConversationState(agent.getState());
            onMessage?.(message, 'sent');
          });

          agent.on('message.received', ({ message }) => {
            setConversationState(agent.getState());
            onMessage?.(message, 'received');
          });

          agent.on('qualification.completed', ({ score, recommendation }) => {
            onQualificationComplete?.(score, recommendation);
          });

          agent.on('error', ({ error, context }) => {
            setError(error.message);
            onError?.(error, context);
          });

          agentRef.current = agent;
          setIsInitialized(true);
          setError(null);

          // Auto-start if requested
          if (autoStart) {
            await agent.start(customerData);
          }
        } catch (err) {
          const error = err as Error;
          setError(error.message);
          onError?.(error, 'initialization');
        }
      };

      initAgent();

      // Cleanup
      return () => {
        if (agentRef.current) {
          agentRef.current.destroy();
          agentRef.current = null;
        }
      };
    }, [config]);

    // Update conversation state when agent state changes
    useEffect(() => {
      if (agentRef.current) {
        setConversationState(agentRef.current.getState());
      }
    }, [isInitialized]);

    // Expose methods via ref
    useImperativeHandle(ref, () => ({
      start: async (data?: CustomerData) => {
        if (!agentRef.current) {
          throw new Error('Agent not initialized');
        }
        const conversationId = await agentRef.current.start(data || customerData);
        setConversationState(agentRef.current.getState());
        return conversationId;
      },

      sendMessage: async (message: string) => {
        if (!agentRef.current) {
          throw new Error('Agent not initialized');
        }
        const response = await agentRef.current.sendMessage(message);
        setConversationState(agentRef.current.getState());
        return response;
      },

      endConversation: async () => {
        if (!agentRef.current) {
          throw new Error('Agent not initialized');
        }
        await agentRef.current.endConversation();
        setConversationState(null);
      },

      getState: () => {
        return agentRef.current?.getState() || null;
      },

      isActive: () => {
        return agentRef.current?.isActive() || false;
      },

      playAudio: async (audioUrl: string) => {
        if (!agentRef.current) {
          throw new Error('Agent not initialized');
        }
        await agentRef.current.playAudio(audioUrl);
      },

      stopAudio: () => {
        agentRef.current?.stopAudio();
      },

      setVoiceEnabled: (enabled: boolean) => {
        agentRef.current?.setVoiceEnabled(enabled);
      }
    }), [customerData]);

    // Render error state
    if (error) {
      return (
        <div className={`ngx-voice-agent-error ${className || ''}`} style={style}>
          <div className="error-message">
            <h3>Connection Error</h3>
            <p>{error}</p>
            <button onClick={() => window.location.reload()}>
              Retry
            </button>
          </div>
        </div>
      );
    }

    // Render loading state
    if (!isInitialized) {
      return (
        <div className={`ngx-voice-agent-loading ${className || ''}`} style={style}>
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Initializing NGX Voice Agent...</p>
          </div>
        </div>
      );
    }

    // Render children or default UI
    return (
      <div className={`ngx-voice-agent ${className || ''}`} style={style}>
        {children || <DefaultVoiceAgentUI state={conversationState} />}
      </div>
    );
  }
);

NGXVoiceAgent.displayName = 'NGXVoiceAgent';

// Default UI component
interface DefaultVoiceAgentUIProps {
  state: ConversationState | null;
}

const DefaultVoiceAgentUI: React.FC<DefaultVoiceAgentUIProps> = ({ state }) => {
  const [inputMessage, setInputMessage] = useState('');

  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      // This would need to be connected to the agent instance
      // For now, it's just a placeholder
      console.log('Send message:', inputMessage);
      setInputMessage('');
    }
  };

  return (
    <div className="ngx-default-ui">
      <div className="ngx-header">
        <div className="ngx-avatar">🤖</div>
        <div className="ngx-title">NGX Assistant</div>
        <div className="ngx-status">
          {state?.status === 'active' ? '🟢 Active' : '⚪ Inactive'}
        </div>
      </div>

      <div className="ngx-messages">
        {state?.messages.map((message) => (
          <div
            key={message.id}
            className={`ngx-message ngx-message-${message.role}`}
          >
            <div className="ngx-message-content">{message.content}</div>
            <div className="ngx-message-time">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        )) || (
          <div className="ngx-welcome-message">
            <p>Hi! I'm your NGX assistant. How can I help you today?</p>
          </div>
        )}
      </div>

      <div className="ngx-input">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Type your message..."
          disabled={state?.status !== 'active'}
        />
        <button
          onClick={handleSendMessage}
          disabled={!inputMessage.trim() || state?.status !== 'active'}
        >
          Send
        </button>
      </div>
    </div>
  );
};