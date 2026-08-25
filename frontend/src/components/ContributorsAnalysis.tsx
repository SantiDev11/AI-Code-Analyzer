import React from 'react';
import type { Contributor } from '../types';
import { formatNumber } from '../utils/format';

interface ContributorsAnalysisProps {
  contributors: Contributor[] | null | undefined;
  contributorsCount?: number;
}

export const ContributorsAnalysis: React.FC<ContributorsAnalysisProps> = ({
  contributors,
  contributorsCount,
}) => {
  // Asegurar lista inmutable y ordenada de mayor a menor numero de contribuciones
  const items = contributors ? [...contributors] : [];
  items.sort((a, b) => (b.contributions || 0) - (a.contributions || 0));

  const totalCount = contributorsCount ?? items.length;

  return (
    <section
      className="contributors-section"
      id="contributors-analysis"
      aria-labelledby="contributors-heading"
    >
      <div className="analyzer-container">
        <div className="contributors-card">
          <header className="contributors-header">
            <span className="repo-section-badge">Equipo y Comunidad</span>
            <div className="contributors-title-row">
              <h2 id="contributors-heading" className="contributors-title">
                Contributors
              </h2>
              {items.length > 0 && (
                <span className="contributors-total-badge">
                  Mostrando <strong>{items.length}</strong>
                  {totalCount > items.length ? ` de ${totalCount}` : ''} contribuidores principales
                </span>
              )}
            </div>
            <p className="contributors-subtitle">
              Personas con mayor número de commits atribuidos directamente en el historial del repositorio.
            </p>
          </header>

          {items.length === 0 ? (
            <div className="contributors-empty" role="status">
              <p className="repo-text-muted">
                No se encontraron datos de contribuidores para este repositorio.
              </p>
            </div>
          ) : (
            <ul className="contributors-grid" aria-label="Lista de principales contribuidores">
              {items.map((contributor, index) => {
                const rank = index + 1;
                const hasAvatar = Boolean(contributor.avatar_url && contributor.avatar_url.trim());

                return (
                  <li key={contributor.username || `contributor-${index}`} className="contributor-item">
                    <article className="contributor-card">
                      <div className="contributor-rank" aria-label={`Puesto número ${rank}`}>
                        #{rank}
                      </div>

                      <div className="contributor-avatar-wrapper">
                        {hasAvatar ? (
                          <img
                            src={contributor.avatar_url}
                            alt={`Avatar de ${contributor.username}`}
                            className="contributor-avatar"
                            loading="lazy"
                            width="48"
                            height="48"
                            onError={(e) => {
                              // Fallback si la imagen no carga
                              e.currentTarget.style.display = 'none';
                              const fallback = e.currentTarget.nextElementSibling;
                              if (fallback instanceof HTMLElement) {
                                fallback.style.display = 'flex';
                              }
                            }}
                          />
                        ) : null}
                        <div
                          className="contributor-avatar-fallback"
                          style={{ display: hasAvatar ? 'none' : 'flex' }}
                          aria-hidden="true"
                        >
                          {(contributor.username || '?').charAt(0).toUpperCase()}
                        </div>
                      </div>

                      <div className="contributor-info">
                        <h3 className="contributor-name">
                          {contributor.profile_url ? (
                            <a
                              href={contributor.profile_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="contributor-link"
                              aria-label={`Ver perfil de ${contributor.username} en GitHub (se abre en nueva pestaña)`}
                            >
                              {contributor.username}
                            </a>
                          ) : (
                            <span>{contributor.username}</span>
                          )}
                        </h3>
                        <p className="contributor-commits">
                          <strong>{formatNumber(contributor.contributions || 0)}</strong>{' '}
                          <span>{(contributor.contributions === 1) ? 'commit atribuido' : 'commits atribuidos'}</span>
                        </p>
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
