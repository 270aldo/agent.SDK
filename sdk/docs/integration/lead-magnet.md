# Lead Magnet Integration Guide

Lead magnets are one of the most effective platforms for NGX Voice Agent integration. This guide shows you how to create high-converting post-download experiences that nurture leads and increase qualification rates.

## 🎯 Overview

Lead magnet integration focuses on:
- **Post-download engagement** - Activate after content delivery
- **Gentle qualification** - Non-aggressive approach to maintain trust
- **Educational tone** - Position as helpful expert, not salesperson
- **High conversion rates** - Typically 15-25% conversion to qualified leads

## 🚀 Quick Setup

### 1. Basic Integration

```html
<!DOCTYPE html>
<html>
<head>
    <title>Free Fitness Guide - Download</title>
</head>
<body>
    <!-- Your lead magnet form -->
    <form id="leadForm">
        <input type="email" name="email" required>
        <input type="text" name="name" required>
        <button type="submit">Download Free Guide</button>
    </form>

    <!-- NGX Voice Agent Script -->
    <script src="https://cdn.ngx.com/voice-agent-sdk.js"></script>
    <script>
        document.getElementById('leadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Process form submission
            const formData = new FormData(e.target);
            await downloadContent(formData);
            
            // Initialize NGX Voice Agent after successful download
            const agent = new NGXVoiceAgent();
            await agent.init({
                apiUrl: 'https://your-api.ngx.com',
                platform: 'lead_magnet',
                trigger: { type: 'auto', threshold: 3 }, // 3 seconds after download
                behavior: {
                    autoStart: true,
                    greeting: 'Thanks for downloading! I\'m here to help you get the most out of your guide.',
                    enableVoice: true
                }
            });

            // Start conversation with user data
            await agent.start({
                name: formData.get('name'),
                email: formData.get('email'),
                goals: { primary: detectGoalFromForm(formData) }
            });
        });
    </script>
</body>
</html>
```

### 2. React Integration

```jsx
import React, { useState } from 'react';
import { NGXVoiceAgent } from '@ngx/voice-agent-react';

export function LeadMagnetPage() {
    const [downloadComplete, setDownloadComplete] = useState(false);
    const [userData, setUserData] = useState(null);

    const handleFormSubmit = async (formData) => {
        // Process download
        await processDownload(formData);
        
        setUserData({
            name: formData.name,
            email: formData.email,
            goals: { primary: formData.goal }
        });
        setDownloadComplete(true);
    };

    const agentConfig = {
        apiUrl: process.env.REACT_APP_NGX_API_URL,
        platform: 'lead_magnet',
        ui: {
            position: 'bottom-right',
            theme: 'light',
            showAvatar: true
        },
        voice: {
            enabled: true,
            autoPlay: true
        },
        behavior: {
            autoStart: true,
            greeting: 'Congratulations on taking the first step! I\'m here to help you succeed.'
        }
    };

    return (
        <div>
            {!downloadComplete ? (
                <LeadMagnetForm onSubmit={handleFormSubmit} />
            ) : (
                <ThankYouPage />
            )}

            {downloadComplete && (
                <NGXVoiceAgent
                    config={agentConfig}
                    customerData={userData}
                    autoStart={true}
                    onConversationStart={(id) => {
                        // Track conversion
                        analytics.track('Lead_Magnet_Conversation_Started', {
                            conversationId: id,
                            downloadType: 'fitness_guide'
                        });
                    }}
                />
            )}
        </div>
    );
}
```

## ⚙️ Configuration Options

### Platform-Specific Configuration

```javascript
const leadMagnetConfig = {
    apiUrl: 'https://your-api.ngx.com',
    platform: 'lead_magnet',
    
    // Trigger Configuration
    trigger: {
        type: 'auto',          // Automatic trigger
        threshold: 3           // 3 seconds after download
    },
    
    // UI Configuration
    ui: {
        position: 'bottom-right',
        size: 'medium',
        theme: 'light',
        showAvatar: true,
        colors: {
            primary: '#4CAF50',     // Success green for downloads
            secondary: '#2196F3',
            background: '#ffffff'
        }
    },
    
    // Behavior Configuration
    behavior: {
        autoStart: true,
        greeting: 'Thanks for downloading our {contentType}! I\'m here to help you get the most out of it.',
        showTransferOption: true,
        enableFollowUp: true
    },
    
    // Voice Configuration
    voice: {
        enabled: true,
        autoPlay: true,
        voice: 'en-US-Standard-J',  // Friendly female voice
        speed: 0.9,                 // Slightly slower for clarity
        volume: 0.8
    },
    
    // Feature Configuration
    features: {
        voiceEnabled: true,
        humanTransfer: true,
        analytics: true,
        followUp: true
    }
};
```

### Content-Aware Configuration

```javascript
// Dynamic configuration based on lead magnet type
function getLeadMagnetConfig(contentType, userGoals) {
    const baseConfig = {
        apiUrl: 'https://your-api.ngx.com',
        platform: 'lead_magnet'
    };
    
    switch (contentType) {
        case 'fitness_guide':
            return {
                ...baseConfig,
                behavior: {
                    greeting: 'Congratulations on downloading your fitness guide! Ready to transform your health?',
                    contextualQuestions: [
                        'What\'s your biggest fitness challenge right now?',
                        'Have you tried any fitness programs before?',
                        'What would success look like for you?'
                    ]
                }
            };
            
        case 'nutrition_plan':
            return {
                ...baseConfig,
                behavior: {
                    greeting: 'Your nutrition plan is ready! I\'m here to help you implement it successfully.',
                    contextualQuestions: [
                        'Do you have any dietary restrictions I should know about?',
                        'What\'s your biggest nutrition challenge?',
                        'Are you cooking for just yourself or a family?'
                    ]
                }
            };
            
        case 'workout_routine':
            return {
                ...baseConfig,
                behavior: {
                    greeting: 'Great choice on the workout routine! Let\'s make sure it fits your lifestyle perfectly.',
                    contextualQuestions: [
                        'How many days per week can you realistically work out?',
                        'Do you prefer home workouts or gym sessions?',
                        'What equipment do you have access to?'
                    ]
                }
            };
    }
    
    return baseConfig;
}
```

## 📊 Conversion Optimization

### A/B Testing Setup

```javascript
// A/B Testing Configuration
const experiments = {
    greeting_tone: {
        variants: [
            'Thanks for downloading! I\'m excited to help you succeed.',
            'Congratulations on taking action! Let\'s maximize your results.',
            'Your guide is ready! I\'m here to ensure you get amazing results.'
        ]
    },
    
    trigger_timing: {
        variants: [
            { type: 'auto', threshold: 2 },   // 2 seconds
            { type: 'auto', threshold: 5 },   // 5 seconds  
            { type: 'auto', threshold: 10 }   // 10 seconds
        ]
    },
    
    ui_position: {
        variants: ['bottom-right', 'center', 'bottom-left']
    }
};

// Select variant based on user ID
function getExperimentVariant(experimentName, userId) {
    const variants = experiments[experimentName].variants;
    const hash = simpleHash(userId + experimentName);
    return variants[hash % variants.length];
}

// Initialize with A/B test configuration
const userExperiment = {
    greeting: getExperimentVariant('greeting_tone', userId),
    trigger: getExperimentVariant('trigger_timing', userId),
    position: getExperimentVariant('ui_position', userId)
};

const agent = new NGXVoiceAgent();
await agent.init({
    apiUrl: 'https://your-api.ngx.com',
    platform: 'lead_magnet',
    trigger: userExperiment.trigger,
    ui: { position: userExperiment.position },
    behavior: { greeting: userExperiment.greeting }
});
```

### Conversion Tracking

```javascript
agent.on('conversation.started', ({ conversationId }) => {
    analytics.track('Lead_Magnet_Conversation_Started', {
        conversationId,
        source: 'lead_magnet',
        contentType: getContentType(),
        userSegment: getUserSegment()
    });
});

agent.on('qualification.completed', ({ score, recommendation }) => {
    analytics.track('Lead_Qualification_Completed', {
        qualificationScore: score,
        recommendation,
        source: 'lead_magnet',
        qualified: score >= 70
    });
    
    // Update lead score in CRM
    updateCRMLeadScore(getUserId(), score);
});

agent.on('human.transfer.requested', ({ conversationId }) => {
    analytics.track('Human_Transfer_Requested', {
        conversationId,
        source: 'lead_magnet',
        transferReason: 'user_requested'
    });
});
```

## 🎨 UI Customization

### Custom Styling

```css
/* Lead Magnet Specific Styles */
.ngx-voice-widget.lead-magnet {
    border: 2px solid #4CAF50;
    box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3);
}

.ngx-voice-widget.lead-magnet .ngx-widget-header {
    background: linear-gradient(135deg, #4CAF50, #45a049);
}

.ngx-voice-widget.lead-magnet .ngx-message.assistant .ngx-message-content {
    background: #f1f8e9;
    border-left: 4px solid #4CAF50;
}

/* Success celebration animation */
.ngx-download-success {
    animation: celebrate 0.6s ease-out;
}

@keyframes celebrate {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}
```

### Custom Components

```javascript
// Custom thank you message component
function createCustomThankYou(downloadType) {
    return `
        <div class="ngx-custom-thank-you">
            <div class="success-icon">🎉</div>
            <h3>Download Complete!</h3>
            <p>Your ${downloadType} has been sent to your email.</p>
            <div class="next-steps">
                <h4>What's Next?</h4>
                <ul>
                    <li>Check your email for the download link</li>
                    <li>Review the material at your own pace</li>
                    <li>Chat with me about any questions</li>
                </ul>
            </div>
        </div>
    `;
}

// Show custom thank you before agent activation
function showThankYouMessage(downloadType) {
    const thankYouHTML = createCustomThankYou(downloadType);
    
    // Display thank you message
    document.getElementById('thank-you-container').innerHTML = thankYouHTML;
    
    // Initialize agent after short delay
    setTimeout(() => {
        initializeNGXAgent();
    }, 2000);
}
```

## 📈 Best Practices

### 1. Timing Optimization

```javascript
// Optimal timing based on content type
const timingStrategy = {
    ebook: { delay: 3, reason: 'Time to realize download completed' },
    video: { delay: 10, reason: 'Time to start watching' },
    checklist: { delay: 5, reason: 'Time to review first items' },
    template: { delay: 7, reason: 'Time to examine template' }
};

function getOptimalTiming(contentType) {
    return timingStrategy[contentType] || { delay: 5, reason: 'Default timing' };
}
```

### 2. Context-Aware Messaging

```javascript
// Message personalization based on user data
function personalizeGreeting(userData, contentType) {
    const { name, goals, industry } = userData;
    
    let greeting = `Hi ${name}! `;
    
    // Add content-specific context
    switch (contentType) {
        case 'fitness_guide':
            greeting += `I see you're interested in ${goals.primary}. That's fantastic! `;
            break;
        case 'business_template':
            greeting += `As someone in ${industry}, this template should be perfect for you. `;
            break;
    }
    
    greeting += `I'm here to help you get the most out of what you just downloaded. What questions do you have?`;
    
    return greeting;
}
```

### 3. Qualification Strategy

```javascript
// Progressive qualification approach
const qualificationFlow = {
    stage1: {
        questions: [
            'What attracted you to this guide?',
            'What\'s your biggest challenge in this area?'
        ],
        goal: 'Understand motivation'
    },
    
    stage2: {
        questions: [
            'Have you tried solving this before?',
            'What didn\'t work in the past?'
        ],
        goal: 'Identify pain points'
    },
    
    stage3: {
        questions: [
            'What would success look like for you?',
            'When do you want to achieve this goal?'
        ],
        goal: 'Establish urgency and outcome'
    },
    
    stage4: {
        questions: [
            'Would you like a personalized plan?',
            'Are you interested in 1-on-1 coaching?'
        ],
        goal: 'Introduce solution'
    }
};
```

## 🔧 Troubleshooting

### Common Issues

1. **Agent not appearing after download**
   ```javascript
   // Debug download detection
   console.log('Download completed:', downloadComplete);
   console.log('Agent initialized:', agentInitialized);
   
   // Ensure proper event sequencing
   ```

2. **Multiple agent instances**
   ```javascript
   // Prevent multiple initializations
   if (window.ngxAgentInitialized) {
       return;
   }
   window.ngxAgentInitialized = true;
   ```

3. **Form submission conflicts**
   ```javascript
   // Prevent form default behavior properly
   form.addEventListener('submit', function(e) {
       e.preventDefault();
       e.stopPropagation();
       handleFormSubmission();
   });
   ```

### Debug Mode

```javascript
const agent = new NGXVoiceAgent();
await agent.init({
    apiUrl: 'https://your-api.ngx.com',
    platform: 'lead_magnet',
    debug: true,
    onDebug: (event, data) => {
        console.log('NGX Debug:', event, data);
    }
});
```

## 📊 Analytics & Reporting

### Key Metrics to Track

```javascript
// Essential lead magnet metrics
const metrics = {
    downloadRate: 'Downloads / Page Views',
    engagementRate: 'Conversations Started / Downloads',
    qualificationRate: 'Qualified Leads / Conversations',
    conversionRate: 'Sales / Qualified Leads',
    
    // Timing metrics
    timeToEngage: 'Download to Conversation Start',
    conversationDuration: 'Average Conversation Length',
    
    // Quality metrics
    leadScore: 'Average Qualification Score',
    followUpAcceptance: 'Follow-up Acceptance Rate'
};

// Implement tracking
agent.on('*', (eventName, eventData) => {
    sendToAnalytics('NGX_LeadMagnet_' + eventName, {
        ...eventData,
        downloadType: getContentType(),
        userSegment: getUserSegment(),
        timestamp: new Date().toISOString()
    });
});
```

---

**Next Steps:**
- [Blog Widget Integration](./blog-widget.md)
- [Landing Page Integration](./landing-page.md)
- [Analytics Setup](../analytics.md)