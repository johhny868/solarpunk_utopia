import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { WelcomeStep } from '../components/onboarding/WelcomeStep'
import { GiftEconomyStep } from '../components/onboarding/GiftEconomyStep'
import { CreateOfferStep } from '../components/onboarding/CreateOfferStep'
import { BrowseOffersStep } from '../components/onboarding/BrowseOffersStep'
import { AgentsHelpStep } from '../components/onboarding/AgentsHelpStep'
import { CompletionStep } from '../components/onboarding/CompletionStep'

/**
 * Onboarding flow for first-time users.
 * GAP-12: Onboarding Flow
 *
 * Shows a guided tour of the app:
 * 1. Welcome & introduction
 * 2. Gift economy explanation
 * 3. Create your first offer
 * 4. Browse community offers
 * 5. How agents help you
 * 6. Completion celebration
 */
export function OnboardingPage() {
  const [currentStep, setCurrentStep] = useState(0)
  const navigate = useNavigate()

  const handleSkip = () => {
    // Mark onboarding as complete
    localStorage.setItem('onboarding_completed', 'true')
    // Navigate to homepage (replace to prevent back button loop)
    navigate('/', { replace: true })
  }

  const stepTitles = [
    'Welcome',
    'Gift Economy',
    'Create Offer',
    'Browse Offers',
    'Smart Helpers',
    'Complete'
  ]

  const steps = [
    <WelcomeStep onNext={() => setCurrentStep(1)} />,
    <GiftEconomyStep
      onNext={() => setCurrentStep(2)}
      onBack={() => setCurrentStep(0)}
    />,
    <CreateOfferStep
      onNext={() => setCurrentStep(3)}
      onBack={() => setCurrentStep(1)}
    />,
    <BrowseOffersStep
      onNext={() => setCurrentStep(4)}
      onBack={() => setCurrentStep(2)}
    />,
    <AgentsHelpStep
      onNext={() => setCurrentStep(5)}
      onBack={() => setCurrentStep(3)}
    />,
    <CompletionStep
      onFinish={() => {
        // Mark onboarding as complete
        localStorage.setItem('onboarding_completed', 'true')
        // Navigate to homepage (replace to prevent back button loop)
        navigate('/', { replace: true })
      }}
    />
  ]

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '2rem'
    }}>
      <div style={{
        maxWidth: '800px',
        width: '100%'
      }}>
        {/* Progress indicator with step info and skip button */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem',
          marginBottom: '2rem'
        }}>
          {/* Step counter and skip button */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            color: 'white'
          }}>
            <div style={{ fontSize: '0.875rem', opacity: 0.9 }}>
              Step {currentStep + 1} of {steps.length}: {stepTitles[currentStep]}
            </div>
            <button
              onClick={handleSkip}
              style={{
                background: 'transparent',
                border: '1px solid rgba(255, 255, 255, 0.5)',
                color: 'white',
                padding: '0.5rem 1rem',
                borderRadius: '0.5rem',
                cursor: 'pointer',
                fontSize: '0.875rem',
                transition: 'all 0.2s ease'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)'
                e.currentTarget.style.borderColor = 'white'
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.background = 'transparent'
                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.5)'
              }}
            >
              Skip to App
            </button>
          </div>

          {/* Progress dots */}
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '0.5rem'
          }}>
            {steps.map((_, index) => (
              <div
                key={index}
                style={{
                  width: '2rem',
                  height: '0.5rem',
                  borderRadius: '0.25rem',
                  background: index === currentStep
                    ? 'white'
                    : 'rgba(255, 255, 255, 0.3)',
                  transition: 'all 0.3s ease'
                }}
              />
            ))}
          </div>
        </div>

        {/* Current step */}
        {steps[currentStep]}
      </div>
    </div>
  )
}
