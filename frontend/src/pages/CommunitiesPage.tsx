/**
 * Communities Management Page
 */

import { useState } from 'react';
import { useCommunity } from '@/contexts/CommunityContext';
import { Card } from '@/components/Card';
import { Loading } from '@/components/Loading';
import { Users, Plus, Settings, UserPlus, Check } from 'lucide-react';

export function CommunitiesPage() {
  const { communities, currentCommunity, selectCommunity, createCommunity, loading, refreshCommunities } = useCommunity();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newCommunityName, setNewCommunityName] = useState('');
  const [newCommunityDescription, setNewCommunityDescription] = useState('');
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreateCommunity = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setCreating(true);

    try {
      await createCommunity(newCommunityName, newCommunityDescription);
      setNewCommunityName('');
      setNewCommunityDescription('');
      setShowCreateForm(false);
      await refreshCommunities();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create community');
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return <Loading text="Loading communities..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Communities</h1>
          <p className="text-gray-600 mt-1">Manage your communities and create new ones</p>
        </div>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
        >
          <Plus className="w-4 h-4" />
          Create Community
        </button>
      </div>

      {/* Create Community Form */}
      {showCreateForm && (
        <Card>
          <form onSubmit={handleCreateCommunity} className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">Create New Community</h2>

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {error}
              </div>
            )}

            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                Community Name *
              </label>
              <input
                type="text"
                id="name"
                value={newCommunityName}
                onChange={(e) => setNewCommunityName(e.target.value)}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                placeholder="e.g., Oak Street Collective"
              />
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                id="description"
                value={newCommunityDescription}
                onChange={(e) => setNewCommunityDescription(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                placeholder="What is this community about?"
              />
            </div>

            <div className="flex gap-3">
              <button
                type="submit"
                disabled={creating || !newCommunityName.trim()}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {creating ? 'Creating...' : 'Create Community'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowCreateForm(false);
                  setError(null);
                }}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
              >
                Cancel
              </button>
            </div>
          </form>
        </Card>
      )}

      {/* Communities List */}
      {communities.length === 0 ? (
        <Card>
          <div className="text-center py-12">
            <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Communities Yet</h3>
            <p className="text-gray-600 mb-4">
              Create your first community to get started with the gift economy.
            </p>
            <button
              onClick={() => setShowCreateForm(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
            >
              <Plus className="w-4 h-4" />
              Create Your First Community
            </button>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {communities.map((community) => (
            <Card key={community.id}>
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Users className="w-6 h-6 text-green-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-gray-900 truncate">{community.name}</h3>
                      {community.description && (
                        <p className="text-sm text-gray-600 line-clamp-2 mt-0.5">{community.description}</p>
                      )}
                    </div>
                  </div>
                  {currentCommunity?.id === community.id && (
                    <div className="flex items-center gap-1 px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium flex-shrink-0">
                      <Check className="w-3 h-3" />
                      Active
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Users className="w-4 h-4" />
                  <span>Community</span>
                  {community.is_public && (
                    <span className="ml-auto px-2 py-0.5 bg-blue-100 text-blue-800 rounded text-xs">
                      Public
                    </span>
                  )}
                </div>

                <div className="flex gap-2 pt-2 border-t border-gray-200">
                  {currentCommunity?.id !== community.id && (
                    <button
                      onClick={() => selectCommunity(community.id)}
                      className="flex-1 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
                    >
                      Switch to This
                    </button>
                  )}
                  <button
                    className="flex items-center gap-2 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium"
                    title="Manage members (coming soon)"
                  >
                    <UserPlus className="w-4 h-4" />
                    <span className="hidden sm:inline">Members</span>
                  </button>
                  <button
                    className="flex items-center gap-2 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium"
                    title="Settings (coming soon)"
                  >
                    <Settings className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
