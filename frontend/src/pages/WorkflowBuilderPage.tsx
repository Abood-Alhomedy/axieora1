import { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge as FlowEdge,
  MarkerType,
  Position,
  Edge,
} from '@xyflow/react'
import pino from 'pino'
import '@xyflow/react/dist/style.css'
import {
  createWorkflowFromPrompt,
  editWorkflow,
  listWorkflows,
  getWorkflow,
  deleteWorkflow,
  runWorkflow,
  type WorkflowCreateResponse,
  type WorkflowDefinition,
  type WorkflowEvent,
} from '../api/client'
import BuilderChat from '../components/BuilderChat'
import { AssistantMessage } from './AgentBuilderPage'
const logger = pino({
  level: 'debug',
})
type ViewTab = 'graph' | 'yaml' | 'code'
type ExecutionStatus = 'idle' | 'running' | 'done' | 'error'

interface StepLog {
  id: number
  type: string
  node?: string
  input?: string
  output?: string
  source?: string
  target?: string
  condition?: string
  timestamp: number
}

interface BuilderMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  workflowResult?: WorkflowCreateResponse | null
}

export default function WorkflowBuilderPage() {

  const availableTools = [
  {
    id: 'web-search',
    name: 'Web Search',
    description: 'Search the web for up-to-date information.',
    icon: '🔍',
  },
  {
    id: 'calculator',
    name: 'Calculator',
    description: 'Perform mathematical calculations.',
    icon: '🧮',
  },
  {
    id: 'file-reader',
    name: 'File Reader',
    description: 'Read and process files.',
    icon: '📄',
  },
]
  const [workflowMenuOpen, setWorkflowMenuOpen] = useState(false)
  const [workflows, setWorkflows] = useState<{ name: string; description: string; executors_count: number; edges_count: number }[]>([])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<WorkflowCreateResponse | null>(null)
  const [selectedWf, setSelectedWf] = useState<{ name: string; definition: any; code: string } | null>(null)
  const [viewTab, setViewTab] = useState<ViewTab>('graph')
  const [chatKey, setChatKey] = useState(Date.now())
  // ── حالة محادثة إنشاء سير العمل ──
  const [builderMessages, setBuilderMessages] = useState<BuilderMessage[]>([])
  const [builderInput, setBuilderInput] = useState('')
  const [isCreating, setIsCreating] = useState(true)
  const builderEndRef = useRef<HTMLDivElement>(null)

  const [rightTab, setRightTab] = useState<'chat' | 'toolbar' | 'editor'>('chat')
  // ── حالة ساحة الاختبار ──
  const [runInput, setRunInput] = useState('')
  const [execStatus, setExecStatus] = useState<ExecutionStatus>('idle')
  const [logs, setLogs] = useState<StepLog[]>([])
  const [activeNodes, setActiveNodes] = useState<Record<string, 'processing' | 'completed' | 'idle'>>({})
  const [activeEdges, setActiveEdges] = useState<Record<string, 'flowing' | 'done' | 'idle'>>({})
  const [nodeOutputs, setNodeOutputs] = useState<Record<string, string>>({})
  const logsEndRef = useRef<HTMLDivElement>(null)

  // ── تقسيم قابل لتغيير الحجم ──
  const [chatPanelPct, setChatPanelPct] = useState(33)
  const centerRef = useRef<HTMLDivElement>(null)
  const isDragging = useRef(false)

  const handleDragStart = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    isDragging.current = true
    logger.info({

      isisDragging: isDragging
    });
    const onMove = (ev: MouseEvent) => {
      if (!isDragging.current || !centerRef.current) return

      const rect = centerRef.current.getBoundingClientRect()
      const pct = ((ev.clientY - rect.top) / rect.height) * 100

      setChatPanelPct(Math.min(80, Math.max(15, pct)))
    }

    const onUp = () => {
      isDragging.current = false
      document.removeEventListener('mousemove', onMove)
      document.removeEventListener('mouseup', onUp)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }

    document.body.style.cursor = 'row-resize'
    document.body.style.userSelect = 'none'

    document.addEventListener('mousemove', onMove)
    document.addEventListener('mouseup', onUp)
  }, [])

  // ── نافذة تفاصيل السجل ──
  const [selectedLog, setSelectedLog] = useState<StepLog | null>(null)

  const refreshList = () => {
    listWorkflows()
      .then(d => setWorkflows(d.workflows))
      .catch(() => { })
  }

  useEffect(() => {
    refreshList()
  }, [])

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  useEffect(() => {
    builderEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [builderMessages, loading])

const handleNew = () => {
  setIsCreating(true)

  setChatKey(Date.now())

  setResult(null)
  setSelectedWf(null)

  setBuilderMessages([])

  resetExecution()

  setWorkflowMenuOpen(false)

  // فتح تبويب الشات مباشرة
  setRightTab('chat')
}

  const handleEditSelectedWf = () => {
    setIsCreating(true)
    setChatKey(Date.now())
  }

  const handleSelectWorkflow = async (name: string) => {
  try {
    setLoading(true)

    const data = await getWorkflow(name)

    setSelectedWf(data)
    setResult(null)

    setIsCreating(false)

    // إعادة تعيين المحادثة والتنفيذ
    setBuilderMessages([])
    setChatKey(Date.now())
    resetExecution()

    setWorkflowMenuOpen(false)
  } catch (error) {
    console.error('Failed to load workflow:', error)
  } finally {
    setLoading(false)
  }
}

  // ── إرسال رسالة محادثة إنشاء سير العمل ──
  const handleBuilderSend = async () => {
    if (!builderInput.trim() || loading) return

    const userMsg: BuilderMessage = {
      role: 'user',
      content: builderInput.trim(),
    }

    setBuilderMessages(prev => [...prev, userMsg])
    setBuilderInput('')
    setLoading(true)
    logger.info({
      lodding: loading
    });
    const currentName = result?.name || selectedWf?.name
    logger.info({

      currnetName: currentName
    });
    try {
      let res: WorkflowCreateResponse

      if (!currentName) {
        res = await createWorkflowFromPrompt(userMsg.content)
      } else {
        res = await editWorkflow(currentName, userMsg.content)
      }

      setResult(res)

      if (res.name) {
        const data = await getWorkflow(res.name)
        setSelectedWf(data)
      }

      resetExecution()
      refreshList()

      const action = currentName ? 'تحديث' : 'إنشاء'

      const assistantMsg: BuilderMessage = {
        role: 'assistant',
        content: res.validation.valid
          ? `✅ تم ${action} سير العمل «${res.name}» بنجاح.

يمكنك الاستمرار في تعديله من خلال المحادثة. مثال:
• «أضف خطوة لتسجيل السجلات»
• «غيّر تفرع الشروط»
• «أضف عقدة جديدة»`
          : `⚠️ تم ${action} سير العمل «${res.name}»، ولكن توجد أخطاء في التحقق:

${res.validation.errors.join('\n')}`,
        workflowResult: res,
      }

      setBuilderMessages(prev => [...prev, assistantMsg])
    } catch (e: any) {
      setBuilderMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: `❌ حدث خطأ: ${e.message}`,
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  // ── تعديل سير العمل المحدد عبر المحادثة ──



  const handleDelete = async (name: string) => {
    if (!confirm(`هل تريد حذف سير العمل "${name}"؟`)) return

    await deleteWorkflow(name)

    setSelectedWf(null)
    setResult(null)
    setIsCreating(false)
    setBuilderMessages([])
    resetExecution()
    refreshList()
  }

  // ── تنفيذ سير العمل في ساحة الاختبار ──
  const resetExecution = () => {
    setLogs([])
    setActiveNodes({})
    setActiveEdges({})
    setNodeOutputs({})
    setExecStatus('idle')
  }

  const activeDef: WorkflowDefinition | null =
    result?.definition ?? selectedWf?.definition ?? null

  const activeCode: string =
    result?.code ?? selectedWf?.code ?? ''

  const activeName: string =
    result?.name ?? selectedWf?.name ?? ''

  const handleRun = async () => {
    if (!activeName || execStatus === 'running') return

    resetExecution()
    setExecStatus('running')

    const message =
      runInput.trim() || 'مرحباً، ابدأ سير العمل!'

    await runWorkflow(
      activeName,
      message,
      (event: WorkflowEvent) => {
        const timestamp = Date.now()

        switch (event.type) {
          case 'start':
            setLogs(prev => [
              ...prev,
              {
                id: prev.length,
                type: 'start',
                timestamp,
              },
            ])
            break

          case 'node_enter':
            setActiveNodes(prev => ({
              ...prev,
              [event.node!]: 'processing',
            }))

            setLogs(prev => [
              ...prev,
              {
                id: prev.length,
                type: 'node_enter',
                node: event.node,
                input: event.input,
                timestamp,
              },
            ])
            break

          case 'node_complete':
            setActiveNodes(prev => ({
              ...prev,
              [event.node!]: 'completed',
            }))

            setNodeOutputs(prev => ({
              ...prev,
              [event.node!]: event.output || '',
            }))

            setLogs(prev => [
              ...prev,
              {
                id: prev.length,
                type: 'node_complete',
                node: event.node,
                output: event.output,
                timestamp,
              },
            ])
            break

          case 'edge_active': {
            const edgeKey = `${event.source}->${event.target}`

            setActiveEdges(prev => ({
              ...prev,
              [edgeKey]: 'flowing',
            }))

            const conditionText = event.condition
              ? ` (الشرط: ${event.condition})`
              : ''

            setLogs(prev => [
              ...prev,
              {
                id: prev.length,
                type: 'edge_active',
                source: event.source,
                target: event.target,
                condition: conditionText,
                timestamp,
              },
            ])

            setTimeout(() => {
              setActiveEdges(prev => ({
                ...prev,
                [edgeKey]: 'done',
              }))
            }, 800)

            break
          }

          case newFunction():
            setLogs(prev => [
              ...prev,
              {
                id: prev.length,
                type: 'edge_skipped',
                source: event.source,
                target: event.target,
                condition: event.condition
                  ? ` (الشرط: ${event.condition})`
                  : '',
                timestamp,
              },
            ])
            break

          case 'done':
            setExecStatus('done')

            setLogs(prev => [
              ...prev,
              {
                id: prev.length,
                type: 'done',
                timestamp,
              },
            ])
            break

          case 'error':
            setExecStatus('error')

            setLogs(prev => [
              ...prev,
              {
                id: prev.length,
                type: 'error',
                output: event.content,
                timestamp,
              },
            ])
            break
        }

        function newFunction() {
          return 'edge_skipped'
        }
      },
    )
  }

  return (
    <div className="devui-shell">
      <div className="devui-body" style={{ display: 'flex', width: '100%', height: 'calc(100vh - 40px)' }}>

        {/* العمود الأوسط: الرسم البياني بكامل المساحة دون أي أشرطة علوية مكررة */}
        <div className="devui-center" ref={centerRef} style={{ flex: 1, position: 'relative', backgroundColor: 'var(--bg-primary)' }}>
          {activeDef ? (
            <div className="devui-center-full">
              <div className="devui-center-body">
                <AnimatedWorkflowGraph
                  definition={activeDef}
                  activeNodes={activeNodes}
                  activeEdges={activeEdges}
                  nodeOutputs={nodeOutputs}
                />
              </div>
            </div>
          ) : (
            <div className="devui-center-full" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <span style={{ color: 'var(--text-muted)', fontSize: 13, userSelect: 'none' }}>
                الرسم البياني سيظهر هنا عند إنشاء سير العمل...
              </span>
            </div>
          )}
        </div>

        {/* العمود الأيمن: القائمة الجانبية (دردشة / أدوات / محرر) المرفقة بالصورة */}
        <div className="devui-right" style={{ width: '380px', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--bg-secondary)', borderLeft: '1px solid var(--border)' }}>

          {/* الأزرار العلوية تماماً كالصورة (Run, Update ...) */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', padding: '12px 16px', gap: '8px' }}>
            <button className="btn btn-secondary btn-sm" style={{ padding: '6px 10px', background: 'transparent', border: '1px solid var(--border)' }}>...</button>
            <button className="btn btn-secondary btn-sm" style={{ padding: '6px 10px', background: 'transparent', border: '1px solid var(--border)' }}>🎨</button>
            <button className="btn btn-secondary btn-sm" style={{ padding: '6px 16px', background: 'transparent', border: '1px solid var(--border)', color: 'white' }}>Update</button>
            <button
              className="btn btn-sm"
              style={{ padding: '6px 16px', display: 'flex', alignItems: 'center', gap: '4px', background: 'white', color: 'black', fontWeight: 600, border: 'none' }}
              onClick={handleRun}
              disabled={execStatus === 'running'}
            >
              {execStatus === 'running' ? <span className="spinner" /> : '▶'} Run
            </button>
          </div>

          {/* التبويبات (Tabs: Chat, Toolbar, Editor) */}
          <div style={{ display: 'flex', borderBottom: '1px solid var(--border)', padding: '0 16px', gap: '24px', fontSize: '13px' }}>
            <div
              onClick={() => setRightTab('chat')}
              style={{ padding: '10px 0', borderBottom: rightTab === 'chat' ? '2px solid white' : '2px solid transparent', cursor: 'pointer',  }}
            >
              Chat
            </div>
            <div
              onClick={() => setRightTab('toolbar')}
              style={{ padding: '10px 0', borderBottom: rightTab === 'toolbar' ? '2px solid white' : '2px solid transparent', cursor: 'pointer' }}
            >
              Toolbar
            </div>
            <div
              onClick={() => setRightTab('editor')}
              style={{ padding: '10px 0', borderBottom: rightTab === 'editor' ? '2px solid white' : '2px solid transparent', cursor: 'pointer', }}
            >
              Editor
            </div>
          </div>

          {/* محتوى اللوحة اليمنى بناءً على التبويب المختار */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

            {/* 1. تبويب الدردشة (Chat) كالصورة */}
            {rightTab === 'chat' && (
              <BuilderChat
                key={chatKey}
                type="workflow"
                initialMessages={[
                  {
                    role: 'system',
                    content: selectedWf || result?.name
                      ? `تم فتح سير العمل في وضع التعديل. ما التغييرات التي تريد إجراؤها؟`
                      : `يرجى تقديم وصف لسير العمل الذي ترغب في إنشائه.`
                  }
                ]}
                currentName={result?.name || selectedWf?.name}
                onClose={() => setRightTab('editor')}
                onSuccess={(resData) => {
                  setResult(resData)
                  if (resData.name) {
                    getWorkflow(resData.name).then(data => setSelectedWf(data))
                  }
                  refreshList()
                }}
              />
            )}

{/* 2. تبويب الأدوات (Toolbar) */}
{rightTab === 'toolbar' && (
  <div
    style={{
      padding: '16px',
      display: 'flex',
      flexDirection: 'column',
      gap: '10px',
      overflowY: 'auto',
      height: '100%',
    }}
  >
    {/* عنوان */}
    <div
      style={{
        fontSize: 13,
        fontWeight: 700,
        color: 'var(--text-muted)',
        marginBottom: 4,
      }}
    >
      🛠 الأدوات
    </div>

    {/* قائمة الأدوات */}
    {availableTools.map((tool) => (
      <div
        key={tool.id}
        className="workflow-tool-item"
        draggable
        onDragStart={(event) => {
          event.dataTransfer.setData(
            'application/reactflow',
            'tool'
          )

          event.dataTransfer.setData(
            'tool-data',
            JSON.stringify(tool)
          )

          event.dataTransfer.effectAllowed = 'move'
        }}
      >
        <div className="workflow-tool-icon">
          {tool.icon}
        </div>

        <div className="workflow-tool-info">
          <div className="workflow-tool-name">
            {tool.name}
          </div>

          <div className="workflow-tool-description">
            {tool.description}
          </div>
        </div>

        <div
          style={{
            color: 'var(--text-muted)',
            fontSize: 16,
            opacity: 0.6,
          }}
        >
          ⠿
        </div>
      </div>
    ))}

    {/* فاصل */}
    <div
      style={{
        height: 1,
        background: 'var(--border)',
        margin: '8px 0',
      }}
    />

    {/* إعدادات سير العمل الحالية */}
    {activeName && (
      <button
        className="btn btn-danger btn-sm"
        onClick={() => handleDelete(activeName)}
      >
        🗑️ حذف سير العمل الحالي
      </button>
    )}
  </div>
)}

            {/* 3. تبويب المحرر وساحة الاختبار (Editor) لرؤية نتائج الـ Run */}
            {rightTab === 'editor' && (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'auto', padding: '12px' }}>
                {execStatus !== 'idle' && (
                  <div className={`playground-wf-status playground-wf-status-${execStatus}`} style={{ marginBottom: 12 }}>
                    {execStatus === 'running' && '⏳ جارٍ التنفيذ...'}
                    {execStatus === 'done' && '✅ اكتمل التنفيذ'}
                    {execStatus === 'error' && '❌ حدث خطأ'}
                  </div>
                )}

                <div className="devui-right-body" style={{ flex: 1 }}>
                  {logs.length === 0 ? (
                    <div className="devui-empty">
                      <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>اضغط على زر Run بالأعلى لتنفيذ سير العمل وعرض السجلات هنا.</span>
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                      {logs.map((log, i) => (
                        <div
                          key={log.id || i}
                          className={`wf-log wf-log-${log.type}`}
                        // onClick={() => handleLogClick(log)}
                        >
                          <div className="wf-log-header">
                            <span className="wf-log-time">
                              {new Date(log.timestamp).toLocaleTimeString()}
                            </span>
                            <span>
                              {log.type === 'start' && '🚀 بدء التنفيذ'}
                              {log.type === 'done' && '✅ اكتمل بنجاح'}
                              {log.type === 'error' && '❌ خطأ!'}
                              {log.type === 'node_enter' && `⚙️ دخول: ${log.node}`}
                              {log.type === 'node_complete' && `✔️ اكتمل: ${log.node}`}
                              {log.type === 'edge_active' && `➡️ انتقال`}
                              {log.type === 'edge_skipped' && `🛑 تم التخطي`}
                            </span>
                          </div>

                          {log.type === 'edge_active' && (
                            <div className="wf-log-edge">
                              {log.source} → {log.target} {log.condition || ''}
                            </div>
                          )}

                          {log.type === 'edge_skipped' && (
                            <div className="wf-log-edge" style={{ opacity: 0.5, textDecoration: 'line-through' }}>
                              {log.source} → {log.target} {log.condition || ''}
                            </div>
                          )}

                          {log.input && (
                            <div className="wf-log-data">
                              <span className="wf-log-data-label">الإدخال:</span>
                              {log.input.length > 100 ? log.input.slice(0, 100) + '...' : log.input}
                            </div>
                          )}

                          {log.output && (
                            <div className="wf-log-data">
                              <span className="wf-log-data-label">الإخراج:</span>
                              {log.output.length > 150 ? log.output.slice(0, 150) + '...' : log.output}
                            </div>
                          )}
                        </div>
                      ))}
                      <div ref={logsEndRef} />
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {selectedLog && (
        <div
          className="log-popup-overlay"
          onClick={() =>
            setSelectedLog(null)
          }
        >
          <div
            className="log-popup"
            onClick={e =>
              e.stopPropagation()
            }
          >

            <div className="log-popup-header">

              <span className="log-popup-title">

                {selectedLog.type === 'start' &&
                  '🟢 بدء التنفيذ'}

                {selectedLog.type ===
                  'node_enter' &&
                  '⏩ جارٍ التنفيذ'}

                {selectedLog.type ===
                  'node_complete' &&
                  '✅ اكتمل'}

                {selectedLog.type ===
                  'edge_active' &&
                  '→ انتقال'}

                {selectedLog.type ===
                  'edge_skipped' &&
                  '⊘ تم التخطي'}

                {selectedLog.type === 'done' &&
                  '🏁 انتهى'}

                {selectedLog.type === 'error' &&
                  '❌ خطأ'}

                {selectedLog.node &&
                  ` — ${selectedLog.node}`}

              </span>

              <button
                className="btn btn-secondary btn-sm"
                onClick={() =>
                  setSelectedLog(null)
                }
              >
                ✕
              </button>
            </div>

            <div className="log-popup-body">

              <table className="log-popup-table">
                <tbody>

                  <tr>
                    <td className="log-popup-label">
                      النوع
                    </td>
                    <td>
                      {selectedLog.type}
                    </td>
                  </tr>

                  {selectedLog.node && (
                    <tr>
                      <td className="log-popup-label">
                        العقدة
                      </td>
                      <td>
                        {selectedLog.node}
                      </td>
                    </tr>
                  )}

                  {selectedLog.source && (
                    <tr>
                      <td className="log-popup-label">
                        المصدر
                      </td>
                      <td>
                        {selectedLog.source}
                      </td>
                    </tr>
                  )}

                  {selectedLog.target && (
                    <tr>
                      <td className="log-popup-label">
                        الهدف
                      </td>
                      <td>
                        {selectedLog.target}
                      </td>
                    </tr>
                  )}

                  {selectedLog.condition && (
                    <tr>
                      <td className="log-popup-label">
                        الشرط
                      </td>
                      <td>
                        {selectedLog.condition}
                      </td>
                    </tr>
                  )}

                  <tr>
                    <td className="log-popup-label">
                      الطابع الزمني
                    </td>
                    <td>
                      {new Date(
                        selectedLog.timestamp,
                      ).toLocaleTimeString()}
                    </td>
                  </tr>

                </tbody>
              </table>

              {selectedLog.input && (
                <div className="log-popup-section">
                  <div className="log-popup-section-title">
                    📥 الإدخال
                  </div>

                  <pre className="log-popup-pre">
                    {selectedLog.input}
                  </pre>
                </div>
              )}

              {selectedLog.output && (
                <div className="log-popup-section">
                  <div className="log-popup-section-title">
                    📤 الإخراج
                  </div>

                  <pre className="log-popup-pre">
                    {selectedLog.output}
                  </pre>
                </div>
              )}

            </div>
          </div>
        </div>
      )}
    </div>
  )
}


// ── الرسم البياني المتحرك لسير العمل ───────────────────────────────

function AnimatedWorkflowGraph({
  definition,
  activeNodes,
  activeEdges,
  nodeOutputs,
}: {
  definition: WorkflowDefinition
  activeNodes: Record<
    string,
    'processing' | 'completed' | 'idle'
  >
  activeEdges: Record<
    string,
    'flowing' | 'done' | 'idle'
  >
  nodeOutputs: Record<string, string>
}) {
  const [nodes, setNodes, onNodesChange,] = useNodesState<Node>([])

  const [
    edges,
    setEdges,
    onEdgesChange,
  ] = useEdgesState<Edge>([])

  const { flowNodes, flowEdges } = useMemo(() => {
    if (!definition?.executors) {
      return {
        flowNodes: [],
        flowEdges: [],
      }
    }

    const executors = definition.executors
    const edgeDefs = definition.edges || []

    // التخطيط التلقائي: استخدام BFS لتحديد المستويات
    const adj: Record<string, string[]> = {}

    executors.forEach(e => {
      adj[e.name] = []
    })

    edgeDefs.forEach(e => {
      if (adj[e.source]) {
        adj[e.source].push(e.target)
      }
    })

    const levels: Record<string, number> = {}
    const queue = [definition.start]

    levels[definition.start] = 0

    while (queue.length) {
      const node = queue.shift()!

      for (const child of adj[node] || []) {
        if (levels[child] === undefined) {
          levels[child] =
            (levels[node] || 0) + 1

          queue.push(child)
        }
      }
    }

    const byLevel: Record<
      number,
      string[]
    > = {}

    Object.entries(levels).forEach(
      ([name, level]) => {
        if (!byLevel[level]) {
          byLevel[level] = []
        }

        byLevel[level].push(name)
      },
    )

    executors.forEach(e => {
      if (levels[e.name] === undefined) {
        const maxLevel = Math.max(
          0,
          ...Object.values(levels),
        )

        levels[e.name] = maxLevel + 1

        if (!byLevel[levels[e.name]]) {
          byLevel[levels[e.name]] = []
        }

        byLevel[levels[e.name]].push(
          e.name,
        )
      }
    })

    const computedNodes: Node[] =
      executors.map(e => {
        const level =
          levels[e.name] ?? 0

        const siblings =
          byLevel[level] || [e.name]

        const idx =
          siblings.indexOf(e.name)

        const totalWidth =
          siblings.length * 220

        const offsetX =
          idx * 220 -
          totalWidth / 2 +
          110

        const nodeState =
          activeNodes[e.name] ||
          'idle'

        const output =
          nodeOutputs[e.name] || ''

        return {
          id: e.name,

          position: {
            x: 300 + offsetX,
            y: level * 150 + 40,
          },

          data: {
            label: (
              <PlaygroundNodeContent
                name={e.name}
                type={e.type}
                isStart={
                  e.name ===
                  definition.start
                }
                state={nodeState}
                output={output}
              />
            ),
          },

          sourcePosition:
            Position.Bottom,

          targetPosition:
            Position.Top,

          style: {
            background:
              'transparent',
            border: 'none',
            padding: 0,
          },
        }
      })

    const computedEdges: FlowEdge[] =
      edgeDefs.map((e, i) => {
        const edgeKey =
          `${e.source}->${e.target}`

        const edgeState =
          activeEdges[edgeKey] ||
          'idle'

        let strokeColor =
          '#4b5563'

        let strokeWidth = 1.5

        let animated = false

        if (edgeState === 'flowing') {
          strokeColor = '#f59e0b'
          strokeWidth = 3
          animated = true
        } else if (
          edgeState === 'done'
        ) {
          strokeColor = '#22c55e'
          strokeWidth = 2
        } else if (e.condition) {
          strokeColor = '#6366f1'
          animated = true
        }

        return {
          id: `e-${i}`,
          source: e.source,
          target: e.target,

          label: e.condition || '',

          labelStyle: {
            fill: '#9ca3af',
            fontSize: 11,
          },

          style: {
            stroke: strokeColor,
            strokeWidth,
          },

          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: strokeColor,
          },

          animated,
        }
      })

    return {
      flowNodes: computedNodes,
      flowEdges: computedEdges,
    }
  }, [
    definition,
    activeNodes,
    activeEdges,
    nodeOutputs,
  ])

  useEffect(() => {
    setNodes(flowNodes)
    setEdges(flowEdges)
  }, [
    flowNodes,
    flowEdges,
    setNodes,
    setEdges,
  ])

  if (!nodes.length) {
    return (
      <div className="empty-state">
        <p>لا توجد بيانات للرسم البياني</p>
      </div>
    )
  }

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      nodesDraggable={true}
      fitView
      proOptions={{
        hideAttribution: true,
      }}
      style={{
        background:
          'var(--bg-panel-body)',
      }}
    >
      <Background
        color="var(--border)"
        gap={20}
      />

      <Controls />
    </ReactFlow>
  )
}


function PlaygroundNodeContent({
  name,
  type,
  isStart,
  state,
  output,
}: {
  name: string
  type: string
  isStart: boolean
  state:
  | 'processing'
  | 'completed'
  | 'idle'
  output: string
}) {
  const stateClass =
    state !== 'idle'
      ? `wf-node-${state}`
      : ''

  return (
    <div
      className={`workflow-node ${type} ${stateClass}`}
      style={
        isStart && state === 'idle'
          ? {
            boxShadow:
              '0 0 12px rgba(99,102,241,0.4)',
          }
          : {}
      }
    >

      <div className="workflow-node-label">

        {state === 'processing' && (
          <span className="wf-node-pulse" />
        )}

        {state === 'completed' &&
          '✅ '}

        {name}

      </div>

      <div className="workflow-node-type">

        {type === 'agent'
          ? '🤖 وكيل'
          : '⚙️ دالة'}

        {isStart &&
          ' (البداية)'}

      </div>

      {output &&
        state === 'completed' && (
          <div
            className="wf-node-output"
            title={output}
          >
            {output.length > 60
              ? output.slice(0, 60) +
              '...'
              : output}
          </div>
        )}

    </div>
  )
}