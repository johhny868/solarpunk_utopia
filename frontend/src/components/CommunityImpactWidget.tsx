/**
 * Community Impact Widget
 *
 * Shows community-level economic impact from gift economy.
 * Privacy-preserving: only shows aggregates, never individual contributions.
 */

import React, { useState, useEffect } from 'react';

interface CommunityMetrics {
  total_value: number;
  transaction_count: number;
  member_count: number;
  by_category: Record<string, number>;
  period_type: string;
  period_start: string;
  period_end: string;
}

interface CommunityImpactWidgetProps {
  communityId: string;
  communityName?: string;
  periodType?: 'day' | 'week' | 'month' | 'year';
}

export const CommunityImpactWidget: React.FC<CommunityImpactWidgetProps> = ({
  communityId,
  communityName = 'Community',
  periodType = 'month',
}) => {
  const [metrics, setMetrics] = useState<CommunityMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMetrics();
  }, [communityId, periodType]);

  const fetchMetrics = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/leakage-metrics/community/${communityId}?period_type=${periodType}`
      );

      const data = await response.json();

      if (data.found) {
        setMetrics(data.metrics);
      } else {
        setMetrics(null);
      }
    } catch (err) {
      setError('Failed to load community metrics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="community-impact-widget loading">
        <div className="spinner"></div>
        <p>Loading community impact...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="community-impact-widget error">
        <p>{error}</p>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="community-impact-widget no-data">
        <h3>{communityName} Impact</h3>
        <p>No exchanges in this community yet.</p>
      </div>
    );
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const perCapita = metrics.member_count > 0
    ? metrics.total_value / metrics.member_count
    : 0;

  const getCategoryIcon = (category: string) => {
    const icons: Record<string, string> = {
      food: '🥗',
      tools: '🔨',
      transport: '🚗',
      skills: '💡',
      housing: '🏠',
      goods: '📦',
      other: '✨',
    };
    return icons[category] || '✨';
  };

  return (
    <div className="community-impact-widget">
      <div className="header">
        <h3>{communityName} Impact</h3>
        <p className="subtitle">
          This {periodType}, we kept this value local
        </p>
      </div>

      <div className="main-stats">
        <div className="stat-card total">
          <div className="value">{formatCurrency(metrics.total_value)}</div>
          <div className="label">Total Circulated</div>
        </div>

        <div className="stat-row">
          <div className="stat-card">
            <div className="value">{metrics.transaction_count}</div>
            <div className="label">Exchanges</div>
          </div>

          <div className="stat-card">
            <div className="value">{metrics.member_count}</div>
            <div className="label">Active Members</div>
          </div>

          <div className="stat-card">
            <div className="value">{formatCurrency(perCapita)}</div>
            <div className="label">Per Person</div>
          </div>
        </div>
      </div>

      {Object.keys(metrics.by_category).length > 0 && (
        <div className="category-breakdown">
          <h4>By Category</h4>
          <div className="categories">
            {Object.entries(metrics.by_category)
              .sort((a, b) => b[1] - a[1])
              .map(([category, value]) => {
                const percentage = (value / metrics.total_value) * 100;
                return (
                  <div key={category} className="category-item">
                    <div className="category-header">
                      <span className="icon">{getCategoryIcon(category)}</span>
                      <span className="name">{category}</span>
                    </div>
                    <div className="category-bar">
                      <div
                        className="fill"
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                    <div className="category-value">
                      {formatCurrency(value)} ({percentage.toFixed(0)}%)
                    </div>
                  </div>
                );
              })}
          </div>
        </div>
      )}

      <div className="message">
        <p>
          This is wealth that stayed in our community instead of being
          extracted by corporations. Every exchange strengthens our collective
          autonomy.
        </p>
      </div>
    </div>
  );
};

export default CommunityImpactWidget;
