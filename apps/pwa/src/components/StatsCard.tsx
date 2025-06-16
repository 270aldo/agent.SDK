import React from 'react'
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react'

interface StatsCardProps {
  title: string
  value: number
  change: number
  icon: LucideIcon
  trend: 'up' | 'down' | 'neutral'
  format?: 'number' | 'currency' | 'percentage'
}

export function StatsCard({ 
  title, 
  value, 
  change, 
  icon: Icon, 
  trend, 
  format = 'number' 
}: StatsCardProps) {
  const formatValue = (val: number) => {
    switch (format) {
      case 'currency':
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
          minimumFractionDigits: 0,
        }).format(val)
      case 'percentage':
        return `${val}%`
      default:
        return new Intl.NumberFormat('en-US').format(val)
    }
  }

  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'text-green-600'
      case 'down':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4" />
      case 'down':
        return <TrendingDown className="w-4 h-4" />
      default:
        return null
    }
  }

  return (
    <div className="card">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
            <Icon className="w-6 h-6 text-primary-600" />
          </div>
        </div>
        <div className="ml-4 flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{formatValue(value)}</p>
        </div>
      </div>
      
      {trend !== 'neutral' && change !== 0 && (
        <div className="mt-4 flex items-center">
          <div className={`flex items-center ${getTrendColor()}`}>
            {getTrendIcon()}
            <span className="ml-1 text-sm font-medium">
              {Math.abs(change)}%
            </span>
          </div>
          <span className="ml-2 text-sm text-gray-500">
            vs previous period
          </span>
        </div>
      )}
    </div>
  )
}