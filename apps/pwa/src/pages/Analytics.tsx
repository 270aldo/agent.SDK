import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Calendar, Download, TrendingUp, Users, Clock, Target } from 'lucide-react'
import { analyticsAPI } from '../services/api'
import { ConversationChart } from '../components/ConversationChart'

export function Analytics() {
  const [period, setPeriod] = useState('week')
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0],
  })

  const { data: metrics, isLoading } = useQuery({
    queryKey: ['analytics-metrics', period, dateRange],
    queryFn: () => analyticsAPI.getMetrics({ period, dateRange }),
  })

  const { data: funnelData } = useQuery({
    queryKey: ['conversion-funnel', period],
    queryFn: () => analyticsAPI.getConversionFunnel({ period }),
  })

  // Mock data for demo
  const mockMetrics = {
    totalConversations: 1247,
    activeConversations: 23,
    completedConversations: 1187,
    averageDuration: 245,
    conversionRate: 23.4,
    transferRate: 8.2,
    satisfactionScore: 4.7,
    trends: {
      period: 'week',
      data: [
        { date: '2025-05-24', conversations: 178, conversions: 42, avgDuration: 235 },
        { date: '2025-05-25', conversations: 203, conversions: 48, avgDuration: 241 },
        { date: '2025-05-26', conversations: 189, conversions: 44, avgDuration: 252 },
        { date: '2025-05-27', conversations: 165, conversions: 38, avgDuration: 228 },
        { date: '2025-05-28', conversations: 198, conversions: 47, avgDuration: 259 },
        { date: '2025-05-29', conversations: 174, conversions: 41, avgDuration: 243 },
        { date: '2025-05-30', conversations: 140, conversions: 32, avgDuration: 237 },
      ]
    }
  }

  const mockFunnelData = [
    { stage: 'Visitors', count: 5420, percentage: 100 },
    { stage: 'Engaged', count: 1687, percentage: 31.1 },
    { stage: 'Conversations', count: 1247, percentage: 23.0 },
    { stage: 'Qualified', count: 623, percentage: 11.5 },
    { stage: 'Conversions', count: 292, percentage: 5.4 },
  ]

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600 mt-1">
            Deep insights into your voice agent performance
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <select 
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="input"
          >
            <option value="today">Today</option>
            <option value="week">Last 7 days</option>
            <option value="month">Last 30 days</option>
            <option value="quarter">Last 90 days</option>
          </select>
          <button className="btn-secondary">
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Conversations</p>
              <p className="text-2xl font-bold text-gray-900">{mockMetrics.totalConversations.toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Target className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Conversion Rate</p>
              <p className="text-2xl font-bold text-gray-900">{mockMetrics.conversionRate}%</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <Clock className="w-6 h-6 text-orange-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg Duration</p>
              <p className="text-2xl font-bold text-gray-900">
                {Math.floor(mockMetrics.averageDuration / 60)}m {mockMetrics.averageDuration % 60}s
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-purple-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Satisfaction</p>
              <p className="text-2xl font-bold text-gray-900">{mockMetrics.satisfactionScore}/5</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">
              Conversation Trends
            </h2>
          </div>
          <ConversationChart />
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">
              Conversion Funnel
            </h2>
          </div>
          <div className="space-y-4">
            {mockFunnelData.map((stage, index) => (
              <div key={stage.stage} className="relative">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-900">{stage.stage}</span>
                  <div className="text-right">
                    <span className="text-sm font-bold text-gray-900">{stage.count.toLocaleString()}</span>
                    <span className="text-xs text-gray-500 ml-2">({stage.percentage}%)</span>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-primary-600 h-3 rounded-full transition-all duration-500"
                    style={{ width: `${stage.percentage}%` }}
                  ></div>
                </div>
                {index < mockFunnelData.length - 1 && (
                  <div className="text-xs text-gray-500 mt-1 text-right">
                    -{((mockFunnelData[index].count - mockFunnelData[index + 1].count) / mockFunnelData[index].count * 100).toFixed(1)}% drop-off
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Performance by Platform */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900">
            Performance by Platform
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Platform
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Conversations
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Conversion Rate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg Duration
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Revenue
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Lead Magnet
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  524
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  26.8%
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  4m 32s
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  $18,420
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Landing Page
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  389
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  22.1%
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  3m 45s
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  $12,850
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Blog Widget
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  267
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  18.4%
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  2m 58s
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  $7,230
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Mobile App
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  67
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  31.3%
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  5m 12s
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  $4,890
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}