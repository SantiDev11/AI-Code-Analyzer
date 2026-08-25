import React from 'react';
import type { Issue } from '../types';
import { formatNumber } from '../utils/format';

interface IssuesAnalysisProps {
  issues: Issue[] | null | undefined;
  issuesCount?: number;
  openIssuesCount?: number;
  closedIssuesCount?: number;
}

function formatIssueDate(dateStr: string): string {
  try {
    const parsed = new Date(dateStr);
    if (isNaN(parsed.getTime())) {
      return dateStr;
    }
    return parsed.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      timeZone: 'UTC',
    });
  } catch {
    return dateStr;
  }
}

export const IssuesAnalysis: React.FC<IssuesAnalysisProps> = ({
  issues,
  issuesCount,
  openIssuesCount,
  closedIssuesCount,
}) => {
  const items = issues ? [...issues] : [];
  const totalCount = issuesCount ?? items.length;
  const openCount = openIssuesCount ?? items.filter((i) => i.state === 'open').length;
  const closedCount = closedIssuesCount ?? items.filter((i) => i.state === 'closed').length;

  return (
    <section
      className="issues-section"
      id="issues-analysis"
      aria-labelledby="issues-heading"
    >
      <div className="analyzer-container">
        <div className="issues-card">
          <header className="issues-header">
            <span className="repo-section-badge">Seguimiento de Tareas</span>
            <div className="issues-title-row">
              <h2 id="issues-heading" className="issues-title">
                Issues
              </h2>
            </div>
            <p className="issues-subtitle">
              Muestra representativa de issues reales del repositorio (excluyendo pull requests).
            </p>
          </header>

          {/* Resumen de contadores semantico dl/dt/dd */}
          <div className="issues-stats-container">
            <dl className="issues-stats-list">
              <div className="issues-stat-card">
                <dt className="issues-stat-label">Total en Muestra</dt>
                <dd className="issues-stat-value">{formatNumber(totalCount)}</dd>
              </div>

              <div className="issues-stat-card">
                <dt className="issues-stat-label">
                  <span className="issues-status-dot open" aria-hidden="true" />
                  <span>Abiertos</span>
                </dt>
                <dd className="issues-stat-value open-text">{formatNumber(openCount)}</dd>
              </div>

              <div className="issues-stat-card">
                <dt className="issues-stat-label">
                  <span className="issues-status-dot closed" aria-hidden="true" />
                  <span>Cerrados</span>
                </dt>
                <dd className="issues-stat-value closed-text">{formatNumber(closedCount)}</dd>
              </div>
            </dl>
          </div>

          {items.length === 0 ? (
            <div className="issues-empty" role="status">
              <p className="repo-text-muted">
                No se encontraron issues recientes en este repositorio.
              </p>
            </div>
          ) : (
            <ul className="issues-list" aria-label="Lista de issues recientes">
              {items.map((issue, index) => {
                const authorName = issue.author ? issue.author.trim() : '';
                const displayAuthor = authorName.length > 0 ? authorName : 'Autor no identificado';
                const isOpen = issue.state === 'open';
                const createdFormatted = formatIssueDate(issue.created_at);
                const updatedFormatted = formatIssueDate(issue.updated_at);

                return (
                  <li key={`${issue.number}-${index}`} className="issue-item">
                    <article className="issue-entry">
                      <div className="issue-state-col">
                        <span
                          className={`issue-state-badge ${isOpen ? 'is-open' : 'is-closed'}`}
                          role="status"
                        >
                          {isOpen ? (
                            <>
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
                              >
                                <circle cx="12" cy="12" r="10" />
                                <circle cx="12" cy="12" r="1" />
                              </svg>
                              <span>Abierto</span>
                            </>
                          ) : (
                            <>
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
                              >
                                <polyline points="20 6 9 17 4 12" />
                              </svg>
                              <span>Cerrado</span>
                            </>
                          )}
                        </span>
                      </div>

                      <div className="issue-content">
                        <h3 className="issue-title">
                          <a
                            href={issue.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="issue-link"
                            aria-label={`Ver issue número ${issue.number}: ${issue.title} en GitHub (se abre en nueva pestaña)`}
                          >
                            <span className="issue-number">#{issue.number}</span> {issue.title}
                          </a>
                        </h3>

                        <footer className="issue-meta">
                          <span className="issue-author">
                            Por{' '}
                            <strong className={issue.author ? 'issue-author-name' : 'issue-author-unknown'}>
                              {displayAuthor}
                            </strong>
                          </span>

                          <span className="issue-meta-separator" aria-hidden="true">
                            •
                          </span>

                          <time dateTime={issue.created_at} className="issue-date" title={`Fecha de creación: ${issue.created_at}`}>
                            Creado el {createdFormatted}
                          </time>

                          <span className="issue-meta-separator" aria-hidden="true">
                            •
                          </span>

                          <time dateTime={issue.updated_at} className="issue-date" title={`Última actualización: ${issue.updated_at}`}>
                            Actualizado el {updatedFormatted}
                          </time>
                        </footer>
                      </div>
                    </article>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </div>
    </section>
  );
};
