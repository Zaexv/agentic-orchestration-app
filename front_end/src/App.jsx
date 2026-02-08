import { useState, useEffect } from 'react'
import { Bot, Send, Plus, MessageSquare, Loader2, ChevronDown, ChevronUp, Briefcase, Mail, Brain, Scale, Zap } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import './App.css'

const AGENTS = [
  {
    id: 'professional',
    name: 'Professional',
    icon: Briefcase,
    color: '#4f9eff',
    description: 'Technical expertise and work-related queries',
    specialties: ['Programming', 'Architecture', 'Problem-solving']
  },
  {
    id: 'communication',
    name: 'Communication',
    icon: Mail,
    color: '#00d9ff',
    description: 'Writing style, tone, and communication patterns',
    specialties: ['Email drafting', 'Content review', 'Tone adjustment']
  },
  {
    id: 'knowledge',
    name: 'Knowledge',
    icon: Brain,
    color: '#a78bfa',
    description: 'Personal knowledge base, facts, and memories',
    specialties: ['Personal info', 'Preferences', 'Experiences']
  },
  {
    id: 'decision',
    name: 'Decision',
    icon: Scale,
    color: '#f472b6',
    description: 'Decision-making support and trade-off analysis',
    specialties: ['Recommendations', 'Trade-offs', 'Evaluations']
  },
  {
    id: 'general',
    name: 'General',
    icon: Bot,
    color: '#8b92b0',
    description: 'General queries and fallback assistance',
    specialties: ['General chat', 'Misc queries', 'Default handler']
  }
]

function App() {
  const [conversations, setConversations] = useState([])
  const [currentConvId, setCurrentConvId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [thinkingSteps, setThinkingSteps] = useState([])
  const [showAgents, setShowAgents] = useState(false)

  useEffect(() => {
    loadConversations()
  }, [])

  const loadConversations = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/conversations?user_id=user')
      const data = await response.json()
      setConversations(data.conversations || [])
    } catch (error) {
      console.error('Error loading conversations:', error)
    }
  }

  const createNewChat = () => {
    setCurrentConvId(null)
    setMessages([])
    setThinkingSteps([])
  }

  const loadConversation = async (convId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/conversations/${convId}/messages?user_id=user`)
      const data = await response.json()
      
      if (data.messages) {
        setCurrentConvId(convId)
        setMessages(data.messages.map(msg => ({
          role: msg.role,
          content: msg.content,
          agent: msg.agent,
          confidence: msg.confidence
        })))
        setThinkingSteps([])
      }
    } catch (error) {
      console.error('Error loading conversation:', error)
      alert('Failed to load conversation')
    }
  }

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)
    setThinkingSteps([])

    try {
      setThinkingSteps([{ step: 'Analyzing query...', done: false }])
      
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          user_id: 'user',
          conversation_id: currentConvId
        })
      })

      const data = await response.json()
      
      const steps = [
        { step: '🎯 Query Analysis', detail: 'Analyzed user intent and context', done: true },
        { step: `🤖 Agent Selection: ${data.agent_used}`, detail: data.routing_history[0]?.reasoning || 'Selected best agent', done: true },
        { step: `📊 Confidence: ${(data.confidence * 100).toFixed(0)}%`, detail: 'Routing confidence score', done: true },
        { step: `⚡ Processing Time: ${data.processing_time_ms?.toFixed(0)}ms`, detail: 'Total execution time', done: true },
      ]
      
      setThinkingSteps(steps)

      setTimeout(() => {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.response,
          agent: data.agent_used,
          confidence: data.confidence,
          trace: {
            reasoning: data.routing_history[0]?.reasoning,
            processingTime: data.processing_time_ms,
            iterations: data.iterations,
            routingHistory: data.routing_history
          }
        }])
        setThinkingSteps([])
        
        if (data.conversation_id && !currentConvId) {
          setCurrentConvId(data.conversation_id)
          loadConversations()
        }
      }, 1000)

    } catch (error) {
      console.error('Error:', error)
      setThinkingSteps([{ step: '❌ Error occurred', detail: error.message, done: false }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <button className="new-chat-btn" onClick={createNewChat}>
            <Plus size={20} />
            <span>New Chat</span>
          </button>
        </div>
        
        <div className="conversations-list">
          {conversations.length === 0 ? (
            <div className="no-conversations">
              <p>No conversations yet</p>
            </div>
          ) : (
            conversations.map(conv => (
              <button
                key={conv.id}
                className={`conversation-item ${currentConvId === conv.id ? 'active' : ''}`}
                onClick={() => loadConversation(conv.id)}
              >
                <MessageSquare size={16} />
                <span>{conv.title}</span>
              </button>
            ))
          )}
        </div>

        {/* Agents Panel */}
        <div className="sidebar-footer">
          <button 
            className="agents-toggle"
            onClick={() => setShowAgents(!showAgents)}
          >
            <Zap size={16} />
            <span>{AGENTS.length} Agents Available</span>
            {showAgents ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
          
          {showAgents && (
            <div className="agents-mini-list">
              {AGENTS.map(agent => {
                const Icon = agent.icon
                return (
                  <div key={agent.id} className="agent-mini-card">
                    <div 
                      className="agent-mini-icon"
                      style={{ backgroundColor: `${agent.color}20`, color: agent.color }}
                    >
                      <Icon size={16} />
                    </div>
                    <div className="agent-mini-info">
                      <div className="agent-mini-name">{agent.name}</div>
                      <div className="agent-mini-desc">{agent.specialties[0]}</div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </aside>

      {/* Main Chat */}
      <div className="main-content">
        {/* Header */}
        <header className="header">
          <div className="logo">
            <Bot size={24} />
            <span>AI Digital Twin</span>
          </div>
        </header>

        {/* Chat Area */}
        <div className="chat-container">
          {messages.length === 0 ? (
            <div className="empty-state">
              <Bot size={48} className="empty-icon" />
              <h2>AI Digital Twin System</h2>
              <p>Powered by {AGENTS.length} specialized agents</p>
              
              {/* Agent Cards */}
              <div className="agents-grid">
                {AGENTS.map(agent => {
                  const Icon = agent.icon
                  return (
                    <div key={agent.id} className="agent-card">
                      <div 
                        className="agent-icon"
                        style={{ backgroundColor: `${agent.color}20`, color: agent.color }}
                      >
                        <Icon size={28} />
                      </div>
                      <h3 className="agent-name">{agent.name}</h3>
                      <p className="agent-description">{agent.description}</p>
                      <div className="agent-specialties">
                        {agent.specialties.map((spec, i) => (
                          <span key={i} className="specialty-tag">{spec}</span>
                        ))}
                      </div>
                    </div>
                  )
                })}
              </div>

              <p className="start-hint">Type a message below to get started</p>
            </div>
          ) : (
            <div className="messages">
              {messages.map((msg, idx) => (
                <Message key={idx} message={msg} />
              ))}
              
              {thinkingSteps.length > 0 && (
                <div className="thinking-process">
                  <div className="thinking-header">
                    <Loader2 size={16} className="spin" />
                    <span>AI Thinking Process</span>
                  </div>
                  {thinkingSteps.map((step, idx) => (
                    <div key={idx} className={`thinking-step ${step.done ? 'done' : ''}`}>
                      <div className="step-main">
                        <span className="step-indicator">
                          {step.done ? '✓' : '○'}
                        </span>
                        <span className="step-text">{step.step}</span>
                      </div>
                      {step.detail && (
                        <div className="step-detail">{step.detail}</div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Input */}
        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Type your message..."
            disabled={loading}
          />
          <button onClick={sendMessage} disabled={loading || !input.trim()}>
            {loading ? <Loader2 size={20} className="spin" /> : <Send size={20} />}
          </button>
        </div>
      </div>
    </div>
  )
}

// Message Component
function Message({ message }) {
  const [showTrace, setShowTrace] = useState(false)

  if (message.role === 'user') {
    return (
      <div className="message user">
        <div className="message-content">{message.content}</div>
      </div>
    )
  }

  return (
    <div className="message assistant">
      <div className="message-header">
        {message.agent && (
          <div className="agent-badge">{message.agent}</div>
        )}
        {message.confidence && (
          <div className="confidence-badge">
            {(message.confidence * 100).toFixed(0)}% confident
          </div>
        )}
        {message.trace && (
          <button 
            className="trace-toggle"
            onClick={() => setShowTrace(!showTrace)}
          >
            {showTrace ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            <span>View Trace</span>
          </button>
        )}
      </div>
      
      <div className="message-content">
        <ReactMarkdown
          components={{
            code({node, inline, className, children, ...props}) {
              const match = /language-(\w+)/.exec(className || '')
              return !inline && match ? (
                <SyntaxHighlighter
                  style={vscDarkPlus}
                  language={match[1]}
                  PreTag="div"
                  customStyle={{
                    margin: '1rem 0',
                    borderRadius: '8px',
                    fontSize: '0.875rem'
                  }}
                  {...props}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              ) : (
                <code className="inline-code" {...props}>
                  {children}
                </code>
              )
            },
            p: ({children}) => <p className="markdown-p">{children}</p>,
            ul: ({children}) => <ul className="markdown-ul">{children}</ul>,
            ol: ({children}) => <ol className="markdown-ol">{children}</ol>,
            li: ({children}) => <li className="markdown-li">{children}</li>,
            h1: ({children}) => <h1 className="markdown-h1">{children}</h1>,
            h2: ({children}) => <h2 className="markdown-h2">{children}</h2>,
            h3: ({children}) => <h3 className="markdown-h3">{children}</h3>,
          }}
        >
          {message.content}
        </ReactMarkdown>
      </div>

      {showTrace && message.trace && (
        <div className="trace-panel">
          <div className="trace-section">
            <div className="trace-label">🧠 Reasoning</div>
            <div className="trace-value">{message.trace.reasoning}</div>
          </div>
          {message.trace.processingTime && (
            <div className="trace-section">
              <div className="trace-label">⚡ Processing Time</div>
              <div className="trace-value">{message.trace.processingTime.toFixed(2)}ms</div>
            </div>
          )}
          {message.trace.iterations && (
            <div className="trace-section">
              <div className="trace-label">🔄 Iterations</div>
              <div className="trace-value">{message.trace.iterations}</div>
            </div>
          )}
          {message.trace.routingHistory && message.trace.routingHistory.length > 0 && (
            <div className="trace-section">
              <div className="trace-label">📋 Routing History</div>
              <div className="trace-routing">
                {message.trace.routingHistory.map((r, i) => (
                  <div key={i} className="routing-item">
                    <span className="routing-agent">{r.agent_name}</span>
                    <span className="routing-confidence">{(r.confidence * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default App
