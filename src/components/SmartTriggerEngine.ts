/**
 * Smart Trigger Engine for NGX Voice Agent
 * Detects optimal moments to engage users based on behavior patterns
 */

export interface TriggerConfig {
  // Exit intent detection
  exitIntent?: {
    enabled: boolean;
    sensitivity?: 'low' | 'medium' | 'high'; // How sensitive to mouse movements
    delay?: number; // Minimum time before trigger can fire (seconds)
    cooldown?: number; // Cooldown between triggers (seconds)
  };
  
  // Scroll-based triggers
  scrollBased?: {
    enabled: boolean;
    percentage?: number; // Scroll percentage to trigger (0-100)
    direction?: 'down' | 'up' | 'both';
    dwellTime?: number; // Time to stay at scroll position before trigger
  };
  
  // Time-based triggers
  timeBased?: {
    enabled: boolean;
    delay?: number; // Time in seconds before trigger
    intervals?: number[]; // Multiple trigger points
    pageVisibility?: boolean; // Only trigger when page is visible
  };
  
  // Engagement-based triggers
  engagement?: {
    enabled: boolean;
    inactiveTime?: number; // Seconds of inactivity before trigger
    clickThreshold?: number; // Number of clicks before trigger
    formInteraction?: boolean; // Trigger on form focus/interaction
  };
  
  // Context-aware triggers
  contextual?: {
    enabled: boolean;
    touchpoint?: string; // Current touchpoint context
    userIntent?: 'cold' | 'warm' | 'hot'; // Detected user intent level
    previousVisits?: number; // Number of previous visits to consider
    referralSource?: string; // Source of traffic
  };
  
  // A/B testing configuration
  testing?: {
    enabled: boolean;
    variant?: 'A' | 'B' | 'C';
    percentage?: number; // Percentage of users to show trigger
  };
}

export interface TriggerEvent {
  type: 'exit-intent' | 'scroll' | 'time' | 'engagement' | 'contextual';
  confidence: number; // 0-1 confidence score
  context: {
    timeOnPage: number;
    scrollDepth: number;
    interactions: number;
    mouseMovements: number;
    touchpoint?: string;
    userBehavior?: 'browsing' | 'reading' | 'searching' | 'converting';
  };
  timestamp: Date;
  shouldTrigger: boolean;
}

type TriggerCallback = (event: TriggerEvent) => void;

export class SmartTriggerEngine {
  private config: TriggerConfig;
  private callbacks: TriggerCallback[] = [];
  private isInitialized = false;
  private sessionStartTime = Date.now();
  private lastTriggerTime = 0;
  private userBehaviorScore = 0;
  
  // Tracking variables
  private mouseMovements = 0;
  private scrollEvents = 0;
  private clickEvents = 0;
  private keyboardEvents = 0;
  private maxScrollDepth = 0;
  private currentScrollPosition = 0;
  private isPageVisible = true;
  private inactivityTimer: NodeJS.Timeout | null = null;
  private lastActivityTime = Date.now();
  
  // Exit intent detection
  private isNearTop = false;
  private mouseY = 0;
  private exitIntentTriggered = false;
  
  constructor(config: TriggerConfig) {
    this.config = {
      exitIntent: { enabled: true, sensitivity: 'medium', delay: 10, cooldown: 60, ...config.exitIntent },
      scrollBased: { enabled: true, percentage: 75, direction: 'down', dwellTime: 3, ...config.scrollBased },
      timeBased: { enabled: true, delay: 30, pageVisibility: true, ...config.timeBased },
      engagement: { enabled: true, inactiveTime: 60, clickThreshold: 3, formInteraction: true, ...config.engagement },
      contextual: { enabled: true, userIntent: 'cold', previousVisits: 0, ...config.contextual },
      testing: { enabled: false, variant: 'A', percentage: 100, ...config.testing },
      ...config
    };
  }

  public initialize(): void {
    if (this.isInitialized) return;
    
    this.setupEventListeners();
    this.startSessionTracking();
    this.initializeTimeTriggers();
    this.isInitialized = true;
    
    console.log('🎯 Smart Trigger Engine initialized', this.config);
  }

  public onTrigger(callback: TriggerCallback): void {
    this.callbacks.push(callback);
  }

  public destroy(): void {
    this.removeEventListeners();
    if (this.inactivityTimer) {
      clearTimeout(this.inactivityTimer);
    }
    this.isInitialized = false;
  }

  private setupEventListeners(): void {
    // Exit intent detection
    if (this.config.exitIntent?.enabled) {
      document.addEventListener('mousemove', this.handleMouseMove.bind(this));
      document.addEventListener('mouseleave', this.handleMouseLeave.bind(this));
    }
    
    // Scroll tracking
    if (this.config.scrollBased?.enabled) {
      window.addEventListener('scroll', this.handleScroll.bind(this), { passive: true });
    }
    
    // Engagement tracking
    if (this.config.engagement?.enabled) {
      document.addEventListener('click', this.handleClick.bind(this));
      document.addEventListener('keydown', this.handleKeyboard.bind(this));
      document.addEventListener('focus', this.handleFormInteraction.bind(this), true);
      document.addEventListener('input', this.handleFormInteraction.bind(this), true);
    }
    
    // Page visibility
    document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
    
    // Inactivity tracking
    this.resetInactivityTimer();
  }

  private removeEventListeners(): void {
    document.removeEventListener('mousemove', this.handleMouseMove.bind(this));
    document.removeEventListener('mouseleave', this.handleMouseLeave.bind(this));
    window.removeEventListener('scroll', this.handleScroll.bind(this));
    document.removeEventListener('click', this.handleClick.bind(this));
    document.removeEventListener('keydown', this.handleKeyboard.bind(this));
    document.removeEventListener('focus', this.handleFormInteraction.bind(this), true);
    document.removeEventListener('input', this.handleFormInteraction.bind(this), true);
    document.removeEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
  }

  private handleMouseMove(event: MouseEvent): void {
    this.mouseMovements++;
    this.mouseY = event.clientY;
    this.lastActivityTime = Date.now();
    this.resetInactivityTimer();
    
    // Exit intent detection
    if (this.config.exitIntent?.enabled && !this.exitIntentTriggered) {
      const sensitivity = this.config.exitIntent.sensitivity || 'medium';
      const threshold = sensitivity === 'high' ? 5 : sensitivity === 'medium' ? 10 : 20;
      
      if (event.clientY <= threshold && event.clientY >= 0) {
        this.detectExitIntent();
      }
    }
  }

  private handleMouseLeave(): void {
    if (this.config.exitIntent?.enabled && !this.exitIntentTriggered) {
      this.detectExitIntent();
    }
  }

  private detectExitIntent(): void {
    const timeOnPage = (Date.now() - this.sessionStartTime) / 1000;
    const minDelay = this.config.exitIntent?.delay || 10;
    const cooldown = this.config.exitIntent?.cooldown || 60;
    
    if (timeOnPage < minDelay) return;
    if (Date.now() - this.lastTriggerTime < cooldown * 1000) return;
    
    this.exitIntentTriggered = true;
    this.fireTrigger({
      type: 'exit-intent',
      confidence: this.calculateExitIntentConfidence(),
      context: this.getContext(),
      timestamp: new Date(),
      shouldTrigger: true
    });
  }

  private handleScroll(): void {
    this.scrollEvents++;
    this.lastActivityTime = Date.now();
    this.resetInactivityTimer();
    
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const documentHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrollPercentage = (scrollTop / documentHeight) * 100;
    
    this.currentScrollPosition = scrollPercentage;
    this.maxScrollDepth = Math.max(this.maxScrollDepth, scrollPercentage);
    
    if (this.config.scrollBased?.enabled) {
      const targetPercentage = this.config.scrollBased.percentage || 75;
      
      if (scrollPercentage >= targetPercentage) {
        setTimeout(() => {
          if (Math.abs(this.currentScrollPosition - scrollPercentage) < 5) {
            this.fireScrollTrigger(scrollPercentage);
          }
        }, (this.config.scrollBased.dwellTime || 3) * 1000);
      }
    }
  }

  private fireScrollTrigger(percentage: number): void {
    this.fireTrigger({
      type: 'scroll',
      confidence: this.calculateScrollConfidence(percentage),
      context: this.getContext(),
      timestamp: new Date(),
      shouldTrigger: true
    });
  }

  private handleClick(): void {
    this.clickEvents++;
    this.lastActivityTime = Date.now();
    this.resetInactivityTimer();
    
    if (this.config.engagement?.enabled) {
      const threshold = this.config.engagement.clickThreshold || 3;
      if (this.clickEvents >= threshold) {
        this.fireEngagementTrigger('clicks');
      }
    }
  }

  private handleKeyboard(): void {
    this.keyboardEvents++;
    this.lastActivityTime = Date.now();
    this.resetInactivityTimer();
  }

  private handleFormInteraction(): void {
    if (this.config.engagement?.formInteraction) {
      this.fireEngagementTrigger('form');
    }
  }

  private handleVisibilityChange(): void {
    this.isPageVisible = !document.hidden;
  }

  private resetInactivityTimer(): void {
    if (this.inactivityTimer) {
      clearTimeout(this.inactivityTimer);
    }
    
    if (this.config.engagement?.enabled) {
      const inactiveTime = this.config.engagement.inactiveTime || 60;
      this.inactivityTimer = setTimeout(() => {
        this.fireEngagementTrigger('inactivity');
      }, inactiveTime * 1000);
    }
  }

  private fireEngagementTrigger(reason: string): void {
    this.fireTrigger({
      type: 'engagement',
      confidence: this.calculateEngagementConfidence(reason),
      context: { ...this.getContext(), engagementReason: reason },
      timestamp: new Date(),
      shouldTrigger: true
    });
  }

  private initializeTimeTriggers(): void {
    if (!this.config.timeBased?.enabled) return;
    
    const delay = this.config.timeBased.delay || 30;
    const intervals = this.config.timeBased.intervals || [delay];
    
    intervals.forEach(interval => {
      setTimeout(() => {
        if (this.config.timeBased?.pageVisibility && !this.isPageVisible) return;
        
        this.fireTrigger({
          type: 'time',
          confidence: this.calculateTimeConfidence(interval),
          context: this.getContext(),
          timestamp: new Date(),
          shouldTrigger: true
        });
      }, interval * 1000);
    });
  }

  private startSessionTracking(): void {
    // Track user behavior patterns
    setInterval(() => {
      this.userBehaviorScore = this.calculateUserBehaviorScore();
    }, 5000); // Update every 5 seconds
  }

  private calculateUserBehaviorScore(): number {
    const timeOnPage = (Date.now() - this.sessionStartTime) / 1000;
    const engagementRate = (this.clickEvents + this.keyboardEvents) / Math.max(timeOnPage / 60, 1);
    const scrollEngagement = this.maxScrollDepth / 100;
    const mouseActivity = Math.min(this.mouseMovements / 100, 1);
    
    return (engagementRate * 0.4 + scrollEngagement * 0.3 + mouseActivity * 0.3);
  }

  private calculateExitIntentConfidence(): number {
    const timeOnPage = (Date.now() - this.sessionStartTime) / 1000;
    const engagementScore = this.userBehaviorScore;
    const scrollDepth = this.maxScrollDepth / 100;
    
    // Higher confidence if user spent time and engaged
    return Math.min(0.3 + (timeOnPage / 60) * 0.2 + engagementScore * 0.3 + scrollDepth * 0.2, 1);
  }

  private calculateScrollConfidence(percentage: number): number {
    const timeOnPage = (Date.now() - this.sessionStartTime) / 1000;
    const engagementScore = this.userBehaviorScore;
    
    return Math.min(0.4 + (percentage / 100) * 0.3 + (timeOnPage / 60) * 0.15 + engagementScore * 0.15, 1);
  }

  private calculateEngagementConfidence(reason: string): number {
    const baseConfidence = reason === 'form' ? 0.8 : reason === 'clicks' ? 0.6 : 0.4;
    const engagementScore = this.userBehaviorScore;
    
    return Math.min(baseConfidence + engagementScore * 0.2, 1);
  }

  private calculateTimeConfidence(interval: number): number {
    const engagementScore = this.userBehaviorScore;
    const scrollDepth = this.maxScrollDepth / 100;
    
    return Math.min(0.5 + engagementScore * 0.3 + scrollDepth * 0.2, 1);
  }

  private getContext() {
    const timeOnPage = (Date.now() - this.sessionStartTime) / 1000;
    
    return {
      timeOnPage,
      scrollDepth: this.maxScrollDepth,
      interactions: this.clickEvents + this.keyboardEvents,
      mouseMovements: this.mouseMovements,
      touchpoint: this.config.contextual?.touchpoint,
      userBehavior: this.getUserBehaviorType()
    };
  }

  private getUserBehaviorType(): 'browsing' | 'reading' | 'searching' | 'converting' {
    const timeOnPage = (Date.now() - this.sessionStartTime) / 1000;
    const scrollDepth = this.maxScrollDepth;
    const interactions = this.clickEvents + this.keyboardEvents;
    
    if (interactions > 5 && scrollDepth > 50) return 'converting';
    if (scrollDepth > 70 && timeOnPage > 60) return 'reading';
    if (interactions > 3) return 'searching';
    return 'browsing';
  }

  private shouldTrigger(confidence: number): boolean {
    // A/B testing check
    if (this.config.testing?.enabled) {
      const percentage = this.config.testing.percentage || 100;
      if (Math.random() * 100 > percentage) return false;
    }
    
    // Cooldown check
    const cooldown = 60; // Default 60 seconds between triggers
    if (Date.now() - this.lastTriggerTime < cooldown * 1000) return false;
    
    // Confidence threshold
    const threshold = 0.5; // Minimum confidence to trigger
    return confidence >= threshold;
  }

  private fireTrigger(event: TriggerEvent): void {
    if (!this.shouldTrigger(event.confidence)) {
      event.shouldTrigger = false;
    }
    
    if (event.shouldTrigger) {
      this.lastTriggerTime = Date.now();
    }
    
    this.callbacks.forEach(callback => {
      try {
        callback(event);
      } catch (error) {
        console.error('Error in trigger callback:', error);
      }
    });
    
    // Analytics tracking
    this.trackTriggerEvent(event);
  }

  private trackTriggerEvent(event: TriggerEvent): void {
    // Send analytics data
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'ngx_trigger_fired', {
        trigger_type: event.type,
        confidence: event.confidence,
        time_on_page: event.context.timeOnPage,
        scroll_depth: event.context.scrollDepth,
        should_trigger: event.shouldTrigger
      });
    }
    
    console.log('🎯 Trigger event:', event);
  }

  // Public methods for manual trigger control
  public manualTrigger(type: string, context?: any): void {
    this.fireTrigger({
      type: type as any,
      confidence: 1.0,
      context: { ...this.getContext(), ...context, manual: true },
      timestamp: new Date(),
      shouldTrigger: true
    });
  }

  public updateConfig(newConfig: Partial<TriggerConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  public getStats() {
    return {
      timeOnPage: (Date.now() - this.sessionStartTime) / 1000,
      scrollDepth: this.maxScrollDepth,
      interactions: this.clickEvents + this.keyboardEvents,
      mouseMovements: this.mouseMovements,
      userBehaviorScore: this.userBehaviorScore
    };
  }
}

// Global type declaration for gtag
declare global {
  interface Window {
    gtag?: (...args: any[]) => void;
  }
}

export default SmartTriggerEngine;