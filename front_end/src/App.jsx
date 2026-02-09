import { useState, useEffect } from 'react'
import { Bot, Send, Plus, MessageSquare, Loader2, ChevronDown, ChevronUp, Briefcase, Mail, Brain, Scale, Zap, Network } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { Agent3D } from './components/Agent3D'
import { Logo3D } from './components/Logo3D'
import 'katex/dist/katex.min.css'
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

const ORCHESTRATION_PATTERNS = [
  {
    id: 'router',
    name: 'Router',
    description: 'Routes each query to the most appropriate specialized agent',
    icon: Network
  },
  // Future patterns can be added here:
  // { id: 'sequential', name: 'Sequential', description: 'Agents work in sequence' },
  // { id: 'hierarchical', name: 'Hierarchical', description: 'Manager agent delegates to sub-agents' },
]

function App() {
  const [conversations, setConversations] = useState([])
  const [currentConvId, setCurrentConvId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [thinkingSteps, setThinkingSteps] = useState([])
  const [showAgents, setShowAgents] = useState(false)
  const [orchestrationPattern, setOrchestrationPattern] = useState('router')

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
      
      // Build thinking steps from iteration details
      const steps = [
        { step: '🎯 Query Analysis', detail: 'Analyzed user intent and context', done: true },
        { step: `🤖 Final Agent: ${data.agent_used}`, detail: `${data.iterations} iteration(s) completed`, done: true },
        { step: `📊 Confidence: ${(data.confidence * 100).toFixed(0)}%`, detail: 'Routing confidence score', done: true },
        { step: `⚡ Processing Time: ${data.processing_time_ms?.toFixed(0)}ms`, detail: 'Total execution time', done: true },
      ]
      
      // Add iteration details if present
      if (data.iteration_details && data.iteration_details.length > 0) {
        // Group by iteration to show the flow
        const iterations = {}
        data.iteration_details.forEach(d => {
          if (!iterations[d.iteration]) iterations[d.iteration] = []
          iterations[d.iteration].push(d)
        })
        
        // Build a summary of the iteration flow
        const iterationSteps = Object.entries(iterations).map(([iter, details]) => {
          const routing = details.find(d => d.action.startsWith('Routed to'))
          const agent = routing?.action.replace('Routed to ', '') || 'unknown'
          const conf = routing?.confidence ? `${(routing.confidence * 100).toFixed(0)}%` : ''
          return `Iter ${iter}: ${agent} (${conf})`
        })
        
        if (iterationSteps.length > 1) {
          steps.splice(1, 0, { 
            step: '🔄 Multi-Iteration Processing', 
            detail: iterationSteps.join(' → '), 
            done: true 
          })
        }
      }
      
      setThinkingSteps(steps)

      setTimeout(() => {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.response,
          agent: data.agent_used,
          confidence: data.confidence,
          trace: {
            reasoning: data.iteration_details?.[0]?.reasoning || 'No details',
            processingTime: data.processing_time_ms,
            iterations: data.iterations,
            iterationDetails: data.iteration_details || []
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

  const currentPattern = ORCHESTRATION_PATTERNS.find(p => p.id === orchestrationPattern)
  const PatternIcon = currentPattern?.icon || Network

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
            <Logo3D size={40} />
            <div className="logo-text">
              <span className="logo-title">AI Digital Twin</span>
              <div className="orchestration-selector">
                <PatternIcon size={14} />
                <select 
                  value={orchestrationPattern}
                  onChange={(e) => setOrchestrationPattern(e.target.value)}
                  className="pattern-select"
                >
                  {ORCHESTRATION_PATTERNS.map(pattern => (
                    <option key={pattern.id} value={pattern.id}>
                      {pattern.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <div className="chat-container">
          {messages.length === 0 ? (
            <div className="empty-state">
              <div className="logo-3d-container">
                <Logo3D size={80} />
              </div>
              <h2>AI Digital Twin System</h2>
              <div className="system-info">
                <div className="info-badge">
                  <PatternIcon size={14} />
                  <span>{currentPattern?.name} Orchestration</span>
                </div>
                <div className="info-badge">
                  <Zap size={14} />
                  <span>{AGENTS.length} Specialized Agents</span>
                </div>
              </div>
              <p className="pattern-description">{currentPattern?.description}</p>
              
              {/* Agent Cards */}
              <div className="agents-grid">
                {AGENTS.map(agent => (
                  <div key={agent.id} className="agent-card">
                    <div className="agent-3d-container">
                      <Agent3D agentId={agent.id} size={100} />
                    </div>
                    <h3 className="agent-name">{agent.name}</h3>
                    <p className="agent-description">{agent.description}</p>
                    <div className="agent-specialties">
                      {agent.specialties.map((spec, i) => (
                        <span key={i} className="specialty-tag">{spec}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              <p className="start-hint">Type a message below to start chatting with your AI agents</p>
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

// Message Component with 3D Agent Face
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
    <div className="message-wrapper assistant">
      {/* 3D Agent Face */}
      {message.agent && (
        <div className="message-agent-face">
          <Agent3D agentId={message.agent} size={70} />
        </div>
      )}

      {/* Message Content */}
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
            remarkPlugins={[remarkGfm, remarkMath]}
            rehypePlugins={[rehypeKatex]}
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
              table: ({children}) => (
                <div className="table-wrapper">
                  <table className="markdown-table">{children}</table>
                </div>
              ),
              thead: ({children}) => <thead className="markdown-thead">{children}</thead>,
              tbody: ({children}) => <tbody className="markdown-tbody">{children}</tbody>,
              tr: ({children}) => <tr className="markdown-tr">{children}</tr>,
              th: ({children}) => <th className="markdown-th">{children}</th>,
              td: ({children}) => <td className="markdown-td">{children}</td>,
              p: ({children}) => <p className="markdown-p">{children}</p>,
              ul: ({children}) => <ul className="markdown-ul">{children}</ul>,
              ol: ({children}) => <ol className="markdown-ol">{children}</ol>,
              li: ({children}) => <li className="markdown-li">{children}</li>,
              h1: ({children}) => <h1 className="markdown-h1">{children}</h1>,
              h2: ({children}) => <h2 className="markdown-h2">{children}</h2>,
              h3: ({children}) => <h3 className="markdown-h3">{children}</h3>,
              blockquote: ({children}) => <blockquote className="markdown-blockquote">{children}</blockquote>,
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>

        {showTrace && message.trace && (
          <div className="trace-panel">
            {message.trace.iterationDetails && message.trace.iterationDetails.length > 0 && (
              <div className="trace-section trace-section-main">
                <div className="trace-label">🔄 Iteration Log</div>
                <div className="trace-iterations">
                  {message.trace.iterationDetails.map((detail, i) => (
                    <div key={i} className="iteration-item">
                      <div className="iteration-header">
                        <span className="iteration-number">#{detail.iteration}</span>
                        <span className="iteration-agent">{detail.agent}</span>
                        {detail.confidence > 0 && (
                          <span className="iteration-confidence">{(detail.confidence * 100).toFixed(0)}%</span>
                        )}
                      </div>
                      <div className="iteration-action">{detail.action}</div>
                      {detail.reasoning && (
                        <div className="iteration-reasoning">{detail.reasoning}</div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            <div className="trace-metadata">
              {message.trace.iterations && (
                <div className="trace-section trace-section-compact">
                  <div className="trace-label">🔁 Total Iterations</div>
                  <div className="trace-value">{message.trace.iterations}</div>
                </div>
              )}
              {message.trace.processingTime && (
                <div className="trace-section trace-section-compact">
                  <div className="trace-label">⚡ Processing Time</div>
                  <div className="trace-value">{message.trace.processingTime.toFixed(2)}ms</div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
