import React from 'react';

interface HeaderProps {
  onOpenHistory?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenHistory }) => {
  return (
    <header className="analyzer-header">
      <div className="analyzer-container analyzer-header-content">
        <a href="/" className="analyzer-brand" aria-label="AI-Code-Analyzer Inicio">
          <div className="analyzer-brand-icon" aria-hidden="true">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="16 18 22 12 16 6" />
              <polyline points="8 6 2 12 8 18" />
              <circle cx="12" cy="12" r="2" />
            </svg>
          </div>
          <span className="analyzer-brand-title">AI-Code-Analyzer</span>
        </a>

        {onOpenHistory ? (
          <button
            type="button"
            className="analyzer-badge demo-badge-trigger"
            onClick={onOpenHistory}
            title="Ver evolución completa del proyecto (Commits, PRs y Capacidades)"
            aria-label="Abrir historial y versión demo del proyecto"
          >
            <span className="demo-badge-dot" aria-hidden="true" />
            <span>v0.1.0 • DEMO</span>
          </button>
        ) : (
          <span className="analyzer-badge">v0.1.0 • DEMO</span>
        )}

        <nav className="analyzer-nav" aria-label="Navegación principal">
          <ul className="analyzer-nav-list">
            {onOpenHistory && (
              <li>
                <button
                  type="button"
                  onClick={onOpenHistory}
                  className="analyzer-nav-link analyzer-nav-demo-btn"
                >
                  ✨ Evolución del Proyecto
                </button>
              </li>
            )}
            <li>
              <a href="#analyzer" className="analyzer-nav-link">
                Analizador
              </a>
            </li>
            <li>
              <a href="#features" className="analyzer-nav-link">
                Capacidades
              </a>
            </li>
            <li>
              <a
                href="/docs"
                target="_blank"
                rel="noreferrer"
                className="analyzer-nav-link"
              >
                API Docs
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

