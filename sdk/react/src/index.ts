// Component exports
export { NGXVoiceAgent } from './components/NGXVoiceAgent';
export type { NGXVoiceAgentProps, NGXVoiceAgentRef } from './components/NGXVoiceAgent';

// Hook exports
export { useNGXVoice } from './hooks/useNGXVoice';
export type { UseNGXVoiceOptions, UseNGXVoiceReturn } from './hooks/useNGXVoice';

// Context exports
export { NGXVoiceProvider, useNGXVoiceContext } from './context/NGXVoiceProvider';
export type { NGXVoiceContextValue, NGXVoiceProviderProps } from './context/NGXVoiceProvider';

// Re-export SDK types for convenience
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