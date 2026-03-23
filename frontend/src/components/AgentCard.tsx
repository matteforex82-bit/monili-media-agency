'use client';

import type { AgentDef } from '@/app/page';

interface Props {
  agent: AgentDef;
  index: number;
}

const STATUS_LABEL: Record<string, string> = {
  offline: 'Offline',
  standby: 'Pronto',
  active:  'In lavoro',
  done:    'Fatto',
  error:   'Errore',
};

const STATUS_COLOR: Record<string, string> = {
  offline: 'var(--cream-border)',
  standby: 'var(--espresso-dim)',
  active:  'var(--terracotta)',
  done:    'var(--sage)',
  error:   'var(--rose-err)',
};

export default function AgentCard({ agent }: Props) {
  const { name, role, icon, status, progress } = agent;
  const isActive  = status === 'active';
  const isDone    = status === 'done';
  const isStandby = status === 'standby' || status === 'offline';

  return (
    <div
      className={`agent-card ${isActive ? 'active' : ''} ${isDone ? 'done' : ''} ${isStandby ? 'standby' : ''}`}
      style={{ padding: '14px 12px' }}
    >
      {/* Icon + status dot */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 10 }}>
        <span style={{
          fontSize: 22,
          lineHeight: 1,
          filter: isStandby ? 'grayscale(0.7) opacity(0.6)' : 'none',
          transition: 'filter 0.3s',
        }}>
          {isDone ? '✅' : icon}
        </span>
        <span style={{
          width: 7,
          height: 7,
          borderRadius: '50%',
          background: STATUS_COLOR[status],
          display: 'block',
          marginTop: 3,
          flexShrink: 0,
          boxShadow: isActive
            ? `0 0 0 3px var(--terracotta-pale)`
            : isDone
            ? `0 0 0 2px var(--sage-pale)`
            : 'none',
          animation: isActive ? 'pulse-dot 1.2s ease-in-out infinite' : 'none',
        }} />
      </div>

      {/* Name */}
      <div style={{
        fontFamily: 'DM Sans',
        fontSize: 10,
        fontWeight: 700,
        letterSpacing: '0.06em',
        textTransform: 'uppercase',
        color: isActive
          ? 'var(--terracotta-dark)'
          : isDone
          ? 'var(--sage)'
          : 'var(--espresso-dim)',
        marginBottom: 2,
        transition: 'color 0.3s',
      }}>
        {name}
      </div>

      {/* Role */}
      <div style={{
        fontSize: 10,
        color: 'var(--espresso-dim)',
        marginBottom: 10,
        lineHeight: 1.35,
        fontFamily: 'DM Sans',
      }}>
        {role}
      </div>

      {/* Progress bar */}
      <div className="progress-bar-track" style={{ marginBottom: 8 }}>
        {(isActive || isDone) && (
          <div
            className={`progress-bar-fill${isDone ? ' done-fill' : ''}`}
            style={{ width: `${isDone ? 100 : progress}%` }}
          />
        )}
      </div>

      {/* Status label */}
      <div style={{
        fontSize: 10,
        fontWeight: 600,
        color: STATUS_COLOR[status],
        fontFamily: 'DM Sans',
        display: 'flex',
        alignItems: 'center',
        gap: 4,
      }}>
        {isActive && (
          <span className="spin-slow" style={{ display: 'inline-block', fontSize: 10 }}>⟳</span>
        )}
        {STATUS_LABEL[status]}
      </div>
    </div>
  );
}
