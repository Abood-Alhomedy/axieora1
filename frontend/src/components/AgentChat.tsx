import { useState, useRef, useEffect } from 'react'
import { runAgent, type ChatMessage } from '../api/client'

interface AgentChatProps {
  agentName: string
}

export default function AgentChat({
  agentName,
}: AgentChatProps) {
  const [messages, setMessages] =
    useState<ChatMessage[]>([])

  const [input, setInput] =
    useState('')

  const [streaming, setStreaming] =
    useState(false)

  const [streamBuffer, setStreamBuffer] =
    useState('')

  const messagesEndRef =
    useRef<HTMLDivElement>(null)

  // تحميل محادثة خاصة بهذا الوكيل
  useEffect(() => {
    const storageKey =
      `agent_chat_${agentName}`

    const savedChat =
      localStorage.getItem(storageKey)

    if (savedChat) {
      try {
        setMessages(JSON.parse(savedChat))
      } catch {
        setMessages([])
      }
    } else {
      setMessages([])
    }

    setStreamBuffer('')
    setInput('')
  }, [agentName])

  // حفظ المحادثة الخاصة بالوكيل
  useEffect(() => {
    if (!agentName) return

    const storageKey =
      `agent_chat_${agentName}`

    localStorage.setItem(
      storageKey,
      JSON.stringify(messages)
    )
  }, [messages, agentName])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: 'smooth',
    })
  }, [messages, streamBuffer])

  const handleSend = async () => {
  if (!input.trim() || streaming) return

  const userMessage: ChatMessage = {
    role: 'user',
    content: input.trim(),
  }

  const newMessages = [
    ...messages,
    userMessage,
  ]

  setMessages(newMessages)

  setInput('')
  setStreaming(true)
  setStreamBuffer('')

  let fullResponse = ''

  await runAgent(
    agentName,
    userMessage.content,
    newMessages,

    (token) => {
      fullResponse += token

      setStreamBuffer(fullResponse)
    },

    (content) => {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content,
        },
      ])

      setStreamBuffer('')
      setStreaming(false)
    },

    (error) => {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: `خطأ: ${error}`,
        },
      ])

      setStreamBuffer('')
      setStreaming(false)
    }
  )
}

  return (
    <div className="agent-chat">

      {/* Header */}
      <div className="agent-chat-header">
        <div>
          <div className="agent-chat-title">
            🤖 {agentName}
          </div>

          <div className="agent-chat-status">
            جاهز للمحادثة
          </div>
        </div>

        {messages.length > 0 && (
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => {
              setMessages([])
              setStreamBuffer('')
            }}
          >
            🗑️ مسح
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="agent-chat-messages">

        {messages.length === 0 && !streaming && (
          <div className="agent-chat-empty">
            <div className="agent-chat-empty-icon">
              💬
            </div>

            <h3>
              ابدأ محادثة جديدة
            </h3>

            <span>
              أرسل رسالة إلى {agentName}
            </span>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`agent-message agent-message-${message.role}`}
          >
            <div className="agent-message-avatar">
              {message.role === 'user'
                ? '👤'
                : '🤖'}
            </div>

            <div className="agent-message-content">
              {message.content}
            </div>
          </div>
        ))}

        {streaming && (
          <div className="agent-message agent-message-assistant">

            <div className="agent-message-avatar">
              🤖
            </div>

            <div className="agent-message-content">

              {streamBuffer ? (
                <>
                  {streamBuffer}
                  <span className="playground-cursor" />
                </>
              ) : (
                <span>
                  جارٍ التفكير...
                </span>
              )}

            </div>
          </div>
        )}

        <div ref={messagesEndRef} />

      </div>

      {/* Input */}
      <div className="agent-chat-input">

        <textarea
          className="form-input chat-textarea"
          placeholder="اكتب رسالتك..."
          value={input}
          disabled={streaming}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => {
            if (
              e.key === 'Enter' &&
              !e.shiftKey
            ) {
              e.preventDefault()

              handleSend()
            }
          }}
        />

        <button
          className="btn btn-primary"
          onClick={handleSend}
          disabled={
            streaming ||
            !input.trim()
          }
        >
          {streaming
            ? '...'
            : 'إرسال'}
        </button>

      </div>

    </div>
  )
}