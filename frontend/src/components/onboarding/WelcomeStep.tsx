interface WelcomeStepProps {
  onNext: () => void
}

export function WelcomeStep({ onNext }: WelcomeStepProps) {
  return (
    <div style={{
      background: 'white',
      borderRadius: '1rem',
      padding: '3rem',
      boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)'
    }}>
      <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem', color: '#667eea' }}>
        Welcome to the Gift Economy! 🌱
      </h1>

      <p style={{ fontSize: '1.2rem', lineHeight: '1.8', color: '#555', marginBottom: '2rem' }}>
        You've just joined a community-powered network where we share resources,
        skills, and knowledge <strong>without money</strong>.
      </p>

      <div style={{
        background: '#f0f7ff',
        borderLeft: '4px solid #667eea',
        padding: '1.5rem',
        borderRadius: '0.5rem',
        marginBottom: '2rem'
      }}>
        <h3 style={{ marginBottom: '1rem', color: '#667eea' }}>What is this?</h3>
        <p style={{ color: '#555', lineHeight: '1.6' }}>
          This is a <strong>mesh network</strong> for mutual aid and solidarity.
          It runs on old phones, works offline, and can't be shut down by anyone.
          Everything you share strengthens the collective.
        </p>
      </div>

      <div style={{
        background: '#fff7ed',
        borderLeft: '4px solid #f59e0b',
        padding: '1.5rem',
        borderRadius: '0.5rem',
        marginBottom: '2rem'
      }}>
        <h3 style={{ marginBottom: '1rem', color: '#f59e0b' }}>What makes it different?</h3>
        <ul style={{ color: '#555', lineHeight: '1.8', paddingLeft: '1.5rem' }}>
          <li>No big tech surveillance</li>
          <li>Works without internet</li>
          <li>Run by the community, not corporations</li>
          <li>Your data stays on your device</li>
        </ul>
      </div>

      <button
        onClick={onNext}
        style={{
          width: '100%',
          padding: '1rem 2rem',
          fontSize: '1.1rem',
          background: '#667eea',
          color: 'white',
          border: 'none',
          borderRadius: '0.5rem',
          cursor: 'pointer',
          fontWeight: 'bold',
          transition: 'all 0.2s'
        }}
        onMouseOver={(e) => e.currentTarget.style.background = '#5568d3'}
        onMouseOut={(e) => e.currentTarget.style.background = '#667eea'}
      >
        Let's Get Started →
      </button>
    </div>
  )
}
