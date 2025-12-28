/**
 * NodeConfigGuard - Ensures node is configured before allowing access
 *
 * Checks if the node has been configured. If not, redirects to /node-config.
 * This runs before any other routes can be accessed.
 */

import { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface NodeConfigGuardProps {
  children: React.ReactNode;
}

export default function NodeConfigGuard({ children }: NodeConfigGuardProps) {
  const [isChecking, setIsChecking] = useState(true);
  const [isConfigured, setIsConfigured] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Don't redirect if already on node-config page
    if (location.pathname === '/node-config') {
      setIsChecking(false);
      setIsConfigured(true); // Allow access to config page itself
      return;
    }

    // Check if node is configured
    const checkNodeConfig = async () => {
      try {
        const response = await axios.get(`${API_URL}/node/config/status`);
        const { configured } = response.data;

        setIsConfigured(configured);

        if (!configured) {
          // Node not configured - redirect to config page
          navigate('/node-config', { replace: true });
        }
      } catch (error) {
        console.error('Failed to check node configuration:', error);
        // On error, assume not configured and redirect
        navigate('/node-config', { replace: true });
      } finally {
        setIsChecking(false);
      }
    };

    checkNodeConfig();
  }, [location.pathname, navigate]);

  if (isChecking) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          fontSize: '1.2rem',
        }}
      >
        Checking node configuration...
      </div>
    );
  }

  if (!isConfigured && location.pathname !== '/node-config') {
    // Still show loading while redirect happens
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          fontSize: '1.2rem',
        }}
      >
        Redirecting to node configuration...
      </div>
    );
  }

  return <>{children}</>;
}
