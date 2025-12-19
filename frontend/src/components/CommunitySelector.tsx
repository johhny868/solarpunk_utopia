/**
 * CommunitySelector - Dropdown to switch between communities
 */

import { useState } from 'react';
import { useCommunity } from '@/contexts/CommunityContext';
import { ChevronDown, Plus, Users } from 'lucide-react';

export function CommunitySelector() {
  const { currentCommunity, communities, selectCommunity, loading } = useCommunity();
  const [isOpen, setIsOpen] = useState(false);

  if (loading) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg animate-pulse">
        <Users className="w-4 h-4 text-gray-400" />
        <span className="text-sm text-gray-500">Loading...</span>
      </div>
    );
  }

  if (!currentCommunity && communities.length === 0) {
    return (
      <a
        href="/communities/create"
        className="flex items-center gap-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
      >
        <Plus className="w-4 h-4" />
        Create Community
      </a>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors min-w-[200px]"
      >
        <Users className="w-4 h-4 text-gray-600 flex-shrink-0" />
        <span className="text-sm font-medium text-gray-900 truncate flex-1 text-left">
          {currentCommunity?.name || 'Select Community'}
        </span>
        <ChevronDown className={`w-4 h-4 text-gray-600 flex-shrink-0 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* Dropdown */}
          <div className="absolute top-full left-0 mt-1 w-full bg-white border border-gray-300 rounded-lg shadow-lg z-20 max-h-64 overflow-y-auto">
            {communities.map((community) => (
              <button
                key={community.id}
                onClick={() => {
                  selectCommunity(community.id);
                  setIsOpen(false);
                }}
                className={`w-full text-left px-4 py-2 hover:bg-gray-50 transition-colors ${
                  currentCommunity?.id === community.id ? 'bg-green-50' : ''
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {community.name}
                    </p>
                    {community.description && (
                      <p className="text-xs text-gray-500 truncate mt-0.5">
                        {community.description}
                      </p>
                    )}
                  </div>
                  {currentCommunity?.id === community.id && (
                    <div className="ml-2 w-2 h-2 bg-green-600 rounded-full flex-shrink-0" />
                  )}
                </div>
              </button>
            ))}

            {/* Divider */}
            <div className="border-t border-gray-200 my-1" />

            {/* Create new community */}
            <a
              href="/communities"
              className="block px-4 py-2 text-sm text-green-600 hover:bg-gray-50 transition-colors font-medium"
              onClick={() => setIsOpen(false)}
            >
              <div className="flex items-center gap-2">
                <Plus className="w-4 h-4" />
                Manage Communities
              </div>
            </a>
          </div>
        </>
      )}
    </div>
  );
}
