// Core types for NGX Voice Agent SDK

export interface CustomerData {
  name?: string;
  email?: string;
  age?: number;
  gender?: 'male' | 'female' | 'other';
  occupation?: string;
  goals?: {
    primary?: string;
    secondary?: string[];
  };
  industry?: 'health' | 'finance' | 'tech' | 'education' | 'other';
}

export interface NGXConfig {
  apiUrl: string;
  apiKey?: string;
  platform: PlatformType;
  features?: FeatureConfig;
  ui?: UIConfig;
  voice?: VoiceConfig;
}

export type PlatformType = 'lead_magnet' | 'landing_page' | 'blog' | 'mobile_app' | 'api_only';

export interface PlatformContext {
  type: PlatformType;
  trigger?: TriggerConfig;
  style?: StyleConfig;
  behavior?: BehaviorConfig;
}

export interface TriggerConfig {
  type: 'manual' | 'auto' | 'scroll' | 'time' | 'exit_intent';
  threshold?: number; // For scroll (percentage) or time (seconds)
}

export interface StyleConfig {
  position?: 'bottom-right' | 'bottom-left' | 'center' | 'fullscreen';
  theme?: 'light' | 'dark' | 'auto';
  colors?: {
    primary?: string;
    secondary?: string;
    background?: string;
    text?: string;
  };
  size?: 'small' | 'medium' | 'large';
}

export interface BehaviorConfig {
  autoStart?: boolean;
  greeting?: string;
  showAvatar?: boolean;
  enableVoice?: boolean;
  transferToHuman?: boolean;
}

export interface FeatureConfig {
  voiceEnabled?: boolean;
  humanTransfer?: boolean;
  analytics?: boolean;
  followUp?: boolean;
}

export interface UIConfig {
  position?: 'bottom-right' | 'bottom-left' | 'center' | 'fullscreen';
  theme?: 'light' | 'dark' | 'auto';
  showAvatar?: boolean;
  customCSS?: string;
}

export interface VoiceConfig {
  enabled?: boolean;
  autoPlay?: boolean;
  voice?: string;
  speed?: number;
  volume?: number;
}

export interface ConversationMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  audio?: string; // URL to audio file
  metadata?: {
    intent?: string;
    sentiment?: string;
    confidence?: number;
  };
}

export interface ConversationState {
  id: string;
  status: 'active' | 'ended' | 'transferred';
  messages: ConversationMessage[];
  customerData?: CustomerData;
  metadata: {
    startTime: Date;
    platform: PlatformType;
    qualificationScore?: number;
    transferRequested?: boolean;
  };
}

export interface NGXEventMap {
  'conversation.started': { conversationId: string; customerData?: CustomerData };
  'conversation.ended': { conversationId: string; reason: string };
  'message.sent': { message: ConversationMessage };
  'message.received': { message: ConversationMessage };
  'voice.started': { messageId: string };
  'voice.ended': { messageId: string };
  'human.transfer.requested': { conversationId: string };
  'qualification.completed': { score: number; recommendation: string };
  'error': { error: Error; context?: string };
}

export interface NGXVoiceAgent {
  // Core methods
  init(config: NGXConfig): Promise<void>;
  start(customerData?: CustomerData): Promise<string>;
  sendMessage(message: string): Promise<ConversationMessage>;
  endConversation(): Promise<void>;
  
  // State management
  getState(): ConversationState | null;
  isActive(): boolean;
  
  // Voice methods
  playAudio(audioUrl: string): Promise<void>;
  stopAudio(): void;
  setVoiceEnabled(enabled: boolean): void;
  
  // Event handling
  on<K extends keyof NGXEventMap>(event: K, listener: (data: NGXEventMap[K]) => void): void;
  off<K extends keyof NGXEventMap>(event: K, listener: (data: NGXEventMap[K]) => void): void;
  emit<K extends keyof NGXEventMap>(event: K, data: NGXEventMap[K]): void;
  
  // Utilities
  destroy(): void;
}

export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ConversationStartResponse {
  conversation_id: string;
  initial_message?: string;
  audio_url?: string;
}

export interface MessageResponse {
  response: string;
  audio_url?: string;
  intent_analysis?: {
    intent: string;
    confidence: number;
    sentiment: string;
  };
  qualification_update?: {
    score: number;
    recommendation: string;
  };
}