/**
 * Production API Status Badge
 * Visible only in production. Shows whether the app uses live backend or mock.
 */

import React, { useEffect, useState } from 'react';
import { ApiEvents, recheckBackend } from '../../services/api';

export default function ProdApiStatus() {
  if (process.env.NODE_ENV !== 'production') return null;

  const [status, setStatus] = useState({ usingMock: false, checked: false, baseURL: '', ts: Date.now(), healthURL: '' });
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const off = ApiEvents.on('backend_status', (s) => setStatus(s));
    // Check once on mount so we render something early
    recheckBackend().then(setStatus).catch(() => {});
    // Auto-hide after a few seconds to avoid persistent UI noise
    const t = setTimeout(() => setVisible(false), 6000);
    return () => { if (off) off(); clearTimeout(t); };
  }, []);

  if (!visible) return null;

  const label = status.checked
    ? (status.usingMock ? 'Using Mock API' : 'Connected: Live API')
    : 'Checking API…';
  const color = status.usingMock ? '#d97706' : '#059669';

  return (
    <div style={{ position: 'fixed', bottom: 12, right: 12, zIndex: 9999 }}>
      <div
        title={status.baseURL || ''}
        style={{
          fontSize: 12, background: color, color: 'white',
          padding: '6px 10px', borderRadius: 999,
          boxShadow: '0 3px 8px rgba(0,0,0,0.15)'
        }}
      >
        {label}
      </div>
    </div>
  );
}
