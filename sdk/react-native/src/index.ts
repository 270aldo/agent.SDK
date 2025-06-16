// React Native SDK exports
export { NGXVoiceAgentNative } from './NGXVoiceAgentNative';
export type { NGXVoiceAgentNativeProps, NGXVoiceAgentNativeRef } from './NGXVoiceAgentNative';

// Re-export core SDK types for convenience
export type {
  NGXConfig,
  CustomerData,
  ConversationMessage,
  ConversationState,
  PlatformType,
  NGXEventMap,
  FeatureConfig,
  UIConfig,
  VoiceConfig
} from '@ngx/voice-agent-sdk';

// React Native specific hooks
export { useNGXVoiceNative } from './hooks/useNGXVoiceNative';
export type { UseNGXVoiceNativeOptions, UseNGXVoiceNativeReturn } from './hooks/useNGXVoiceNative';