/**
 * GAP-62: User Status Badge
 *
 * Displays a user's status (active, resting, sabbatical) with empathy and support
 */

import React from 'react';

interface UserStatusBadgeProps {
  status: 'active' | 'resting' | 'sabbatical';
  statusNote?: string;
  userName?: string;
  showFullMessage?: boolean;  // Show full supportive message
}

export const UserStatusBadge: React.FC<UserStatusBadgeProps> = ({
  status,
  statusNote,
  userName = 'This person',
  showFullMessage = false
}) => {
  if (status === 'active') {
    return null;  // Don't show badge for active users
  }

  return (
    <div className={`rounded-lg p-4 ${
      status === 'resting' ? 'bg-blue-50 border border-blue-200' : 'bg-purple-50 border border-purple-200'
    }`}>
      <div className="flex items-center space-x-2 mb-2">
        <span className="text-lg">
          {status === 'resting' ? '🌙' : '✨'}
        </span>
        <span className="font-medium text-gray-900">
          {userName} is {status === 'resting' ? 'resting' : 'on sabbatical'}
        </span>
      </div>

      {statusNote && (
        <p className="text-sm text-gray-600 italic mb-2">
          "{statusNote}"
        </p>
      )}

      {showFullMessage && (
        <p className="text-sm text-gray-700">
          {status === 'resting' && (
            <>
              Right now, {userName.split(' ')[0] || userName} is in a season of needing support.
              Mutual aid means we support each other through all seasons.
            </>
          )}
          {status === 'sabbatical' && (
            <>
              {userName.split(' ')[0] || userName} is taking extended time away.
              The network is here when they're ready to return.
            </>
          )}
        </p>
      )}

      {!statusNote && showFullMessage && (
        <p className="text-xs text-gray-500 mt-2">
          No explanation needed. Everyone deserves rest.
        </p>
      )}
    </div>
  );
};
