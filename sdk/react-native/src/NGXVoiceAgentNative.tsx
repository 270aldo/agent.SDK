import React, { useEffect, useRef, useState, forwardRef, useImperativeHandle } from 'react';
import {
  View,
  Text,
  Modal,
  TouchableOpacity,
  TextInput,
  ScrollView,
  StyleSheet,
  Platform,
  Alert,
  StatusBar,
  KeyboardAvoidingView,
  SafeAreaView,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import Sound from 'react-native-sound';
import {
  NGXVoiceAgent as CoreAgent,
  NGXConfig,
  CustomerData,
  ConversationState,
  ConversationMessage,
} from '@ngx/voice-agent-sdk';

export interface NGXVoiceAgentNativeProps {
  config: NGXConfig;
  customerData?: CustomerData;
  autoStart?: boolean;
  visible?: boolean;
  onConversationStart?: (conversationId: string) => void;
  onConversationEnd?: (conversationId: string, reason: string) => void;
  onMessage?: (message: ConversationMessage, type: 'sent' | 'received') => void;
  onQualificationComplete?: (score: number, recommendation: string) => void;
  onError?: (error: Error, context?: string) => void;
  onClose?: () => void;
  style?: any;
  theme?: 'light' | 'dark';
}

export interface NGXVoiceAgentNativeRef {
  start: (customerData?: CustomerData) => Promise<string>;
  sendMessage: (message: string) => Promise<ConversationMessage>;
  endConversation: () => Promise<void>;
  getState: () => ConversationState | null;
  isActive: () => boolean;
  show: () => void;
  hide: () => void;
}

export const NGXVoiceAgentNative = forwardRef<NGXVoiceAgentNativeRef, NGXVoiceAgentNativeProps>(
  ({
    config,
    customerData,
    autoStart = false,
    visible = false,
    onConversationStart,
    onConversationEnd,
    onMessage,
    onQualificationComplete,
    onError,
    onClose,
    style,
    theme = 'light'
  }, ref) => {
    const agentRef = useRef<CoreAgent | null>(null);
    const soundRef = useRef<Sound | null>(null);
    
    const [isInitialized, setIsInitialized] = useState(false);
    const [conversationState, setConversationState] = useState<ConversationState | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(visible);
    const [inputMessage, setInputMessage] = useState('');
    const [isOnline, setIsOnline] = useState(true);

    // Network status monitoring
    useEffect(() => {
      const unsubscribe = NetInfo.addEventListener(state => {
        setIsOnline(state.isConnected || false);
      });

      return () => unsubscribe();
    }, []);

    // Initialize agent
    useEffect(() => {
      const initAgent = async () => {
        try {
          setLoading(true);
          
          // Check for cached configuration
          const cachedConfig = await AsyncStorage.getItem('@ngx_config');
          const finalConfig = cachedConfig ? { ...config, ...JSON.parse(cachedConfig) } : config;

          const agent = new CoreAgent();
          await agent.init(finalConfig);
          
          // Set up event listeners
          agent.on('conversation.started', ({ conversationId }) => {
            setConversationState(agent.getState());
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
            
            // Play audio if available
            if (message.audio) {
              playAudio(message.audio);
            }
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
        if (soundRef.current) {
          soundRef.current.release();
          soundRef.current = null;
        }
      };
    }, [config]);

    // Sync modal visibility
    useEffect(() => {
      setModalVisible(visible);
    }, [visible]);

    // Audio playback
    const playAudio = (audioUrl: string) => {
      if (soundRef.current) {
        soundRef.current.release();
      }

      soundRef.current = new Sound(audioUrl, '', (error) => {
        if (error) {
          console.warn('Failed to load audio:', error);
          return;
        }
        
        soundRef.current?.play((success) => {
          if (!success) {
            console.warn('Audio playback failed');
          }
          soundRef.current?.release();
          soundRef.current = null;
        });
      });
    };

    // Exposed methods via ref
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

      show: () => {
        setModalVisible(true);
      },

      hide: () => {
        setModalVisible(false);
        onClose?.();
      }
    }), [customerData, onClose]);

    // Send message handler
    const handleSendMessage = async () => {
      if (!inputMessage.trim() || !agentRef.current) return;

      try {
        await agentRef.current.sendMessage(inputMessage);
        setInputMessage('');
      } catch (err) {
        Alert.alert('Error', 'Failed to send message. Please try again.');
      }
    };

    // Start conversation handler
    const handleStartConversation = async () => {
      if (!agentRef.current) return;

      try {
        setLoading(true);
        await agentRef.current.start(customerData);
      } catch (err) {
        Alert.alert('Error', 'Failed to start conversation. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    // Close modal handler
    const handleClose = () => {
      setModalVisible(false);
      onClose?.();
    };

    // Render offline banner
    const renderOfflineBanner = () => {
      if (isOnline) return null;

      return (
        <View style={[styles.offlineBanner, { backgroundColor: theme === 'dark' ? '#ff4444' : '#ff6b6b' }]}>
          <Text style={styles.offlineText}>No internet connection</Text>
        </View>
      );
    };

    // Render error state
    const renderError = () => (
      <View style={[styles.container, styles.centerContent, { backgroundColor: theme === 'dark' ? '#1a1a1a' : '#fff' }]}>
        <Text style={[styles.errorTitle, { color: theme === 'dark' ? '#fff' : '#333' }]}>Connection Error</Text>
        <Text style={[styles.errorMessage, { color: theme === 'dark' ? '#ccc' : '#666' }]}>{error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={() => window.location?.reload?.()}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );

    // Render loading state
    const renderLoading = () => (
      <View style={[styles.container, styles.centerContent, { backgroundColor: theme === 'dark' ? '#1a1a1a' : '#fff' }]}>
        <Text style={[styles.loadingText, { color: theme === 'dark' ? '#fff' : '#333' }]}>
          Initializing NGX Voice Agent...
        </Text>
      </View>
    );

    // Render welcome screen
    const renderWelcome = () => (
      <View style={[styles.container, { backgroundColor: theme === 'dark' ? '#1a1a1a' : '#fff' }]}>
        <View style={styles.welcomeContent}>
          <Text style={[styles.welcomeTitle, { color: theme === 'dark' ? '#fff' : '#333' }]}>
            👋 Hi! I'm your NGX assistant
          </Text>
          <Text style={[styles.welcomeMessage, { color: theme === 'dark' ? '#ccc' : '#666' }]}>
            I'm here to help you achieve your fitness goals. Ready to get started?
          </Text>
          <TouchableOpacity
            style={styles.startButton}
            onPress={handleStartConversation}
            disabled={loading}
          >
            <Text style={styles.startButtonText}>
              {loading ? 'Starting...' : 'Start Conversation'}
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    );

    // Render chat interface
    const renderChat = () => (
      <View style={[styles.container, { backgroundColor: theme === 'dark' ? '#1a1a1a' : '#fff' }]}>
        <ScrollView style={styles.messagesContainer}>
          {conversationState?.messages.map((message) => (
            <View
              key={message.id}
              style={[
                styles.messageContainer,
                message.role === 'user' ? styles.userMessage : styles.assistantMessage
              ]}
            >
              <View
                style={[
                  styles.messageBubble,
                  message.role === 'user' 
                    ? styles.userBubble 
                    : [styles.assistantBubble, { backgroundColor: theme === 'dark' ? '#2a2a2a' : '#f0f0f0' }]
                ]}
              >
                <Text style={[
                  styles.messageText,
                  message.role === 'user' 
                    ? styles.userText 
                    : { color: theme === 'dark' ? '#fff' : '#333' }
                ]}>
                  {message.content}
                </Text>
              </View>
              <Text style={[styles.messageTime, { color: theme === 'dark' ? '#888' : '#999' }]}>
                {message.timestamp.toLocaleTimeString()}
              </Text>
            </View>
          ))}
        </ScrollView>

        <View style={[styles.inputContainer, { backgroundColor: theme === 'dark' ? '#2a2a2a' : '#f8f9fa' }]}>
          <TextInput
            style={[styles.textInput, { 
              backgroundColor: theme === 'dark' ? '#1a1a1a' : '#fff',
              color: theme === 'dark' ? '#fff' : '#333',
              borderColor: theme === 'dark' ? '#444' : '#ddd'
            }]}
            value={inputMessage}
            onChangeText={setInputMessage}
            placeholder="Type your message..."
            placeholderTextColor={theme === 'dark' ? '#888' : '#999'}
            multiline
            onSubmitEditing={handleSendMessage}
          />
          <TouchableOpacity
            style={[styles.sendButton, { opacity: inputMessage.trim() ? 1 : 0.5 }]}
            onPress={handleSendMessage}
            disabled={!inputMessage.trim()}
          >
            <Text style={styles.sendButtonText}>Send</Text>
          </TouchableOpacity>
        </View>
      </View>
    );

    // Main render
    return (
      <Modal
        visible={modalVisible}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={handleClose}
      >
        <SafeAreaView style={[styles.modalContainer, { backgroundColor: theme === 'dark' ? '#000' : '#fff' }]}>
          <StatusBar barStyle={theme === 'dark' ? 'light-content' : 'dark-content'} />
          
          {renderOfflineBanner()}
          
          <View style={[styles.header, { backgroundColor: theme === 'dark' ? '#1a1a1a' : '#fff' }]}>
            <Text style={[styles.headerTitle, { color: theme === 'dark' ? '#fff' : '#333' }]}>
              NGX Assistant
            </Text>
            <TouchableOpacity onPress={handleClose} style={styles.closeButton}>
              <Text style={[styles.closeButtonText, { color: theme === 'dark' ? '#fff' : '#333' }]}>✕</Text>
            </TouchableOpacity>
          </View>

          <KeyboardAvoidingView 
            style={styles.flex} 
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          >
            {error ? renderError() : 
             !isInitialized ? renderLoading() :
             !conversationState ? renderWelcome() :
             renderChat()}
          </KeyboardAvoidingView>
        </SafeAreaView>
      </Modal>
    );
  }
);

const styles = StyleSheet.create({
  modalContainer: {
    flex: 1,
  },
  flex: {
    flex: 1,
  },
  container: {
    flex: 1,
  },
  centerContent: {
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  offlineBanner: {
    padding: 10,
    alignItems: 'center',
  },
  offlineText: {
    color: '#fff',
    fontWeight: '600',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
  },
  closeButton: {
    padding: 8,
  },
  closeButtonText: {
    fontSize: 18,
    fontWeight: '600',
  },
  // Error state
  errorTitle: {
    fontSize: 20,
    fontWeight: '600',
    marginBottom: 10,
  },
  errorMessage: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
  },
  retryButton: {
    backgroundColor: '#667eea',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 25,
  },
  retryButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  // Loading state
  loadingText: {
    fontSize: 16,
  },
  // Welcome screen
  welcomeContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  welcomeTitle: {
    fontSize: 24,
    fontWeight: '600',
    marginBottom: 10,
    textAlign: 'center',
  },
  welcomeMessage: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 30,
    lineHeight: 24,
  },
  startButton: {
    backgroundColor: '#667eea',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
  },
  startButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  // Chat interface
  messagesContainer: {
    flex: 1,
    padding: 16,
  },
  messageContainer: {
    marginBottom: 16,
  },
  userMessage: {
    alignItems: 'flex-end',
  },
  assistantMessage: {
    alignItems: 'flex-start',
  },
  messageBubble: {
    maxWidth: '80%',
    padding: 12,
    borderRadius: 18,
    marginBottom: 4,
  },
  userBubble: {
    backgroundColor: '#667eea',
  },
  assistantBubble: {
    backgroundColor: '#f0f0f0',
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
  userText: {
    color: '#fff',
  },
  messageTime: {
    fontSize: 12,
    marginHorizontal: 12,
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 16,
    alignItems: 'flex-end',
  },
  textInput: {
    flex: 1,
    borderWidth: 1,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginRight: 12,
    maxHeight: 100,
    fontSize: 16,
  },
  sendButton: {
    backgroundColor: '#667eea',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 20,
  },
  sendButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
});

NGXVoiceAgentNative.displayName = 'NGXVoiceAgentNative';