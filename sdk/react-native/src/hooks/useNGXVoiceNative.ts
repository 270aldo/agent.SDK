import { useState, useEffect, useCallback, useRef } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Alert } from 'react-native';
import {
  NGXVoiceAgent,
  NGXConfig,
  CustomerData,
  ConversationState,
  ConversationMessage
} from '@ngx/voice-agent-sdk';

export interface UseNGXVoiceNativeOptions {
  config: NGXConfig;
  customerData?: CustomerData;
  autoStart?: boolean;
  enableOfflineMode?: boolean;
  cacheConversations?: boolean;
}

export interface UseNGXVoiceNativeReturn {
  // State
  isInitialized: boolean;
  isActive: boolean;
  conversationState: ConversationState | null;
  error: string | null;
  loading: boolean;
  isOnline: boolean;

  // Actions
  start: (customerData?: CustomerData) => Promise<string | null>;
  sendMessage: (message: string) => Promise<ConversationMessage | null>;
  endConversation: () => Promise<void>;
  
  // Offline capabilities
  syncOfflineData: () => Promise<void>;
  getCachedConversations: () => Promise<ConversationState[]>;
  clearCache: () => Promise<void>;

  // Mobile-specific
  requestPermissions: () => Promise<boolean>;
  enablePushNotifications: () => Promise<void>;
}

const STORAGE_KEYS = {
  CONFIG: '@ngx_config',
  CONVERSATIONS: '@ngx_conversations',
  OFFLINE_MESSAGES: '@ngx_offline_messages',
  USER_DATA: '@ngx_user_data',
};

export function useNGXVoiceNative({
  config,
  customerData,
  autoStart = false,
  enableOfflineMode = true,
  cacheConversations = true
}: UseNGXVoiceNativeOptions): UseNGXVoiceNativeReturn {
  const agentRef = useRef<NGXVoiceAgent | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isActive, setIsActive] = useState(false);
  const [conversationState, setConversationState] = useState<ConversationState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [isOnline, setIsOnline] = useState(true);

  // Cache management
  const saveToCache = async (key: string, data: any) => {
    if (!cacheConversations) return;
    
    try {
      await AsyncStorage.setItem(key, JSON.stringify(data));
    } catch (err) {
      console.warn('Failed to save to cache:', err);
    }
  };

  const loadFromCache = async (key: string) => {
    try {
      const cached = await AsyncStorage.getItem(key);
      return cached ? JSON.parse(cached) : null;
    } catch (err) {
      console.warn('Failed to load from cache:', err);
      return null;
    }
  };

  // Initialize agent
  useEffect(() => {
    const initAgent = async () => {
      try {
        setLoading(true);
        
        // Load cached configuration
        const cachedConfig = await loadFromCache(STORAGE_KEYS.CONFIG);
        const finalConfig = cachedConfig ? { ...config, ...cachedConfig } : config;

        // Save current config
        await saveToCache(STORAGE_KEYS.CONFIG, finalConfig);

        const agent = new NGXVoiceAgent();
        await agent.init(finalConfig);
        
        // Set up event listeners
        agent.on('conversation.started', ({ conversationId }) => {
          setIsActive(true);
          const state = agent.getState();
          setConversationState(state);
          
          // Cache conversation
          if (state && cacheConversations) {
            saveToCache(`${STORAGE_KEYS.CONVERSATIONS}_${conversationId}`, state);
          }
        });

        agent.on('conversation.ended', ({ conversationId, reason }) => {
          setIsActive(false);
          setConversationState(null);
        });

        agent.on('message.sent', ({ message }) => {
          const state = agent.getState();
          setConversationState(state);
          
          // Cache updated state
          if (state && cacheConversations) {
            saveToCache(`${STORAGE_KEYS.CONVERSATIONS}_${state.id}`, state);
          }
        });

        agent.on('message.received', ({ message }) => {
          const state = agent.getState();
          setConversationState(state);
          
          // Cache updated state
          if (state && cacheConversations) {
            saveToCache(`${STORAGE_KEYS.CONVERSATIONS}_${state.id}`, state);
          }
        });

        agent.on('error', ({ error, context }) => {
          setError(error.message);
          
          // Handle offline errors
          if (enableOfflineMode && error.message.includes('network')) {
            setIsOnline(false);
            Alert.alert(
              'Connection Lost',
              'You can continue using the app offline. Your data will sync when connection is restored.',
              [{ text: 'OK' }]
            );
          }
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
        
        if (enableOfflineMode) {
          // Try to load cached data for offline mode
          const cachedState = await loadFromCache(STORAGE_KEYS.CONVERSATIONS);
          if (cachedState) {
            setConversationState(cachedState);
            setIsOnline(false);
          }
        }
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
  }, [config, autoStart, customerData, enableOfflineMode, cacheConversations]);

  // Actions
  const start = useCallback(async (data?: CustomerData): Promise<string | null> => {
    if (!agentRef.current && !enableOfflineMode) {
      setError('Agent not initialized');
      return null;
    }

    try {
      setLoading(true);
      setError(null);
      
      const finalData = data || customerData;
      
      if (agentRef.current) {
        const conversationId = await agentRef.current.start(finalData);
        setConversationState(agentRef.current.getState());
        return conversationId;
      } else if (enableOfflineMode) {
        // Create offline conversation
        const offlineId = `offline_${Date.now()}`;
        const offlineState: ConversationState = {
          id: offlineId,
          status: 'active',
          messages: [],
          customerData: finalData,
          metadata: {
            startTime: new Date(),
            platform: config.platform
          }
        };
        
        setConversationState(offlineState);
        setIsActive(true);
        await saveToCache(`${STORAGE_KEYS.CONVERSATIONS}_${offlineId}`, offlineState);
        
        return offlineId;
      }
      
      return null;
    } catch (err) {
      const error = err as Error;
      setError(error.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, [customerData, config.platform, enableOfflineMode]);

  const sendMessage = useCallback(async (message: string): Promise<ConversationMessage | null> => {
    if (!agentRef.current && !conversationState) {
      setError('No active conversation');
      return null;
    }

    try {
      setLoading(true);
      setError(null);
      
      if (agentRef.current && isOnline) {
        const response = await agentRef.current.sendMessage(message);
        setConversationState(agentRef.current.getState());
        return response;
      } else if (enableOfflineMode && conversationState) {
        // Handle offline message
        const userMessage: ConversationMessage = {
          id: `msg_${Date.now()}_user`,
          role: 'user',
          content: message,
          timestamp: new Date()
        };

        const updatedState = {
          ...conversationState,
          messages: [...conversationState.messages, userMessage]
        };

        setConversationState(updatedState);
        await saveToCache(`${STORAGE_KEYS.CONVERSATIONS}_${conversationState.id}`, updatedState);
        
        // Queue for sync when online
        const offlineMessages = await loadFromCache(STORAGE_KEYS.OFFLINE_MESSAGES) || [];
        offlineMessages.push({
          conversationId: conversationState.id,
          message: userMessage,
          timestamp: new Date()
        });
        await saveToCache(STORAGE_KEYS.OFFLINE_MESSAGES, offlineMessages);

        return userMessage;
      }
      
      return null;
    } catch (err) {
      const error = err as Error;
      setError(error.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, [conversationState, isOnline, enableOfflineMode]);

  const endConversation = useCallback(async (): Promise<void> => {
    if (!agentRef.current && !conversationState) {
      setError('No active conversation');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      if (agentRef.current && isOnline) {
        await agentRef.current.endConversation();
      }
      
      setConversationState(null);
      setIsActive(false);
    } catch (err) {
      const error = err as Error;
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }, [conversationState, isOnline]);

  // Offline capabilities
  const syncOfflineData = useCallback(async (): Promise<void> => {
    if (!isOnline || !agentRef.current) return;

    try {
      const offlineMessages = await loadFromCache(STORAGE_KEYS.OFFLINE_MESSAGES) || [];
      
      for (const item of offlineMessages) {
        try {
          await agentRef.current.sendMessage(item.message.content);
        } catch (err) {
          console.warn('Failed to sync message:', err);
        }
      }
      
      // Clear synced messages
      await AsyncStorage.removeItem(STORAGE_KEYS.OFFLINE_MESSAGES);
      setIsOnline(true);
    } catch (err) {
      console.warn('Sync failed:', err);
    }
  }, [isOnline]);

  const getCachedConversations = useCallback(async (): Promise<ConversationState[]> => {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const conversationKeys = keys.filter(key => key.startsWith(STORAGE_KEYS.CONVERSATIONS));
      
      const conversations = await Promise.all(
        conversationKeys.map(async (key) => {
          const data = await loadFromCache(key);
          return data;
        })
      );
      
      return conversations.filter(Boolean);
    } catch (err) {
      console.warn('Failed to get cached conversations:', err);
      return [];
    }
  }, []);

  const clearCache = useCallback(async (): Promise<void> => {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const ngxKeys = keys.filter(key => key.startsWith('@ngx_'));
      await AsyncStorage.multiRemove(ngxKeys);
    } catch (err) {
      console.warn('Failed to clear cache:', err);
    }
  }, []);

  // Mobile-specific functions
  const requestPermissions = useCallback(async (): Promise<boolean> => {
    // This would implement permission requests for microphone, etc.
    // Implementation depends on react-native-permissions
    return true;
  }, []);

  const enablePushNotifications = useCallback(async (): Promise<void> => {
    // This would implement push notification setup
    // Implementation depends on your push notification service
  }, []);

  return {
    // State
    isInitialized,
    isActive,
    conversationState,
    error,
    loading,
    isOnline,

    // Actions
    start,
    sendMessage,
    endConversation,

    // Offline capabilities
    syncOfflineData,
    getCachedConversations,
    clearCache,

    // Mobile-specific
    requestPermissions,
    enablePushNotifications
  };
}