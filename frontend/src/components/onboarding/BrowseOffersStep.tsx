interface BrowseOffersStepProps {
  onNext: () => void
  onBack: () => void
}

export function BrowseOffersStep({ onNext, onBack }: BrowseOffersStepProps) {
  return (
    <div style={{
      background: 'white',
      borderRadius: '1rem',
      padding: '3rem',
      boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)'
    }}>
      <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem', color: '#667eea' }}>
        Browse Community Offers 🌍
      </h1>

      <p style={{ fontSize: '1.2rem', lineHeight: '1.8', color: '#555', marginBottom: '2rem' }}>
        See what your neighbors are sharing. You might find exactly what you need!
      </p>

      <div style={{
        background: '#f0fdf4',
        padding: '1.5rem',
        borderRadius: '0.5rem',
        borderLeft: '4px solid #22c55e',
        marginBottom: '1.5rem'
      }}>
        <h3 style={{ color: '#22c55e', marginBottom: '0.5rem' }}>🗺️ Local First</h3>
        <p style={{ color: '#555', lineHeight: '1.6' }}>
          The mesh network shows you offers from people nearby first.
          This builds resilience in your local community.
        </p>
      </div>

      <div style={{
        background: '#fef3c7',
        padding: '1.5rem',
        borderRadius: '0.5rem',
        borderLeft: '4px solid #f59e0b',
        marginBottom: '2rem'
      }}>
        <h3 style={{ color: '#f59e0b', marginBottom: '0.5rem' }}>📱 Works Offline</h3>
        <p style={{ color: '#555', lineHeight: '1.6' }}>
          All offers are stored on your device. You can browse even without internet,
          and exchanges sync when you're back in range.
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
          Continue →
        </button>
      </div>
    </div>
  )
}
