/**
 * Network Impact Widget
 *
 * Shows network-wide economic impact.
 * Demonstrates the scale of the gift economy movement.
 */

import React, { useState, useEffect } from 'react';

interface NetworkMetrics {
  total_value: number;
  transaction_count: number;
  active_communities: number;
  active_members: number;
  by_category: Record<string, number>;
  period_type: string;
  period_start: string;
  period_end: string;
}

interface NetworkImpactWidgetProps {
  periodType?: 'day' | 'week' | 'month' | 'year';
}

export const NetworkImpactWidget: React.FC<NetworkImpactWidgetProps> = ({
  periodType = 'month',
}) => {
  const [metrics, setMetrics] = useState<NetworkMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMetrics();
  }, [periodType]);

  const fetchMetrics = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/leakage-metrics/network?period_type=${periodType}`
      );

      const data = await response.json();

      if (data.found) {
        setMetrics(data.metrics);
      } else {
        setMetrics(null);
      }
    } catch (err) {
      setError('Failed to load network metrics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="network-impact-widget loading">
        <div className="spinner"></div>
        <p>Loading network impact...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="network-impact-widget error">
        <p>{error}</p>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="network-impact-widget no-data">
        <h3>Network Impact</h3>
        <p>No network-wide data yet.</p>
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

  const formatLargeNumber = (num: number) => {
    if (num >= 1_000_000) {
      return `${(num / 1_000_000).toFixed(1)}M`;
    } else if (num >= 1_000) {
      return `${(num / 1_000).toFixed(1)}K`;
    }
    return num.toString();
  };

  return (
    <div className="network-impact-widget">
      <div className="header">
        <h3>Network-Wide Impact</h3>
        <p className="subtitle">
          Together, we're building real alternatives
        </p>
      </div>

      <div className="hero-stat">
        <div className="big-number">
          {formatCurrency(metrics.total_value)}
        </div>
        <div className="label">
          Kept out of extractive systems this {periodType}
        </div>
      </div>

      <div className="network-stats">
        <div className="stat-grid">
          <div className="stat-item">
            <div className="icon">🤝</div>
            <div className="value">{formatLargeNumber(metrics.transaction_count)}</div>
            <div className="label">Exchanges</div>
          </div>

          <div className="stat-item">
            <div className="icon">👥</div>
            <div className="value">{formatLargeNumber(metrics.active_members)}</div>
            <div className="label">Active Members</div>
          </div>

          <div className="stat-item">
            <div className="icon">🌱</div>
            <div className="value">{metrics.active_communities}</div>
            <div className="label">Communities</div>
          </div>
        </div>
      </div>

      <div className="impact-message">
        <h4>What This Means</h4>
        <div className="impact-facts">
          <div className="fact">
            <span className="bullet">•</span>
            <span className="text">
              ${formatLargeNumber(metrics.total_value)} that didn't enrich
              shareholders
            </span>
          </div>
          <div className="fact">
            <span className="bullet">•</span>
            <span className="text">
              {formatLargeNumber(metrics.transaction_count)} acts of mutual aid
              instead of market transactions
            </span>
          </div>
          <div className="fact">
            <span className="bullet">•</span>
            <span className="text">
              {formatLargeNumber(metrics.active_members)} people building
              economic autonomy
            </span>
          </div>
        </div>
      </div>

      <div className="vision-statement">
        <p>
          Every exchange is a prefiguration of the world we're building. A
          world where we take care of each other, not because there's profit in
          it, but because we're all we've got.
        </p>
      </div>
    </div>
  );
};

export default NetworkImpactWidget;
