import { Agent3D as OriginalAgent3D } from './Agent3D'

export function Agent3D({ agentId, size = 100 }) {
  console.log('🎨 Agent3D rendering:', { agentId, size });
  
  return (
    <div style={{ 
      border: '2px solid red',
      width: size,
      height: size,
      position: 'relative'
    }}>
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        background: 'rgba(255,0,0,0.3)',
        color: 'white',
        fontSize: '10px',
        padding: '2px',
        zIndex: 1000
      }}>
        {agentId}
      </div>
      <OriginalAgent3D agentId={agentId} size={size} />
    </div>
  )
}
