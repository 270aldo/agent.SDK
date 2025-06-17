// Main SDK exports
export { NGXVoiceAgent } from './core/NGXVoiceAgent';
export { APIClient } from './core/APIClient';
export { VoiceManager } from './core/VoiceManager';
export { PlatformManager } from './core/PlatformManager';

// Advanced Components
export { EnergyBall } from './components/EnergyBall';
export { ModernVoiceInterface } from './components/ModernVoiceInterface';
export { SmartTriggerEngine } from './components/SmartTriggerEngine';
export { UniversalEmbed } from './embed/UniversalEmbed';
export { ContextualAISystem } from './ai/ContextualAISystem';

// Type exports
export type {
  NGXConfig,
  CustomerData,
  ConversationMessage,
  ConversationState,
  PlatformType,
  PlatformContext,
  TriggerConfig,
  StyleConfig,
  BehaviorConfig,
  FeatureConfig,
  UIConfig,
  VoiceConfig,
  NGXEventMap,
  NGXVoiceAgent as INGXVoiceAgent,
  APIResponse,
  ConversationStartResponse,
  MessageResponse
} from './types';

// Widget factory function for easy integration
export function createNGXWidget(config: import('./types').NGXConfig): import('./core/NGXVoiceAgent').NGXVoiceAgent {
  const agent = new NGXVoiceAgent();
  
  // Auto-initialize in browser environment
  if (typeof window !== 'undefined') {
    agent.init(config).catch(console.error);
  }
  
  return agent;
}

// Global widget initialization for script tag usage
if (typeof window !== 'undefined') {
  // @ts-ignore
  window.NGXVoiceAgent = NGXVoiceAgent;
  // @ts-ignore
  window.createNGXWidget = createNGXWidget;
}