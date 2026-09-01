import React, { useState, useRef, useEffect } from 'react'
import {
  type CopilotQuestion,
  type CopilotQuestionOption,
  sendCopilotMessage,
  createWorkflowFromPrompt,
  editWorkflow,
  type AgentCreateResponse,
  type WorkflowCreateResponse
} from '../api/client'

// يجب الانتباه إلى أننا قمنا بجلب AssistantMessage من صفحة AgentBuilderPage لاستخدامها هنا
import { AssistantMessage } from '../pages/AgentBuilderPage'

export interface BuilderMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  questions?: CopilotQuestion[]
  agentResult?: any | null
  workflowResult?: any | null
}

interface BuilderChatProps {
  // هل الدردشة حالياً لوكيل أم لسير عمل؟
  type: 'agent' | 'workflow'
  
  // الرسائل الافتتاحية للمحادثة
  initialMessages?: BuilderMessage[]
  
  // هل نحن في وضع الإنشاء أم التعديل؟
  currentName?: string | null
  
  // الإجراءات
  onClose: () => void
  onSuccess: (result: any) => void // دالة لبث النتيجة (الوكيل أو السير) عند اكتماله
}

export default function BuilderChat({
  type,
  initialMessages = [],
  currentName,
  onClose,
  onSuccess
}: BuilderChatProps) {
  const [messages, setMessages] = useState<BuilderMessage[]>(initialMessages)
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const endRef = useRef<HTMLDivElement>(null)

  // النزول التلقائي للأسفل
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // دالة الإرسال الرئيسية (تختلف بناء على نوعها إذا كانت لوكيل أم لورك فلو)
  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMsg: BuilderMessage = {
      role: 'user',
      content: input.trim(),
    }

    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      if (type === 'agent') {
        const res = await sendCopilotMessage(userMsg.content)
        handleCopilotResponse(res)
      } else {
        let res: WorkflowCreateResponse
        if (!currentName) {
          res = await createWorkflowFromPrompt(userMsg.content)
        } else {
          res = await editWorkflow(currentName, userMsg.content)
        }
        handleWorkflowResponse(res)
      }
    } catch (e: any) {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: `❌ حدث خطأ: ${e.message}` },
      ])
    } finally {
      setLoading(false)
    }
  }

  // دالة استجابة الكوبايلوت الخاصة بالوكلاء (Agents)
  const handleCopilotResponse = (res: any) => {
    const assistantMsg: BuilderMessage = {
      role: 'assistant',
      content: res.message,
      questions: res.questions ?? [],
    }

    setMessages(prev => [...prev, assistantMsg])

    // إذا كانت النتيجة جاهزة ونجح بناء الوكيل
    if (res.status === 'building' && res.agent) {
      onSuccess(res.agent) 
    }
  }

  // دالة استجابة بناء مسارات العمل (Workflows)
  const handleWorkflowResponse = (res: WorkflowCreateResponse) => {
    const action = currentName ? 'تحديث' : 'إنشاء'
    const assistantMsg: BuilderMessage = {
      role: 'assistant',
      content: res.validation.valid
        ? `✅ تم ${action} سير العمل «${res.name}» بنجاح.\n\nيمكنك الاستمرار في تعديله من خلال المحادثة. مثال:\n• «أضف خطوة لتسجيل السجلات»\n• «غيّر تفرع الشروط»`
        : `⚠️ تم ${action} سير العمل «${res.name}»، ولكن توجد أخطاء في التحقق:\n\n${res.validation.errors.join('\n')}`,
      workflowResult: res,
    }
    setMessages(prev => [...prev, assistantMsg])
    onSuccess(res)
  }

  // دالة اختيار إجابة جاهزة من الكوبايلوت (للـ Agents)
  const handleCopilotOptionSelect = async (
    question: CopilotQuestion,
    option: CopilotQuestionOption
  ) => {
    if (loading) return

    const userMsg: BuilderMessage = {
      role: 'user',
      content: option.label,
    }

    setMessages(prev => [...prev, userMsg])
    setLoading(true)

    try {
      const res = await sendCopilotMessage(option.label)
      handleCopilotResponse(res)
    } catch (e: any) {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: `❌ حدث خطأ: ${e.message}` },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="devui-center-full">
      <div className="builder-chat-header">
        <span className="builder-chat-header-title">
          💬 {type === 'agent' ? 'دردشة إنشاء الوكيل' : 'محادثة الدردشة'}
        </span>
        <button className="btn btn-secondary btn-sm" onClick={onClose}>
          ✕ إغلاق
        </button>
      </div>

      <div className="builder-chat-messages">
        {messages.map((msg, i) => {
          const isLast = i === messages.length - 1;

          if (msg.role === 'assistant') {
            if (type === 'agent') {
              return (
                <AssistantMessage
                  key={i}
                  msg={msg}
                  isLast={isLast}
                  onOptionSelect={handleCopilotOptionSelect}
                  loading={loading}
                />
              )
            } else {
              return (
                <div key={i} className="builder-msg builder-msg-assistant">
                  <div className="builder-msg-role">🤖 الذكاء الاصطناعي</div>
                  <div className="builder-msg-content">{msg.content}</div>
                </div>
              )
            }
          }

          return (
            <div key={i} className={`builder-msg builder-msg-${msg.role}`}>
              <div className="builder-msg-role">
                {msg.role === 'user' && '👤 أنت'}
                {msg.role === 'system' && '🔧 النظام'}
              </div>
              <div className="builder-msg-content">{msg.content}</div>
            </div>
          );
        })}

        {loading && (
          <div className="builder-msg builder-msg-assistant">
            <div className="builder-msg-role">🤖 الذكاء الاصطناعي</div>
            <div className="builder-msg-content">
              <span className="playground-thinking">جارٍ العمل...</span>
            </div>
          </div>
        )}

        <div ref={endRef} />
      </div>

      <div className="builder-chat-footer">
        <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end' }}>
          <textarea
            className="form-input chat-textarea"
            placeholder={
              currentName
                ? 'أدخل التعديلات واضغط لإرسال...'
                : 'أدخل الوصف...'
            }
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault()
                handleSend()
              }
            }}
            disabled={loading}
            rows={2}
            style={{ flex: 1, padding: '10px 14px', fontSize: 13 }}
          />

          <button
            className="btn btn-primary btn-sm"
            onClick={handleSend}
            disabled={loading || !input.trim()}
            style={{ alignSelf: 'flex-end', marginBottom: 2 }}
          >
            {loading ? <span className="spinner" /> : 'إرسال'}
          </button>
        </div>

        <div className="chat-textarea-hint">Ctrl+Enter للإرسال</div>
      </div>
    </div>
  )
}