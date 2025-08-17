import React, { useEffect, useState } from 'react';
import { ApiEvents } from '../../services/api';

export default function GlobalBanner() {
  const [message, setMessage] = useState(null);

  useEffect(() => {
    const off = ApiEvents.on('token_refreshed', () => {
      setMessage('Session refreshed');
      const t = setTimeout(() => setMessage(null), 3000);
      return () => clearTimeout(t);
    });
    return () => { if (off) off(); };
  }, []);

  if (!message) return null;

  return (
    <div style={{
      position: 'fixed', top: 12, right: 12, zIndex: 1000,
      background: '#2563eb', color: 'white', padding: '8px 12px',
      borderRadius: 8, boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
    }}>
      {message}
    </div>
  );
}
