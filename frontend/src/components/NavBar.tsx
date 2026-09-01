import { Route, Routes, NavLink } from 'react-router-dom'

import WorkflowBuilderPage from '../pages/WorkflowBuilderPage'
import HomePage from '../pages/HomePage'

import AgentBuilderPage from '../pages/AgentBuilderPage'
import { useGlobalFunctions } from '../functions/GlobalFunctions'
import AllChats from '../pages/AllChats'
import { useEffect, useState } from 'react'

export default function NavBar() {
  const [chatsOpen, setChatsOpen] = useState(false)
  const {
    sidebarOpen,
    sidebarCollapsed,
    darkMode,
    navbarAction,
    language,
    t,
    toggleLanguage,
    closeSidebar,
    toggleSidebar,
    toggleSidebarCollapsed,
    toggleTheme,
    agents,
    loadAgents,
  } = useGlobalFunctions()

  useEffect(() => {
    loadAgents()
  }, [loadAgents])

  const navLinkClass = ({
    isActive,
  }: {
    isActive: boolean
  }) => {
    return `sidebar-link ${isActive ? 'active' : ''}`
  }

  return (
    <div
      className={`app-layout ${sidebarCollapsed ? 'sidebar-collapsed' : ''
        }`}
    >
      {/* ترويسة الهاتف */}
      <div className="mobile-header">
        <button
          className="mobile-hamburger"
          onClick={toggleSidebar}
        >
          {sidebarOpen ? '✕' : '☰'}
        </button>

        <span className="mobile-title">
          منشئ أكواد MAF
        </span>
      </div>

      {/* طبقة التعتيم */}
      <div
        className={`sidebar-overlay ${sidebarOpen
          ? 'sidebar-overlay--visible'
          : ''
          }`}
        onClick={closeSidebar}
      />

      {/* Navbar */}
      <nav
        className={`sidebar ${sidebarOpen ? 'sidebar--open' : ''
          }`}
      >
        {/* الشعار */}
        <div className="sidebar-brand">
          <div className="sidebar-brand-icon">
            ⚡
          </div>

          {!sidebarCollapsed && (
            <div className="sidebar-brand-text">
              <h1>إطار الوكلاء</h1>

              <span className="sidebar-subtitle">
                منشئ الأكواد
              </span>
            </div>
          )}
        </div>

        {!sidebarCollapsed && (
          <div className="sidebar-section">
            التنقل
          </div>
        )}

        {/* الرئيسية */}
        <NavLink
          to="/"
          end
          className={navLinkClass}
          onClick={closeSidebar}
        >
          <span className="sidebar-link-icon">
            🏠
          </span>

          {!sidebarCollapsed && t('home')}
        </NavLink>


        <NavLink
          to="/agents/new"
          className={navLinkClass}
          onClick={closeSidebar}
        >
          <span className="sidebar-link-icon">
            ＋
          </span>
          {!sidebarCollapsed && t('newChat')}
        </NavLink>


        {/* المحادثات */}


        {/* قائمة المحادثات المنسدلة */}
        <div className="sidebar-chats">
          <button
            type="button"
            className={`sidebar-link sidebar-chats-toggle ${chatsOpen ? 'active' : ''
              }`}
            onClick={() => {
              setChatsOpen(prev => !prev)
            }}
          >
            <span className="sidebar-link-icon">
              🤖
            </span>

            {!sidebarCollapsed && (
              <>
                <span className="sidebar-chats-title">
                  {t('chats')}
                </span>

                <span className="sidebar-chats-arrow">
                  {chatsOpen ? '⌄' : '›'}
                </span>
              </>
            )}
          </button>

          {/* المحادثات */}
          {!sidebarCollapsed && chatsOpen && (
            <div className="sidebar-chats-list">

              {agents.length === 0 ? (
                <div className="sidebar-chats-empty">
                  لا توجد محادثات
                </div>
              ) : (
                agents.map((agent) => (
                  <NavLink
                    key={agent.name}
                    to={`/agents/${encodeURIComponent(agent.name)}`}
                    className={({ isActive }) =>
                      `sidebar-chat-item ${isActive ? 'active' : ''
                      }`
                    }
                    onClick={closeSidebar}
                    title={agent.name}
                  >
                    <span className="sidebar-chat-icon">
                      💬
                    </span>

                    <span className="sidebar-chat-name">
                      {agent.name}
                    </span>
                  </NavLink>
                ))
              )}

            </div>
          )}
        </div>

        {/* سير العمل */}
        <NavLink
          to="/workflows"
          className={navLinkClass}
          onClick={closeSidebar}
        >
          <span className="sidebar-link-icon">
            🔀
          </span>

          {!sidebarCollapsed && t('workflows')}
        </NavLink>

        {/* زر الإجراء السريع من الصفحة الحالية */}


        {/* دفع الأزرار للأسفل */}
        <div style={{ flex: 1 }} />

        {/* زر تبديل اللغة */}
        <button
          className="sidebar-theme-btn" // نستخدم نفس الكلاس للتنسيق
          onClick={toggleLanguage}
          style={{ marginTop: 8 }}
        >
          🌐
          {!sidebarCollapsed && (language === 'ar' ? ' English' : ' عربي')}
        </button>

        {/* الوضع الليلي */}
        <button
          className="sidebar-theme-btn"
          onClick={toggleTheme}
          title={
            darkMode
              ? 'التبديل إلى الوضع الفاتح'
              : 'التبديل إلى الوضع الداكن'
          }
        >
          {darkMode ? '☀️' : '🌙'}

          {!sidebarCollapsed &&
            (darkMode ? ' فاتح' : ' داكن')}
        </button>

        {/* تصغير الشريط */}
        <button
          className="sidebar-collapse-btn "
          style={{ direction: 'ltr' }}
          onClick={toggleSidebarCollapsed}
          title={
            sidebarCollapsed
              ? 'فتح الشريط الجانبي'
              : 'إغلاق الشريط الجانبي'
          }
        >
          {sidebarCollapsed ? '»' : '«'}
        </button>
      </nav>

      {/* Main + Routes */}
      <main className="main-content">
        <Routes>
          <Route
            path="/"
            element={<HomePage />}
          />

          <Route
            path="/allchats"
            element={<AllChats />}
          />

          <Route
            path="/workflows"
            element={<WorkflowBuilderPage />}
          />
          <Route
            path="/agents/new"
            element={<AgentBuilderPage isNewMode={true} />}
          />

          <Route
            path="/agents/:agentName"
            element={<AgentBuilderPage />}
          />
        </Routes>
      </main>
    </div>
  )
}