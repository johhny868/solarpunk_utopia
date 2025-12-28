/**
 * Node Configuration Page - First-run setup
 *
 * This appears before any users can log in, configuring the node's
 * identity on the .multiversemesh network.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function NodeConfigPage() {
  const [meshName, setMeshName] = useState('');
  const [nodeDescription, setNodeDescription] = useState('');
  const [adminContact, setAdminContact] = useState('');
  const [enableAI, setEnableAI] = useState(false);
  const [enableBridge, setEnableBridge] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate mesh name
    if (!meshName.trim()) {
      setError('Please enter a mesh name');
      return;
    }

    if (!/^[a-zA-Z0-9-_]+$/.test(meshName)) {
      setError('Mesh name can only contain letters, numbers, hyphens, and underscores');
      return;
    }

    setLoading(true);

    try {
      await axios.post(`${API_URL}/node/config`, {
        mesh_name: meshName.trim(),
        node_description: nodeDescription.trim() || null,
        admin_contact: adminContact.trim() || null,
        enable_ai_inference: enableAI,
        enable_bridge_mode: enableBridge,
      });

      // Redirect to login after successful configuration
      navigate('/login');
    } catch (err: any) {
      console.error('Configuration error:', err);
      setError(
        err.response?.data?.detail || 'Configuration failed. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-6 sm:p-8">
        {/* Header */}
        <div className="text-center mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
            Configure Your Node
          </h1>
          <p className="text-sm sm:text-base text-gray-600">
            Set up your identity on the .multiversemesh network
          </p>
        </div>

        {/* Configuration Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Mesh Name */}
          <div>
            <label
              htmlFor="meshName"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Mesh Name <span className="text-red-500">*</span>
            </label>
            <input
              id="meshName"
              type="text"
              value={meshName}
              onChange={(e) => setMeshName(e.target.value)}
              placeholder="e.g., alice, food-coop, bridge-01"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              disabled={loading}
              autoFocus
            />
            <p className="text-xs text-gray-500 mt-1">
              Your address: <strong>{meshName || 'yourname'}.multiversemesh</strong>
            </p>
          </div>

          {/* Node Description */}
          <div>
            <label
              htmlFor="nodeDescription"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Description (optional)
            </label>
            <input
              id="nodeDescription"
              type="text"
              value={nodeDescription}
              onChange={(e) => setNodeDescription(e.target.value)}
              placeholder="e.g., Personal device, Community hub"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              disabled={loading}
            />
          </div>

          {/* Admin Contact */}
          <div>
            <label
              htmlFor="adminContact"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Contact Info (optional)
            </label>
            <input
              id="adminContact"
              type="text"
              value={adminContact}
              onChange={(e) => setAdminContact(e.target.value)}
              placeholder="e.g., alice@example.com, @alice"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              disabled={loading}
            />
          </div>

          {/* Service Toggles */}
          <div className="space-y-4 border-t pt-4">
            <p className="text-sm font-medium text-gray-700">Services</p>

            {/* AI Inference */}
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={enableAI}
                onChange={(e) => setEnableAI(e.target.checked)}
                className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                disabled={loading}
              />
              <span className="ml-2 text-sm text-gray-700">
                <strong>Share AI compute</strong> with the mesh
              </span>
            </label>

            {/* Bridge Mode */}
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={enableBridge}
                onChange={(e) => setEnableBridge(e.target.checked)}
                className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                disabled={loading}
              />
              <span className="ml-2 text-sm text-gray-700">
                <strong>Act as bridge</strong> between mesh islands
              </span>
            </label>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !meshName.trim()}
            className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold py-3 px-4 rounded-lg transition-colors"
          >
            {loading ? 'Configuring...' : 'Configure Node'}
          </button>
        </form>

        {/* Info */}
        <div className="mt-6 sm:mt-8 pt-4 sm:pt-6 border-t border-gray-200">
          <p className="text-xs sm:text-sm text-gray-500 text-center leading-relaxed">
            This is a one-time setup. You can change these settings later.
          </p>
        </div>
      </div>
    </div>
  );
}
