# 🎨 AI Digital Twin - Frontend

> Modern chat interface with 3D agent avatars built with React 19, Vite, and Three.js

## 🚀 Features

### Visual Design
- **Dark Space Theme** - Clean, modern UI with navy blues and cosmic accents
- **3D Cartoon Avatars** - Unique character faces for each agent using Three.js
- **Animated Logo** - 3D animated logo with sphere and torus design
- **Responsive Layout** - Sidebar navigation with conversation management

### Agent Personalities
Each agent has a distinctive 3D cartoon face that reflects their role:

- 👔 **Professional** - Businessman with glasses and tie
- 😄 **Communication** - Friendly face with big smile and rosy cheeks  
- 📚 **Knowledge** - Wise scholar with floating book
- ⚖️ **Decision** - Split-colored face (pink/purple) with balance scale
- 🤖 **General** - Robot with digital display and antenna

### Chat Features
- **Real-time Thinking Process** - See AI reasoning steps as they happen
- **Expandable Trace Panel** - View detailed routing history and confidence scores
- **Rich Markdown Support** - Code syntax highlighting, tables, lists, blockquotes
- **Conversation History** - Load and continue past conversations
- **Orchestration Selector** - Choose between routing patterns (Router, Sequential, etc.)

### Technical Stack
- **React 19.2.0** - Latest React with modern hooks
- **Vite 7.3.1** - Fast build tool and dev server
- **Three.js** - 3D rendering via @react-three/fiber
- **react-markdown** - GitHub Flavored Markdown with remark-gfm
- **react-syntax-highlighter** - Code blocks with VS Code Dark+ theme
- **Lucide React** - Beautiful icons
- **Axios** - HTTP client for API calls

## 📦 Installation

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🏗️ Project Structure

```
front_end/
├── src/
│   ├── App.jsx              # Main chat application
│   ├── App.css              # Styles for entire app
│   ├── index.css            # Global styles & CSS variables
│   ├── main.jsx             # App entry point
│   └── components/
│       ├── Agent3D.jsx      # 3D agent face components
│       └── Logo3D.jsx       # 3D animated logo
├── index.html               # HTML template
├── package.json             # Dependencies
├── vite.config.js           # Vite configuration
└── README.md                # This file
```

## 🎨 Components

### App.jsx
Main application component containing:
- Conversation sidebar with new chat button
- Chat message display with user/assistant messages
- Input area with send button
- Thinking process visualization
- Agent selection display
- Orchestration pattern selector

### Agent3D.jsx
3D cartoon faces using Three.js primitives:
- Each agent has unique geometry and personality
- Animations: rotation, floating, blinking, talking
- Flat-shaded cartoon aesthetic
- Size configurable via props

### Logo3D.jsx
Animated 3D logo component:
- Central sphere with orbiting torus
- Continuous rotation animation
- Used in header and empty state

## 🎨 Styling

### CSS Variables
```css
--bg-dark: #0a0e27        /* Main background */
--bg-card: #1a1f3a        /* Card backgrounds */
--bg-hover: #252b47       /* Hover states */
--border: #2d3551         /* Borders */
--accent-blue: #4f9eff    /* Primary accent */
--accent-cyan: #00d9ff    /* Secondary accent */
```

### Key Styles
- **Dark theme** with space navy colors
- **Glassmorphism** effects on cards
- **Smooth animations** and transitions
- **Responsive** layout with flexbox/grid
- **Syntax highlighting** for code blocks
- **Table styling** with hover effects

## 🔌 API Integration

Backend runs on `http://localhost:8000`:

```javascript
// Send message
POST /api/chat
{
  message: string,
  user_id: string,
  conversation_id?: string
}

// Get conversations
GET /api/conversations?user_id=user

// Load conversation
GET /api/conversations/{id}/messages?user_id=user
```

## 🎭 Agent Face Design

Each face is built with Three.js primitives:

```jsx
// Example: Professional Agent
- CylinderGeometry (face base)
- SphereGeometry (eyes)
- TorusGeometry (glasses)
- BoxGeometry (tie)
- Animations via useFrame hook
```

**Design Philosophy:**
- Simple geometric shapes (cylinders, spheres, boxes)
- Bright, saturated colors
- Cartoon proportions (big eyes, exaggerated features)
- Personality through accessories (glasses, book, balance)
- Smooth animations (rotation, floating, blinking)

## 🚀 Development

### Dev Server
```bash
npm run dev
# Runs on http://localhost:5173
```

### Build
```bash
npm run build
# Outputs to dist/
```

### Linting
```bash
npm run lint
```

## 📱 Features in Detail

### Thinking Process
Shows real-time AI reasoning:
- Query analysis
- Agent selection with reasoning
- Confidence scores
- Processing time

### Trace Panel
Expandable panel showing:
- Routing reasoning
- Processing time in ms
- Iteration count
- Full routing history with confidence scores

### Markdown Rendering
Supports:
- Headers (h1-h6)
- Lists (ordered/unordered)
- Code blocks with syntax highlighting
- Inline code
- Tables with GitHub Flavored Markdown
- Blockquotes
- Links

### 3D Rendering
- Canvas with transparent background
- Multiple light sources (ambient, directional, point)
- Camera positioned at [0, 0, 3.5]
- FOV 45 degrees
- Optimized for 70x70px (chat) and 100x100px (cards)

## 🎯 Performance

- **Fast dev server** - Vite HMR
- **Optimized builds** - Code splitting and minification
- **Lazy rendering** - 3D faces only render when visible
- **Smooth animations** - 60fps with requestAnimationFrame

## 🔧 Configuration

### Vite Config
```javascript
// vite.config.js
export default {
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
}
```

## 📝 Notes

- Node.js 20.19+ or 22.12+ recommended
- Backend must be running on port 8000
- 3D rendering requires WebGL support
- Optimized for modern browsers (Chrome, Firefox, Safari, Edge)

## 🤝 Contributing

When adding new features:
1. Follow existing component patterns
2. Use CSS variables for colors
3. Keep 3D faces simple and performant
4. Update this README

---

**Built with React 19, Vite, Three.js, and ❤️**
