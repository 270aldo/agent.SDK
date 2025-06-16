# NGX Voice Agent Configuration Guide

This guide covers all configuration options available for the NGX Voice Agent SDK across different platforms and use cases.

## 🔧 Basic Configuration

### Minimal Setup

```javascript
const config = {
    apiUrl: 'https://your-api.ngx.com',
    platform: 'lead_magnet'
};

const agent = new NGXVoiceAgent();
await agent.init(config);
```

### Complete Configuration

```javascript
const config = {
    // Required
    apiUrl: 'https://your-api.ngx.com',
    platform: 'lead_magnet', // 'lead_magnet' | 'landing_page' | 'blog' | 'mobile_app' | 'api_only'
    
    // Optional
    apiKey: 'your_api_key', // For server-side usage only
    
    // Feature Configuration
    features: {
        voiceEnabled: true,
        humanTransfer: true,
        analytics: true,
        followUp: true,
        offlineMode: false
    },
    
    // UI Configuration
    ui: {
        position: 'bottom-right', // 'bottom-right' | 'bottom-left' | 'center' | 'fullscreen'
        size: 'medium', // 'small' | 'medium' | 'large'
        theme: 'light', // 'light' | 'dark' | 'auto'
        showAvatar: true,
        customCSS: '',
        colors: {
            primary: '#667eea',
            secondary: '#764ba2',
            background: '#ffffff',
            text: '#333333'
        }
    },
    
    // Voice Configuration
    voice: {
        enabled: true,
        autoPlay: true,
        voice: 'en-US-Standard-J',
        speed: 1.0,
        volume: 1.0
    },
    
    // Trigger Configuration
    trigger: {
        type: 'auto', // 'auto' | 'manual' | 'scroll' | 'time' | 'exit_intent'
        threshold: 3, // Seconds for 'time', percentage for 'scroll'
        conditions: []
    },
    
    // Behavior Configuration
    behavior: {
        autoStart: true,
        greeting: 'Hi! How can I help you today?',
        enableVoice: true,
        transferToHuman: true,
        contextualQuestions: []
    },
    
    // Analytics Configuration
    analytics: {
        enabled: true,
        trackingId: 'your_tracking_id',
        customEvents: [],
        debugMode: false
    },
    
    // Privacy Configuration
    privacy: {
        dataRetention: '30days',
        anonymizeData: false,
        enableGDPRCompliance: true,
        cookieConsent: true
    }
};
```

## 🎯 Platform-Specific Configurations

### Lead Magnet Configuration

```javascript
const leadMagnetConfig = {
    apiUrl: 'https://your-api.ngx.com',
    platform: 'lead_magnet',
    
    trigger: {
        type: 'auto',
        threshold: 3 // 3 seconds after download
    },
    
    ui: {
        position: 'bottom-right',
        size: 'medium',
        theme: 'light',
        colors: {
            primary: '#4CAF50', // Success green
            secondary: '#45a049',
            background: '#ffffff'
        }
    },
    
    behavior: {
        autoStart: true,
        greeting: 'Thanks for downloading! I\'m here to help you get the most out of your guide.',
        contextualQuestions: [
            'What attracted you to this guide?',
            'What\'s your biggest challenge in this area?',
            'Have you tried solving this before?'
        ]
    },
    
    voice: {
        enabled: true,
        autoPlay: true,
        voice: 'en-US-Standard-J', // Friendly female voice
        speed: 0.9, // Slightly slower for clarity
        volume: 0.8
    }
};
```

### Landing Page Configuration

```javascript
const landingPageConfig = {
    apiUrl: 'https://your-api.ngx.com',
    platform: 'landing_page',
    
    trigger: {
        type: 'scroll',
        threshold: 70, // 70% scroll depth
        conditions: [
            () => !sessionStorage.getItem('ngx_engaged'),
            () => document.querySelector('.pricing-section').getBoundingClientRect().top < window.innerHeight
        ]
    },
    
    ui: {
        position: 'center',
        size: 'large',
        theme: 'auto',
        colors: {
            primary: '#ff6b6b',
            secondary: '#ff8e53',
            background: '#ffffff'
        },
        customCSS: `
            .ngx-voice-widget {
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                border-radius: 15px;
            }
        `
    },
    
    behavior: {
        autoStart: true,
        greeting: 'Ready to transform your life? Let me help you choose the perfect program!',
        transferToHuman: true,
        contextualQuestions: [
            'What\'s your primary fitness goal?',
            'What\'s held you back in the past?',
            'How committed are you to making a change?'
        ]
    }
};
```

### Blog Widget Configuration

```javascript
const blogWidgetConfig = {
    apiUrl: 'https://your-api.ngx.com',
    platform: 'blog',
    
    trigger: {
        type: 'time',
        threshold: 30, // 30 seconds reading time
        conditions: [
            () => getScrollPercentage() > 40,
            () => getReadingTime() > 20
        ]
    },
    
    ui: {
        position: 'bottom-right',
        size: 'small',
        theme: 'light',
        showAvatar: true
    },
    
    behavior: {
        autoStart: false, // Wait for user interaction
        greeting: 'Questions about this article? I\'m here to help!',
        contextualQuestions: [
            'How can I help you apply this information?',
            'Do you have questions about the content?',
            'Would you like personalized recommendations?'
        ]
    },
    
    // Blog-specific configuration
    content: {
        articleTitle: document.title,
        articleCategory: getArticleCategory(),
        readingTime: getEstimatedReadingTime(),
        keywords: extractKeywords()
    }
};
```

### Mobile App Configuration

```javascript
const mobileConfig = {
    apiUrl: 'https://your-api.ngx.com',
    platform: 'mobile_app',
    
    features: {
        voiceEnabled: true,
        humanTransfer: true,
        analytics: true,
        followUp: true,
        offlineMode: true, // Enable offline capabilities
        pushNotifications: true
    },
    
    ui: {
        position: 'fullscreen',
        size: 'large',
        theme: 'auto', // Follows system theme
        adaptiveUI: true, // Adapts to screen size
        safeArea: true // Respects safe area insets
    },
    
    behavior: {
        autoStart: false, // Manual start for mobile
        greeting: 'Hi! I\'m your NGX assistant. How can I help you today?',
        enableVoice: true,
        transferToHuman: true
    },
    
    // Mobile-specific features
    mobile: {
        hapticFeedback: true,
        orientationLock: false,
        backgroundMode: 'limited',
        cacheStrategy: 'aggressive',
        dataUsageOptimization: true
    }
};
```

## 🎨 UI Customization

### Color Themes

```javascript
// Light Theme
const lightTheme = {
    theme: 'light',
    colors: {
        primary: '#667eea',
        secondary: '#764ba2',
        background: '#ffffff',
        text: '#333333',
        textSecondary: '#666666',
        border: '#e2e8f0',
        success: '#4CAF50',
        error: '#f44336',
        warning: '#ff9800'
    }
};

// Dark Theme
const darkTheme = {
    theme: 'dark',
    colors: {
        primary: '#667eea',
        secondary: '#764ba2',
        background: '#1a202c',
        text: '#ffffff',
        textSecondary: '#a0aec0',
        border: '#2d3748',
        success: '#48bb78',
        error: '#fc8181',
        warning: '#f6ad55'
    }
};

// Custom Brand Theme
const brandTheme = {
    theme: 'custom',
    colors: {
        primary: '#your-brand-primary',
        secondary: '#your-brand-secondary',
        background: '#your-brand-background',
        text: '#your-brand-text',
        // ... other colors
    }
};
```

### Custom CSS

```javascript
const config = {
    // ... other config
    ui: {
        customCSS: `
            /* Custom widget styling */
            .ngx-voice-widget {
                font-family: 'Your Brand Font', sans-serif;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            }
            
            /* Custom header styling */
            .ngx-widget-header {
                background: linear-gradient(135deg, #your-color-1, #your-color-2);
                border-radius: 20px 20px 0 0;
            }
            
            /* Custom message styling */
            .ngx-message.assistant .ngx-message-content {
                background: #your-assistant-color;
                border-left: 4px solid #your-accent-color;
                border-radius: 15px 15px 15px 5px;
            }
            
            .ngx-message.user .ngx-message-content {
                background: #your-user-color;
                border-radius: 15px 15px 5px 15px;
            }
            
            /* Custom button styling */
            .ngx-send-button {
                background: linear-gradient(45deg, #your-primary, #your-secondary);
                border-radius: 25px;
                transition: all 0.3s ease;
            }
            
            .ngx-send-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            }
            
            /* Animation customization */
            .ngx-voice-widget.show {
                animation: slideInUp 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            }
            
            @keyframes slideInUp {
                from {
                    transform: translateY(100px);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }
        `
    }
};
```

## 🗣️ Voice Configuration

### Voice Options

```javascript
const voiceConfig = {
    voice: {
        enabled: true,
        autoPlay: true,
        
        // Voice selection (platform-dependent)
        voice: 'en-US-Standard-J', // Google Cloud TTS
        // voice: 'Samantha',       // System TTS (macOS)
        // voice: 'Microsoft Zira', // System TTS (Windows)
        
        // Voice parameters
        speed: 1.0,    // 0.25 to 4.0
        pitch: 1.0,    // 0.0 to 2.0
        volume: 1.0,   // 0.0 to 1.0
        
        // Advanced options
        ssmlEnabled: true,
        emotionalTone: 'friendly', // 'neutral' | 'friendly' | 'professional' | 'excited'
        
        // Voice optimization
        compression: 'high',
        streaming: true,
        caching: true,
        
        // Fallback options
        fallbackVoice: 'system-default',
        enableSilence: false,
        retryAttempts: 3
    }
};
```

### SSML Support

```javascript
// Using SSML for enhanced voice control
const agent = new NGXVoiceAgent();

agent.on('message.received', ({ message }) => {
    if (message.audio && agent.config.voice.ssmlEnabled) {
        // Enhance message with SSML
        const enhancedMessage = enhanceWithSSML(message.content);
        agent.playAudio(enhancedMessage);
    }
});

function enhanceWithSSML(text) {
    return `
        <speak>
            <prosody rate="medium" pitch="medium">
                ${text}
            </prosody>
            <break time="0.5s"/>
        </speak>
    `;
}
```

## 🎚️ Trigger Configuration

### Advanced Trigger Setup

```javascript
const advancedTriggers = {
    // Multiple trigger types
    triggers: [
        {
            name: 'scroll_trigger',
            type: 'scroll',
            threshold: 70,
            priority: 1,
            conditions: [
                () => !localStorage.getItem('ngx_engaged_today'),
                () => getTimeOnPage() > 30
            ],
            cooldown: 3600000 // 1 hour cooldown
        },
        
        {
            name: 'exit_intent',
            type: 'exit_intent',
            priority: 2,
            conditions: [
                () => getScrollPercentage() > 50,
                () => !sessionStorage.getItem('ngx_exit_triggered')
            ],
            maxTriggers: 1 // Only trigger once per session
        },
        
        {
            name: 'idle_trigger',
            type: 'idle',
            threshold: 60, // 60 seconds of inactivity
            priority: 3,
            conditions: [
                () => document.hasFocus(),
                () => getScrollPercentage() > 25
            ]
        }
    ],
    
    // Global trigger conditions
    globalConditions: [
        () => !isMobile() || getMobileEngagement() > 0.5,
        () => getConnectionSpeed() !== 'slow',
        () => !isBot()
    ]
};
```

### Custom Trigger Functions

```javascript
// Custom trigger implementations
class CustomTriggers {
    static timeBasedTrigger(seconds, conditions = []) {
        return new Promise((resolve) => {
            setTimeout(() => {
                const shouldTrigger = conditions.every(condition => condition());
                if (shouldTrigger) {
                    resolve(true);
                }
            }, seconds * 1000);
        });
    }
    
    static scrollBasedTrigger(percentage, element = document.body) {
        return new Promise((resolve) => {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.intersectionRatio >= percentage / 100) {
                        resolve(true);
                        observer.disconnect();
                    }
                });
            });
            
            observer.observe(element);
        });
    }
    
    static engagementBasedTrigger(engagementScore) {
        return new Promise((resolve) => {
            const checkEngagement = () => {
                const score = calculateEngagementScore();
                if (score >= engagementScore) {
                    resolve(true);
                } else {
                    setTimeout(checkEngagement, 5000);
                }
            };
            
            checkEngagement();
        });
    }
}

// Usage
const config = {
    // ... other config
    trigger: {
        type: 'custom',
        customTrigger: async () => {
            const timeCondition = CustomTriggers.timeBasedTrigger(30);
            const scrollCondition = CustomTriggers.scrollBasedTrigger(60);
            const engagementCondition = CustomTriggers.engagementBasedTrigger(0.7);
            
            // Trigger when any condition is met
            return Promise.race([timeCondition, scrollCondition, engagementCondition]);
        }
    }
};
```

## 📊 Analytics Configuration

### Comprehensive Analytics Setup

```javascript
const analyticsConfig = {
    analytics: {
        enabled: true,
        
        // Platform integrations
        platforms: {
            googleAnalytics: {
                enabled: true,
                trackingId: 'GA_TRACKING_ID',
                customDimensions: {
                    conversationId: 'dimension1',
                    qualificationScore: 'dimension2',
                    platform: 'dimension3'
                }
            },
            
            mixpanel: {
                enabled: true,
                token: 'MIXPANEL_TOKEN',
                superProperties: {
                    product: 'ngx-voice-agent',
                    version: '1.0.0'
                }
            },
            
            segment: {
                enabled: true,
                writeKey: 'SEGMENT_WRITE_KEY'
            }
        },
        
        // Event configuration
        events: {
            // Automatically tracked events
            autoTrack: [
                'conversation.started',
                'conversation.ended',
                'message.sent',
                'message.received',
                'qualification.completed',
                'human.transfer.requested'
            ],
            
            // Custom events
            customEvents: [
                {
                    name: 'special_offer_shown',
                    trigger: 'qualification.completed',
                    condition: (data) => data.score >= 80
                },
                {
                    name: 'high_engagement',
                    trigger: 'message.sent',
                    condition: (data, context) => context.messageCount >= 5
                }
            ]
        },
        
        // Data collection
        dataCollection: {
            collectUserAgent: true,
            collectReferrer: true,
            collectPageMetrics: true,
            collectPerformanceMetrics: true,
            collectErrorLogs: true
        },
        
        // Privacy controls
        privacy: {
            anonymizeIPs: true,
            respectDoNotTrack: true,
            enableConsentMode: true,
            dataRetentionDays: 365
        }
    }
};
```

### Custom Analytics Implementation

```javascript
// Custom analytics implementation
class NGXAnalytics {
    constructor(config) {
        this.config = config;
        this.eventQueue = [];
        this.context = {};
    }
    
    track(eventName, properties = {}) {
        const event = {
            name: eventName,
            properties: {
                ...properties,
                timestamp: new Date().toISOString(),
                sessionId: this.getSessionId(),
                ...this.context
            }
        };
        
        // Add to queue
        this.eventQueue.push(event);
        
        // Send to configured platforms
        this.sendToAllPlatforms(event);
    }
    
    setContext(contextData) {
        this.context = { ...this.context, ...contextData };
    }
    
    sendToAllPlatforms(event) {
        const { platforms } = this.config.analytics;
        
        if (platforms.googleAnalytics?.enabled) {
            this.sendToGA(event);
        }
        
        if (platforms.mixpanel?.enabled) {
            this.sendToMixpanel(event);
        }
        
        if (platforms.segment?.enabled) {
            this.sendToSegment(event);
        }
    }
    
    sendToGA(event) {
        gtag('event', event.name, {
            custom_parameter_1: event.properties.conversationId,
            custom_parameter_2: event.properties.qualificationScore,
            // ... map other properties
        });
    }
    
    sendToMixpanel(event) {
        mixpanel.track(event.name, event.properties);
    }
    
    sendToSegment(event) {
        analytics.track(event.name, event.properties);
    }
}

// Usage with NGX Agent
const analyticsInstance = new NGXAnalytics(analyticsConfig);

const agent = new NGXVoiceAgent();
await agent.init(config);

// Set up analytics tracking
agent.on('*', (eventName, eventData) => {
    analyticsInstance.track(`NGX_${eventName}`, eventData);
});

// Set conversation context
agent.on('conversation.started', ({ conversationId, customerData }) => {
    analyticsInstance.setContext({
        conversationId,
        customerSegment: determineSegment(customerData),
        platform: config.platform
    });
});
```

## 🔒 Security & Privacy Configuration

### Privacy-First Configuration

```javascript
const privacyConfig = {
    privacy: {
        // GDPR Compliance
        enableGDPRCompliance: true,
        gdprSettings: {
            requireConsent: true,
            consentBanner: {
                enabled: true,
                message: 'We use AI to improve your experience. Do you consent to data processing?',
                acceptText: 'Accept',
                declineText: 'Decline'
            },
            rightToErasure: true,
            dataPortability: true
        },
        
        // Data handling
        dataRetention: '30days', // '7days' | '30days' | '1year' | 'indefinite'
        anonymizeData: true,
        dataMinimization: true,
        
        // Cookie management
        cookieConsent: true,
        cookieSettings: {
            necessary: true,
            analytics: 'consent-required',
            marketing: 'consent-required'
        },
        
        // Regional compliance
        regionalCompliance: {
            ccpa: true, // California Consumer Privacy Act
            pipeda: true, // Personal Information Protection and Electronic Documents Act (Canada)
            lgpd: true // Lei Geral de Proteção de Dados (Brazil)
        }
    },
    
    security: {
        // API security
        apiSecurity: {
            enableCORS: true,
            allowedOrigins: ['https://yourdomain.com'],
            rateLimiting: {
                enabled: true,
                maxRequests: 100,
                windowMs: 900000 // 15 minutes
            }
        },
        
        // Content security
        contentSecurity: {
            sanitizeInput: true,
            preventXSS: true,
            validateMessages: true
        },
        
        // Transport security
        transportSecurity: {
            enforceHTTPS: true,
            enableHSTS: true,
            requireSRI: true // Subresource Integrity
        }
    }
};
```

---

**Next Steps:**
- [Events & Callbacks](./events.md)
- [Voice & Audio Configuration](./voice-audio.md)
- [Platform Types](./platform-types.md)