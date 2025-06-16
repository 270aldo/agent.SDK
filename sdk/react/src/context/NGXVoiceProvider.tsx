import React, { createContext, useContext, useRef, useState, useEffect, ReactNode } from 'react';
import {
  NGXVoiceAgent,
  NGXConfig,
  CustomerData,
  ConversationState,
  ConversationMessage
} from '@ngx/voice-agent-sdk';

export interface NGXVoiceContextValue {
  // Agent instance
  agent: NGXVoiceAgent | null;
  
  // State
  isInitialized: boolean;
  isActive: boolean;
  conversationState: ConversationState | null;
  error: string | null;
  loading: boolean;

  // Actions
  start: (customerData?: CustomerData) => Promise<string | null>;
  sendMessage: (message: string) => Promise<ConversationMessage | null>;
  endConversation: () => Promise<void>;
  playAudio: (audioUrl: string) => Promise<void>;
  stopAudio: () => void;
  setVoiceEnabled: (enabled: boolean) => void;

  // Configuration
  updateConfig: (newConfig: Partial<NGXConfig>) => Promise<void>;
}

const NGXVoiceContext = createContext<NGXVoiceContextValue | null>(null);

export interface NGXVoiceProviderProps {
  config: NGXConfig;
  customerData?: CustomerData;
  autoStart?: boolean;
  children: ReactNode;
  onConversationStart?: (conversationId: string) => void;
  onConversationEnd?: (conversationId: string, reason: string) => void;
  onMessage?: (message: ConversationMessage, type: 'sent' | 'received') => void;
  onQualificationComplete?: (score: number, recommendation: string) => void;
  onError?: (error: Error, context?: string) => void;
}

export const NGXVoiceProvider: React.FC<NGXVoiceProviderProps> = ({
  config,
  customerData,
  autoStart = false,
  children,
  onConversationStart,
  onConversationEnd,
  onMessage,
  onQualificationComplete,
  onError
}) => {
  const agentRef = useRef<NGXVoiceAgent | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isActive, setIsActive] = useState(false);
  const [conversationState, setConversationState] = useState<ConversationState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [currentConfig, setCurrentConfig] = useState(config);

  // Initialize agent
  useEffect(() => {
    const initAgent = async () => {
      try {
        setLoading(true);
        setError(null);

        // Destroy existing agent if it exists
        if (agentRef.current) {
          agentRef.current.destroy();
        }

        const agent = new NGXVoiceAgent();
        await agent.init(currentConfig);

        // Set up event listeners
        agent.on('conversation.started', ({ conversationId, customerData: data }) => {
          setIsActive(true);
          setConversationState(agent.getState());
          onConversationStart?.(conversationId);
        });

        agent.on('conversation.ended', ({ conversationId, reason }) => {
          setIsActive(false);
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

        // Auto-start if requested
        if (autoStart) {
          await agent.start(customerData);
        }
      } catch (err) {
        const error = err as Error;
        setError(error.message);
        onError?.(error, 'initialization');
      } finally {
        setLoading(false);
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
  }, [currentConfig, autoStart, customerData, onConversationStart, onConversationEnd, onMessage, onQualificationComplete, onError]);

  // Action handlers
  const start = async (data?: CustomerData): Promise<string | null> => {
    if (!agentRef.current) {
      setError('Agent not initialized');
      return null;
    }

    try {
      setLoading(true);
      setError(null);
      const conversationId = await agentRef.current.start(data || customerData);
      setConversationState(agentRef.current.getState());
      return conversationId;
    } catch (err) {
      const error = err as Error;
      setError(error.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (message: string): Promise<ConversationMessage | null> => {
    if (!agentRef.current) {
      setError('Agent not initialized');
      return null;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await agentRef.current.sendMessage(message);
      setConversationState(agentRef.current.getState());
      return response;
    } catch (err) {
      const error = err as Error;
      setError(error.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const endConversation = async (): Promise<void> => {
    if (!agentRef.current) {
      setError('Agent not initialized');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await agentRef.current.endConversation();
      setConversationState(null);
      setIsActive(false);
    } catch (err) {
      const error = err as Error;
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const playAudio = async (audioUrl: string): Promise<void> => {
    if (!agentRef.current) {
      setError('Agent not initialized');
      return;
    }

    try {
      await agentRef.current.playAudio(audioUrl);
    } catch (err) {
      const error = err as Error;
      setError(error.message);
    }
  };

  const stopAudio = (): void => {
    agentRef.current?.stopAudio();
  };

  const setVoiceEnabled = (enabled: boolean): void => {
    agentRef.current?.setVoiceEnabled(enabled);
  };

  const updateConfig = async (newConfig: Partial<NGXConfig>): Promise<void> => {
    const updatedConfig = { ...currentConfig, ...newConfig };
    setCurrentConfig(updatedConfig);
  };

  const contextValue: NGXVoiceContextValue = {
    // Agent instance
    agent: agentRef.current,
    
    // State
    isInitialized,
    isActive,
    conversationState,
    error,
    loading,

    // Actions
    start,
    sendMessage,
    endConversation,
    playAudio,
    stopAudio,
    setVoiceEnabled,

    // Configuration
    updateConfig
  };

  return (
    <NGXVoiceContext.Provider value={contextValue}>
      {children}
    </NGXVoiceContext.Provider>
  );
};

// Custom hook to use the NGX Voice context
export const useNGXVoiceContext = (): NGXVoiceContextValue => {
  const context = useContext(NGXVoiceContext);
  
  if (!context) {
    throw new Error('useNGXVoiceContext must be used within an NGXVoiceProvider');
  }
  
  return context;
};