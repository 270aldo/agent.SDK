import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { notificationsAPI } from '../services/api'

export function useNotifications() {
  const [unreadCount, setUnreadCount] = useState(0)

  const { data: notifications } = useQuery({
    queryKey: ['notifications'],
    queryFn: notificationsAPI.getNotifications,
    refetchInterval: 30000, // Check every 30 seconds
  })

  useEffect(() => {
    if (notifications) {
      const unread = notifications.filter((n: any) => !n.read).length
      setUnreadCount(unread)
    }
  }, [notifications])

  const markAsRead = async (id: string) => {
    try {
      await notificationsAPI.markAsRead(id)
      setUnreadCount(prev => Math.max(0, prev - 1))
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
    }
  }

  const markAllAsRead = async () => {
    try {
      await notificationsAPI.markAllAsRead()
      setUnreadCount(0)
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error)
    }
  }

  return {
    notifications: notifications || [],
    unreadCount,
    markAsRead,
    markAllAsRead,
  }
}