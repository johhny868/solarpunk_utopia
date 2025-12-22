import { useNavigate } from 'react-router-dom'

interface CreateOfferStepProps {
  onNext: () => void
  onBack: () => void
}

export function CreateOfferStep({ onNext, onBack }: CreateOfferStepProps) {
  const navigate = useNavigate()

  const handleCreateNow = () => {
    // Mark onboarding as complete and go to create offer page
    localStorage.setItem('onboarding_completed', 'true')
    navigate('/offers/create')
  }

  return (
    <div style={{
      background: 'white',
      borderRadius: '1rem',
      padding: '3rem',
      boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)'
    }}>
      <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem', color: '#667eea' }}>
        Create Your First Offer 🌾
      </h1>

      <p style={{ fontSize: '1.2rem', lineHeight: '1.8', color: '#555', marginBottom: '2rem' }}>
        What can you share with the community? It doesn't have to be big - even small things make a difference.
      </p>

      <div style={{ display: 'grid', gap: '1rem', marginBottom: '2rem' }}>
        <div style={{ padding: '1rem', background: '#f9fafb', borderRadius: '0.5rem' }}>
          <strong>Examples:</strong>
          <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem', color: '#555' }}>
            <li>Extra vegetables from your garden</li>
            <li>An hour of guitar lessons</li>
            <li>Help with coding or design</li>
            <li>A spare bike or tools</li>
            <li>Childcare skills</li>
            <li>Translation services</li>
          </ul>
        </div>
      </div>

      <div style={{
        background: '#e0f2fe',
        padding: '1.5rem',
        borderRadius: '0.5rem',
        borderLeft: '4px solid #0ea5e9',
        marginBottom: '2rem'
      }}>
        <p style={{ color: '#555', lineHeight: '1.6' }}>
          <strong>Tip:</strong> You can always add more offers later.
          Start with one thing you feel comfortable sharing.
        </p>
      </div>

      <div style={{ display: 'flex', gap: '1rem' }}>
        <button
          onClick={onBack}
          style={{
            flex: 1,
            padding: '1rem',
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
          onClick={handleCreateNow}
          style={{
            flex: 2,
            padding: '1rem',
            fontSize: '1.1rem',
            background: '#10b981',
            color: 'white',
            border: 'none',
            borderRadius: '0.5rem',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          Create Offer Now →
        </button>
        <button
          data-testid="onboarding-next"
          onClick={onNext}
          style={{
            flex: 1,
            padding: '1rem',
            fontSize: '1.1rem',
            background: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '0.5rem',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          Skip
        </button>
      </div>
    </div>
  )
}
