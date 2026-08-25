import React from 'react';
import type { PullRequest } from '../types';
import { formatNumber } from '../utils/format';

interface PullRequestsAnalysisProps {
  pullRequests: PullRequest[] | null | undefined;
  pullRequestsCount?: number;
  openPullRequestsCount?: number;
  closedPullRequestsCount?: number;
  mergedPullRequestsCount?: number;
}

function formatPRDate(dateStr: string): string {
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

export const PullRequestsAnalysis: React.FC<PullRequestsAnalysisProps> = ({
  pullRequests,
  pullRequestsCount,
  openPullRequestsCount,
  closedPullRequestsCount,
  mergedPullRequestsCount,
}) => {
  const items = pullRequests ? [...pullRequests] : [];
  const totalCount = pullRequestsCount ?? items.length;
  const openCount = openPullRequestsCount ?? items.filter((pr) => pr.state === 'open').length;
  const closedCount = closedPullRequestsCount ?? items.filter((pr) => pr.state === 'closed').length;
  const mergedCount =
    mergedPullRequestsCount ?? items.filter((pr) => pr.state === 'closed' && Boolean(pr.merged_at)).length;

  return (
    <section
      className="prs-section"
      id="pull-requests-analysis"
      aria-labelledby="prs-heading"
    >
      <div className="analyzer-container">
        <div className="prs-card">
          <header className="prs-header">
            <span className="repo-section-badge">Colaboración y Cambios</span>
            <div className="prs-title-row">
              <h2 id="prs-heading" className="prs-title">
                Pull Requests
              </h2>
            </div>
            <p className="prs-subtitle">
              Muestra reciente de propuestas de cambio, estados de integración y ramas involucradas.
            </p>
          </header>

          {/* Resumen metrico semantico dl/dt/dd */}
          <div className="prs-stats-container">
            <dl className="prs-stats-list">
              <div className="prs-stat-card">
                <dt className="prs-stat-label">Total en Muestra</dt>
                <dd className="prs-stat-value">{formatNumber(totalCount)}</dd>
              </div>

              <div className="prs-stat-card">
                <dt className="prs-stat-label">
                  <span className="prs-status-dot open" aria-hidden="true" />
                  <span>Abiertos</span>
                </dt>
                <dd className="prs-stat-value open-text">{formatNumber(openCount)}</dd>
              </div>

              <div className="prs-stat-card">
                <dt className="prs-stat-label">
                  <span className="prs-status-dot closed" aria-hidden="true" />
                  <span>Cerrados</span>
                </dt>
                <dd className="prs-stat-value closed-text">{formatNumber(closedCount)}</dd>
              </div>

              <div className="prs-stat-card">
                <dt className="prs-stat-label">
                  <span className="prs-status-dot merged" aria-hidden="true" />
                  <span>Mergeados</span>
                </dt>
                <dd className="prs-stat-value merged-text">{formatNumber(mergedCount)}</dd>
              </div>
            </dl>
          </div>

          {items.length === 0 ? (
            <div className="prs-empty" role="status">
              <p className="repo-text-muted">
                No se encontraron pull requests recientes en este repositorio.
              </p>
            </div>
          ) : (
            <ul className="prs-list" aria-label="Lista de pull requests recientes">
              {items.map((pr, index) => {
                const authorName = pr.author ? pr.author.trim() : '';
                const displayAuthor = authorName.length > 0 ? authorName : 'Autor no identificado';
                const isMerged = pr.state === 'closed' && Boolean(pr.merged_at);
                const isOpen = pr.state === 'open';
                const createdFormatted = formatPRDate(pr.created_at);
                const mergedFormatted = pr.merged_at ? formatPRDate(pr.merged_at) : null;
                const closedFormatted = pr.closed_at ? formatPRDate(pr.closed_at) : null;

                let stateClass = 'is-closed';

                if (isMerged) {
                  stateClass = 'is-merged';
                } else if (isOpen) {
                  stateClass = 'is-open';
                }

                return (
                  <li key={`${pr.number}-${index}`} className="pr-item">
                    <article className="pr-entry">
                      <div className="pr-state-col">
                        <span className={`pr-state-badge ${stateClass}`} role="status">
                          {isMerged ? (
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
                                <circle cx="18" cy="18" r="3" />
                                <circle cx="6" cy="6" r="3" />
                                <path d="M6 9v12" />
                                <path d="M18 9a9 9 0 0 0-9 9" />
                              </svg>
                              <span>Merged</span>
                            </>
                          ) : isOpen ? (
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
                                <circle cx="18" cy="18" r="3" />
                                <circle cx="6" cy="6" r="3" />
                                <path d="M13 6h3a2 2 0 0 1 2 2v7" />
                                <line x1="6" y1="9" x2="6" y2="21" />
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
                                <circle cx="18" cy="18" r="3" />
                                <circle cx="6" cy="6" r="3" />
                                <path d="M6 9v12" />
                                <path d="m15 9-6 6" />
                              </svg>
                              <span>Cerrado</span>
                            </>
                          )}
                        </span>
                      </div>

                      <div className="pr-content">
                        <div className="pr-main-row">
                          <h3 className="pr-title">
                            <a
                              href={pr.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="pr-link"
                              aria-label={`Ver pull request número ${pr.number}: ${pr.title} en GitHub (se abre en nueva pestaña)`}
                            >
                              <span className="pr-number">#{pr.number}</span> {pr.title}
                            </a>
                          </h3>

                          {(pr.source_branch || pr.target_branch) && (
                            <div className="pr-branches-wrap" title={`De ${pr.source_branch || '?'} a ${pr.target_branch || '?'}`}>
                              <code className="pr-branch-tag">{pr.source_branch || 'rama desconocida'}</code>
                              <span className="pr-branch-arrow" aria-hidden="true">→</span>
                              <code className="pr-branch-tag target">{pr.target_branch || 'rama base'}</code>
                            </div>
                          )}
                        </div>

                        <footer className="pr-meta">
                          <span className="pr-author">
                            Por{' '}
                            <strong className={pr.author ? 'pr-author-name' : 'pr-author-unknown'}>
                              {displayAuthor}
                            </strong>
                          </span>

                          <span className="pr-meta-separator" aria-hidden="true">
                            •
                          </span>

                          <time dateTime={pr.created_at} className="pr-date" title={`Fecha de apertura: ${pr.created_at}`}>
                            Abierto el {createdFormatted}
                          </time>

                          {isMerged && mergedFormatted && pr.merged_at && (
                            <>
                              <span className="pr-meta-separator" aria-hidden="true">
                                •
                              </span>
                              <time dateTime={pr.merged_at} className="pr-date pr-merged-date" title={`Fecha de merge: ${pr.merged_at}`}>
                                Mergeado el {mergedFormatted}
                              </time>
                            </>
                          )}

                          {!isMerged && pr.closed_at && closedFormatted && (
                            <>
                              <span className="pr-meta-separator" aria-hidden="true">
                                •
                              </span>
                              <time dateTime={pr.closed_at} className="pr-date" title={`Fecha de cierre: ${pr.closed_at}`}>
                                Cerrado el {closedFormatted}
                              </time>
                            </>
                          )}
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
