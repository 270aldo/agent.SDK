import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, Filter, Download, Eye, MessageCircle } from 'lucide-react'
import { conversationsAPI } from '../services/api'
import type { ConversationFilters } from '../types'

export function Conversations() {
  const [filters, setFilters] = useState<ConversationFilters>({
    search: '',
    status: [],
    platform: [],
    sentiment: [],
    leadQuality: [],
  })
  const [showFilters, setShowFilters] = useState(false)

  const { data, isLoading, error } = useQuery({
    queryKey: ['conversations', filters],
    queryFn: () => conversationsAPI.getConversations(filters),
  })

  const handleFilterChange = (key: keyof ConversationFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const getPlatformColor = (platform: string) => {
    const colors = {
      lead_magnet: 'bg-blue-100 text-blue-800',
      landing_page: 'bg-green-100 text-green-800',
      blog: 'bg-purple-100 text-purple-800',
      mobile_app: 'bg-orange-100 text-orange-800',
    }
    return colors[platform as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  const getStatusColor = (status: string) => {
    const colors = {
      active: 'bg-green-100 text-green-800',
      completed: 'bg-blue-100 text-blue-800',
      transferred: 'bg-yellow-100 text-yellow-800',
      abandoned: 'bg-red-100 text-red-800',
    }
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-24 bg-gray-200 rounded-lg"></div>
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
          <h1 className="text-3xl font-bold text-gray-900">Conversations</h1>
          <p className="text-gray-600 mt-1">
            Manage and analyze all voice agent conversations
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="btn-secondary">
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search conversations..."
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              className="pl-10 input w-full"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`btn ${showFilters ? 'btn-primary' : 'btn-secondary'}`}
          >
            <Filter className="w-4 h-4 mr-2" />
            Filters
          </button>
        </div>

        {showFilters && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4 pt-4 border-t border-gray-200">
            <div>
              <label className="label">Platform</label>
              <select 
                className="input mt-1"
                onChange={(e) => handleFilterChange('platform', e.target.value ? [e.target.value] : [])}
              >
                <option value="">All platforms</option>
                <option value="lead_magnet">Lead Magnet</option>
                <option value="landing_page">Landing Page</option>
                <option value="blog">Blog Widget</option>
                <option value="mobile_app">Mobile App</option>
              </select>
            </div>
            <div>
              <label className="label">Status</label>
              <select 
                className="input mt-1"
                onChange={(e) => handleFilterChange('status', e.target.value ? [e.target.value] : [])}
              >
                <option value="">All statuses</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
                <option value="transferred">Transferred</option>
                <option value="abandoned">Abandoned</option>
              </select>
            </div>
            <div>
              <label className="label">Sentiment</label>
              <select 
                className="input mt-1"
                onChange={(e) => handleFilterChange('sentiment', e.target.value ? [e.target.value] : [])}
              >
                <option value="">All sentiments</option>
                <option value="positive">Positive</option>
                <option value="neutral">Neutral</option>
                <option value="negative">Negative</option>
              </select>
            </div>
            <div>
              <label className="label">Lead Quality</label>
              <select 
                className="input mt-1"
                onChange={(e) => handleFilterChange('leadQuality', e.target.value ? [e.target.value] : [])}
              >
                <option value="">All qualities</option>
                <option value="hot">Hot</option>
                <option value="warm">Warm</option>
                <option value="cold">Cold</option>
                <option value="unqualified">Unqualified</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Conversations Table */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            All Conversations ({data?.total || 0})
          </h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Conversation
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Platform
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Quality Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Started
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data?.conversations?.map((conversation) => (
                <tr key={conversation.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <MessageCircle className="w-5 h-5 text-gray-400 mr-3" />
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {conversation.id}
                        </div>
                        <div className="text-sm text-gray-500">
                          {conversation.messagesCount} messages
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPlatformColor(conversation.platform)}`}>
                      {conversation.platform.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(conversation.status)}`}>
                      {conversation.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="text-sm font-medium text-gray-900">
                        {conversation.qualificationScore}%
                      </div>
                      <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-primary-600 h-2 rounded-full"
                          style={{ width: `${conversation.qualificationScore}%` }}
                        ></div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(conversation.startedAt).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button className="text-primary-600 hover:text-primary-900 mr-3">
                      <Eye className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing 1 to {data?.conversations?.length || 0} of {data?.total || 0} results
            </div>
            <div className="flex space-x-2">
              <button className="btn-secondary">Previous</button>
              <button className="btn-secondary">Next</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}