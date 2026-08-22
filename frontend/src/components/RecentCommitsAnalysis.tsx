import React from 'react';
import type { Commit } from '../types';

interface RecentCommitsAnalysisProps {
  commits: Commit[] | null | undefined;
}

function formatCommitDate(dateStr: string): string {
  try {
    const parsed = new Date(dateStr);
    if (isNaN(parsed.getTime())) {
      return dateStr;
    }
    return parsed.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'UTC',
    }) + ' UTC';
  } catch {
    return dateStr;
  }
}

export const RecentCommitsAnalysis: React.FC<RecentCommitsAnalysisProps> = ({ commits }) => {
  const items = commits ? [...commits] : [];

  return (
    <section
      className="commits-section"
      id="recent-commits-analysis"
      aria-labelledby="commits-heading"
    >
      <div className="analyzer-container">
        <div className="commits-card">
          <header className="commits-header">
            <span className="repo-section-badge">Historial Reciente</span>
            <div className="commits-title-row">
              <h2 id="commits-heading" className="commits-title">
                Recent Commits
              </h2>
              {items.length > 0 && (
                <span className="commits-count-badge">
                  Mostrando <strong>{items.length}</strong> commits de la rama principal
                </span>
              )}
            </div>
            <p className="commits-subtitle">
              Últimas confirmaciones de código ordenadas cronológicamente de la más reciente a la más antigua.
            </p>
          </header>

          {items.length === 0 ? (
            <div className="commits-empty" role="status">
              <p className="repo-text-muted">
                No hay commits recientes disponibles para este repositorio.
              </p>
            </div>
          ) : (
            <ol className="commits-timeline" aria-label="Historial de commits recientes">
              {items.map((commit, index) => {
                const authorName = commit.author ? commit.author.trim() : '';
                const displayAuthor = authorName.length > 0 ? authorName : 'Autor no identificado';
                const formattedDate = formatCommitDate(commit.date);

                return (
                  <li key={`${commit.sha}-${index}`} className="commit-item">
                    <article className="commit-entry">
                      <div className="commit-timeline-marker" aria-hidden="true">
                        <span className="commit-dot" />
                      </div>

                      <div className="commit-content">
                        <div className="commit-main-row">
                          <p className="commit-message" title={commit.message}>
                            {commit.message}
                          </p>

                          <a
                            href={commit.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="commit-sha-badge"
                            aria-label={`Ver commit ${commit.sha} en GitHub (se abre en nueva pestaña)`}
                          >
                            <code>{commit.sha}</code>
                            <svg
                              width="12"
                              height="12"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              aria-hidden="true"
                              className="commit-external-icon"
                            >
                              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                              <polyline points="15 3 21 3 21 9" />
                              <line x1="10" y1="14" x2="21" y2="3" />
                            </svg>
                          </a>
                        </div>

                        <footer className="commit-meta">
                          <span className="commit-author">
                            <svg
                              width="14"
                              height="14"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              aria-hidden="true"
                              className="commit-author-icon"
                            >
                              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                              <circle cx="12" cy="7" r="4" />
                            </svg>
                            <span className={commit.author ? 'commit-author-name' : 'commit-author-unknown'}>
                              {displayAuthor}
                            </span>
                          </span>

                          <span className="commit-date-separator" aria-hidden="true">
                            •
                          </span>

                          <time dateTime={commit.date} className="commit-time">
                            {formattedDate}
                          </time>
                        </footer>
                      </div>
                    </article>
                  </li>
                );
              })}
            </ol>
          )}
        </div>
      </div>
    </section>
  );
};
