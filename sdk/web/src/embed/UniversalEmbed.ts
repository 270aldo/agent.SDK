/**
 * NGX Voice Agent Universal Embed System
 * One-line integration for any website
 * 
 * Usage: <script src="https://cdn.ngx.com/voice-agent.js" data-touchpoint="landing-page"></script>
 */

import { SmartTriggerEngine, TriggerConfig, TriggerEvent } from '../components/SmartTriggerEngine';

interface EmbedConfig {
  // Core configuration
  apiUrl?: string;
  apiKey?: string;
  
  // Touchpoint context
  touchpoint: 'landing-page' | 'lead-magnet' | 'blog' | 'webinar-end' | 'exit-intent' | 'email-campaign' | 'custom';
  context?: {
    pageType?: string;
    productCategory?: string;
    campaignId?: string;
    userSegment?: string;
    customData?: Record<string, any>;
  };
  
  // UI configuration
  ui?: {
    size?: 'compact' | 'medium' | 'large' | 'fullscreen';
    position?: 'bottom-right' | 'bottom-left' | 'center' | 'top-right' | 'top-left';
    theme?: 'auto' | 'light' | 'dark';
    customCSS?: string;
  };
  
  // Branding
  branding?: {
    primaryColor?: string;
    secondaryColor?: string;
    logo?: string;
    companyName?: string;
    agentName?: string;
  };
  
  // Trigger configuration
  triggers?: TriggerConfig;
  
  // A/B testing
  testing?: {
    enabled?: boolean;
    variant?: string;
    percentage?: number;
  };
  
  // Analytics
  analytics?: {
    enabled?: boolean;
    gtag?: boolean;
    customTracker?: (event: string, data: any) => void;
  };
  
  // Behavior settings
  behavior?: {
    autoShow?: boolean;
    persistState?: boolean;
    maxShowsPerSession?: number;
    maxShowsPerDay?: number;
    respectDoNotTrack?: boolean;
  };
}

interface EmbedAPI {
  // Control methods
  show(): void;
  hide(): void;
  toggle(): void;
  destroy(): void;
  
  // Configuration
  updateConfig(config: Partial<EmbedConfig>): void;
  
  // State management
  getState(): any;
  setState(state: any): void;
  
  // Analytics
  track(event: string, data?: any): void;
  
  // Events
  on(event: string, callback: Function): void;
  off(event: string, callback: Function): void;
}

class NGXVoiceAgentEmbed implements EmbedAPI {
  private config: EmbedConfig;
  private triggerEngine: SmartTriggerEngine;
  private container: HTMLElement | null = null;
  private isVisible = false;
  private isInitialized = false;
  private eventListeners: Map<string, Function[]> = new Map();
  private sessionData: any = {};
  
  constructor(config: EmbedConfig) {
    this.config = this.normalizeConfig(config);
    this.triggerEngine = new SmartTriggerEngine(this.config.triggers || {});
    
    // Initialize immediately if DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.initialize());
    } else {
      this.initialize();
    }
  }

  private normalizeConfig(config: EmbedConfig): EmbedConfig {
    return {
      apiUrl: config.apiUrl || 'https://api.ngx.com/voice-agent',
      touchpoint: config.touchpoint || 'custom',
      ui: {
        size: 'medium',
        position: 'bottom-right',
        theme: 'auto',
        ...config.ui
      },
      branding: {
        companyName: 'NGX',
        agentName: 'Expert Assistant',
        primaryColor: '#667eea',
        secondaryColor: '#764ba2',
        ...config.branding
      },
      behavior: {
        autoShow: false,
        persistState: true,
        maxShowsPerSession: 3,
        maxShowsPerDay: 5,
        respectDoNotTrack: true,
        ...config.behavior
      },
      analytics: {
        enabled: true,
        gtag: true,
        ...config.analytics
      },
      testing: {
        enabled: false,
        percentage: 100,
        ...config.testing
      },
      ...config
    };
  }

  private async initialize(): Promise<void> {
    if (this.isInitialized) return;
    
    try {
      // Check if should show based on behavior settings
      if (!this.shouldShowAgent()) {
        console.log('NGX Voice Agent: Skipping initialization due to behavior settings');
        return;
      }
      
      // Create container
      this.createContainer();
      
      // Load styles
      await this.loadStyles();
      
      // Initialize trigger engine
      this.initializeTriggerEngine();
      
      // Set up session tracking
      this.initializeSessionTracking();
      
      // Auto-show if configured
      if (this.config.behavior?.autoShow) {
        setTimeout(() => this.show(), 2000);
      }
      
      this.isInitialized = true;
      this.emit('initialized', { config: this.config });
      this.track('agent_initialized', { touchpoint: this.config.touchpoint });
      
      console.log('🚀 NGX Voice Agent initialized', this.config);
      
    } catch (error) {
      console.error('Failed to initialize NGX Voice Agent:', error);
      this.track('initialization_error', { error: error.message });
    }
  }

  private shouldShowAgent(): boolean {
    const behavior = this.config.behavior!;
    
    // Check Do Not Track
    if (behavior.respectDoNotTrack && navigator.doNotTrack === '1') {
      return false;
    }
    
    // Check A/B testing
    if (this.config.testing?.enabled) {
      const percentage = this.config.testing.percentage || 100;
      if (Math.random() * 100 > percentage) {
        return false;
      }
    }
    
    // Check session limits
    const sessionShows = this.getSessionData('shows', 0);
    if (sessionShows >= (behavior.maxShowsPerSession || 3)) {
      return false;
    }
    
    // Check daily limits
    const dailyShows = this.getDailyData('shows', 0);
    if (dailyShows >= (behavior.maxShowsPerDay || 5)) {
      return false;
    }
    
    return true;
  }

  private createContainer(): void {
    this.container = document.createElement('div');
    this.container.id = 'ngx-voice-agent-embed';
    this.container.style.cssText = `
      position: fixed;
      z-index: 2147483647;
      pointer-events: none;
      transition: all 0.3s ease;
    `;
    
    // Set position
    const position = this.config.ui?.position || 'bottom-right';
    switch (position) {
      case 'bottom-right':
        this.container.style.bottom = '24px';
        this.container.style.right = '24px';
        break;
      case 'bottom-left':
        this.container.style.bottom = '24px';
        this.container.style.left = '24px';
        break;
      case 'top-right':
        this.container.style.top = '24px';
        this.container.style.right = '24px';
        break;
      case 'top-left':
        this.container.style.top = '24px';
        this.container.style.left = '24px';
        break;
      case 'center':
        this.container.style.top = '50%';
        this.container.style.left = '50%';
        this.container.style.transform = 'translate(-50%, -50%)';
        break;
    }
    
    document.body.appendChild(this.container);
  }

  private async loadStyles(): Promise<void> {
    return new Promise((resolve) => {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = `${this.config.apiUrl}/embed/styles.css`;
      link.onload = () => resolve();
      link.onerror = () => {
        console.warn('Failed to load NGX Voice Agent styles, using inline styles');
        this.injectInlineStyles();
        resolve();
      };
      document.head.appendChild(link);
    });
  }

  private injectInlineStyles(): void {
    const style = document.createElement('style');
    style.textContent = `
      #ngx-voice-agent-embed {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      }
      
      .ngx-trigger-button {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea, #764ba2);
        border: none;
        cursor: pointer;
        pointer-events: auto;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 24px;
      }
      
      .ngx-trigger-button:hover {
        transform: scale(1.1);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4);
      }
      
      .ngx-agent-interface {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 400px;
        height: 600px;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
        pointer-events: auto;
        z-index: 2147483647;
      }
      
      @media (max-width: 768px) {
        .ngx-agent-interface {
          width: calc(100vw - 32px);
          height: calc(100vh - 64px);
        }
      }
    `;
    document.head.appendChild(style);
  }

  private initializeTriggerEngine(): void {
    this.triggerEngine.onTrigger((event: TriggerEvent) => {
      if (event.shouldTrigger) {
        this.handleTriggerEvent(event);
      }
    });
    
    this.triggerEngine.initialize();
  }

  private handleTriggerEvent(event: TriggerEvent): void {
    console.log('🎯 Trigger activated:', event);
    
    this.track('trigger_activated', {
      type: event.type,
      confidence: event.confidence,
      context: event.context
    });
    
    this.emit('trigger', event);
    
    // Auto-show if configured
    if (!this.isVisible) {
      this.show();
    }
  }

  private initializeSessionTracking(): void {
    // Track page view
    this.track('page_view', {
      touchpoint: this.config.touchpoint,
      url: window.location.href,
      referrer: document.referrer
    });
    
    // Track session start
    if (!this.getSessionData('started')) {
      this.setSessionData('started', Date.now());
      this.track('session_start', {
        touchpoint: this.config.touchpoint
      });
    }
    
    // Track page unload
    window.addEventListener('beforeunload', () => {
      this.track('session_end', {
        duration: Date.now() - this.getSessionData('started', Date.now()),
        triggers: this.triggerEngine.getStats()
      });
    });
  }

  // Public API methods
  public show(): void {
    if (!this.isInitialized || this.isVisible) return;
    
    this.incrementSessionData('shows');
    this.incrementDailyData('shows');
    
    this.renderInterface();
    this.isVisible = true;
    
    this.emit('show');
    this.track('agent_shown', {
      method: 'api',
      touchpoint: this.config.touchpoint
    });
  }

  public hide(): void {
    if (!this.isVisible) return;
    
    const interface_ = document.getElementById('ngx-agent-interface');
    if (interface_) {
      interface_.style.opacity = '0';
      interface_.style.transform = 'translate(-50%, -50%) scale(0.8)';
      setTimeout(() => {
        interface_.remove();
      }, 300);
    }
    
    this.isVisible = false;
    this.emit('hide');
    this.track('agent_hidden');
  }

  public toggle(): void {
    if (this.isVisible) {
      this.hide();
    } else {
      this.show();
    }
  }

  public destroy(): void {
    this.triggerEngine.destroy();
    if (this.container) {
      this.container.remove();
    }
    this.isInitialized = false;
    this.emit('destroy');
  }

  public updateConfig(newConfig: Partial<EmbedConfig>): void {
    this.config = { ...this.config, ...newConfig };
    if (newConfig.triggers) {
      this.triggerEngine.updateConfig(newConfig.triggers);
    }
    this.emit('configUpdated', newConfig);
  }

  public getState(): any {
    return {
      isVisible: this.isVisible,
      isInitialized: this.isInitialized,
      config: this.config,
      sessionData: this.sessionData,
      triggerStats: this.triggerEngine.getStats()
    };
  }

  public setState(state: any): void {
    this.sessionData = { ...this.sessionData, ...state };
  }

  public track(event: string, data: any = {}): void {
    const eventData = {
      event,
      timestamp: Date.now(),
      url: window.location.href,
      touchpoint: this.config.touchpoint,
      variant: this.config.testing?.variant,
      ...data
    };
    
    // Google Analytics
    if (this.config.analytics?.gtag && window.gtag) {
      window.gtag('event', event, {
        event_category: 'ngx_voice_agent',
        ...eventData
      });
    }
    
    // Custom tracker
    if (this.config.analytics?.customTracker) {
      this.config.analytics.customTracker(event, eventData);
    }
    
    // Internal tracking
    console.log('📊 NGX Analytics:', eventData);
  }

  public on(event: string, callback: Function): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event)!.push(callback);
  }

  public off(event: string, callback: Function): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  private emit(event: string, data?: any): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error);
        }
      });
    }
  }

  private renderInterface(): void {
    if (!this.container) return;
    
    const interface_ = document.createElement('div');
    interface_.id = 'ngx-agent-interface';
    interface_.className = 'ngx-agent-interface';
    interface_.style.opacity = '0';
    interface_.style.transform = 'translate(-50%, -50%) scale(0.8)';
    
    // Create a simple interface for now
    interface_.innerHTML = `
      <div style="padding: 24px; text-align: center;">
        <div style="width: 120px; height: 120px; border-radius: 50%; 
                    background: linear-gradient(135deg, ${this.config.branding?.primaryColor}, ${this.config.branding?.secondaryColor}); 
                    margin: 0 auto 24px; display: flex; align-items: center; justify-content: center; color: white; font-size: 24px;">
          🎤
        </div>
        <h3 style="margin: 0 0 8px 0; color: #333;">
          ${this.config.branding?.companyName} ${this.config.branding?.agentName}
        </h3>
        <p style="margin: 0 0 24px 0; color: #666;">
          ${this.getTouchpointMessage()}
        </p>
        <button onclick="window.ngxVoiceAgent.hide()" 
                style="background: linear-gradient(135deg, ${this.config.branding?.primaryColor}, ${this.config.branding?.secondaryColor}); 
                       color: white; border: none; padding: 12px 24px; border-radius: 12px; cursor: pointer; font-weight: 600;">
          Iniciar Conversación (7 min)
        </button>
        <button onclick="window.ngxVoiceAgent.hide()" 
                style="background: transparent; color: #666; border: 1px solid #ddd; padding: 8px 16px; 
                       border-radius: 8px; cursor: pointer; margin-left: 12px;">
          Cerrar
        </button>
      </div>
    `;
    
    document.body.appendChild(interface_);
    
    // Animate in
    setTimeout(() => {
      interface_.style.opacity = '1';
      interface_.style.transform = 'translate(-50%, -50%) scale(1)';
    }, 10);
  }

  private getTouchpointMessage(): string {
    const touchpoint = this.config.touchpoint;
    const companyName = this.config.branding?.companyName || 'NGX';
    
    switch (touchpoint) {
      case 'landing-page':
        return `¡Hola! Soy el asistente experto de ${companyName}. ¿Tienes 7 minutos para una conversación que podría transformar tu perspectiva?`;
      case 'lead-magnet':
        return `¡Excelente! Descargaste nuestro recurso. ¿Conversamos 7 minutos sobre cómo aplicarlo a tu caso?`;
      case 'webinar-end':
        return `¡Increíble sesión! Tengo 7 minutos para ayudarte con preguntas específicas sobre tu transformación.`;
      case 'exit-intent':
        return `¡Espera! Antes de irte, ¿puedo hacerte 2 preguntas para enviarte algo personalizado?`;
      default:
        return `¡Hola! Soy tu asistente experto de ${companyName}. ¿Tienes 7 minutos para una conversación personalizada?`;
    }
  }

  // Session and local storage helpers
  private getSessionData(key: string, defaultValue: any = null): any {
    const data = sessionStorage.getItem(`ngx_voice_agent_${key}`);
    return data ? JSON.parse(data) : defaultValue;
  }

  private setSessionData(key: string, value: any): void {
    sessionStorage.setItem(`ngx_voice_agent_${key}`, JSON.stringify(value));
  }

  private incrementSessionData(key: string): void {
    const current = this.getSessionData(key, 0);
    this.setSessionData(key, current + 1);
  }

  private getDailyData(key: string, defaultValue: any = null): any {
    const today = new Date().toDateString();
    const data = localStorage.getItem(`ngx_voice_agent_daily_${today}_${key}`);
    return data ? JSON.parse(data) : defaultValue;
  }

  private incrementDailyData(key: string): void {
    const today = new Date().toDateString();
    const current = this.getDailyData(key, 0);
    localStorage.setItem(`ngx_voice_agent_daily_${today}_${key}`, JSON.stringify(current + 1));
  }
}

// Auto-initialize if script tag has data attributes
function autoInitialize(): void {
  const script = document.querySelector('script[src*="voice-agent.js"]') as HTMLScriptElement;
  if (!script) return;
  
  const config: EmbedConfig = {
    touchpoint: (script.dataset.touchpoint as any) || 'custom',
    context: {
      pageType: script.dataset.pageType,
      productCategory: script.dataset.productCategory,
      campaignId: script.dataset.campaignId,
      userSegment: script.dataset.userSegment
    },
    ui: {
      size: (script.dataset.size as any) || 'medium',
      position: (script.dataset.position as any) || 'bottom-right',
      theme: (script.dataset.theme as any) || 'auto'
    },
    branding: {
      companyName: script.dataset.companyName,
      primaryColor: script.dataset.primaryColor,
      secondaryColor: script.dataset.secondaryColor
    },
    behavior: {
      autoShow: script.dataset.autoShow === 'true',
      maxShowsPerSession: parseInt(script.dataset.maxShowsPerSession || '3'),
      maxShowsPerDay: parseInt(script.dataset.maxShowsPerDay || '5')
    }
  };
  
  // Initialize
  const embed = new NGXVoiceAgentEmbed(config);
  
  // Expose global API
  (window as any).ngxVoiceAgent = embed;
  
  console.log('🚀 NGX Voice Agent auto-initialized from script tag');
}

// Auto-initialize if running in browser
if (typeof window !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoInitialize);
  } else {
    autoInitialize();
  }
}

// Export for manual initialization
export { NGXVoiceAgentEmbed, EmbedConfig, EmbedAPI };
export default NGXVoiceAgentEmbed;