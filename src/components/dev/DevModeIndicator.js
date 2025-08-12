/**
 * Development Mode Indicator
 * Shows whether the app is using live backend or mock.
 */

import React, { useEffect, useState } from 'react';
import { ApiEvents, recheckBackend } from '../../services/api';

const DevModeIndicator = () => {
  if (process.env.NODE_ENV !== 'development') return null;

  const [status, setStatus] = useState({ usingMock: false, checked: false, baseURL: '', ts: Date.now(), healthURL: '' });
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const off = ApiEvents.on('backend_status', (s) => setStatus(s));
    return () => { if (off) off(); };
  }, []);

  const label = status.checked
    ? (status.usingMock ? 'Mock API' : 'Live API')
    : 'Checking API...';
  const color = status.usingMock ? '#d97706' : '#059669';

  return (
    <div style={{ position: 'fixed', bottom: 10, right: 12, zIndex: 9999 }}>
      <div
        onClick={() => setOpen((v) => !v)}
        style={{
          cursor: 'pointer',
          fontSize: 12, background: color, color: 'white',
          padding: '6px 10px', borderRadius: 999,
          boxShadow: '0 3px 8px rgba(0,0,0,0.15)'
        }}
      >
        {label}
      </div>
      {open && (
        <div style={{
          position: 'absolute', bottom: 36, right: 0,
          background: 'white', color: '#111827', border: '1px solid #e5e7eb',
          borderRadius: 8, padding: 10, width: 260,
          boxShadow: '0 8px 24px rgba(0,0,0,0.18)'
        }}>
          <div style={{ fontWeight: 600, marginBottom: 6 }}>API Status</div>
          <div style={{ fontSize: 12, marginBottom: 4 }}>
            <span style={{ color: '#6b7280' }}>Base URL:</span><br />
            <code style={{ fontSize: 11 }}>{status.baseURL || 'n/a'}</code>
          </div>
          <div style={{ fontSize: 12, marginBottom: 4 }}>
            <span style={{ color: '#6b7280' }}>Health:</span><br />
            <a href={status.healthURL} target="_blank" rel="noreferrer" style={{ fontSize: 11 }}>
              {status.healthURL || 'n/a'}
            </a>
          </div>
          <div style={{ fontSize: 12 }}>
            <span style={{ color: '#6b7280' }}>Updated:</span><br />
            <span style={{ fontSize: 11 }}>{new Date(status.ts).toLocaleString()}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 8 }}>
            <button
              onClick={async (e) => {
                e.stopPropagation();
                const btn = e.currentTarget;
                const prev = btn.textContent;
                btn.textContent = 'Checking...';
                btn.disabled = true;
                try {
                  const s = await recheckBackend();
                  setStatus(s);
                } finally {
                  btn.textContent = prev;
                  btn.disabled = false;
                }
              }}
              style={{
                fontSize: 12, padding: '6px 10px', borderRadius: 6,
                background: '#374151', color: 'white', border: 'none', cursor: 'pointer'
              }}
            >
              Re-check
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DevModeIndicator;
