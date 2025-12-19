/**
 * Personal Impact Widget
 *
 * Shows user's personal economic impact from gift economy participation.
 * Privacy-preserving: only user sees their own stats.
 */

import React, { useState, useEffect } from 'react';

interface PersonalMetrics {
  total_value: number;
  given_value: number;
  received_value: number;
  transaction_count: number;
  by_category: Record<string, number>;
  period_type: string;
  period_start: string;
  period_end: string;
}

interface PersonalImpactWidgetProps {
  agentId: string;
  periodType?: 'day' | 'week' | 'month' | 'year';
}

export const PersonalImpactWidget: React.FC<PersonalImpactWidgetProps> = ({
  agentId,
  periodType = 'month',
}) => {
  const [metrics, setMetrics] = useState<PersonalMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMetrics();
  }, [agentId, periodType]);

  const fetchMetrics = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/leakage-metrics/personal/${agentId}?period_type=${periodType}`
      );

      const data = await response.json();

      if (data.found) {
        setMetrics(data.metrics);
      } else {
        setMetrics(null);
      }
    } catch (err) {
      setError('Failed to load impact metrics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="personal-impact-widget loading">
        <div className="spinner"></div>
        <p>Loading your impact...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="personal-impact-widget error">
        <p>{error}</p>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="personal-impact-widget no-data">
        <h3>Your Impact This {periodType}</h3>
        <p>No exchanges completed yet. Start giving or receiving!</p>
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
    <div className="personal-impact-widget">
      <div className="header">
        <h3>Your Impact This {periodType.charAt(0).toUpperCase() + periodType.slice(1)}</h3>
        <p className="subtitle">
          Economic value kept in community, not extracted
        </p>
      </div>

      <div className="main-stat">
        <div className="value-circle">
          <span className="amount">{formatCurrency(metrics.total_value)}</span>
          <span className="label">Kept Local</span>
        </div>
      </div>

      <div className="breakdown">
        <div className="stat-row">
          <span className="label">Given</span>
          <span className="value">{formatCurrency(metrics.given_value)}</span>
        </div>
        <div className="stat-row">
          <span className="label">Received</span>
          <span className="value">{formatCurrency(metrics.received_value)}</span>
        </div>
        <div className="stat-row">
          <span className="label">Exchanges</span>
          <span className="value">{metrics.transaction_count}</span>
        </div>
      </div>

      {Object.keys(metrics.by_category).length > 0 && (
        <div className="category-breakdown">
          <h4>By Category</h4>
          <div className="categories">
            {Object.entries(metrics.by_category).map(([category, value]) => (
              <div key={category} className="category-item">
                <span className="icon">{getCategoryIcon(category)}</span>
                <span className="name">{category}</span>
                <span className="value">{formatCurrency(value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="message">
        <p>
          Every exchange is a transaction that didn't go to Amazon, Uber, or
          landlords. You're building real alternatives.
        </p>
      </div>
    </div>
  );
};

export default PersonalImpactWidget;
