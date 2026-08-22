import React from 'react';
import type { Repository } from '../../types';

interface RepositoryHeaderProps {
  repository: Repository;
}

export const RepositoryHeader: React.FC<RepositoryHeaderProps> = ({ repository }) => {
  return (
    <header className="repo-overview-header">
      <div className="repo-overview-title-row">
        <h2 className="repo-overview-title">
          <a
            href={repository.url}
            target="_blank"
            rel="noopener noreferrer"
            className="repo-overview-link"
            aria-label={`Ver repositorio ${repository.full_name} en GitHub (se abre en nueva pestaña)`}
          >
            {repository.full_name}
          </a>
        </h2>
        <div className="repo-overview-badges">
          {repository.is_archived && (
            <span className="repo-badge repo-badge-warning" role="status">
              Archivado
            </span>
          )}
          <span className="repo-badge repo-badge-branch" title="Rama por defecto">
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
              <line x1="6" y1="3" x2="6" y2="15" />
              <circle cx="18" cy="6" r="3" />
              <circle cx="6" cy="18" r="3" />
              <path d="M18 9a9 9 0 0 1-9 9" />
            </svg>
            <span>{repository.default_branch}</span>
          </span>
          {repository.primary_language && (
            <span className="repo-badge repo-badge-lang">
              <span className="repo-lang-dot" aria-hidden="true" />
              <span>{repository.primary_language}</span>
            </span>
          )}
        </div>
      </div>

      <p className="repo-overview-description">
        {repository.description ? (
          repository.description
        ) : (
          <span className="repo-text-muted">Sin descripción proporcionada en GitHub.</span>
        )}
      </p>
    </header>
  );
};
