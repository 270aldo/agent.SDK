import React from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { 
  BarChart3, 
  MessageCircle, 
  Bot, 
  Settings, 
  Home,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import { useSidebar } from '../hooks/useSidebar'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Conversations', href: '/conversations', icon: MessageCircle },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Agents', href: '/agents', icon: Bot },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export function Sidebar() {
  const location = useLocation()
  const { isCollapsed, toggle } = useSidebar()

  return (
    <div className={`
      bg-white shadow-sm border-r border-gray-200 transition-all duration-300
      ${isCollapsed ? 'w-16' : 'w-64'}
    `}>
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        {!isCollapsed && (
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">NGX Voice</h1>
              <p className="text-xs text-gray-500">Dashboard</p>
            </div>
          </div>
        )}
        <button
          onClick={toggle}
          className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
        >
          {isCollapsed ? (
            <ChevronRight className="w-4 h-4 text-gray-500" />
          ) : (
            <ChevronLeft className="w-4 h-4 text-gray-500" />
          )}
        </button>
      </div>

      <nav className="mt-6 px-3">
        <ul className="space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <li key={item.name}>
                <NavLink
                  to={item.href}
                  className={`
                    flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors
                    ${isActive 
                      ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-700' 
                      : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                    }
                    ${isCollapsed ? 'justify-center' : ''}
                  `}
                >
                  <item.icon className={`w-5 h-5 ${isCollapsed ? '' : 'mr-3'}`} />
                  {!isCollapsed && item.name}
                </NavLink>
              </li>
            )
          })}
        </ul>
      </nav>

      {!isCollapsed && (
        <div className="absolute bottom-4 left-4 right-4">
          <div className="bg-primary-50 rounded-lg p-4">
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <div>
                <p className="text-sm font-medium text-gray-900">System Status</p>
                <p className="text-xs text-gray-600">All systems operational</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}