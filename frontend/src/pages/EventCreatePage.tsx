// Event creation page for stewards to generate event QR codes
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import QRCode from 'react-qr-code';
import { onboardingApi, type CreateEventRequest, type EventInvite } from '../api/onboarding';

export function EventCreatePage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<CreateEventRequest>({
    event_name: '',
    event_type: 'workshop',
    event_start: '',
    event_end: '',
    event_location: '',
    max_attendees: 200,
    temporary_trust_level: 0.3,
  });
  const [createdEvent, setCreatedEvent] = useState<EventInvite | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const event = await onboardingApi.createEvent(formData);
      setCreatedEvent(event);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create event');
      console.error('Error creating event:', err);
    } finally {
      setLoading(false);
    }
  };

  if (createdEvent) {
    const joinUrl = `${window.location.origin}/join/event/${createdEvent.invite_code}`;

    return (
      <div className="max-w-2xl mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6">Event Created!</h1>

        <div className="bg-white p-6 rounded-lg shadow-md mb-6">
          <h2 className="text-xl font-semibold mb-4">{createdEvent.event_name}</h2>

          <div className="flex justify-center mb-6">
            <div className="bg-white p-4 rounded-lg">
              <QRCode value={joinUrl} size={256} />
            </div>
          </div>

          <div className="space-y-2 mb-6">
            <p><strong>Invite Code:</strong> {createdEvent.invite_code}</p>
            <p><strong>Max Attendees:</strong> {createdEvent.max_attendees}</p>
            <p><strong>Current Attendees:</strong> {createdEvent.attendee_count}</p>
            <p><strong>Location:</strong> {createdEvent.event_location}</p>
            <p><strong>Start:</strong> {new Date(createdEvent.event_start).toLocaleString()}</p>
            <p><strong>End:</strong> {new Date(createdEvent.event_end).toLocaleString()}</p>
          </div>

          <div className="bg-blue-50 p-4 rounded-lg mb-6">
            <h3 className="font-semibold mb-2">Share this QR code:</h3>
            <p className="text-sm text-gray-700">
              Attendees can scan this QR code or visit: <br />
              <code className="bg-gray-100 px-2 py-1 rounded text-xs">{joinUrl}</code>
            </p>
          </div>

          <div className="flex gap-4">
            <button
              onClick={() => {
                setCreatedEvent(null);
                setFormData({
                  event_name: '',
                  event_type: 'workshop',
                  event_start: '',
                  event_end: '',
                  event_location: '',
                  max_attendees: 200,
                  temporary_trust_level: 0.3,
                });
              }}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Create Another Event
            </button>
            <button
              onClick={() => navigate('/events')}
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              View My Events
            </button>
            <button
              onClick={() => window.print()}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Print QR Code
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Create Event Invite</h1>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md">
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Event Name *</label>
          <input
            type="text"
            required
            value={formData.event_name}
            onChange={(e) => setFormData({ ...formData, event_name: e.target.value })}
            className="w-full px-3 py-2 border rounded-md"
            placeholder="Portland Solarpunk Workshop"
          />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Event Type *</label>
          <select
            required
            value={formData.event_type}
            onChange={(e) => setFormData({ ...formData, event_type: e.target.value as any })}
            className="w-full px-3 py-2 border rounded-md"
          >
            <option value="workshop">Workshop</option>
            <option value="gathering">Gathering</option>
            <option value="meeting">Meeting</option>
            <option value="conference">Conference</option>
            <option value="other">Other</option>
          </select>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Location *</label>
          <input
            type="text"
            required
            value={formData.event_location}
            onChange={(e) => setFormData({ ...formData, event_location: e.target.value })}
            className="w-full px-3 py-2 border rounded-md"
            placeholder="Portland Community Center"
          />
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-2">Start Date/Time *</label>
            <input
              type="datetime-local"
              required
              value={formData.event_start}
              onChange={(e) => setFormData({ ...formData, event_start: e.target.value })}
              className="w-full px-3 py-2 border rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">End Date/Time *</label>
            <input
              type="datetime-local"
              required
              value={formData.event_end}
              onChange={(e) => setFormData({ ...formData, event_end: e.target.value })}
              className="w-full px-3 py-2 border rounded-md"
            />
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Max Attendees</label>
          <input
            type="number"
            min="1"
            max="1000"
            value={formData.max_attendees}
            onChange={(e) => setFormData({ ...formData, max_attendees: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border rounded-md"
          />
          <p className="text-sm text-gray-600 mt-1">Maximum number of people who can join via this invite</p>
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">Temporary Trust Level</label>
          <input
            type="number"
            min="0.1"
            max="0.9"
            step="0.1"
            value={formData.temporary_trust_level}
            onChange={(e) => setFormData({ ...formData, temporary_trust_level: parseFloat(e.target.value) })}
            className="w-full px-3 py-2 border rounded-md"
          />
          <p className="text-sm text-gray-600 mt-1">
            Trust level granted during the event (0.3 recommended for workshops)
          </p>
        </div>

        <div className="flex gap-4">
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400"
          >
            {loading ? 'Creating...' : 'Create Event Invite'}
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
        <h3 className="font-semibold mb-2">About Event Invites</h3>
        <p className="text-sm text-gray-700">
          Event invites allow you to quickly onboard attendees at workshops, gatherings, and conferences.
          Attendees will receive temporary trust and can participate during the event. After the event,
          they'll need to get full vouches to continue as members.
        </p>
      </div>
    </div>
  );
}
