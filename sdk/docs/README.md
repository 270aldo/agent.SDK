# NGX Voice Agent SDK Documentation

Welcome to the NGX Voice Agent SDK - a comprehensive solution for integrating AI-powered voice agents across web, mobile, and desktop platforms.

## 🚀 Quick Start

### Web Integration (JavaScript/TypeScript)

```bash
npm install @ngx/voice-agent-sdk
```

```javascript
import { NGXVoiceAgent } from '@ngx/voice-agent-sdk';

const agent = new NGXVoiceAgent();

await agent.init({
  apiUrl: 'https://your-ngx-api.com',
  platform: 'lead_magnet',
  features: {
    voiceEnabled: true,
    humanTransfer: true
  }
});

const conversationId = await agent.start({
  name: 'John Doe',
  email: 'john@example.com',
  goals: { primary: 'weight_loss' }
});
```

### React Integration

```bash
npm install @ngx/voice-agent-react
```

```jsx
import { NGXVoiceAgent } from '@ngx/voice-agent-react';

function App() {
  const config = {
    apiUrl: 'https://your-ngx-api.com',
    platform: 'landing_page',
    ui: { position: 'bottom-right', theme: 'light' }
  };

  return (
    <NGXVoiceAgent
      config={config}
      autoStart={true}
      onConversationStart={(id) => console.log('Started:', id)}
    />
  );
}
```

### React Native Integration

```bash
npm install @ngx/voice-agent-react-native
```

```jsx
import { NGXVoiceAgentNative } from '@ngx/voice-agent-react-native';

function MobileApp() {
  return (
    <NGXVoiceAgentNative
      config={{
        apiUrl: 'https://your-ngx-api.com',
        platform: 'mobile_app'
      }}
      visible={true}
      theme="dark"
    />
  );
}
```

## 📚 Documentation

### Core Concepts
- [Platform Types](./platform-types.md) - Understanding different integration scenarios
- [Configuration](./configuration.md) - Complete configuration reference
- [Events & Callbacks](./events.md) - Handling agent events
- [Voice & Audio](./voice-audio.md) - Audio features and customization

### Integration Guides
- [Lead Magnet Integration](./integration/lead-magnet.md)
- [Landing Page Integration](./integration/landing-page.md)
- [Blog Widget Integration](./integration/blog-widget.md)
- [Mobile App Integration](./integration/mobile.md)
- [Custom Platform Integration](./integration/custom.md)

### API Reference
- [Web SDK API](./api/web-sdk.md)
- [React Components API](./api/react.md)
- [React Native API](./api/react-native.md)
- [Backend API](./api/backend.md)

### Examples
- [Complete Examples Repository](../examples/)
- [CodePen Demos](https://codepen.io/collection/ngx-voice-agent)
- [Live Demo](https://demo.ngx-voice-agent.com)

## 🎯 Platform-Specific Features

### Lead Magnet Integration
Perfect for post-download engagement with automatic trigger after content consumption.

**Key Features:**
- Auto-trigger after 3 seconds
- Context-aware messaging
- Gentle qualification approach
- High conversion rates

### Landing Page Integration
Optimized for high-intent visitors with conversion-focused interactions.

**Key Features:**
- Scroll-triggered activation (70% scroll)
- Full-screen modal experience
- A/B testing ready
- Conversion optimization

### Blog Widget Integration
Contextual assistance based on article content with educational approach.

**Key Features:**
- Content-aware responses
- Time-based triggers
- Exit-intent detection
- Educational tone

### Mobile App Integration
Native mobile experience with offline capabilities and push notifications.

**Key Features:**
- Offline conversation caching
- Push notification integration
- Native UI components
- Touch-optimized interface

## 🛠️ Advanced Configuration

### Multi-Platform Setup

```javascript
// Platform-specific configurations
const configs = {
  lead_magnet: {
    apiUrl: 'https://api.ngx.com',
    platform: 'lead_magnet',
    trigger: { type: 'auto', threshold: 3 },
    behavior: { autoStart: true, greeting: 'Thanks for downloading!' }
  },
  
  landing_page: {
    apiUrl: 'https://api.ngx.com',
    platform: 'landing_page',
    trigger: { type: 'scroll', threshold: 70 },
    ui: { position: 'center', size: 'large' }
  },
  
  blog: {
    apiUrl: 'https://api.ngx.com',
    platform: 'blog',
    trigger: { type: 'time', threshold: 30 },
    ui: { position: 'bottom-right', size: 'small' }
  }
};

// Initialize based on current page context
const currentPlatform = detectPlatform(); // Your platform detection logic
const agent = new NGXVoiceAgent();
await agent.init(configs[currentPlatform]);
```

### Custom Styling

```javascript
const agent = new NGXVoiceAgent();
await agent.init({
  apiUrl: 'https://api.ngx.com',
  platform: 'landing_page',
  ui: {
    position: 'center',
    theme: 'dark',
    colors: {
      primary: '#667eea',
      secondary: '#764ba2',
      background: '#1a202c',
      text: '#ffffff'
    },
    customCSS: `
      .ngx-voice-widget {
        font-family: 'Custom Font', sans-serif;
        border-radius: 20px;
      }
      .ngx-message.assistant .ngx-message-content {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
      }
    `
  }
});
```

### Event Handling

```javascript
agent.on('conversation.started', ({ conversationId, customerData }) => {
  // Track conversation start
  analytics.track('NGX_Conversation_Started', {
    conversationId,
    platform: 'lead_magnet',
    userType: customerData?.industry || 'unknown'
  });
});

agent.on('qualification.completed', ({ score, recommendation }) => {
  // Handle qualification results
  if (score >= 80) {
    // High-quality lead
    triggerHighPriorityNotification();
  }
  
  // Update CRM
  updateCRM({
    qualificationScore: score,
    recommendation,
    status: 'qualified'
  });
});

agent.on('human.transfer.requested', ({ conversationId }) => {
  // Handle transfer to human agent
  notifyHumanAgents(conversationId);
  showTransferMessage();
});
```

## 🔧 Development & Testing

### Local Development

```bash
# Clone the repository
git clone https://github.com/ngx/voice-agent-sdk.git
cd voice-agent-sdk

# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

### Testing Integration

```javascript
// Test configuration
const testConfig = {
  apiUrl: process.env.NODE_ENV === 'development' 
    ? 'http://localhost:8000' 
    : 'https://api.ngx.com',
  platform: 'lead_magnet',
  features: {
    voiceEnabled: false, // Disable voice in tests
    analytics: false     // Disable analytics in tests
  }
};

// Mock responses for testing
if (process.env.NODE_ENV === 'test') {
  agent.on('message.received', ({ message }) => {
    // Assert expected responses
    expect(message.content).toContain('weight loss');
  });
}
```

## 📊 Analytics & Monitoring

### Built-in Analytics

The SDK automatically tracks key metrics:

- **Conversation Metrics:**
  - Start rate by platform
  - Message volume and engagement
  - Conversation duration
  - Completion rates

- **Qualification Metrics:**
  - Lead quality scores
  - Conversion funnel performance
  - A/B testing results

- **Platform Performance:**
  - Trigger effectiveness
  - Platform-specific conversion rates
  - User experience metrics

### Custom Analytics Integration

```javascript
agent.on('*', (eventName, eventData) => {
  // Send all events to your analytics platform
  yourAnalytics.track(`NGX_${eventName}`, {
    ...eventData,
    timestamp: new Date(),
    platform: agent.config.platform,
    sessionId: generateSessionId()
  });
});
```

## 🚨 Error Handling & Debugging

### Error Handling Best Practices

```javascript
agent.on('error', ({ error, context }) => {
  console.error(`NGX Error in ${context}:`, error);
  
  // Handle specific error types
  switch (error.name) {
    case 'NetworkError':
      showOfflineMessage();
      enableOfflineMode();
      break;
      
    case 'ConfigurationError':
      showConfigurationHelp();
      break;
      
    case 'AuthenticationError':
      refreshApiKey();
      break;
      
    default:
      showGenericErrorMessage();
  }
  
  // Report to error tracking service
  errorTracker.captureException(error, {
    context,
    platform: agent.config.platform,
    userId: getCurrentUserId()
  });
});
```

### Debug Mode

```javascript
const agent = new NGXVoiceAgent();
await agent.init({
  apiUrl: 'https://api.ngx.com',
  platform: 'lead_magnet',
  debug: true, // Enable debug logging
  logLevel: 'verbose' // Detailed logging
});

// Debug events
agent.on('debug', ({ level, message, data }) => {
  if (level === 'error') {
    console.error('NGX Debug:', message, data);
  } else {
    console.log('NGX Debug:', message, data);
  }
});
```

## 🔒 Security & Privacy

### API Key Management

```javascript
// Never expose API keys in client-side code
// Use environment variables or secure key management

const config = {
  apiUrl: 'https://api.ngx.com',
  // Don't include apiKey in public-facing configurations
  // Authentication should be handled server-side
  platform: 'lead_magnet'
};

// For server-side applications only:
if (typeof window === 'undefined') {
  config.apiKey = process.env.NGX_API_KEY;
}
```

### Data Privacy

```javascript
agent.init({
  apiUrl: 'https://api.ngx.com',
  platform: 'lead_magnet',
  privacy: {
    dataRetention: '30days',
    anonymizeData: true,
    enableGDPRCompliance: true,
    cookieConsent: true
  }
});
```

## 📞 Support & Community

- **Documentation:** [docs.ngx-voice-agent.com](https://docs.ngx-voice-agent.com)
- **API Reference:** [api.ngx-voice-agent.com](https://api.ngx-voice-agent.com)
- **GitHub Issues:** [github.com/ngx/voice-agent-sdk/issues](https://github.com/ngx/voice-agent-sdk/issues)
- **Discord Community:** [discord.gg/ngx-voice-agent](https://discord.gg/ngx-voice-agent)
- **Email Support:** [support@ngx.com](mailto:support@ngx.com)

## 📄 License

MIT License - see [LICENSE](../LICENSE) for details.

---

**Ready to get started?** Choose your platform and follow the integration guide for your specific use case. Our SDK is designed to get you up and running in minutes while providing the flexibility to customize every aspect of the user experience.