import React from 'react'
import { formatDistanceToNow } from 'date-fns'
import { MessageCircle, ExternalLink, Zap, Clock } from 'lucide-react'
import type { Conversation } from '../types'

interface RecentConversationsProps {
  conversations?: Conversation[]
}

export function RecentConversations({ conversations = [] }: RecentConversationsProps) {
  const getPlatformBadge = (platform: string) => {
    const colors = {
      lead_magnet: 'bg-blue-100 text-blue-800',
      landing_page: 'bg-green-100 text-green-800',
      blog: 'bg-purple-100 text-purple-800',
      mobile_app: 'bg-orange-100 text-orange-800',
    }
    
    const labels = {
      lead_magnet: 'Lead Magnet',
      landing_page: 'Landing Page',
      blog: 'Blog Widget',
      mobile_app: 'Mobile App',
    }

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[platform as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
        {labels[platform as keyof typeof labels] || platform}
      </span>
    )
  }

  const getStatusBadge = (status: string) => {
    const colors = {
      active: 'bg-green-100 text-green-800',
      completed: 'bg-blue-100 text-blue-800',
      transferred: 'bg-yellow-100 text-yellow-800',
      abandoned: 'bg-red-100 text-red-800',
    }

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
        {status}
      </span>
    )
  }

  const getLeadQualityColor = (quality: string) => {
    switch (quality) {
      case 'hot':
        return 'text-red-600'
      case 'warm':
        return 'text-orange-600'
      case 'cold':
        return 'text-blue-600'
      default:
        return 'text-gray-600'
    }
  }

  if (conversations.length === 0) {
    return (
      <div className="text-center py-12">
        <MessageCircle className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">No conversations</h3>
        <p className="mt-1 text-sm text-gray-500">
          Get started by configuring your agents.
        </p>
      </div>
    )
  }

  return (
    <div className="overflow-hidden">
      <div className="space-y-4">
        {conversations.map((conversation) => (
          <div
            key={conversation.id}
            className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-2">
                  {getPlatformBadge(conversation.platform)}
                  {getStatusBadge(conversation.status)}
                  {conversation.transferredToHuman && (
                    <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-purple-100 text-purple-800">
                      <ExternalLink className="w-3 h-3 mr-1" />
                      Transferred
                    </span>
                  )}
                </div>
                
                <p className="text-sm text-gray-900 truncate">
                  {conversation.lastMessage || 'No messages yet'}
                </p>
                
                <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                  <div className="flex items-center">
                    <Clock className="w-3 h-3 mr-1" />
                    {formatDistanceToNow(new Date(conversation.startedAt), { addSuffix: true })}
                  </div>
                  <div className="flex items-center">
                    <MessageCircle className="w-3 h-3 mr-1" />
                    {conversation.messagesCount} messages
                  </div>
                  <div className={`flex items-center font-medium ${getLeadQualityColor(conversation.leadQuality)}`}>
                    <Zap className="w-3 h-3 mr-1" />
                    {conversation.leadQuality} lead
                  </div>
                </div>
              </div>
              
              <div className="ml-4 flex-shrink-0 text-right">
                <div className="text-sm font-medium text-gray-900">
                  {conversation.qualificationScore}%
                </div>
                <div className="text-xs text-gray-500">
                  Quality Score
                </div>
                <div className="mt-1 text-xs text-gray-500">
                  {conversation.conversionProbability}% conversion
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 text-center">
        <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
          View all conversations →
        </button>
      </div>
    </div>
  )
}