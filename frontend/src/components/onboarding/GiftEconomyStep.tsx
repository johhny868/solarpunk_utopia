interface GiftEconomyStepProps {
  onNext: () => void
  onBack: () => void
}

export function GiftEconomyStep({ onNext, onBack }: GiftEconomyStepProps) {
  return (
    <div style={{
      background: 'white',
      borderRadius: '1rem',
      padding: '3rem',
      boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)'
    }}>
      <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem', color: '#667eea' }}>
        How Does Gift Economy Work? 🎁
      </h1>

      <p style={{ fontSize: '1.2rem', lineHeight: '1.8', color: '#555', marginBottom: '2rem' }}>
        It's simple: you give what you can, take what you need. No ledgers, no debt, no guilt.
      </p>

      <div style={{ display: 'grid', gap: '1.5rem', marginBottom: '2rem' }}>
        <div style={{
          background: '#ecfdf5',
          padding: '1.5rem',
          borderRadius: '0.5rem',
          borderLeft: '4px solid #10b981'
        }}>
          <h3 style={{ color: '#10b981', marginBottom: '0.5rem' }}>✨ Offer What You Have</h3>
          <p style={{ color: '#555', lineHeight: '1.6' }}>
            Got extra tomatoes? A spare bike? Skills to teach? Post it as an <strong>Offer</strong>.
            The community can see what you're sharing.
          </p>
        </div>

        <div style={{
          background: '#fef3c7',
          padding: '1.5rem',
          borderRadius: '0.5rem',
          borderLeft: '4px solid #f59e0b'
        }}>
          <h3 style={{ color: '#f59e0b', marginBottom: '0.5rem' }}>🔍 Ask For What You Need</h3>
          <p style={{ color: '#555', lineHeight: '1.6' }}>
            Need help fixing your roof? Looking for childcare? Post a <strong>Need</strong>.
            Someone nearby might have exactly what you're looking for.
          </p>
        </div>

        <div style={{
          background: '#e0e7ff',
          padding: '1.5rem',
          borderRadius: '0.5rem',
          borderLeft: '4px solid #6366f1'
        }}>
          <h3 style={{ color: '#6366f1', marginBottom: '0.5rem' }}>🤖 Agents Match You</h3>
          <p style={{ color: '#555', lineHeight: '1.6' }}>
            AI agents work in the background to connect offers with needs.
            They suggest matches, coordinate timing, and help things flow smoothly.
          </p>
        </div>
      </div>

      <div style={{
        background: '#fff1f2',
        borderLeft: '4px solid #f43f5e',
        padding: '1.5rem',
        borderRadius: '0.5rem',
        marginBottom: '2rem'
      }}>
        <h3 style={{ marginBottom: '0.5rem', color: '#f43f5e' }}>⚡ Important</h3>
        <p style={{ color: '#555', lineHeight: '1.6' }}>
          There's <strong>no keeping score</strong>. You don't "owe" anyone.
          Give freely, receive gratefully. That's it.
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
          I'm Ready to Share →
        </button>
      </div>
    </div>
  )
}
