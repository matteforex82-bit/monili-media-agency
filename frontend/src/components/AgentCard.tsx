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

const TEAM_COLORS: Record<string, { bg: string; fg: string }> = {
  Anna: { bg: 'var(--bot-anna)', fg: 'var(--bot-anna-fg)' },
  Dario: { bg: 'var(--bot-dario)', fg: 'var(--bot-dario-fg)' },
  Vera: { bg: 'var(--bot-vera)', fg: 'var(--bot-vera-fg)' },
  Carla: { bg: 'var(--bot-carla)', fg: 'var(--bot-carla-fg)' },
  Paolo: { bg: 'var(--bot-paolo)', fg: 'var(--bot-paolo-fg)' },
};

export default function AgentCard({ agent }: Props) {
  const { name, role, status, progress } = agent;
  const isActive  = status === 'active';
  const isDone    = status === 'done';
  const isStandby = status === 'standby' || status === 'offline';
  const colors = TEAM_COLORS[name] || TEAM_COLORS.Anna;

  return (
    <div
      className={`agent-card ${isActive ? 'active' : ''} ${isDone ? 'done' : ''} ${isStandby ? 'standby' : ''}`}
      style={{ padding: '14px 12px' }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 10 }}>
        <span className="bot-avatar" style={{ background: colors.bg, color: colors.fg }}>
          {name[0]}
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
        fontFamily: 'var(--bot-font-sans)',
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
        fontFamily: 'var(--bot-font-sans)',
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
        fontFamily: 'var(--bot-font-sans)',
        display: 'flex',
        alignItems: 'center',
        gap: 4,
      }}>
        {isActive && (
          <span className="spin-slow" style={{ display: 'inline-block', fontSize: 10 }}>...</span>
        )}
        {STATUS_LABEL[status]}
      </div>
    </div>
  );
}

