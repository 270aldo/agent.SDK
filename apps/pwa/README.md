# NGX Voice Agent PWA Dashboard

A Progressive Web App (PWA) for managing and monitoring NGX Voice Agents.

## Features

- 📊 **Real-time Analytics** - Monitor conversation metrics and performance
- 💬 **Conversation Management** - View and analyze all voice agent interactions
- 🤖 **Agent Configuration** - Create and configure voice agents for different platforms
- 🔔 **Smart Notifications** - Real-time alerts and notifications
- 📱 **Progressive Web App** - Installable, offline-capable dashboard
- 🎨 **Modern UI** - Clean, responsive design with Tailwind CSS

## Tech Stack

- **React 18** - Modern React with hooks and concurrent features
- **TypeScript** - Type safety and better developer experience
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **React Query** - Data fetching and caching
- **React Router** - Client-side routing
- **Recharts** - Chart and data visualization
- **Lucide React** - Beautiful icon library

## Development

### Prerequisites

- Node.js 18+ 
- npm 9+

### Setup

1. Install dependencies:
```bash
npm install
```

2. Copy environment variables:
```bash
cp .env.example .env.local
```

3. Start development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000)

### Build

```bash
npm run build
```

### Testing

```bash
npm run test
```

### Linting

```bash
npm run lint
```

## PWA Features

### Offline Support
- Service worker caches essential resources
- Graceful degradation when offline
- Background sync for data updates

### Installation
- Add to home screen on mobile devices
- Desktop app experience
- Native app-like navigation

### Performance
- Code splitting for optimal loading
- Resource caching strategies
- Optimized bundle sizes

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Layout.tsx
│   ├── Header.tsx
│   ├── Sidebar.tsx
│   └── ...
├── pages/              # Route components
│   ├── Dashboard.tsx
│   ├── Conversations.tsx
│   ├── Analytics.tsx
│   └── ...
├── hooks/              # Custom React hooks
│   ├── useAuth.ts
│   ├── useNotifications.ts
│   └── ...
├── services/           # API and external services
│   └── api.ts
├── types/              # TypeScript type definitions
│   └── index.ts
└── utils/              # Utility functions
```

## Configuration

### Environment Variables

- `VITE_API_URL` - Backend API URL
- `VITE_APP_NAME` - Application name
- `VITE_ENVIRONMENT` - Environment (development/production)

### Authentication

The dashboard uses JWT-based authentication. For demo purposes, use:
- Email: `admin@ngx.com`
- Password: `demo123`

## Deployment

### Static Hosting

```bash
npm run build
# Deploy dist/ folder to your hosting provider
```

### Docker

```bash
docker build -t ngx-voice-pwa .
docker run -p 3000:3000 ngx-voice-pwa
```

### PWA Deployment Checklist

- [ ] HTTPS enabled
- [ ] Service worker registered
- [ ] Web app manifest configured
- [ ] Icons for all device sizes
- [ ] Offline functionality tested

## API Integration

The dashboard connects to the NGX Voice Agent backend API. Ensure the API is running and configured properly:

1. Backend API running on configured port
2. CORS enabled for dashboard domain
3. Authentication endpoints available
4. WebSocket connections for real-time data

## Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details