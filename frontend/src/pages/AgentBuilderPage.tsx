import { useState, useEffect, useRef, useCallback } from 'react'
import BuilderChat from '../components/BuilderChat'
import { useGlobalFunctions } from '../functions/GlobalFunctions'
import {

  type CopilotQuestion,
  type CopilotQuestionOption,
  sendCopilotMessage, // ← أضف هذا
  // ... باقي الاستيرادات
} from '../api/client'
import {

  createAgentFromDefinition,
  editAgent,
  listAgents,
  getAgent,
  deleteAgent,
  runAgent,
  type AgentCreateResponse,
  type AgentDefinition,
  type ChatMessage,
} from '../api/client'
import { useParams } from 'react-router-dom'
import AgentChat from '../components/AgentChat'

type TabMode = 'chat' | 'manual'

interface BuilderMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  questions?: CopilotQuestion[]
  agentResult?: AgentCreateResponse | null
}

const TypewriterMessage = ({ content, onComplete }: { content: string, onComplete?: () => void }) => {
  const [displayed, setDisplayed] = useState('');

  useEffect(() => {
    let i = 0;
    setDisplayed('');

    if (!content || content.length === 0) {
      onComplete?.();
      return;
    }

    const timer = setInterval(() => {
      i++;
      setDisplayed(content.substring(0, i));
      if (i >= content.length) {
        clearInterval(timer);
        onComplete?.();
      }
    }, 15); // Adjust typing speed here

    return () => clearInterval(timer);
  }, [content, onComplete]); // Only re-run when content or onComplete changes

  return <>{displayed}</>;
};

export function AssistantMessage ({ msg, isLast, onOptionSelect, loading }: any){
  const [isTyping, setIsTyping] = useState(isLast);
  // Auto-scroll logic helper by allowing layout to update smoothly
  useEffect(() => {
    if (!isLast) {
      setIsTyping(false);
    }
  }, [isLast]);

  return (
    <div className="builder-msg builder-msg-assistant">
      <div className="builder-msg-role">🤖 الذكاء الاصطناعي</div>
      <div className="builder-msg-content">
        {isTyping ? (
          <TypewriterMessage content={msg.content} onComplete={() => setIsTyping(false)} />
        ) : (
          msg.content
        )}
      </div>

      {!isTyping && msg.questions && msg.questions.length > 0 && (
        <div className="copilot-questions">
          {msg.questions.map((question: any) => (
            <div key={question.id} className="copilot-question">
              <div className="copilot-question-text">{question.question}</div>
              <div className="copilot-options">
                {question.options.map((option: any) => (
                  <button
                    key={option.value}
                    type="button"
                    className={
                      option.value === question.default_value
                        ? 'copilot-option copilot-option-default'
                        : 'copilot-option'
                    }
                    onClick={() => onOptionSelect(question, option)}
                    disabled={loading}
                  >
                    <span>{option.label}</span>
                    {option.value === question.default_value && <small>مقترح</small>}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default function AgentBuilderPage({
  isNewMode = false,
}: {
  isNewMode?: boolean
}) {
  const { agentName } = useParams()


  const { setNavbarAction } = useGlobalFunctions()
  const [tab, setTab] = useState<TabMode>('chat')
  const [agents, setAgents] = useState<{ name: string; description: string; model: string; source_workflow?: string | null }[]>([])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AgentCreateResponse | null>(null)
  const [selectedAgent, setSelectedAgent] = useState<{ name: string; definition: Record<string, unknown>; code: string } | null>(null)

  // ── حالة دردشة بناء الوكيل ──
  const [builderMessages, setBuilderMessages] = useState<BuilderMessage[]>([])
  const [builderInput, setBuilderInput] = useState('')
  const [isCreating, setIsCreating] = useState(false)
  const [chatKey, setChatKey] = useState(Date.now())
  const builderEndRef = useRef<HTMLDivElement>(null)

  // الوضع اليدوي
  const [manualForm, setManualForm] = useState<AgentDefinition>({
    name: '',
    description: '',
    instructions: '',
    model: 'gpt-4o',
    tools: [],
    temperature: 0.7,
  })

  // ── حالة بيئة الاختبار ──
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [chatInput, setChatInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [streamBuffer, setStreamBuffer] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // ── تقسيم قابل لتغيير الحجم ──
  const [chatPanelPct, setChatPanelPct] = useState(33)
  const centerRef = useRef<HTMLDivElement>(null)
  const isDragging = useRef(false)

  const handleDragStart = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    isDragging.current = true
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

  // ── تبويب عرض النتيجة ──
  const [resultView, setResultView] = useState<'yaml' | 'code'>('yaml')

  const refreshList = () => {
    listAgents().then(d => setAgents(d.agents)).catch(() => { })
  }

  useEffect(() => { refreshList() }, [])

  // ── إنشاء جديد ──
  const handleNew = useCallback(() => {
    setIsCreating(true)
    setBuilderMessages([{
      role: 'system',
      content: 'سيتم إنشاء وكيل ذكي جديد. ما نوع الوكيل الذي تريد إنشاءه؟ يرجى وصفه.',
    }])
    setResult(null)
    setSelectedAgent(null)
    setMessages([])
    setStreamBuffer('')
    setBuilderInput('')
  }, [])

  // ── تسجيل زر «إنشاء جديد» في الـ Navbar ──
  // ── استكشاف وضع الإنشاء الجديد ──
  useEffect(() => {
    if (isNewMode) {
      setTab('chat')
      handleNew()
    } else {
      setIsCreating(false)
      setResult(null)
      setSelectedAgent(null)
      setMessages([])
      setStreamBuffer('')
      setBuilderInput('')
    }
  }, [isNewMode, handleNew])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamBuffer])

  useEffect(() => {
    builderEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [builderMessages, loading])


  // // ── إرسال رسالة إلى دردشة بناء الوكيل ──
  // const handleBuilderSend = async () => {
  //   if (!builderInput.trim() || loading) return
  //   const userMsg: BuilderMessage = { role: 'user', content: builderInput.trim() }
  //   setBuilderMessages(prev => [...prev, userMsg])
  //   setBuilderInput('')
  //   setLoading(true)

  //   const currentName = result?.name || selectedAgent?.name

  //   try {
  //     let res: AgentCreateResponse
  //     if (!currentName) {
  //       res = await createAgentFromPrompt(userMsg.content)
  //     } else {
  //       res = await editAgent(currentName, userMsg.content)
  //     }

  //     setResult(res)
  //     if (res.name) {
  //       const data = await getAgent(res.name)
  //       setSelectedAgent(data)
  //       setMessages([])
  //       setStreamBuffer('')
  //     }
  //     refreshList()

  //     const action = currentName ? 'تحديث' : 'إنشاء'
  //     const assistantMsg: BuilderMessage = {
  //       role: 'assistant',
  //       content: res.validation.valid
  //         ? `✅ تم ${action} الوكيل «${res.name}» بنجاح.\n\nيمكنك متابعة تعديله من خلال الدردشة. مثال:\n• «اجعل أسلوبه أكثر تهذيبًا»\n• «أضف أداة»\n• «اجعل قيمة Temperature تساوي 0.3»`
  //         : `⚠️ تم ${action} الوكيل «${res.name}»، ولكن توجد أخطاء في التحقق:\n${res.validation.errors.join('\n')}`,
  //       agentResult: res,
  //     }
  //     setBuilderMessages(prev => [...prev, assistantMsg])
  //   } catch (e: any) {
  //     setBuilderMessages(prev => [...prev, {
  //       role: 'assistant',
  //       content: `❌ حدث خطأ: ${e.message}`,
  //     }])
  //   } finally {
  //     setLoading(false)
  //   }
  // }

  // ── إرسال رسالة إلى دردشة بناء الوكيل ──
  // ── إرسال رسالة إلى دردشة بناء الوكيل ──
  const handleCopilotOptionSelect = async (
    question: CopilotQuestion,
    option: CopilotQuestionOption
  ) => {
    if (loading) return

    const userMessage = option.label

    const userMsg: BuilderMessage = {
      role: 'user',
      content: option.label,
    }

    setBuilderMessages(prev => [
      ...prev,
      userMsg,
    ])

    setLoading(true)

    try {
      const res = await sendCopilotMessage(
        userMessage
      )

      const assistantMsg: BuilderMessage = {
        role: 'assistant',
        content: res.message,
        questions: res.questions ?? [],
      }

      setBuilderMessages(prev => [
        ...prev,
        assistantMsg,
      ])

      if (res.status === 'building' && res.agent) {
        setResult(res.agent)

        setSelectedAgent({
          name: res.agent.name,
          definition:
            res.agent.definition as unknown as Record<string, unknown>,
          code: res.agent.code,
        })

        refreshList()
      }
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
  const handleBuilderSend = async () => {
    if (!builderInput.trim() || loading) return
    const userMsg: BuilderMessage = { role: 'user', content: builderInput.trim() }
    setBuilderMessages(prev => [...prev, userMsg])
    setBuilderInput('')
    setLoading(true)

    const currentName = result?.name || selectedAgent?.name

    try {
      if (!currentName) {
        // 1. نحن في وضع إنشاء وكيل جديد (استخدام Copilot التفاعلي)
        const res = await sendCopilotMessage(userMsg.content)

        const assistantMsg: BuilderMessage = {
          role: 'assistant',
          content: res.message, // رسالة الكوبايلوت (قد تكون سؤالاً توضيحياً)
          questions: res.questions ?? [],
        }
        setBuilderMessages(prev => [...prev, assistantMsg])

        // إذا قرر الكوبايلوت أن جميع المتطلبات جاهزة وتم البناء في السيرفر
        if (res.status === 'building') {
          setBuilderMessages(prev => [...prev, {
            role: 'system',
            content: `✅ تم إنشاء الوكيل بنجاح!`
          }])

          // تحديث الواجهة لعرض الوكيل الجديد
          if (res.agent) {
            setResult(res.agent)
            setSelectedAgent({
              name: res.agent.name,
              definition: res.agent.definition as unknown as Record<string, unknown>,
              code: res.agent.code
            })
          }
          refreshList()
        }

      } else {
        // 2. نحن في وضع تعديل وكيل موجود مسبقاً
        const res = await editAgent(currentName, userMsg.content)

        setResult(res)
        if (res.name) {
          const data = await getAgent(res.name)
          setSelectedAgent(data)
          setMessages([])
          setStreamBuffer('')
        }
        refreshList()

        const assistantMsg: BuilderMessage = {
          role: 'assistant',
          content: res.validation.valid
            ? `✅ تم تحديث الوكيل «${res.name}» بنجاح.\n\nيمكنك متابعة تعديله من خلال الدردشة. مثال:\n• «اجعل أسلوبه أكثر تهذيبًا»\n• «أضف أداة»\n• «اجعل قيمة Temperature تساوي 0.3»`
            : `⚠️ تم تحديث الوكيل «${res.name}»، ولكن توجد أخطاء في التحقق:\n${res.validation.errors.join('\n')}`,
          agentResult: res,
        }
        setBuilderMessages(prev => [...prev, assistantMsg])
      }
    } catch (e: any) {
      setBuilderMessages(prev => [...prev, {
        role: 'assistant',
        content: `❌ حدث خطأ: ${e.message}`,
      }])
    } finally {
      setLoading(false)
    }
  }

  // ── تعديل الوكيل المحدد عبر الدردشة ──
  const handleEditSelectedAgent = () => {
    if (!selectedAgent) return
    setIsCreating(true)
    setBuilderMessages([{
      role: 'system',
      content: `تم فتح الوكيل «${selectedAgent.name}» في وضع التعديل. ما التغييرات التي تريد إجراءها؟`,
    }])
    setBuilderInput('')
  }

  const handleManualCreate = async () => {
    if (!manualForm.name || !manualForm.instructions) return
    setLoading(true)
    setResult(null)
    try {
      const res = await createAgentFromDefinition(manualForm)
      setResult(res)
      if (res.name) {
        const data = await getAgent(res.name)
        setSelectedAgent(data)
        setMessages([])
        setStreamBuffer('')
      }
      refreshList()
    } catch (e: any) {
      setResult({ name: '', definition: {} as any, code: '', validation: { valid: false, errors: [e.message] }, message: e.message })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
  if (!agentName) return

  const loadSelectedAgent = async () => {
    try {
      const decodedName = decodeURIComponent(agentName)

      const data = await getAgent(decodedName)

      setSelectedAgent(data)

      setResult(null)

      setIsCreating(false)

      setBuilderMessages([])

      setMessages([])

      setStreamBuffer('')

      setTab('chat')
    } catch (error) {
      console.error('Error loading agent:', error)
    }
  }

  loadSelectedAgent()
}, [agentName])

  const handleSelectAgent = async (name: string) => {
    try {
      const data = await getAgent(name)
      setSelectedAgent(data)
      setResult(null)
      setIsCreating(false)
      setBuilderMessages([])
      setMessages([])
      setStreamBuffer('')
    } catch { }
  }

  const handleDelete = async (name: string) => {
    if (!confirm(`هل تريد حذف الوكيل «${name}»؟`)) return
    await deleteAgent(name)
    setSelectedAgent(null)
    setResult(null)
    setIsCreating(false)
    setBuilderMessages([])
    setMessages([])
    refreshList()
  }

  // ── دردشة بيئة الاختبار ──
  const currentAgentName = result?.name || selectedAgent?.name || ''
  const currentInstructions = (() => {
    if (selectedAgent?.definition) {
      return (selectedAgent.definition as Record<string, unknown>).instructions as string || ''
    }
    return ''
  })()

  const handleSend = async () => {
    if (!chatInput.trim() || !currentAgentName || streaming) return
    const userMsg: ChatMessage = { role: 'user', content: chatInput.trim() }
    const newMessages = [...messages, userMsg]
    setMessages(newMessages)
    setChatInput('')
    setStreaming(true)
    setStreamBuffer('')
    let fullResponse = ''
    await runAgent(
      currentAgentName,
      userMsg.content,
      newMessages,
      (token) => { fullResponse += token; setStreamBuffer(fullResponse) },
      (content) => { setMessages(prev => [...prev, { role: 'assistant', content }]); setStreamBuffer(''); setStreaming(false) },
      (error) => { setMessages(prev => [...prev, { role: 'assistant', content: `خطأ: ${error}` }]); setStreamBuffer(''); setStreaming(false) },
    )
  }

  const activeName = result?.name || selectedAgent?.name || ''

  // مكوّن فرعي لأزرار تبويب لوحة النتائج
  // const ResultTabButtons = () => (
  //   <div className="devui-tabs tabs" style={{ borderBottom: 'none', marginBottom: 0 }}>
  //     <button className={`tab ${resultView === 'yaml' ? 'active' : ''}`} onClick={() => setResultView('yaml')}>
  //       YAML
  //     </button>
  //     <button className={`tab ${resultView === 'code' ? 'active' : ''}`} onClick={() => setResultView('code')}>
  //       Python
  //     </button>
  //   </div>
  // )

  // ── تحديد وضع عرض لوحة الوسط ──
  const showBuilderChat = tab === 'chat' && isCreating
  const hasAgent = !!(result || selectedAgent)
  const showEmpty = tab === 'chat' && !isCreating && !hasAgent

  return (
    <div className="devui-shell">
      {/* ── شريط الأدوات العلوي ── */}
      <div className="devui-toolbar">
        <div className="devui-toolbar-title">🤖 الوكلاء</div>
        <div className="devui-tabs tabs" style={{ borderBottom: 'none', marginBottom: 0, flexShrink: 0 }}>
          <button className={`tab ${tab === 'chat' ? 'active' : ''}`} onClick={() => setTab('chat')}>
            💬 اللغة الطبيعية
          </button>
          <button className={`tab ${tab === 'manual' ? 'active' : ''}`} onClick={() => setTab('manual')}>
            يدوي
          </button>
        </div>
      </div>

      {/* ── جسم الصفحة بثلاثة أعمدة ── */}
      <div className="devui-body">


        {/* الوسط: دردشة بناء الوكيل + عرض الكود / النموذج اليدوي */}
<div className="devui-center" ref={centerRef}>

  {showBuilderChat && (
    <BuilderChat
      key={chatKey}
      type="agent"
      initialMessages={[
        {
          role: 'system',
          content:
            selectedAgent || result?.name
              ? 'تم استدعاء وضع التعديل. ما التغييرات التي تريد إجراؤها؟'
              : 'سيتم إنشاء وكيل ذكي جديد. ما نوع الوكيل الذي تريد إنشاءه؟',
        }
      ]}
      currentName={
        result?.name ||
        selectedAgent?.name
      }
      onClose={() => setIsCreating(false)}
      onSuccess={(agentData) => {
        setResult(agentData)

        setSelectedAgent({
          name: agentData.name,
          definition: agentData.definition,
          code: agentData.code,
        })

        refreshList()
      }}
    />
  )}

  {/* فتح الدردشة مع الوكيل */}
  {selectedAgent && !isCreating && (
    <AgentChat
      agentName={selectedAgent.name}
    />
  )}

</div>

        {/* اليمين: ساحة اختبار الدردشة */}
        {/* <div className="devui-right">
          <div className="devui-right-header">
            <span className="devui-right-header-title">
              🎮 {activeName ? activeName : 'ساحة الاختبار'}
            </span>

            {activeName && messages.length > 0 && (
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => {
                  setMessages([])
                  setStreamBuffer('')
                }}
              >
                🗑️
              </button>
            )}
          </div>

          {activeName ? (
            <>
              {currentInstructions && messages.length === 0 && !streaming && (
                <div style={{ padding: '0 12px', marginTop: 8, flexShrink: 0 }}>
                  <div className="devui-system-prompt">
                    <div className="devui-system-prompt-label">موجه النظام</div>

                    {currentInstructions.length > 200
                      ? currentInstructions.slice(0, 200) + '...'
                      : currentInstructions}
                  </div>
                </div>
              )}

              <div className="devui-messages">
                {messages.length === 0 && !streaming && (
                  <div className="devui-empty">
                    <span style={{ fontSize: 12 }}>
                      أرسل رسالة لاختبار الوكيل
                    </span>
                  </div>
                )}

                {messages.map((msg, i) => (
                  <div
                    key={i}
                    className={`playground-msg playground-msg-${msg.role}`}
                  >
                    <div className="playground-msg-role">
                      {msg.role === 'user'
                        ? '👤 أنت'
                        : `🤖 ${activeName}`}
                    </div>

                    <div className="playground-msg-content">
                      {msg.content}
                    </div>
                  </div>
                ))}

                {streaming && streamBuffer && (
                  <div className="playground-msg playground-msg-assistant">
                    <div className="playground-msg-role">
                      🤖 {activeName}
                    </div>

                    <div className="playground-msg-content">
                      {streamBuffer}
                      <span className="playground-cursor" />
                    </div>
                  </div>
                )}

                {streaming && !streamBuffer && (
                  <div className="playground-msg playground-msg-assistant">
                    <div className="playground-msg-role">
                      🤖 {activeName}
                    </div>

                    <div className="playground-msg-content">
                      <span className="playground-thinking">
                        جارٍ التفكير...
                      </span>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              <div className="devui-right-footer">
                <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end' }}>
                  <textarea
                    className="form-input chat-textarea"
                    placeholder="أدخل رسالة..."
                    value={chatInput}
                    onChange={e => setChatInput(e.target.value)}
                    onKeyDown={e => {
                      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                        e.preventDefault()
                        handleSend()
                      }
                    }}
                    disabled={streaming}
                    rows={2}
                    style={{ flex: 1, padding: '8px 12px', fontSize: 13 }}
                  />

                  <button
                    className="btn btn-primary btn-sm"
                    onClick={handleSend}
                    disabled={streaming || !chatInput.trim()}
                    style={{ alignSelf: 'flex-end', marginBottom: 2 }}
                  >
                    {streaming ? <span className="spinner" /> : 'إرسال'}
                  </button>
                </div>

                <div className="chat-textarea-hint">
                  Ctrl+Enter للإرسال
                </div>
              </div>
            </>
          ) : (
            <div className="devui-empty">
              <div className="devui-empty-icon">💬</div>
              <span>اختر وكيلًا لبدء الدردشة</span>
            </div>
          )}
        </div> */}

      </div>
    </div>
  )
}

// نهاية AgentBuilderPage