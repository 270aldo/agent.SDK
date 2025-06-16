// Auth Types
export interface User {
  id: string
  email: string
  name: string
  role: 'admin' | 'operator' | 'viewer'
  avatar?: string
  createdAt: string
  lastLoginAt?: string
}

export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  token: string | null
}

// Conversation Types
export interface Conversation {
  id: string
  userId?: string
  platform: 'lead_magnet' | 'landing_page' | 'blog' | 'mobile_app'
  status: 'active' | 'completed' | 'transferred' | 'abandoned'
  startedAt: string
  endedAt?: string
  duration?: number
  messagesCount: number
  sentiment: 'positive' | 'neutral' | 'negative'
  qualificationScore: number
  conversionProbability: number
  transferredToHuman: boolean
  leadQuality: 'hot' | 'warm' | 'cold' | 'unqualified'
  lastMessage?: string
  metadata: {
    userAgent?: string
    location?: string
    referrer?: string
    sessionId: string
  }
}

export interface Message {
  id: string
  conversationId: string
  type: 'user' | 'agent' | 'system'
  content: string
  timestamp: string
  metadata?: {
    intent?: string
    entities?: Record<string, any>
    sentiment?: number
    confidence?: number
  }
}

// Analytics Types
export interface ConversationMetrics {
  totalConversations: number
  activeConversations: number
  completedConversations: number
  averageDuration: number
  conversionRate: number
  transferRate: number
  satisfactionScore: number
  trends: {
    period: 'day' | 'week' | 'month'
    data: Array<{
      date: string
      conversations: number
      conversions: number
      avgDuration: number
    }>
  }
}

export interface PlatformMetrics {
  platform: string
  conversations: number
  conversions: number
  avgDuration: number
  conversionRate: number
  revenue?: number
}

export interface LeadQualityMetrics {
  hot: number
  warm: number
  cold: number
  unqualified: number
  distribution: Array<{
    quality: string
    count: number
    percentage: number
  }>
}

// Agent Configuration Types
export interface AgentConfig {
  id: string
  name: string
  platform: string
  isActive: boolean
  personality: {
    tone: 'professional' | 'friendly' | 'casual' | 'enthusiastic'
    style: 'consultative' | 'direct' | 'educational' | 'nurturing'
    expertise: string[]
  }
  triggers: {
    type: 'auto' | 'scroll' | 'time' | 'exit_intent' | 'manual'
    threshold?: number
    conditions?: Record<string, any>
  }
  ui: {
    position: 'bottom-right' | 'bottom-left' | 'center' | 'fullscreen'
    size: 'small' | 'medium' | 'large'
    theme: 'light' | 'dark' | 'auto'
    brandColors?: {
      primary: string
      secondary: string
      accent: string
    }
  }
  behavior: {
    autoStart: boolean
    enableVoice: boolean
    enableTransfer: boolean
    maxDuration: number
    followUpEnabled: boolean
  }
  qualificationCriteria: {
    minEngagementTime: number
    requiredFields: string[]
    scoringWeights: Record<string, number>
  }
}

// Dashboard Types
export interface DashboardStats {
  todayConversations: number
  todayConversions: number
  activeAgents: number
  revenue: number
  trends: {
    conversations: number
    conversions: number
    revenue: number
  }
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  error?: string
  pagination?: {
    page: number
    limit: number
    total: number
    pages: number
  }
}

// Filter and Search Types
export interface ConversationFilters {
  platform?: string[]
  status?: string[]
  sentiment?: string[]
  leadQuality?: string[]
  dateRange?: {
    start: string
    end: string
  }
  search?: string
}

export interface AnalyticsFilters {
  period: 'today' | 'week' | 'month' | 'quarter' | 'year' | 'custom'
  platform?: string[]
  dateRange?: {
    start: string
    end: string
  }
}

// Settings Types
export interface AppSettings {
  notifications: {
    email: boolean
    push: boolean
    sms: boolean
    webhook: boolean
  }
  analytics: {
    retentionPeriod: number
    enableRealTime: boolean
    exportFormat: 'json' | 'csv' | 'xlsx'
  }
  security: {
    sessionTimeout: number
    mfaEnabled: boolean
    ipWhitelist: string[]
  }
  integrations: {
    crm: {
      enabled: boolean
      provider?: string
      apiKey?: string
    }
    email: {
      enabled: boolean
      provider?: string
      apiKey?: string
    }
    sms: {
      enabled: boolean
      provider?: string
      apiKey?: string
    }
  }
}