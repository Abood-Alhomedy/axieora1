import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { listAgents, listWorkflows } from '../api/client'
import { type Language, translations } from './locales'
type ActionType =
  | 'create'
  | 'edit'
  | 'delete'
  | 'send'
  | 'reset'

type ResourceType =
  | 'agent'
  | 'workflow'

type GlobalAction = {
  action: ActionType
  resource: ResourceType
  id?: string
  data?: unknown
}

type NavbarAction = {
  label: string
  onClick: () => void
} | null

type GlobalContextType = {
  sidebarOpen: boolean
  setSidebarOpen: React.Dispatch<React.SetStateAction<boolean>>
  sidebarCollapsed: boolean
  setSidebarCollapsed: React.Dispatch<React.SetStateAction<boolean>>
  darkMode: boolean
  setDarkMode: React.Dispatch<React.SetStateAction<boolean>>
  loading: boolean
  agents: any[]
  workflows: any[]
  navbarAction: NavbarAction
  setNavbarAction: React.Dispatch<React.SetStateAction<NavbarAction>>
  closeSidebar: () => void
  toggleSidebar: () => void
  toggleTheme: () => void
  toggleSidebarCollapsed: () => void
  loadAgents: () => Promise<any[]>
  loadWorkflows: () => Promise<any[]>
  executeAction: (action: GlobalAction) => Promise<void>

  language: Language
  setLanguage: React.Dispatch<React.SetStateAction<Language>>
  toggleLanguage: () => void
  t: (key: keyof typeof translations['ar']) => string
}

const GlobalContext = createContext<GlobalContextType | undefined>(undefined)

export function GlobalProvider({ children }: { children: ReactNode }) {

  /* ===================================== Navbar ===================================== */
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  /* ===================================== Theme ===================================== */
  const [darkMode, setDarkMode] = useState(() => {
    return (localStorage.getItem('theme') === 'dark')
  })

    /* ===================================== Language ===================================== */
  const [language, setLanguage] = useState<Language>(() => {
    return (localStorage.getItem('language') as Language) || 'ar'
  })

  useEffect(() => {
    // لتحديث أبعاد الصفحة واتجاهها حسب اللغة
    document.documentElement.dir = language === 'ar' ? 'rtl' : 'ltr'
    document.documentElement.lang = language
    localStorage.setItem('language', language)
  }, [language])

  const toggleLanguage = () => {
    setLanguage(prev => prev === 'ar' ? 'en' : 'ar')
  }

  // الدالة t لجلب النص بناءً على مفتاحه
  const t = useCallback((key: keyof typeof translations['ar']) => {
    return translations[language][key] || key
  }, [language])

  /* ===================================== Loading ===================================== */
  const [loading, setLoading] = useState(false)

  /* ===================================== Data ===================================== */
  const [agents, setAgents] = useState<any[]>([])
  const [workflows, setWorkflows] = useState<any[]>([])

  /* ===================================== Navbar Action ===================================== */
  const [navbarAction, setNavbarAction] = useState<NavbarAction>(null)

  /* ===================================== Theme Effect ===================================== */
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light')
    localStorage.setItem('theme', darkMode ? 'dark' : 'light')
  }, [darkMode])

  /* ===================================== Sidebar ===================================== */
  const closeSidebar = () => { setSidebarOpen(false) }
  const toggleSidebar = () => { setSidebarOpen(prev => !prev) }
  const toggleSidebarCollapsed = () => { setSidebarCollapsed(prev => !prev) }

  /* ===================================== Theme ===================================== */
  const toggleTheme = () => { setDarkMode(prev => !prev) }

  /* ===================================== Load Agents ===================================== */
  const loadAgents = useCallback(async () => {
    try {
      const data = await listAgents()
      setAgents(data.agents)
      return data.agents
    } catch (error) {
      console.error(error)
      return []
    }
  }, [])

  /* ===================================== Load Workflows ===================================== */
  const loadWorkflows = useCallback(async () => {
    try {
      const data = await listWorkflows()
      setWorkflows(data.workflows)
      return data.workflows
    } catch (error) {
      console.error(error)
      return []
    }
  }, [])

  /* ===================================== Execute Global Action ===================================== */
  const executeAction = useCallback(async ({ action, resource, id, data }: GlobalAction) => {
    try {
      setLoading(true)
      console.log({ action, resource, id, data })
      /*
        ====================================
        هنا سيتم ربط جميع API functions
        مثال:
        if (resource === 'agent') {
          if (action === 'delete') { await deleteAgent(id) }
          if (action === 'edit') { await updateAgent(id, data) }
        }
        ====================================
      */
      if (resource === 'agent') { await loadAgents() }
      if (resource === 'workflow') { await loadWorkflows() }
    } catch (error) {
      console.error('Global Action Error:', error)
      throw error
    } finally {
      setLoading(false)
    }
  }, [loadAgents, loadWorkflows])

  return (
    <GlobalContext.Provider value={{
      sidebarOpen, setSidebarOpen,
      sidebarCollapsed, setSidebarCollapsed,
      darkMode, setDarkMode,
      loading,
      agents,
      workflows,
      navbarAction, setNavbarAction,
      closeSidebar,
      toggleSidebar,
      toggleSidebarCollapsed,
      toggleTheme,
      loadAgents,
      loadWorkflows,
      executeAction,
      language,
      setLanguage,
      toggleLanguage,
      t,
    }}>
      {children}
    </GlobalContext.Provider>
  )
}

/* ===================================== Hook للاستدعاء ===================================== */
export function useGlobalFunctions() {
  const context = useContext(GlobalContext)
  if (!context) {
    throw new Error('useGlobalFunctions يجب استخدامه داخل GlobalProvider')
  }
  return context
}