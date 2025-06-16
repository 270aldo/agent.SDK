import React from 'react'
import { TrendingUp, Users, Clock, DollarSign } from 'lucide-react'
import type { PlatformMetrics as PlatformMetricsType } from '../types'

interface PlatformMetricsProps {
  data?: PlatformMetricsType[]
}

export function PlatformMetrics({ data = [] }: PlatformMetricsProps) {
  if (data.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-400">No platform data available</div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {data.map((platform, index) => (
        <div
          key={platform.platform}
          className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-gray-900">
              {platform.platform}
            </h3>
            <div className="text-right">
              <div className="text-lg font-bold text-gray-900">
                {platform.conversionRate.toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500">Conversion Rate</div>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center text-sm text-gray-600">
                  <Users className="w-4 h-4 mr-2" />
                  Conversations
                </div>
                <span className="text-sm font-medium">{platform.conversations}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center text-sm text-gray-600">
                  <TrendingUp className="w-4 h-4 mr-2" />
                  Conversions
                </div>
                <span className="text-sm font-medium">{platform.conversions}</span>
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center text-sm text-gray-600">
                  <Clock className="w-4 h-4 mr-2" />
                  Avg Duration
                </div>
                <span className="text-sm font-medium">
                  {Math.floor(platform.avgDuration / 60)}m {platform.avgDuration % 60}s
                </span>
              </div>
              
              {platform.revenue && (
                <div className="flex items-center justify-between">
                  <div className="flex items-center text-sm text-gray-600">
                    <DollarSign className="w-4 h-4 mr-2" />
                    Revenue
                  </div>
                  <span className="text-sm font-medium">
                    ${platform.revenue.toLocaleString()}
                  </span>
                </div>
              )}
            </div>
          </div>
          
          {/* Progress bar for conversion rate */}
          <div className="mt-3">
            <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
              <span>Performance</span>
              <span>{platform.conversionRate.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${Math.min(platform.conversionRate, 100)}%` }}
              ></div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}