import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  MessageCircle, 
  TrendingUp, 
  Bot, 
  DollarSign,
  ArrowUpRight,
  ArrowDownRight,
  Users,
  Clock
} from 'lucide-react'
import { StatsCard } from '../components/StatsCard'
import { ConversationChart } from '../components/ConversationChart'
import { RecentConversations } from '../components/RecentConversations'
import { PlatformMetrics } from '../components/PlatformMetrics'
import { dashboardAPI } from '../services/api'

export function Dashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: dashboardAPI.getStats,
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  const { data: conversations } = useQuery({
    queryKey: ['recent-conversations'],
    queryFn: () => dashboardAPI.getRecentConversations(10),
    refetchInterval: 10000, // Refresh every 10 seconds
  })

  const { data: platformMetrics } = useQuery({
    queryKey: ['platform-metrics'],
    queryFn: dashboardAPI.getPlatformMetrics,
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="h-96 bg-gray-200 rounded-lg"></div>
            <div className="h-96 bg-gray-200 rounded-lg"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Monitor your voice agents performance and analytics
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <select className="input">
            <option>Last 24 hours</option>
            <option>Last 7 days</option>
            <option>Last 30 days</option>
          </select>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Today's Conversations"
          value={stats?.todayConversations || 0}
          change={stats?.trends.conversations || 0}
          icon={MessageCircle}
          trend={stats?.trends.conversations > 0 ? 'up' : 'down'}
        />
        <StatsCard
          title="Conversions"
          value={stats?.todayConversions || 0}
          change={stats?.trends.conversions || 0}
          icon={TrendingUp}
          trend={stats?.trends.conversions > 0 ? 'up' : 'down'}
        />
        <StatsCard
          title="Active Agents"
          value={stats?.activeAgents || 0}
          change={0}
          icon={Bot}
          trend="neutral"
        />
        <StatsCard
          title="Revenue"
          value={stats?.revenue || 0}
          change={stats?.trends.revenue || 0}
          icon={DollarSign}
          trend={stats?.trends.revenue > 0 ? 'up' : 'down'}
          format="currency"
        />
      </div>

      {/* Charts and Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">
              Conversation Trends
            </h2>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-primary-500 rounded-full"></div>
                <span>Conversations</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span>Conversions</span>
              </div>
            </div>
          </div>
          <ConversationChart />
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">
              Platform Performance
            </h2>
          </div>
          <PlatformMetrics data={platformMetrics} />
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900">
                Recent Conversations
              </h2>
              <a 
                href="/conversations" 
                className="text-primary-600 hover:text-primary-700 text-sm font-medium"
              >
                View all
              </a>
            </div>
            <RecentConversations conversations={conversations} />
          </div>
        </div>

        <div className="space-y-6">
          {/* Quick Actions */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Quick Actions
            </h3>
            <div className="space-y-3">
              <button className="w-full btn-primary text-left">
                <Bot className="w-4 h-4 mr-2" />
                Create New Agent
              </button>
              <button className="w-full btn-secondary text-left">
                <Users className="w-4 h-4 mr-2" />
                View Live Conversations
              </button>
              <button className="w-full btn-ghost text-left">
                <Clock className="w-4 h-4 mr-2" />
                Schedule Report
              </button>
            </div>
          </div>

          {/* System Health */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              System Health
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">API Response Time</span>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium">245ms</span>
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Uptime</span>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium">99.9%</span>
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Active Sessions</span>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium">1,247</span>
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}