interface AgentsHelpStepProps {
  onNext: () => void
  onBack: () => void
}

export function AgentsHelpStep({ onNext, onBack }: AgentsHelpStepProps) {
  return (
    <div style={{
      background: 'white',
      borderRadius: '1rem',
      padding: '3rem',
      boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)'
    }}>
      <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem', color: '#667eea' }}>
        How AI Agents Help You 🤖
      </h1>

      <p style={{ fontSize: '1.2rem', lineHeight: '1.8', color: '#555', marginBottom: '2rem' }}>
        Agents are like helpful assistants running in the background.
        They work for the community, not for profit.
      </p>

      <div style={{ display: 'grid', gap: '1.5rem', marginBottom: '2rem' }}>
        <div style={{
          background: '#ede9fe',
          padding: '1.5rem',
          borderRadius: '0.5rem',
          borderLeft: '4px solid #8b5cf6'
        }}>
          <h3 style={{ color: '#8b5cf6', marginBottom: '0.5rem' }}>🎯 Matchmaker Agent</h3>
          <p style={{ color: '#555', lineHeight: '1.6' }}>
            Finds connections between offers and needs. Suggests matches based on location,
            timing, and compatibility.
          </p>
        </div>

        <div style={{
          background: '#fce7f3',
          padding: '1.5rem',
          borderRadius: '0.5rem',
          borderLeft: '4px solid #ec4899'
        }}>
          <h3 style={{ color: '#ec4899', marginBottom: '0.5rem' }}>📅 Scheduler Agent</h3>
          <p style={{ color: '#555', lineHeight: '1.6' }}>
            Helps coordinate timing when multiple people are involved.
            Respects everyone's availability and constraints.
          </p>
        </div>

        <div style={{
          background: '#e0f2fe',
          padding: '1.5rem',
          borderRadius: '0.5rem',
          borderLeft: '4px solid #0ea5e9'
        }}>
          <h3 style={{ color: '#0ea5e9', marginBottom: '0.5rem' }}>🛡️ Trust Agent</h3>
          <p style={{ color: '#555', lineHeight: '1.6' }}>
            Helps maintain community safety through the web-of-trust system.
            Prevents infiltration while keeping things accessible.
          </p>
        </div>
      </div>

      <div style={{
        background: '#fff7ed',
        padding: '1.5rem',
        borderRadius: '0.5rem',
        borderLeft: '4px solid #f59e0b',
        marginBottom: '2rem'
      }}>
        <p style={{ color: '#555', lineHeight: '1.6' }}>
          <strong>Privacy Note:</strong> Agents run locally on your device or trusted community nodes.
          Your data never goes to big tech companies.
        </p>
      </div>

      <div style={{ display: 'flex', gap: '1rem' }}>
        <button
          onClick={onBack}
          style={{
            flex: 1,
            padding: '1rem 2rem',
            fontSize: '1.1rem',
            background: '#e5e7eb',
            color: '#374151',
            border: 'none',
            borderRadius: '0.5rem',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          ← Back
        </button>
        <button
          data-testid="onboarding-next"
          onClick={onNext}
          style={{
            flex: 2,
            padding: '1rem 2rem',
            fontSize: '1.1rem',
            background: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '0.5rem',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          Finish Onboarding →
        </button>
      </div>
    </div>
  )
}
