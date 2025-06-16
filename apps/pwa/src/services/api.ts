import axios from 'axios'
import type { 
  User, 
  Conversation, 
  DashboardStats,
  ConversationMetrics,
  PlatformMetrics,
  AgentConfig,
  ApiResponse 
} from '../types'

// API Base Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('ngx_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('ngx_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  async login(email: string, password: string): Promise<{ user: User; token: string }> {
    // Mock implementation for demo
    if (email === 'admin@ngx.com' && password === 'demo123') {
      const mockUser: User = {
        id: '1',
        email: 'admin@ngx.com',
        name: 'Admin User',
        role: 'admin',
        createdAt: new Date().toISOString(),
        lastLoginAt: new Date().toISOString(),
      }
      const mockToken = 'mock-jwt-token-' + Date.now()
      return { user: mockUser, token: mockToken }
    }
    throw new Error('Invalid credentials')
  },

  async verifyToken(token: string): Promise<User> {
    // Mock implementation
    return {
      id: '1',
      email: 'admin@ngx.com',
      name: 'Admin User',
      role: 'admin',
      createdAt: new Date().toISOString(),
      lastLoginAt: new Date().toISOString(),
    }
  },

  async refreshToken(token: string): Promise<{ user: User; token: string }> {
    const response = await apiClient.post('/auth/refresh', { token })
    return response.data
  },
}

// Dashboard API
export const dashboardAPI = {
  async getStats(): Promise<DashboardStats> {
    // Mock data for demo
    return {
      todayConversations: 247,
      todayConversions: 42,
      activeAgents: 8,
      revenue: 12450,
      trends: {
        conversations: 15,
        conversions: 8,
        revenue: 22,
      },
    }
  },

  async getRecentConversations(limit: number = 10): Promise<Conversation[]> {
    // Mock data
    const mockConversations: Conversation[] = Array.from({ length: limit }, (_, i) => ({
      id: `conv-${i + 1}`,
      platform: ['lead_magnet', 'landing_page', 'blog', 'mobile_app'][i % 4] as any,
      status: ['active', 'completed', 'transferred', 'abandoned'][i % 4] as any,
      startedAt: new Date(Date.now() - i * 3600000).toISOString(),
      messagesCount: Math.floor(Math.random() * 20) + 5,
      sentiment: ['positive', 'neutral', 'negative'][i % 3] as any,
      qualificationScore: Math.floor(Math.random() * 100),
      conversionProbability: Math.floor(Math.random() * 100),
      transferredToHuman: Math.random() > 0.8,
      leadQuality: ['hot', 'warm', 'cold', 'unqualified'][i % 4] as any,
      lastMessage: `Sample message ${i + 1}...`,
      metadata: {
        sessionId: `session-${i + 1}`,
        location: 'US',
        userAgent: 'Chrome',
      },
    }))
    return mockConversations
  },

  async getPlatformMetrics(): Promise<PlatformMetrics[]> {
    return [
      {
        platform: 'Lead Magnet',
        conversations: 124,
        conversions: 28,
        avgDuration: 240,
        conversionRate: 22.6,
        revenue: 4200,
      },
      {
        platform: 'Landing Page',
        conversations: 89,
        conversions: 19,
        avgDuration: 180,
        conversionRate: 21.3,
        revenue: 3800,
      },
      {
        platform: 'Blog Widget',
        conversations: 67,
        conversions: 8,
        avgDuration: 150,
        conversionRate: 11.9,
        revenue: 1600,
      },
      {
        platform: 'Mobile App',
        conversations: 45,
        conversions: 12,
        avgDuration: 320,
        conversionRate: 26.7,
        revenue: 2400,
      },
    ]
  },
}

// Conversations API
export const conversationsAPI = {
  async getConversations(filters?: any): Promise<{ conversations: Conversation[]; total: number }> {
    const response = await apiClient.get('/conversations', { params: filters })
    return response.data
  },

  async getConversation(id: string): Promise<Conversation> {
    const response = await apiClient.get(`/conversations/${id}`)
    return response.data
  },

  async getMessages(conversationId: string): Promise<any[]> {
    const response = await apiClient.get(`/conversations/${conversationId}/messages`)
    return response.data
  },
}

// Analytics API
export const analyticsAPI = {
  async getMetrics(filters?: any): Promise<ConversationMetrics> {
    const response = await apiClient.get('/analytics/metrics', { params: filters })
    return response.data
  },

  async getConversionFunnel(filters?: any): Promise<any> {
    const response = await apiClient.get('/analytics/funnel', { params: filters })
    return response.data
  },
}

// Agents API
export const agentsAPI = {
  async getAgents(): Promise<AgentConfig[]> {
    const response = await apiClient.get('/agents')
    return response.data
  },

  async createAgent(config: Partial<AgentConfig>): Promise<AgentConfig> {
    const response = await apiClient.post('/agents', config)
    return response.data
  },

  async updateAgent(id: string, config: Partial<AgentConfig>): Promise<AgentConfig> {
    const response = await apiClient.put(`/agents/${id}`, config)
    return response.data
  },

  async deleteAgent(id: string): Promise<void> {
    await apiClient.delete(`/agents/${id}`)
  },
}

// Notifications API
export const notificationsAPI = {
  async getNotifications(): Promise<any[]> {
    // Mock data
    return [
      {
        id: '1',
        title: 'New high-quality lead',
        message: 'A new lead with 95% qualification score',
        type: 'success',
        read: false,
        createdAt: new Date().toISOString(),
      },
      {
        id: '2',
        title: 'Agent performance alert',
        message: 'Lead magnet agent conversion rate dropped',
        type: 'warning',
        read: false,
        createdAt: new Date(Date.now() - 3600000).toISOString(),
      },
    ]
  },

  async markAsRead(id: string): Promise<void> {
    await apiClient.patch(`/notifications/${id}/read`)
  },

  async markAllAsRead(): Promise<void> {
    await apiClient.patch('/notifications/read-all')
  },
}

export default apiClient