import { useState, useEffect, createContext, useContext } from 'react'
import type { User, AuthState } from '../types'
import { authAPI } from '../services/api'

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export function useAuthProvider(): AuthContextType {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
    token: null,
  })

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('ngx_token')
      if (token) {
        try {
          const user = await authAPI.verifyToken(token)
          setState({
            user,
            isAuthenticated: true,
            isLoading: false,
            token,
          })
        } catch (error) {
          localStorage.removeItem('ngx_token')
          setState({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            token: null,
          })
        }
      } else {
        setState({
          user: null,
          isAuthenticated: false,
          isLoading: false,
          token: null,
        })
      }
    }

    initAuth()
  }, [])

  const login = async (email: string, password: string) => {
    try {
      const { user, token } = await authAPI.login(email, password)
      localStorage.setItem('ngx_token', token)
      setState({
        user,
        isAuthenticated: true,
        isLoading: false,
        token,
      })
    } catch (error) {
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem('ngx_token')
    setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      token: null,
    })
  }

  const refreshToken = async () => {
    try {
      const token = localStorage.getItem('ngx_token')
      if (!token) throw new Error('No token available')
      
      const { user, token: newToken } = await authAPI.refreshToken(token)
      localStorage.setItem('ngx_token', newToken)
      setState(prev => ({
        ...prev,
        user,
        token: newToken,
      }))
    } catch (error) {
      logout()
      throw error
    }
  }

  return {
    ...state,
    login,
    logout,
    refreshToken,
  }
}

export { AuthContext }