import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/Layout'
import { AuthGuard } from './components/AuthGuard'
import { Dashboard } from './pages/Dashboard'
import { Conversations } from './pages/Conversations'
import { Analytics } from './pages/Analytics'
import { Agents } from './pages/Agents'
import { Settings } from './pages/Settings'
import { Login } from './pages/Login'
import { useAuth } from './hooks/useAuth'

function App() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading-dots">
          <div></div>
          <div></div>
          <div></div>
          <div></div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={
          <AuthGuard>
            <Layout />
          </AuthGuard>
        }>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="conversations" element={<Conversations />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="agents" element={<Agents />} />
          <Route path="settings" element={<Settings />} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </div>
  )
}

export default App