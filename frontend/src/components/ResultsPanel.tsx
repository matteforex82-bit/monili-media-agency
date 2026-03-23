'use client';

import { useState } from 'react';

interface Props {
  results: Record<string, string>;
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const TABS = [
  { id: 'analisi',  label: 'Analisi',  icon: '🔍' },
  { id: 'shooting', label: 'Shooting', icon: '📷' },
  { id: 'reel',     label: 'Reel',     icon: '🎬' },
  { id: 'copy',     label: 'Caption',  icon: '✍️' },
  { id: 'hashtag',  label: 'Hashtag',  icon: '#️⃣' },
];

export default function ResultsPanel({ results, activeTab, onTabChange }: Props) {
  const [copied, setCopied] = useState(false);
  const content = results[activeTab] || '';

  const handleCopy = () => {
    navigator.clipboard.writeText(content).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  const renderContent = (text: string) => {
    const lines = text.split('\n');
    return lines.map((line, i) => {
      // H1
      if (line.startsWith('# ')) {
        return (
          <h2 key={i} style={{
            fontFamily: 'Playfair Display',
            fontWeight: 700,
            fontSize: 20,
            color: 'var(--espresso)',
            marginBottom: 14,
            marginTop: i > 0 ? 22 : 0,
            lineHeight: 1.3,
          }}>
            {line.slice(2)}
          </h2>
        );
      }
      // H2
      if (line.startsWith('## ')) {
        return (
          <h3 key={i} style={{
            fontFamily: 'DM Sans',
            fontWeight: 700,
            fontSize: 11,
            textTransform: 'uppercase',
            letterSpacing: '0.10em',
            color: 'var(--terracotta-dark)',
            marginTop: 18,
            marginBottom: 8,
          }}>
            {line.slice(3)}
          </h3>
        );
      }
      // Code fence
      if (line.startsWith('```')) return null;
      // HR
      if (line.startsWith('---')) {
        return <div key={i} className="hr-warm" style={{ margin: '16px 0' }} />;
      }
      // Bold with **
      if (line.includes('**')) {
        const parts = line.split(/\*\*(.*?)\*\*/g);
        return (
          <p key={i} style={{ fontSize: 13.5, lineHeight: 1.72, marginBottom: 5, color: 'var(--espresso)' }}>
            {parts.map((part, j) =>
              j % 2 === 1
                ? <strong key={j} style={{ color: 'var(--terracotta-dark)', fontWeight: 700 }}>{part}</strong>
                : part
            )}
          </p>
        );
      }
      // Table row
      if (line.startsWith('|')) {
        const cells = line.split('|').filter(c => c.trim());
        const nextLine = lines[i + 1] || '';
        const isHeader = nextLine.startsWith('|--');
        if (line.includes('---')) return null;
        return (
          <div key={i} style={{ display: 'flex', marginBottom: 2 }}>
            {cells.map((cell, j) => (
              <div key={j} style={{
                flex: 1,
                padding: '6px 10px',
                fontFamily: isHeader ? 'DM Sans' : 'DM Sans',
                fontSize: 12,
                fontWeight: isHeader ? 700 : 400,
                color: isHeader ? 'var(--espresso)' : 'var(--espresso-mid)',
                borderBottom: '1px solid var(--border)',
                background: isHeader ? 'var(--cream-2)' : j % 2 === 0 ? 'rgba(250,247,240,0.6)' : '#fff',
              }}>
                {cell.trim()}
              </div>
            ))}
          </div>
        );
      }
      // Empty line
      if (!line.trim()) return <div key={i} style={{ height: 8 }} />;
      // Backtick line (code-ish)
      if (line.startsWith('`')) {
        return (
          <div key={i} style={{
            fontFamily: 'DM Mono',
            fontSize: 11.5,
            background: 'var(--cream-2)',
            border: '1px solid var(--border)',
            borderRadius: 6,
            padding: '8px 12px',
            marginBottom: 6,
            color: 'var(--espresso-mid)',
            lineHeight: 1.6,
            overflowX: 'auto',
          }}>
            {line.replace(/^`+|`+$/g, '')}
          </div>
        );
      }
      // Default paragraph
      return (
        <p key={i} style={{
          fontSize: 13.5,
          lineHeight: 1.72,
          marginBottom: 4,
          color: line.startsWith('>') ? 'var(--terracotta)' : 'var(--espresso-mid)',
          fontFamily: 'DM Sans',
          fontStyle: line.startsWith('*') && !line.startsWith('**') ? 'italic' : 'normal',
        }}>
          {line.startsWith('*') && !line.startsWith('**') ? line.slice(1, -1) : line}
        </p>
      );
    });
  };

  return (
    <div className="card" style={{ overflow: 'hidden' }}>
      {/* Tab bar */}
      <div style={{
        display: 'flex',
        borderBottom: '1px solid var(--border)',
        background: 'var(--cream-2)',
        overflowX: 'auto',
        alignItems: 'center',
        padding: '0 8px',
      }}>
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`result-tab ${activeTab === tab.id ? 'active' : ''}`}
          >
            <span style={{ fontSize: 14 }}>{tab.icon}</span>
            {tab.label}
          </button>
        ))}

        <div style={{ flex: 1 }} />

        <button
          onClick={handleCopy}
          className="btn-secondary"
          style={{ padding: '5px 14px', fontSize: 12, margin: '4px 4px 4px 0', flexShrink: 0 }}
        >
          {copied ? '✓ Copiato!' : '⎘ Copia'}
        </button>
      </div>

      {/* Content */}
      <div
        key={activeTab}
        className="fade-up"
        style={{
          padding: '24px 28px',
          minHeight: 300,
          maxHeight: 480,
          overflowY: 'auto',
        }}
      >
        {content ? renderContent(content) : (
          <p style={{ color: 'var(--espresso-dim)', fontFamily: 'DM Sans', fontSize: 13 }}>
            Nessun contenuto disponibile.
          </p>
        )}
      </div>
    </div>
  );
}
