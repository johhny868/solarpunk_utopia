interface CompletionStepProps {
  onFinish: () => void
}

export function CompletionStep({ onFinish }: CompletionStepProps) {
  return (
    <div style={{
      background: 'white',
      borderRadius: '1rem',
      padding: '3rem',
      boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
      textAlign: 'center'
    }}>
      <div style={{ fontSize: '5rem', marginBottom: '1rem' }}>🎉</div>

      <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem', color: '#667eea' }}>
        You're All Set!
      </h1>

      <p style={{ fontSize: '1.2rem', lineHeight: '1.8', color: '#555', marginBottom: '2rem' }}>
        Welcome to the gift economy. You're now part of a resilient, community-powered network.
      </p>

      <div style={{
        background: '#ecfdf5',
        padding: '2rem',
        borderRadius: '0.5rem',
        marginBottom: '2rem',
        textAlign: 'left'
      }}>
        <h3 style={{ color: '#10b981', marginBottom: '1rem' }}>What to do next:</h3>
        <ul style={{ color: '#555', lineHeight: '1.8', paddingLeft: '1.5rem' }}>
          <li><strong>Browse Offers</strong> to see what people are sharing</li>
          <li><strong>Create an Offer</strong> to contribute to the community</li>
          <li><strong>Post a Need</strong> if you're looking for something</li>
          <li><strong>Join a Cell</strong> to connect with your local area</li>
          <li><strong>Send Messages</strong> to coordinate with other members</li>
        </ul>
      </div>

      <div style={{
        background: '#f0f9ff',
        padding: '1.5rem',
        borderRadius: '0.5rem',
        borderLeft: '4px solid #0ea5e9',
        marginBottom: '2rem',
        textAlign: 'left'
      }}>
        <p style={{ color: '#555', lineHeight: '1.6' }}>
          <strong>Remember:</strong> This is about mutual aid, not transactions.
          Give what you can, take what you need, and trust the community.
        </p>
      </div>

      <button
        data-testid="onboarding-finish"
        onClick={onFinish}
        style={{
          width: '100%',
          padding: '1.5rem 2rem',
          fontSize: '1.2rem',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          border: 'none',
          borderRadius: '0.5rem',
          cursor: 'pointer',
          fontWeight: 'bold',
          boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)'
        }}
      >
        Enter the Network →
      </button>

      <p style={{ marginTop: '1rem', color: '#999', fontSize: '0.9rem' }}>
        Solidarity forever ✊
      </p>
    </div>
  )
}
