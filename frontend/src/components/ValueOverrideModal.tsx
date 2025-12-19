/**
 * Value Override Modal
 *
 * Allows users to correct the estimated economic value of an exchange.
 * Appears when completing an exchange.
 */

import React, { useState } from 'react';

interface ValueOverrideModalProps {
  exchangeId: string;
  agentId: string;
  estimatedValue: number;
  category: string;
  onSave: (newValue: number) => void;
  onCancel: () => void;
  onSkip: () => void;
}

export const ValueOverrideModal: React.FC<ValueOverrideModalProps> = ({
  exchangeId,
  agentId,
  estimatedValue,
  category,
  onSave,
  onCancel,
  onSkip,
}) => {
  const [customValue, setCustomValue] = useState<string>(estimatedValue.toString());
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSave = async () => {
    const newValue = parseFloat(customValue);

    if (isNaN(newValue) || newValue < 0) {
      setError('Please enter a valid positive number');
      return;
    }

    setSaving(true);
    setError(null);

    try {
      const response = await fetch(
        `/leakage-metrics/exchange/${exchangeId}/override-value`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            new_value: newValue,
            agent_id: agentId,
          }),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to update value');
      }

      onSave(newValue);
    } catch (err) {
      setError('Failed to save value. Please try again.');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  return (
    <div className="modal-overlay">
      <div className="modal value-override-modal">
        <div className="modal-header">
          <h3>Estimate Economic Value</h3>
          <button className="close-button" onClick={onCancel}>
            ×
          </button>
        </div>

        <div className="modal-body">
          <p className="explanation">
            Help us track the economic impact of this exchange. We estimated
            the counterfactual value (what you would have paid in the market),
            but you can correct it.
          </p>

          <div className="current-estimate">
            <div className="label">Our Estimate ({category}):</div>
            <div className="value">{formatCurrency(estimatedValue)}</div>
          </div>

          <div className="form-group">
            <label htmlFor="custom-value">Your Estimate (USD):</label>
            <div className="input-group">
              <span className="prefix">$</span>
              <input
                id="custom-value"
                type="number"
                min="0"
                step="0.01"
                value={customValue}
                onChange={(e) => setCustomValue(e.target.value)}
                placeholder="Enter amount"
                disabled={saving}
              />
            </div>
            {error && <div className="error-message">{error}</div>}
          </div>

          <div className="help-text">
            <p>
              <strong>Ask yourself:</strong> What would this have cost if I had
              to buy it or pay for it in the market?
            </p>
            <p>Examples:</p>
            <ul>
              <li>Tool rental: What would Home Depot charge per day?</li>
              <li>Ride: What would Uber cost for this trip?</li>
              <li>Meal: What would this cost at a restaurant?</li>
              <li>Skills: What's the hourly rate for this expertise?</li>
            </ul>
          </div>
        </div>

        <div className="modal-footer">
          <button
            className="button secondary"
            onClick={onSkip}
            disabled={saving}
          >
            Use Estimate ({formatCurrency(estimatedValue)})
          </button>
          <button
            className="button primary"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save My Estimate'}
          </button>
        </div>

        <div className="privacy-note">
          <small>
            🔒 Your specific value is private. Only aggregates are shared with
            the community.
          </small>
        </div>
      </div>
    </div>
  );
};

export default ValueOverrideModal;
