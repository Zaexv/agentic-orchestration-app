# System Architecture

This document describes the architecture of the AI Digital Twin Agent Orchestration System.

## Table of Contents
- [High-Level Overview](#high-level-overview)
- [Component Architecture](#component-architecture)
- [Agent Orchestration Flow](#agent-orchestration-flow)
- [Multi-Iteration Processing](#multi-iteration-processing)
- [Shared Memory System](#shared-memory-system)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)

## High-Level Overview

The system is a multi-agent AI orchestration platform that routes user queries to specialized agents, supports multi-iteration refinement, and maintains shared conversation memory.

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React UI<br/>3D Agent Visualization]
    end
    
    subgraph "API Layer"
        API[FastAPI Server<br/>Port 8000]
    end
    
    subgraph "Orchestration Layer"
        Router[Router Agent<br/>LLM-based routing]
        Workflow[LangGraph Workflow<br/>Multi-iteration logic]
    end
    
    subgraph "Agent Layer"
        Professional[Professional Agent]
        Communication[Communication Agent]
        Knowledge[Knowledge Agent]
        Decision[Decision Agent]
        General[General Agent]
    end
    
    subgraph "Storage Layer"
        SQLite[(SQLite DB<br/>Conversations)]
        ChromaDB[(ChromaDB<br/>Vector Store)]
    end
    
    UI -->|HTTP Request| API
    API -->|Invoke| Workflow
    Workflow -->|Route| Router
    Router -->|Select Agent| Professional
    Router -->|Select Agent| Communication
    Router -->|Select Agent| Knowledge
    Router -->|Select Agent| Decision
    Router -->|Select Agent| General
    Professional -->|Query RAG| ChromaDB
    Communication -->|Query RAG| ChromaDB
    Knowledge -->|Query RAG| ChromaDB
    Decision -->|Query RAG| ChromaDB
    General -->|Query RAG| ChromaDB
    API -->|Persist| SQLite
    Workflow -->|Iteration Control| Router
```

## Component Architecture

### Frontend (React + Three.js)

```mermaid
graph LR
    subgraph "React Application"
        App[App.jsx<br/>Main Component]
        Agent3D[Agent3D.jsx<br/>3D Face Renderer]
        Logo3D[Logo3D.jsx<br/>Animated Logo]
        
        App --> Agent3D
        App --> Logo3D
    end
    
    subgraph "Features"
        Chat[Chat Interface]
        Thinking[Thinking Steps]
        Trace[Iteration Trace]
        Conv[Conversation Mgmt]
    end
    
    App --> Chat
    App --> Thinking
    App --> Trace
    App --> Conv
```

**Key Features:**
- Real-time chat interface with markdown support
- 3D cartoon faces for each agent (Three.js)
- Thinking process visualization
- Detailed iteration trace panel
- Conversation history management

### Backend (FastAPI + LangGraph)

```mermaid
graph TB
    subgraph "API Endpoints"
        ChatAPI[/api/chat<br/>Main endpoint]
        GraphAPI[/api/chat/graph<br/>Direct workflow]
        ConvAPI[/api/conversations<br/>History mgmt]
    end
    
    subgraph "Core Services"
        Workflow[LangGraph Workflow]
        Router[Router Service]
        Agents[Agent Services]
        RAG[RAG Service]
    end
    
    subgraph "Data Access"
        DB[Database Layer]
        Vector[Vector Store]
    end
    
    ChatAPI --> Workflow
    GraphAPI --> Workflow
    ConvAPI --> DB
    
    Workflow --> Router
    Workflow --> Agents
    
    Router --> RAG
    Agents --> RAG
    
    RAG --> Vector
    ChatAPI --> DB
```

## Agent Orchestration Flow

### Router Orchestration Pattern

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Router
    participant Agent
    participant LLM
    participant RAG
    
    User->>API: Send Query
    API->>Router: Route Query
    Router->>LLM: Analyze Query + Context
    LLM-->>Router: Agent Selection + Confidence
    Router->>Agent: Execute with selected agent
    Agent->>RAG: Retrieve relevant docs
    RAG-->>Agent: Return documents
    Agent->>LLM: Generate response with context
    LLM-->>Agent: Response
    Agent-->>API: Return result
    API->>User: Send response
```

### Agent Selection Logic

```mermaid
flowchart TD
    Start[Query Received] --> LLM[LLM Analysis]
    LLM --> Keywords[Keyword Fallback]
    
    LLM --> Prof{Professional<br/>Keywords?}
    LLM --> Comm{Communication<br/>Keywords?}
    LLM --> Know{Knowledge<br/>Keywords?}
    LLM --> Dec{Decision<br/>Keywords?}
    LLM --> Gen[General<br/>Fallback]
    
    Prof -->|Yes| ProfAgent[Professional Agent]
    Comm -->|Yes| CommAgent[Communication Agent]
    Know -->|Yes| KnowAgent[Knowledge Agent]
    Dec -->|Yes| DecAgent[Decision Agent]
    
    ProfAgent --> Execute[Execute Agent]
    CommAgent --> Execute
    KnowAgent --> Execute
    DecAgent --> Execute
    Gen --> Execute
```

## Multi-Iteration Processing

The system supports iterative refinement through confidence-based retry and continuation signals.

```mermaid
stateDiagram-v2
    [*] --> RouterNode: Start
    
    RouterNode --> AgentNode: Route to Agent
    AgentNode --> ShouldContinue: Check Conditions
    
    ShouldContinue --> RouterNode: Continue (Low Confidence)
    ShouldContinue --> RouterNode: Continue (Continuation Signal)
    ShouldContinue --> End: Stop (Max Iterations)
    ShouldContinue --> End: Stop (Conditions Met)
    
    End --> [*]
    
    note right of ShouldContinue
        Continue if:
        - Confidence < 70% (max 2 iter)
        - Continuation keywords (max 3 iter)
        - Not reached max_iterations (5)
    end note
```

### Iteration Logic

```mermaid
flowchart TD
    Start[Agent Response] --> CheckMax{Max Iterations<br/>Reached?}
    CheckMax -->|Yes| End[End]
    CheckMax -->|No| CheckConf{Confidence<br/>< 70%?}
    
    CheckConf -->|Yes| CheckRetry{Iterations<br/>< 2?}
    CheckRetry -->|Yes| Continue[Continue - Retry]
    CheckRetry -->|No| End
    
    CheckConf -->|No| CheckSignal{Contains<br/>Continuation<br/>Keywords?}
    CheckSignal -->|Yes| CheckIter{Iterations<br/>< 3?}
    CheckIter -->|Yes| Continue
    CheckIter -->|No| End
    
    CheckSignal -->|No| End
    
    Continue --> Route[Route to Agent]
    Route --> Start
```

**Continuation Keywords:**
- "let me"
- "I'll also"
- "additionally"
- "furthermore"
- "I can also"
- "would you like"
- "shall i"

## Shared Memory System

All agents share conversation history to maintain context across interactions.

```mermaid
graph TB
    subgraph "Request N"
        QueryN[User Query N]
        RouterN[Router]
        AgentN[Selected Agent]
    end
    
    subgraph "Shared Memory"
        DB[(SQLite<br/>Conversation DB)]
        History[Last 10 Messages]
        Context[Last 5 Messages]
    end
    
    subgraph "Request N+1"
        QueryN1[User Query N+1]
        RouterN1[Router]
        AgentN1[Different Agent]
    end
    
    QueryN --> DB
    DB --> History
    DB --> Context
    
    History --> AgentN
    Context --> RouterN
    
    AgentN --> DB
    
    DB --> History
    DB --> Context
    
    History --> AgentN1
    Context --> RouterN1
```

**Memory Scope:**
- **Router**: Last 5 messages (context for routing decisions)
- **Agents**: Last 10 messages (full recent history)
- **Storage**: All messages persisted in SQLite
- **Cross-agent**: Any agent can see messages from all other agents

## Data Flow

### Complete Request Flow

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant Frontend
    participant API
    participant Workflow
    participant Router
    participant Agent
    participant RAG
    participant DB
    
    User->>Frontend: Type message
    Frontend->>API: POST /api/chat
    API->>DB: Load conversation history
    DB-->>API: Return messages
    API->>Workflow: run_workflow(state)
    
    loop Iteration (up to 5 times)
        Workflow->>Router: router_node()
        Router->>Router: Analyze query + context (last 5 msgs)
        Router-->>Workflow: Agent + Confidence
        
        Workflow->>Agent: agent_node()
        Agent->>RAG: retrieve_documents()
        RAG-->>Agent: Relevant docs
        Agent->>Agent: Generate response (with last 10 msgs)
        Agent-->>Workflow: Response
        
        Workflow->>Workflow: should_continue()
        alt Continue (low confidence or continuation)
            Workflow->>Workflow: Increment iteration
        else Stop
            Workflow->>Workflow: End workflow
        end
    end
    
    Workflow-->>API: Final state + iteration_log
    API->>DB: Save messages
    API-->>Frontend: Response + iteration_details
    Frontend->>User: Display message + trace
```

### RAG Query Flow

```mermaid
flowchart LR
    Query[User Query] --> Router[Router Agent]
    Router --> Agent[Selected Agent]
    
    Agent --> RAG[RAG Retriever]
    RAG --> Domain{Agent Domain}
    
    Domain -->|Professional| ProfDB[(Professional<br/>Collection)]
    Domain -->|Communication| CommDB[(Communication<br/>Collection)]
    Domain -->|Knowledge| KnowDB[(Knowledge<br/>Collection)]
    Domain -->|Decision| DecDB[(Decision<br/>Collection)]
    Domain -->|General| GenDB[(General<br/>Collection)]
    
    RAG --> Shared[(Shared<br/>Collection)]
    
    ProfDB --> Docs[Retrieved Docs]
    CommDB --> Docs
    KnowDB --> Docs
    DecDB --> Docs
    GenDB --> Docs
    Shared --> Docs
    
    Docs --> Agent
    Agent --> LLM[Generate Response]
```

## Technology Stack

### Backend Stack

```mermaid
graph TB
    subgraph "Framework"
        FastAPI[FastAPI 0.104+<br/>Web Framework]
    end
    
    subgraph "Orchestration"
        LangGraph[LangGraph<br/>Workflow Engine]
        LangChain[LangChain<br/>LLM Framework]
    end
    
    subgraph "AI/ML"
        OpenAI[OpenAI API<br/>GPT Models]
        Embeddings[Text Embeddings]
    end
    
    subgraph "Storage"
        SQLite[SQLite<br/>Conversation DB]
        Chroma[ChromaDB<br/>Vector Store]
    end
    
    FastAPI --> LangGraph
    LangGraph --> LangChain
    LangChain --> OpenAI
    LangChain --> Embeddings
    
    FastAPI --> SQLite
    LangChain --> Chroma
```

### Frontend Stack

```mermaid
graph TB
    subgraph "Core"
        React[React 19.2<br/>UI Framework]
        Vite[Vite 7.3<br/>Build Tool]
    end
    
    subgraph "3D Rendering"
        Three[Three.js<br/>WebGL Library]
        R3F[@react-three/fiber<br/>React Renderer]
        Drei[@react-three/drei<br/>Helpers]
    end
    
    subgraph "UI Libraries"
        Markdown[react-markdown<br/>Markdown Renderer]
        Syntax[react-syntax-highlighter<br/>Code Highlighting]
        Icons[lucide-react<br/>Icons]
    end
    
    React --> Three
    React --> R3F
    R3F --> Drei
    React --> Markdown
    React --> Syntax
    React --> Icons
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development"
        DevFront[Frontend<br/>:5173]
        DevBack[Backend<br/>:8000]
    end
    
    subgraph "Production"
        Nginx[Nginx<br/>Reverse Proxy]
        ProdFront[Frontend<br/>Static Files]
        ProdBack[Backend<br/>Gunicorn]
    end
    
    subgraph "Data"
        DataDB[SQLite DB<br/>/data/conversations.db]
        DataVec[ChromaDB<br/>/data/chroma/]
    end
    
    DevFront -.->|Development| DevBack
    
    Nginx -->|Serve| ProdFront
    Nginx -->|Proxy| ProdBack
    
    ProdBack --> DataDB
    ProdBack --> DataVec
    DevBack --> DataDB
    DevBack --> DataVec
```

## Key Design Patterns

### 1. Router Pattern
- Single router agent makes all routing decisions
- LLM-based with keyword fallback for reliability
- Context-aware (uses last 5 messages)

### 2. Multi-Iteration Pattern
- Automatic retry on low confidence
- Continuation on detected signals
- Maximum 5 iterations per request

### 3. Shared Memory Pattern
- All agents see full conversation history
- No memory isolation between agents
- Context-aware routing and responses

### 4. RAG Pattern
- Each agent has isolated document collection
- Shared collection accessible to all
- Retrieval before generation

## Performance Considerations

- **Iteration Limit**: Max 5 iterations prevents infinite loops
- **Context Window**: Last 10 messages keeps token usage manageable
- **Async Processing**: FastAPI handles concurrent requests
- **Vector Search**: ChromaDB provides fast similarity search
- **Caching**: React hot reload for fast development

## Security & Configuration

- Environment variables for API keys
- CORS configuration for frontend
- Database path configuration
- Adjustable iteration limits
- Confidence thresholds

## Future Enhancements

Potential areas for expansion:
- Additional orchestration patterns (sequential, hierarchical)
- Dynamic agent registration
- Multi-modal support (images, audio)
- Real-time streaming responses
- Agent performance metrics
- Custom RAG domains per user
