import { useState, useEffect } from 'react'
import { useGlobalFunctions } from '../functions/GlobalFunctions'
import { getAgent } from '../api/client'
import { useParams } from 'react-router-dom'

export default function AllChats() {
  const { agents, loadAgents } = useGlobalFunctions()

  const { agentName } = useParams()

  const [selectedAgent, setSelectedAgent] =
    useState<{ name: string } | null>(null)

  useEffect(() => {
    loadAgents()
  }, [loadAgents])

  useEffect(() => {
    if (agentName) {
      const decodedName = decodeURIComponent(agentName)

      setSelectedAgent({
        name: decodedName,
      })
    }
  }, [agentName])
  const handleSelectAgent = async (name: string) => {
    try {
      setSelectedAgent({ name })
      // إذا كنت تريد تنفيذ شيء إضافي مثل فتح الدردشة فوراً يمكنك إضافته هنا
    } catch { }
  }

  return (
    <div className="devui-shell">
      <div className="devui-body">
        <div className="devui-list-panel" style={{ width: '100%', maxWidth: '800px', margin: '0 auto', border: 'none' }}>
          <div className="devui-list-header">
            <span className="devui-list-header-title">المحادثات السابقة</span>
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{agents.length}</span>
          </div>
          <div className="devui-list-body">
            {agents.length === 0 ? (
              <div className="devui-empty">
                <div className="devui-empty-icon">🤖</div>
                <span>لا يوجد محادثات / وكلاء بعد</span>
              </div>
            ) : (
              agents.map(a => (
                <div
                  key={a.name}
                  className={`devui-list-item ${selectedAgent?.name === a.name ? 'devui-list-item--active' : ''}`}
                  onClick={() => handleSelectAgent(a.name)}
                >
                  <div className="devui-list-item-name">
                    {a.name}
                    {a.source_workflow && (
                      <span
                        className="badge badge-workflow"
                        title={`تم إنشاء الوكيل تلقائيًا من سير العمل «${a.source_workflow}»`}
                      >
                        WF
                      </span>
                    )}
                  </div>

                  <div className="devui-list-item-desc">{a.description}</div>

                  <div className="devui-list-item-meta">
                    {a.model}
                    {a.source_workflow && (
                      <span style={{ marginLeft: 6, opacity: 0.7 }}>
                        ← {a.source_workflow}
                      </span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}