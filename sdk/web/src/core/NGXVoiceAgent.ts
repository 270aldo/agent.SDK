import { EventEmitter } from 'eventemitter3';
import {
  NGXConfig,
  NGXVoiceAgent as INGXVoiceAgent,
  NGXEventMap,
  CustomerData,
  ConversationState,
  ConversationMessage,
  PlatformType,
  APIResponse,
  ConversationStartResponse,
  MessageResponse
} from '../types';
import { APIClient } from './APIClient';
import { VoiceManager } from './VoiceManager';
import { PlatformManager } from './PlatformManager';

export class NGXVoiceAgent extends EventEmitter<NGXEventMap> implements INGXVoiceAgent {
  private config?: NGXConfig;
  private apiClient?: APIClient;
  private voiceManager?: VoiceManager;
  private platformManager?: PlatformManager;
  private conversationState: ConversationState | null = null;
  private isInitialized = false;

  constructor() {
    super();
  }

  async init(config: NGXConfig): Promise<void> {
    try {
      this.config = config;
      
      // Initialize API client
      this.apiClient = new APIClient(config.apiUrl, config.apiKey);
      
      // Initialize voice manager if voice is enabled
      if (config.voice?.enabled || config.features?.voiceEnabled) {
        this.voiceManager = new VoiceManager(config.voice || {});
      }
      
      // Initialize platform manager
      this.platformManager = new PlatformManager(config.platform, config.ui);
      
      this.isInitialized = true;
      
      console.log(`NGX Voice Agent initialized for platform: ${config.platform}`);
    } catch (error) {
      this.emit('error', { 
        error: error as Error, 
        context: 'initialization' 
      });
      throw error;
    }
  }

  async start(customerData?: CustomerData): Promise<string> {
    if (!this.isInitialized || !this.apiClient || !this.config) {
      throw new Error('NGX Voice Agent not initialized');
    }

    try {
      // Start conversation via API
      const response = await this.apiClient.startConversation({
        customer_data: customerData,
        program_type: 'PRIME', // Default program
        platform: this.config.platform
      });

      // Create conversation state
      this.conversationState = {
        id: response.conversation_id,
        status: 'active',
        messages: [],
        customerData,
        metadata: {
          startTime: new Date(),
          platform: this.config.platform
        }
      };

      // Add initial message if provided
      if (response.initial_message) {
        const initialMessage: ConversationMessage = {
          id: `msg_${Date.now()}`,
          role: 'assistant',
          content: response.initial_message,
          timestamp: new Date()
        };

        if (response.audio_url) {
          initialMessage.audio = response.audio_url;
        }

        this.conversationState.messages.push(initialMessage);

        // Auto-play voice if enabled
        if (this.voiceManager && response.audio_url) {
          this.voiceManager.playAudio(response.audio_url);
        }

        this.emit('message.received', { message: initialMessage });
      }

      this.emit('conversation.started', { 
        conversationId: response.conversation_id, 
        customerData 
      });

      return response.conversation_id;
    } catch (error) {
      this.emit('error', { 
        error: error as Error, 
        context: 'conversation_start' 
      });
      throw error;
    }
  }

  async sendMessage(message: string): Promise<ConversationMessage> {
    if (!this.conversationState || !this.apiClient) {
      throw new Error('No active conversation');
    }

    try {
      // Add user message to state
      const userMessage: ConversationMessage = {
        id: `msg_${Date.now()}_user`,
        role: 'user',
        content: message,
        timestamp: new Date()
      };

      this.conversationState.messages.push(userMessage);
      this.emit('message.sent', { message: userMessage });

      // Send message to API
      const response = await this.apiClient.sendMessage(
        this.conversationState.id,
        message
      );

      // Create assistant response message
      const assistantMessage: ConversationMessage = {
        id: `msg_${Date.now()}_assistant`,
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        metadata: response.intent_analysis
      };

      if (response.audio_url) {
        assistantMessage.audio = response.audio_url;
      }

      this.conversationState.messages.push(assistantMessage);

      // Update qualification score if provided
      if (response.qualification_update) {
        this.conversationState.metadata.qualificationScore = response.qualification_update.score;
        this.emit('qualification.completed', {
          score: response.qualification_update.score,
          recommendation: response.qualification_update.recommendation
        });
      }

      // Auto-play voice if enabled
      if (this.voiceManager && response.audio_url) {
        this.voiceManager.playAudio(response.audio_url);
      }

      this.emit('message.received', { message: assistantMessage });

      return assistantMessage;
    } catch (error) {
      this.emit('error', { 
        error: error as Error, 
        context: 'send_message' 
      });
      throw error;
    }
  }

  async endConversation(): Promise<void> {
    if (!this.conversationState || !this.apiClient) {
      throw new Error('No active conversation');
    }

    try {
      await this.apiClient.endConversation(this.conversationState.id);
      
      const conversationId = this.conversationState.id;
      this.conversationState.status = 'ended';
      
      this.emit('conversation.ended', { 
        conversationId, 
        reason: 'user_ended' 
      });

      this.conversationState = null;
    } catch (error) {
      this.emit('error', { 
        error: error as Error, 
        context: 'conversation_end' 
      });
      throw error;
    }
  }

  getState(): ConversationState | null {
    return this.conversationState;
  }

  isActive(): boolean {
    return this.conversationState?.status === 'active';
  }

  async playAudio(audioUrl: string): Promise<void> {
    if (!this.voiceManager) {
      throw new Error('Voice not enabled');
    }

    try {
      await this.voiceManager.playAudio(audioUrl);
    } catch (error) {
      this.emit('error', { 
        error: error as Error, 
        context: 'audio_playback' 
      });
      throw error;
    }
  }

  stopAudio(): void {
    if (this.voiceManager) {
      this.voiceManager.stopAudio();
    }
  }

  setVoiceEnabled(enabled: boolean): void {
    if (this.voiceManager) {
      this.voiceManager.setEnabled(enabled);
    }
  }

  destroy(): void {
    // Clean up resources
    if (this.voiceManager) {
      this.voiceManager.destroy();
    }

    if (this.platformManager) {
      this.platformManager.destroy();
    }

    // End active conversation
    if (this.conversationState?.status === 'active') {
      this.endConversation().catch(console.error);
    }

    // Remove all listeners
    this.removeAllListeners();

    // Reset state
    this.conversationState = null;
    this.isInitialized = false;
    
    console.log('NGX Voice Agent destroyed');
  }
}