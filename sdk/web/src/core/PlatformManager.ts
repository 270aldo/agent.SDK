import { PlatformType, UIConfig, TriggerConfig, StyleConfig } from '../types';

export class PlatformManager {
  private platform: PlatformType;
  private uiConfig?: UIConfig;
  private triggerConfig?: TriggerConfig;
  private styleConfig?: StyleConfig;
  private widgetElement?: HTMLElement;
  private isDestroyed = false;

  constructor(platform: PlatformType, uiConfig?: UIConfig) {
    this.platform = platform;
    this.uiConfig = uiConfig;
    this.setupPlatformDefaults();
  }

  private setupPlatformDefaults(): void {
    switch (this.platform) {
      case 'lead_magnet':
        this.triggerConfig = { type: 'auto', threshold: 3 }; // 3 seconds after page load
        this.styleConfig = {
          position: 'bottom-right',
          size: 'medium',
          theme: 'light'
        };
        break;

      case 'landing_page':
        this.triggerConfig = { type: 'scroll', threshold: 70 }; // 70% scroll
        this.styleConfig = {
          position: 'center',
          size: 'large',
          theme: 'auto'
        };
        break;

      case 'blog':
        this.triggerConfig = { type: 'time', threshold: 30 }; // 30 seconds
        this.styleConfig = {
          position: 'bottom-right',
          size: 'small',
          theme: 'light'
        };
        break;

      case 'mobile_app':
        this.styleConfig = {
          position: 'fullscreen',
          size: 'large',
          theme: 'auto'
        };
        break;

      default:
        this.styleConfig = {
          position: 'bottom-right',
          size: 'medium',
          theme: 'light'
        };
    }

    // Override with user config
    if (this.uiConfig) {
      this.styleConfig = { ...this.styleConfig, ...this.uiConfig };
    }
  }

  createWidget(): HTMLElement {
    if (this.widgetElement) {
      return this.widgetElement;
    }

    const widget = document.createElement('div');
    widget.id = 'ngx-voice-agent-widget';
    widget.className = this.getWidgetClasses();
    
    // Apply styles
    this.applyWidgetStyles(widget);

    // Add basic structure
    widget.innerHTML = this.getWidgetHTML();

    // Append to body
    document.body.appendChild(widget);
    this.widgetElement = widget;

    return widget;
  }

  private getWidgetClasses(): string {
    const classes = ['ngx-voice-widget'];
    
    if (this.styleConfig?.position) {
      classes.push(`ngx-position-${this.styleConfig.position}`);
    }
    
    if (this.styleConfig?.size) {
      classes.push(`ngx-size-${this.styleConfig.size}`);
    }
    
    if (this.styleConfig?.theme) {
      classes.push(`ngx-theme-${this.styleConfig.theme}`);
    }

    return classes.join(' ');
  }

  private applyWidgetStyles(widget: HTMLElement): void {
    const baseStyles: Record<string, string> = {
      position: 'fixed',
      zIndex: '10000',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
      borderRadius: '12px',
      backgroundColor: '#ffffff',
      border: '1px solid #e2e8f0',
      overflow: 'hidden',
      transition: 'all 0.3s ease'
    };

    // Position-specific styles
    switch (this.styleConfig?.position) {
      case 'bottom-right':
        Object.assign(baseStyles, {
          bottom: '20px',
          right: '20px',
          width: '350px',
          maxHeight: '500px'
        });
        break;
      
      case 'bottom-left':
        Object.assign(baseStyles, {
          bottom: '20px',
          left: '20px',
          width: '350px',
          maxHeight: '500px'
        });
        break;
      
      case 'center':
        Object.assign(baseStyles, {
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '400px',
          maxHeight: '600px'
        });
        break;
      
      case 'fullscreen':
        Object.assign(baseStyles, {
          top: '0',
          left: '0',
          width: '100%',
          height: '100%',
          borderRadius: '0',
          border: 'none'
        });
        break;
    }

    // Size-specific adjustments
    switch (this.styleConfig?.size) {
      case 'small':
        baseStyles.width = '280px';
        baseStyles.maxHeight = '400px';
        break;
      
      case 'large':
        baseStyles.width = '420px';
        baseStyles.maxHeight = '700px';
        break;
    }

    // Theme-specific styles
    if (this.styleConfig?.theme === 'dark') {
      baseStyles.backgroundColor = '#1a202c';
      baseStyles.borderColor = '#2d3748';
      baseStyles.color = '#ffffff';
    }

    // Apply custom colors
    if (this.styleConfig?.colors?.background) {
      baseStyles.backgroundColor = this.styleConfig.colors.background;
    }

    // Apply styles to element
    Object.assign(widget.style, baseStyles);

    // Add custom CSS if provided
    if (this.uiConfig?.customCSS) {
      const styleElement = document.createElement('style');
      styleElement.textContent = this.uiConfig.customCSS;
      document.head.appendChild(styleElement);
    }
  }

  private getWidgetHTML(): string {
    return `
      <div class="ngx-widget-header">
        <div class="ngx-widget-title">
          <span class="ngx-widget-avatar">🤖</span>
          <span class="ngx-widget-name">NGX Assistant</span>
        </div>
        <button class="ngx-widget-close" onclick="this.closest('.ngx-voice-widget').style.display='none'">
          ✕
        </button>
      </div>
      <div class="ngx-widget-content">
        <div class="ngx-chat-messages"></div>
        <div class="ngx-chat-input">
          <input type="text" placeholder="Type your message..." />
          <button class="ngx-send-button">Send</button>
        </div>
      </div>
    `;
  }

  setupTriggers(onTrigger: () => void): void {
    if (!this.triggerConfig || this.platform === 'api_only') {
      return;
    }

    switch (this.triggerConfig.type) {
      case 'auto':
        setTimeout(onTrigger, (this.triggerConfig.threshold || 3) * 1000);
        break;

      case 'time':
        setTimeout(onTrigger, (this.triggerConfig.threshold || 30) * 1000);
        break;

      case 'scroll':
        this.setupScrollTrigger(onTrigger, this.triggerConfig.threshold || 70);
        break;

      case 'exit_intent':
        this.setupExitIntentTrigger(onTrigger);
        break;

      case 'manual':
        // No automatic trigger - must be called manually
        break;
    }
  }

  private setupScrollTrigger(onTrigger: () => void, threshold: number): void {
    let triggered = false;

    const handleScroll = () => {
      if (triggered || this.isDestroyed) return;

      const scrollPercentage = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
      
      if (scrollPercentage >= threshold) {
        triggered = true;
        onTrigger();
        window.removeEventListener('scroll', handleScroll);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
  }

  private setupExitIntentTrigger(onTrigger: () => void): void {
    let triggered = false;

    const handleMouseLeave = (event: MouseEvent) => {
      if (triggered || this.isDestroyed) return;
      
      if (event.clientY <= 0) {
        triggered = true;
        onTrigger();
        document.removeEventListener('mouseleave', handleMouseLeave);
      }
    };

    document.addEventListener('mouseleave', handleMouseLeave);
  }

  showWidget(): void {
    if (this.widgetElement) {
      this.widgetElement.style.display = 'block';
    }
  }

  hideWidget(): void {
    if (this.widgetElement) {
      this.widgetElement.style.display = 'none';
    }
  }

  updateWidgetContent(content: string): void {
    if (this.widgetElement) {
      const messagesContainer = this.widgetElement.querySelector('.ngx-chat-messages');
      if (messagesContainer) {
        messagesContainer.innerHTML = content;
      }
    }
  }

  destroy(): void {
    this.isDestroyed = true;
    
    if (this.widgetElement) {
      this.widgetElement.remove();
      this.widgetElement = undefined;
    }
  }
}