// Event join page - allows users to join events by scanning QR or entering code
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { onboardingApi, type JoinEventRequest, type JoinEventResponse } from '../api/onboarding';
import { useAuth } from '../contexts/AuthContext';

export function EventJoinPage() {
  const { inviteCode } = useParams<{ inviteCode?: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [formData, setFormData] = useState<JoinEventRequest>({
    invite_code: inviteCode || '',
    user_name: user?.name || '',
    location: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<JoinEventResponse | null>(null);

  useEffect(() => {
    if (inviteCode) {
      setFormData(prev => ({ ...prev, invite_code: inviteCode }));
    }
  }, [inviteCode]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await onboardingApi.joinEvent(formData);
      setSuccess(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to join event');
      console.error('Error joining event:', err);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="max-w-2xl mx-auto p-6">
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <svg className="w-12 h-12 text-green-600 mr-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h1 className="text-2xl font-bold text-green-900">Welcome!</h1>
              <p className="text-green-700">{success.message}</p>
            </div>
          </div>

          <div className="space-y-2 mb-6">
            <p><strong>Event:</strong> {success.event_name}</p>
            <p><strong>Your Trust Score:</strong> {success.your_trust_score.toFixed(2)}</p>
            <p><strong>Temporary Trust Level:</strong> {success.temporary_trust_level.toFixed(2)}</p>
          </div>

          <div className="bg-blue-50 p-4 rounded-lg mb-6">
            <h3 className="font-semibold mb-2">What's Next?</h3>
            <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
              <li>You can now participate in this event</li>
              <li>Post offers and needs related to the event</li>
              <li>Connect with other attendees</li>
              <li>After the event, get vouched by full members to continue</li>
            </ul>
          </div>

          <div className="flex gap-4">
            <button
              onClick={() => navigate('/')}
              className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              Go to Home
            </button>
            <button
              onClick={() => navigate('/offers/create')}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Post an Offer
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Join Event</h1>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md">
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Invite Code *</label>
          <input
            type="text"
            required
            value={formData.invite_code}
            onChange={(e) => setFormData({ ...formData, invite_code: e.target.value.toUpperCase() })}
            className="w-full px-3 py-2 border rounded-md font-mono"
            placeholder="WS2025ABC"
          />
          <p className="text-sm text-gray-600 mt-1">
            Enter the event invite code or scan the QR code provided by the event organizer
          </p>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Your Name *</label>
          <input
            type="text"
            required
            value={formData.user_name}
            onChange={(e) => setFormData({ ...formData, user_name: e.target.value })}
            className="w-full px-3 py-2 border rounded-md"
            placeholder="Your name"
          />
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">Your Location (optional)</label>
          <input
            type="text"
            value={formData.location}
            onChange={(e) => setFormData({ ...formData, location: e.target.value })}
            className="w-full px-3 py-2 border rounded-md"
            placeholder="City, State"
          />
        </div>

        <div className="flex gap-4">
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400"
          >
            {loading ? 'Joining...' : 'Join Event'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/')}
            className="px-6 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
          >
            Cancel
          </button>
        </div>
      </form>

      <div className="mt-6 bg-blue-50 p-4 rounded-lg">
        <h3 className="font-semibold mb-2">About Event Participation</h3>
        <p className="text-sm text-gray-700 mb-2">
          When you join an event, you'll receive temporary trust that allows you to participate
          during the event. This trust is valid during the event period.
        </p>
        <p className="text-sm text-gray-700">
          To continue as a full member after the event, you'll need to get vouched by existing
          members who can attest to your participation and trustworthiness.
        </p>
      </div>
    </div>
  );
}
