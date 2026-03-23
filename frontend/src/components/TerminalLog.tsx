'use client';

import { useEffect, useRef } from 'react';
import type { LogEntry } from '@/app/page';

interface Props {
  logs: LogEntry[];
}

const LOG_CONFIG: Record<LogEntry['type'], { color: string; bg: string; borderColor: string }> = {
  info:    { color: 'var(--espresso-mid)',  bg: 'transparent',              borderColor: 'transparent' },
  success: { color: 'var(--sage)',          bg: 'var(--sage-pale)',         borderColor: 'var(--sage)' },
  warn:    { color: '#C4883A',             bg: 'rgba(196,136,58,0.08)',    borderColor: '#C4883A' },
  data:    { color: 'var(--terracotta)',    bg: 'var(--terracotta-pale)',   borderColor: 'var(--terracotta)' },
};

export default function TerminalLog({ logs }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="activity-feed" style={{ maxHeight: 280, overflowY: 'auto' }}>
      {/* Header */}
      <div className="activity-feed-header">
        <span style={{ fontSize: 14 }}>📋</span>
        <span style={{ fontFamily: 'DM Sans', fontWeight: 600, fontSize: 12, color: 'var(--espresso-mid)' }}>
          Aggiornamenti in tempo reale
        </span>
        {logs.length > 0 && (
          <span style={{
            marginLeft: 'auto',
            fontFamily: 'DM Mono',
            fontSize: 10,
            color: 'var(--espresso-dim)',
          }}>
            {logs.length} eventi
          </span>
        )}
      </div>

      {/* Entries */}
      <div style={{ padding: '6px 0' }}>
        {logs.length === 0 && (
          <div style={{
            padding: '14px 16px',
            color: 'var(--espresso-dim)',
            fontFamily: 'DM Sans',
            fontSize: 13,
            display: 'flex',
            alignItems: 'center',
            gap: 8,
          }}>
            <span className="spin-slow" style={{ display: 'inline-block' }}>⟳</span>
            Avvio del team in corso...
          </div>
        )}

        {logs.map((log, i) => {
          const cfg = LOG_CONFIG[log.type];
          return (
            <div
              key={i}
              className="activity-row fade-up"
              style={{
                borderLeftColor: cfg.borderColor,
                background: cfg.bg,
              }}
            >
              {/* Timestamp */}
              <span style={{
                fontFamily: 'DM Mono',
                fontSize: 10,
                color: 'var(--espresso-dim)',
                flexShrink: 0,
                paddingTop: 1,
                minWidth: 64,
              }}>
                {log.time}
              </span>

              {/* Agent pill */}
              <span style={{
                fontFamily: 'DM Sans',
                fontSize: 10,
                fontWeight: 700,
                color: 'var(--terracotta-dark)',
                background: 'var(--terracotta-pale)',
                padding: '1px 8px',
                borderRadius: 99,
                flexShrink: 0,
                whiteSpace: 'nowrap',
              }}>
                {log.agent}
              </span>

              {/* Message */}
              <span style={{
                fontFamily: 'DM Sans',
                fontSize: 12,
                color: cfg.color,
                lineHeight: 1.5,
                flex: 1,
              }}>
                {log.msg}
              </span>
            </div>
          );
        })}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}
