import { useState, useEffect, useCallback, useRef } from 'react';
import {
  NGXVoiceAgent,
  NGXConfig,
  CustomerData,
  ConversationState,
  ConversationMessage
} from '@ngx/voice-agent-sdk';

export interface UseNGXVoiceOptions {
  config: NGXConfig;
  customerData?: CustomerData;
  autoStart?: boolean;
}

export interface UseNGXVoiceReturn {
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

  // Event handlers
  onConversationStart: (callback: (conversationId: string) => void) => void;
  onConversationEnd: (callback: (conversationId: string, reason: string) => void) => void;
  onMessage: (callback: (message: ConversationMessage, type: 'sent' | 'received') => void) => void;
  onQualificationComplete: (callback: (score: number, recommendation: string) => void) => void;
  onError: (callback: (error: Error, context?: string) => void) => void;
}

export function useNGXVoice({
  config,
  customerData,
  autoStart = false
}: UseNGXVoiceOptions): UseNGXVoiceReturn {
  const agentRef = useRef<NGXVoiceAgent | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isActive, setIsActive] = useState(false);
  const [conversationState, setConversationState] = useState<ConversationState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Event callback refs
  const eventCallbacks = useRef<{
    onConversationStart?: (conversationId: string) => void;
    onConversationEnd?: (conversationId: string, reason: string) => void;
    onMessage?: (message: ConversationMessage, type: 'sent' | 'received') => void;
    onQualificationComplete?: (score: number, recommendation: string) => void;
    onError?: (error: Error, context?: string) => void;
  }>({});

  // Initialize agent
  useEffect(() => {
    const initAgent = async () => {
      try {
        setLoading(true);
        const agent = new NGXVoiceAgent();
        await agent.init(config);

        // Set up event listeners
        agent.on('conversation.started', ({ conversationId }) => {
          setIsActive(true);
          setConversationState(agent.getState());
          eventCallbacks.current.onConversationStart?.(conversationId);
        });

        agent.on('conversation.ended', ({ conversationId, reason }) => {
          setIsActive(false);
          setConversationState(null);
          eventCallbacks.current.onConversationEnd?.(conversationId, reason);
        });

        agent.on('message.sent', ({ message }) => {
          setConversationState(agent.getState());
          eventCallbacks.current.onMessage?.(message, 'sent');
        });

        agent.on('message.received', ({ message }) => {
          setConversationState(agent.getState());
          eventCallbacks.current.onMessage?.(message, 'received');
        });

        agent.on('qualification.completed', ({ score, recommendation }) => {
          eventCallbacks.current.onQualificationComplete?.(score, recommendation);
        });

        agent.on('error', ({ error, context }) => {
          setError(error.message);
          eventCallbacks.current.onError?.(error, context);
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
        eventCallbacks.current.onError?.(error, 'initialization');
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
  }, [config, autoStart, customerData]);

  // Update isActive state
  useEffect(() => {
    if (agentRef.current) {
      setIsActive(agentRef.current.isActive());
    }
  }, [conversationState]);

  // Action handlers
  const start = useCallback(async (data?: CustomerData): Promise<string | null> => {
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
  }, [customerData]);

  const sendMessage = useCallback(async (message: string): Promise<ConversationMessage | null> => {
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
  }, []);

  const endConversation = useCallback(async (): Promise<void> => {
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
  }, []);

  const playAudio = useCallback(async (audioUrl: string): Promise<void> => {
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
  }, []);

  const stopAudio = useCallback((): void => {
    agentRef.current?.stopAudio();
  }, []);

  const setVoiceEnabled = useCallback((enabled: boolean): void => {
    agentRef.current?.setVoiceEnabled(enabled);
  }, []);

  // Event handler setters
  const onConversationStart = useCallback((callback: (conversationId: string) => void) => {
    eventCallbacks.current.onConversationStart = callback;
  }, []);

  const onConversationEnd = useCallback((callback: (conversationId: string, reason: string) => void) => {
    eventCallbacks.current.onConversationEnd = callback;
  }, []);

  const onMessage = useCallback((callback: (message: ConversationMessage, type: 'sent' | 'received') => void) => {
    eventCallbacks.current.onMessage = callback;
  }, []);

  const onQualificationComplete = useCallback((callback: (score: number, recommendation: string) => void) => {
    eventCallbacks.current.onQualificationComplete = callback;
  }, []);

  const onError = useCallback((callback: (error: Error, context?: string) => void) => {
    eventCallbacks.current.onError = callback;
  }, []);

  return {
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

    // Event handlers
    onConversationStart,
    onConversationEnd,
    onMessage,
    onQualificationComplete,
    onError
  };
}