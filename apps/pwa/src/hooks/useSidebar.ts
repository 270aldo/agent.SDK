import { useState, useEffect } from 'react'

export function useSidebar() {
  const [isCollapsed, setIsCollapsed] = useState(() => {
    const saved = localStorage.getItem('sidebar-collapsed')
    return saved ? JSON.parse(saved) : false
  })

  useEffect(() => {
    localStorage.setItem('sidebar-collapsed', JSON.stringify(isCollapsed))
  }, [isCollapsed])

  const toggle = () => setIsCollapsed(!isCollapsed)
  const expand = () => setIsCollapsed(false)
  const collapse = () => setIsCollapsed(true)

  return {
    isCollapsed,
    toggle,
    expand,
    collapse,
  }
}