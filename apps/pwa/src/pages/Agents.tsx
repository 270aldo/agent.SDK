import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Plus, Settings, Play, Pause, Edit3, Trash2, Copy, Bot } from 'lucide-react'
import { agentsAPI } from '../services/api'
import type { AgentConfig } from '../types'

export function Agents() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  
  const { data: agents, isLoading, refetch } = useQuery({
    queryKey: ['agents'],
    queryFn: agentsAPI.getAgents,
  })

  // Mock data for demo
  const mockAgents: AgentConfig[] = [
    {
      id: '1',
      name: 'Lead Magnet Assistant',
      platform: 'lead_magnet',
      isActive: true,
      personality: {
        tone: 'friendly',
        style: 'consultative',
        expertise: ['fitness', 'nutrition', 'wellness']
      },
      triggers: {
        type: 'auto',
        threshold: 3
      },
      ui: {
        position: 'bottom-right',
        size: 'medium',
        theme: 'light',
        brandColors: {
          primary: '#3b82f6',
          secondary: '#1f2937',
          accent: '#10b981'
        }
      },
      behavior: {
        autoStart: true,
        enableVoice: true,
        enableTransfer: true,
        maxDuration: 600,
        followUpEnabled: true
      },
      qualificationCriteria: {
        minEngagementTime: 60,
        requiredFields: ['name', 'email', 'goal'],
        scoringWeights: {
          engagement: 0.3,
          intent: 0.4,
          fit: 0.3
        }
      }
    },
    {
      id: '2',
      name: 'Landing Page Converter',
      platform: 'landing_page',
      isActive: true,
      personality: {
        tone: 'professional',
        style: 'direct',
        expertise: ['sales', 'product', 'pricing']
      },
      triggers: {
        type: 'scroll',
        threshold: 70
      },
      ui: {
        position: 'center',
        size: 'large',
        theme: 'light'
      },
      behavior: {
        autoStart: false,
        enableVoice: true,
        enableTransfer: true,
        maxDuration: 900,
        followUpEnabled: true
      },
      qualificationCriteria: {
        minEngagementTime: 120,
        requiredFields: ['name', 'email', 'company', 'budget'],
        scoringWeights: {
          engagement: 0.2,
          intent: 0.5,
          fit: 0.3
        }
      }
    },
    {
      id: '3',
      name: 'Blog Content Helper',
      platform: 'blog',
      isActive: false,
      personality: {
        tone: 'casual',
        style: 'educational',
        expertise: ['content', 'seo', 'marketing']
      },
      triggers: {
        type: 'time',
        threshold: 30
      },
      ui: {
        position: 'bottom-left',
        size: 'small',
        theme: 'auto'
      },
      behavior: {
        autoStart: false,
        enableVoice: false,
        enableTransfer: false,
        maxDuration: 300,
        followUpEnabled: false
      },
      qualificationCriteria: {
        minEngagementTime: 30,
        requiredFields: ['email'],
        scoringWeights: {
          engagement: 0.5,
          intent: 0.3,
          fit: 0.2
        }
      }
    }
  ]

  const handleToggleAgent = async (agentId: string, isActive: boolean) => {
    try {
      await agentsAPI.updateAgent(agentId, { isActive: !isActive })
      refetch()
    } catch (error) {
      console.error('Failed to toggle agent:', error)
    }
  }

  const handleCloneAgent = async (agent: AgentConfig) => {
    try {
      await agentsAPI.createAgent({
        ...agent,
        id: undefined,
        name: `${agent.name} (Copy)`,
        isActive: false
      })
      refetch()
    } catch (error) {
      console.error('Failed to clone agent:', error)
    }
  }

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

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-64 bg-gray-200 rounded-lg"></div>
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
          <h1 className="text-3xl font-bold text-gray-900">Voice Agents</h1>
          <p className="text-gray-600 mt-1">
            Configure and manage your AI voice agents
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create Agent
        </button>
      </div>

      {/* Agents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {mockAgents.map((agent) => (
          <div key={agent.id} className="card hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                  agent.isActive ? 'bg-green-100' : 'bg-gray-100'
                }`}>
                  <Bot className={`w-6 h-6 ${
                    agent.isActive ? 'text-green-600' : 'text-gray-400'
                  }`} />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
                  {getPlatformBadge(agent.platform)}
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleToggleAgent(agent.id, agent.isActive)}
                  className={`p-2 rounded-lg transition-colors ${
                    agent.isActive 
                      ? 'bg-green-100 text-green-600 hover:bg-green-200' 
                      : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
                  }`}
                  title={agent.isActive ? 'Pause Agent' : 'Start Agent'}
                >
                  {agent.isActive ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div className="space-y-3 mb-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Trigger:</span>
                <span className="font-medium capitalize">
                  {agent.triggers.type} {agent.triggers.threshold && `(${agent.triggers.threshold})`}
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Personality:</span>
                <span className="font-medium capitalize">
                  {agent.personality.tone}, {agent.personality.style}
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Voice Enabled:</span>
                <span className={`font-medium ${agent.behavior.enableVoice ? 'text-green-600' : 'text-gray-400'}`}>
                  {agent.behavior.enableVoice ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Max Duration:</span>
                <span className="font-medium">
                  {Math.floor(agent.behavior.maxDuration / 60)}m
                </span>
              </div>
            </div>

            <div className="flex items-center space-x-2 pt-4 border-t border-gray-200">
              <button className="flex-1 btn-secondary text-sm">
                <Settings className="w-4 h-4 mr-2" />
                Configure
              </button>
              <button 
                onClick={() => handleCloneAgent(agent)}
                className="btn-ghost p-2"
                title="Clone Agent"
              >
                <Copy className="w-4 h-4" />
              </button>
              <button className="btn-ghost p-2 text-red-600" title="Delete Agent">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}

        {/* Create New Agent Card */}
        <div 
          onClick={() => setShowCreateModal(true)}
          className="card border-2 border-dashed border-gray-300 hover:border-primary-500 cursor-pointer transition-colors flex items-center justify-center min-h-[280px]"
        >
          <div className="text-center">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Plus className="w-6 h-6 text-primary-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Create New Agent</h3>
            <p className="text-gray-600 text-sm">
              Set up a new voice agent for your platform
            </p>
          </div>
        </div>
      </div>

      {/* Performance Overview */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900">
            Agent Performance Overview
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Agent
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Conversations (24h)
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Conversion Rate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg Quality Score
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {mockAgents.map((agent, index) => (
                <tr key={agent.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <Bot className="w-5 h-5 text-gray-400 mr-3" />
                      <div>
                        <div className="text-sm font-medium text-gray-900">{agent.name}</div>
                        <div className="text-sm text-gray-500">{agent.platform}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      agent.isActive 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {agent.isActive ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {Math.floor(Math.random() * 100) + 10}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {(Math.random() * 30 + 10).toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {Math.floor(Math.random() * 40 + 60)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Agent Modal would go here */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Create New Agent</h3>
            <p className="text-gray-600 mb-4">
              This feature will be implemented in the next iteration.
            </p>
            <button
              onClick={() => setShowCreateModal(false)}
              className="btn-primary w-full"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}