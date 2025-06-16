# Landing Page Integration Guide

Landing page integration is designed for high-intent visitors ready to convert. This guide shows you how to create compelling conversion experiences that turn visitors into qualified leads and customers.

## 🎯 Overview

Landing page integration focuses on:
- **High-conversion triggers** - Activate at optimal moments (scroll, time, exit intent)
- **Sales-focused messaging** - Direct approach for ready-to-buy visitors
- **Immersive experience** - Full-screen or modal overlay for maximum attention
- **A/B testing ready** - Easy experimentation with different approaches

## 🚀 Quick Setup

### 1. Basic Integration

```html
<!DOCTYPE html>
<html>
<head>
    <title>NGX PRIME - Transform Your Body</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <!-- Your landing page content -->
    <section class="hero">
        <h1>Transform Your Body in 90 Days</h1>
        <p>Join thousands who've achieved their dream physique</p>
        <button id="cta-button">Start Your Transformation</button>
    </section>

    <!-- More landing page sections -->
    <section class="features">...</section>
    <section class="testimonials">...</section>
    <section class="pricing">...</section>

    <!-- NGX Voice Agent Script -->
    <script src="https://cdn.ngx.com/voice-agent-sdk.js"></script>
    <script>
        // Initialize NGX Voice Agent
        const agent = new NGXVoiceAgent();
        
        // Configuration for landing page
        const config = {
            apiUrl: 'https://your-api.ngx.com',
            platform: 'landing_page',
            
            // Scroll-triggered activation
            trigger: {
                type: 'scroll',
                threshold: 70  // 70% scroll depth
            },
            
            // Full-screen modal experience
            ui: {
                position: 'center',
                size: 'large',
                theme: 'auto'
            },
            
            // Sales-focused behavior
            behavior: {
                autoStart: true,
                greeting: 'I can see you\'re interested in transforming your body. Let me help you choose the perfect program!',
                enableVoice: true,
                transferToHuman: true
            }
        };

        // Initialize agent
        agent.init(config).then(() => {
            console.log('NGX Agent ready for landing page');
        });

        // Manual trigger for CTA buttons
        document.getElementById('cta-button').addEventListener('click', () => {
            agent.start({
                goals: { primary: 'body_transformation' },
                source: 'hero_cta'
            });
        });

        // Track conversions
        agent.on('qualification.completed', ({ score, recommendation }) => {
            if (score >= 80) {
                // High-quality lead - show special offer
                showSpecialOffer();
            }
        });
    </script>
</body>
</html>
```

### 2. React Integration

```jsx
import React, { useState, useEffect } from 'react';
import { NGXVoiceAgent, useNGXVoice } from '@ngx/voice-agent-react';

export function LandingPage() {
    const [showAgent, setShowAgent] = useState(false);
    const [userIntent, setUserIntent] = useState(null);

    // NGX Voice Agent configuration
    const agentConfig = {
        apiUrl: process.env.REACT_APP_NGX_API_URL,
        platform: 'landing_page',
        
        trigger: {
            type: 'scroll',
            threshold: 70
        },
        
        ui: {
            position: 'center',
            size: 'large',
            theme: 'light',
            colors: {
                primary: '#ff6b6b',
                secondary: '#4ecdc4',
                background: '#ffffff'
            }
        },
        
        behavior: {
            autoStart: true,
            greeting: 'Ready to transform your life? Let\'s find the perfect program for you!',
            enableVoice: true
        }
    };

    // Use NGX Voice Hook
    const {
        start,
        sendMessage,
        conversationState,
        isActive,
        onQualificationComplete
    } = useNGXVoice({ config: agentConfig });

    // Handle qualification results
    useEffect(() => {
        onQualificationComplete((score, recommendation) => {
            setUserIntent({ score, recommendation });
            
            if (score >= 80) {
                // High-intent user - show premium offer
                trackConversion('high_intent_qualified', { score });
            } else if (score >= 60) {
                // Medium-intent - show standard offer
                trackConversion('medium_intent_qualified', { score });
            }
        });
    }, [onQualificationComplete]);

    // CTA handlers
    const handleHeroCTA = () => {
        start({
            goals: { primary: 'weight_loss' },
            source: 'hero_cta',
            intent: 'high'
        });
    };

    const handlePricingCTA = (planType) => {
        start({
            goals: { primary: 'body_transformation' },
            source: 'pricing_cta',
            selectedPlan: planType,
            intent: 'very_high'
        });
    };

    return (
        <div className="landing-page">
            <HeroSection onCTAClick={handleHeroCTA} />
            <FeaturesSection />
            <TestimonialsSection />
            <PricingSection onPlanSelect={handlePricingCTA} />
            
            {/* NGX Voice Agent Component */}
            <NGXVoiceAgent
                config={agentConfig}
                onConversationStart={(id) => {
                    trackEvent('conversation_started', { 
                        source: 'landing_page',
                        conversationId: id 
                    });
                }}
                onConversationEnd={(id, reason) => {
                    trackEvent('conversation_ended', { 
                        conversationId: id, 
                        reason 
                    });
                }}
            />
        </div>
    );
}
```

### 3. Advanced Multi-Trigger Setup

```javascript
// Advanced landing page configuration with multiple triggers
const landingPageAgent = new NGXVoiceAgent();

const advancedConfig = {
    apiUrl: 'https://your-api.ngx.com',
    platform: 'landing_page',
    
    // Multiple trigger strategies
    triggers: [
        {
            name: 'scroll_trigger',
            type: 'scroll',
            threshold: 70,
            priority: 1,
            condition: () => !sessionStorage.getItem('ngx_engaged')
        },
        {
            name: 'time_trigger',
            type: 'time',
            threshold: 45, // 45 seconds
            priority: 2,
            condition: () => !sessionStorage.getItem('ngx_engaged')
        },
        {
            name: 'exit_intent',
            type: 'exit_intent',
            priority: 3,
            condition: () => !sessionStorage.getItem('ngx_engaged')
        }
    ],
    
    // Dynamic UI based on trigger
    ui: {
        position: 'center',
        size: 'large',
        theme: 'auto',
        customization: {
            scroll_trigger: {
                title: 'I can help you choose the right program!',
                subtitle: 'Based on what you\'ve been reading...'
            },
            time_trigger: {
                title: 'Still have questions?',
                subtitle: 'Let me help you decide...'
            },
            exit_intent: {
                title: 'Wait! Don\'t leave empty-handed',
                subtitle: 'Let me help you get started today'
            }
        }
    }
};

// Initialize with advanced configuration
await landingPageAgent.init(advancedConfig);

// Handle different trigger types
landingPageAgent.on('trigger.activated', ({ triggerName, context }) => {
    const customization = advancedConfig.ui.customization[triggerName];
    
    // Customize greeting based on trigger
    let greeting;
    switch (triggerName) {
        case 'scroll_trigger':
            greeting = 'I see you\'re exploring our programs. Let me help you find the perfect fit!';
            break;
        case 'time_trigger':
            greeting = 'Taking your time to research? Smart! Let me answer any questions you have.';
            break;
        case 'exit_intent':
            greeting = 'Before you go, let me show you how we can help you succeed!';
            break;
    }
    
    // Start conversation with contextual data
    landingPageAgent.start({
        triggerType: triggerName,
        customGreeting: greeting,
        urgency: triggerName === 'exit_intent' ? 'high' : 'medium'
    });
    
    // Mark as engaged
    sessionStorage.setItem('ngx_engaged', 'true');
});
```

## ⚙️ Conversion Optimization

### A/B Testing Framework

```javascript
// A/B Testing for Landing Pages
class LandingPageABTest {
    constructor() {
        this.experiments = {
            trigger_timing: {
                variants: [
                    { name: 'early', scroll: 50, time: 30 },
                    { name: 'medium', scroll: 70, time: 45 },
                    { name: 'late', scroll: 90, time: 60 }
                ]
            },
            
            message_tone: {
                variants: [
                    { 
                        name: 'consultative',
                        greeting: 'Let me help you find the perfect program for your goals.'
                    },
                    { 
                        name: 'urgent',
                        greeting: 'Ready to transform your body? Let\'s get you started today!'
                    },
                    { 
                        name: 'social_proof',
                        greeting: 'Join 50,000+ people who\'ve transformed their lives. Which program interests you?'
                    }
                ]
            },
            
            ui_style: {
                variants: [
                    { name: 'modal', position: 'center', size: 'large' },
                    { name: 'sidebar', position: 'bottom-right', size: 'medium' },
                    { name: 'fullscreen', position: 'fullscreen', size: 'large' }
                ]
            }
        };
    }
    
    getVariant(experimentName, userId) {
        const variants = this.experiments[experimentName].variants;
        const hash = this.simpleHash(userId + experimentName);
        return variants[hash % variants.length];
    }
    
    getConfiguration(userId) {
        const triggerVariant = this.getVariant('trigger_timing', userId);
        const messageVariant = this.getVariant('message_tone', userId);
        const uiVariant = this.getVariant('ui_style', userId);
        
        return {
            apiUrl: 'https://your-api.ngx.com',
            platform: 'landing_page',
            
            trigger: {
                type: 'scroll',
                threshold: triggerVariant.scroll
            },
            
            ui: {
                position: uiVariant.position,
                size: uiVariant.size
            },
            
            behavior: {
                greeting: messageVariant.greeting
            },
            
            // Track experiment data
            experiments: {
                trigger_timing: triggerVariant.name,
                message_tone: messageVariant.name,
                ui_style: uiVariant.name
            }
        };
    }
    
    simpleHash(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return Math.abs(hash);
    }
}

// Usage
const abTest = new LandingPageABTest();
const userId = getUserId(); // Your user identification method
const config = abTest.getConfiguration(userId);

const agent = new NGXVoiceAgent();
await agent.init(config);

// Track experiment results
agent.on('qualification.completed', ({ score }) => {
    analytics.track('AB_Test_Conversion', {
        userId,
        experiments: config.experiments,
        qualificationScore: score,
        converted: score >= 70
    });
});
```

### Dynamic Pricing Integration

```javascript
// Dynamic pricing based on qualification
agent.on('qualification.completed', ({ score, recommendation }) => {
    const pricingStrategy = determinePricingStrategy(score, recommendation);
    
    // Show appropriate offer based on qualification
    switch (pricingStrategy.tier) {
        case 'premium':
            showPremiumOffer({
                discount: 20,
                urgency: 'high',
                bonuses: ['1-on-1 coaching', 'Custom meal plan']
            });
            break;
            
        case 'standard':
            showStandardOffer({
                discount: 10,
                urgency: 'medium',
                bonuses: ['Group coaching', 'Recipe book']
            });
            break;
            
        case 'basic':
            showBasicOffer({
                discount: 5,
                urgency: 'low',
                bonuses: ['Email support']
            });
            break;
    }
});

function determinePricingStrategy(score, recommendation) {
    if (score >= 85) {
        return { tier: 'premium', confidence: 'high' };
    } else if (score >= 65) {
        return { tier: 'standard', confidence: 'medium' };
    } else {
        return { tier: 'basic', confidence: 'low' };
    }
}
```

## 🎨 UI Customization

### Brand-Aligned Styling

```css
/* Landing Page Specific Styles */
.ngx-voice-widget.landing-page {
    font-family: 'Montserrat', sans-serif;
    border-radius: 15px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.ngx-voice-widget.landing-page .ngx-widget-header {
    background: linear-gradient(135deg, #ff6b6b, #ff8e53);
    padding: 1.5rem;
}

.ngx-voice-widget.landing-page .ngx-widget-title {
    font-size: 1.2rem;
    font-weight: 600;
}

/* Conversion-focused button styling */
.ngx-voice-widget.landing-page .ngx-cta-button {
    background: linear-gradient(45deg, #ff6b6b, #ff8e53);
    border: none;
    border-radius: 25px;
    padding: 12px 24px;
    color: white;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
}

.ngx-voice-widget.landing-page .ngx-cta-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(255, 107, 107, 0.6);
}

/* Message styling for sales focus */
.ngx-voice-widget.landing-page .ngx-message.assistant .ngx-message-content {
    background: linear-gradient(135deg, #f8f9fa, #e9ecef);
    border-left: 4px solid #ff6b6b;
    font-weight: 500;
}

/* Special offer highlight */
.ngx-special-offer {
    background: linear-gradient(135deg, #28a745, #20c997);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    animation: pulse-glow 2s infinite;
}

@keyframes pulse-glow {
    0% { box-shadow: 0 0 5px rgba(40, 167, 69, 0.5); }
    50% { box-shadow: 0 0 20px rgba(40, 167, 69, 0.8); }
    100% { box-shadow: 0 0 5px rgba(40, 167, 69, 0.5); }
}
```

### Mobile-Responsive Design

```css
/* Mobile optimization for landing pages */
@media (max-width: 768px) {
    .ngx-voice-widget.landing-page {
        width: 95%;
        height: 90%;
        bottom: 2.5%;
        right: 2.5%;
        border-radius: 20px;
    }
    
    .ngx-voice-widget.landing-page .ngx-widget-header {
        padding: 1rem;
    }
    
    .ngx-voice-widget.landing-page .ngx-widget-title {
        font-size: 1rem;
    }
    
    .ngx-voice-widget.landing-page .ngx-message-content {
        font-size: 0.9rem;
        line-height: 1.4;
    }
}

/* Tablet optimization */
@media (min-width: 769px) and (max-width: 1024px) {
    .ngx-voice-widget.landing-page {
        width: 80%;
        max-width: 500px;
    }
}
```

## 📊 Analytics & Tracking

### Conversion Funnel Tracking

```javascript
// Comprehensive landing page analytics
class LandingPageAnalytics {
    constructor(agent) {
        this.agent = agent;
        this.funnelSteps = [
            'page_view',
            'scroll_50',
            'scroll_70',
            'agent_triggered',
            'conversation_started',
            'qualification_completed',
            'offer_presented',
            'conversion'
        ];
        
        this.setupTracking();
    }
    
    setupTracking() {
        // Page view tracking
        this.trackFunnelStep('page_view', {
            url: window.location.href,
            referrer: document.referrer,
            timestamp: new Date()
        });
        
        // Scroll tracking
        this.setupScrollTracking();
        
        // Agent event tracking
        this.setupAgentTracking();
    }
    
    setupScrollTracking() {
        let trackedSteps = new Set();
        
        window.addEventListener('scroll', () => {
            const scrollPercent = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
            
            if (scrollPercent >= 50 && !trackedSteps.has('scroll_50')) {
                this.trackFunnelStep('scroll_50', { scrollPercent });
                trackedSteps.add('scroll_50');
            }
            
            if (scrollPercent >= 70 && !trackedSteps.has('scroll_70')) {
                this.trackFunnelStep('scroll_70', { scrollPercent });
                trackedSteps.add('scroll_70');
            }
        });
    }
    
    setupAgentTracking() {
        this.agent.on('trigger.activated', (data) => {
            this.trackFunnelStep('agent_triggered', data);
        });
        
        this.agent.on('conversation.started', (data) => {
            this.trackFunnelStep('conversation_started', data);
        });
        
        this.agent.on('qualification.completed', (data) => {
            this.trackFunnelStep('qualification_completed', data);
            
            if (data.score >= 70) {
                this.trackFunnelStep('offer_presented', {
                    qualificationScore: data.score,
                    recommendation: data.recommendation
                });
            }
        });
        
        this.agent.on('conversion.completed', (data) => {
            this.trackFunnelStep('conversion', data);
        });
    }
    
    trackFunnelStep(step, data = {}) {
        const eventData = {
            funnelStep: step,
            sessionId: this.getSessionId(),
            userId: this.getUserId(),
            timestamp: new Date().toISOString(),
            page: 'landing_page',
            ...data
        };
        
        // Send to your analytics platform
        analytics.track(`Landing_Page_${step}`, eventData);
        
        // Store for funnel analysis
        this.storeFunnelStep(step, eventData);
    }
    
    getFunnelConversionRate() {
        const steps = this.getStoredFunnelSteps();
        const conversions = {};
        
        this.funnelSteps.forEach(step => {
            conversions[step] = steps.filter(s => s.step === step).length;
        });
        
        return conversions;
    }
}

// Initialize analytics
const agent = new NGXVoiceAgent();
const analytics = new LandingPageAnalytics(agent);

await agent.init(landingPageConfig);
```

### Heat Map Integration

```javascript
// Heat map tracking for agent interactions
function setupHeatMapTracking(agent) {
    agent.on('ui.element.clicked', ({ element, position, timestamp }) => {
        // Track clicks within the agent interface
        heatMap.track('click', {
            x: position.x,
            y: position.y,
            element: element,
            component: 'ngx_voice_agent',
            timestamp: timestamp
        });
    });
    
    agent.on('ui.element.hovered', ({ element, duration }) => {
        // Track hover patterns
        heatMap.track('hover', {
            element: element,
            duration: duration,
            component: 'ngx_voice_agent'
        });
    });
    
    // Track scroll within agent interface
    document.querySelector('.ngx-chat-messages').addEventListener('scroll', (e) => {
        heatMap.track('scroll', {
            scrollTop: e.target.scrollTop,
            component: 'ngx_chat_messages'
        });
    });
}
```

## 🔧 Performance Optimization

### Lazy Loading

```javascript
// Lazy load agent for better page performance
function lazyLoadNGXAgent() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                loadNGXAgent();
                observer.unobserve(entry.target);
            }
        });
    });
    
    // Observe trigger element (could be pricing section, etc.)
    const triggerElement = document.getElementById('pricing-section');
    observer.observe(triggerElement);
}

async function loadNGXAgent() {
    // Dynamically import SDK
    const { NGXVoiceAgent } = await import('https://cdn.ngx.com/voice-agent-sdk.js');
    
    // Initialize agent
    const agent = new NGXVoiceAgent();
    await agent.init(landingPageConfig);
    
    console.log('NGX Agent loaded and ready');
}

// Start lazy loading
lazyLoadNGXAgent();
```

### Preloading Strategy

```javascript
// Preload agent resources on user intent
function preloadOnIntent() {
    let preloadTriggered = false;
    
    // Preload on first meaningful interaction
    ['mouseenter', 'touchstart', 'scroll'].forEach(eventType => {
        document.addEventListener(eventType, () => {
            if (!preloadTriggered) {
                preloadTriggered = true;
                preloadNGXResources();
            }
        }, { once: true, passive: true });
    });
}

function preloadNGXResources() {
    // Preload SDK
    const script = document.createElement('link');
    script.rel = 'preload';
    script.href = 'https://cdn.ngx.com/voice-agent-sdk.js';
    script.as = 'script';
    document.head.appendChild(script);
    
    // Preload audio resources
    const audio = document.createElement('link');
    audio.rel = 'preload';
    audio.href = 'https://cdn.ngx.com/voice/greeting.mp3';
    audio.as = 'audio';
    document.head.appendChild(audio);
}

preloadOnIntent();
```

---

**Next Steps:**
- [Blog Widget Integration](./blog-widget.md)
- [Mobile App Integration](./mobile.md)
- [Analytics Setup](../analytics.md)