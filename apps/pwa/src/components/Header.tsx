import React from 'react'
import { Bell, Search, User, LogOut, Settings } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import { useNotifications } from '../hooks/useNotifications'

export function Header() {
  const { user, logout } = useAuth()
  const { unreadCount } = useNotifications()
  const [showUserMenu, setShowUserMenu] = React.useState(false)

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center flex-1">
          <div className="max-w-lg w-full">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Search conversations, agents..."
                className="input pl-10 w-full"
              />
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <button className="relative p-2 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-lg">
            <Bell className="h-6 w-6" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>

          {/* User Menu */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                {user?.avatar ? (
                  <img src={user.avatar} alt={user.name} className="w-8 h-8 rounded-full" />
                ) : (
                  <User className="w-4 h-4 text-white" />
                )}
              </div>
              <div className="text-left">
                <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
              </div>
            </button>

            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                <a
                  href="/settings"
                  className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  <Settings className="w-4 h-4 mr-3" />
                  Settings
                </a>
                <div className="border-t border-gray-100 my-1"></div>
                <button
                  onClick={logout}
                  className="flex items-center w-full px-4 py-2 text-sm text-red-700 hover:bg-red-50"
                >
                  <LogOut className="w-4 h-4 mr-3" />
                  Sign Out
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}