import React from 'react';
import type { Repository } from '../../types';
import { formatNumber } from '../../utils/format';

interface RepositoryStatsProps {
  repository: Repository;
}

export const RepositoryStats: React.FC<RepositoryStatsProps> = ({ repository }) => {
  return (
    <div className="repo-stats-container">
      <dl className="repo-stats-list">
        <div className="repo-stat-card">
          <dt className="repo-stat-label">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
              className="repo-stat-icon"
            >
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
            </svg>
            <span>Stars</span>
          </dt>
          <dd className="repo-stat-value">{formatNumber(repository.stars)}</dd>
        </div>

        <div className="repo-stat-card">
          <dt className="repo-stat-label">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
              className="repo-stat-icon"
            >
              <line x1="6" y1="3" x2="6" y2="15" />
              <circle cx="18" cy="6" r="3" />
              <circle cx="6" cy="18" r="3" />
              <path d="M18 9a9 9 0 0 1-9 9" />
            </svg>
            <span>Forks</span>
          </dt>
          <dd className="repo-stat-value">{formatNumber(repository.forks)}</dd>
        </div>

        <div className="repo-stat-card">
          <dt className="repo-stat-label">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
              className="repo-stat-icon"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <span>Open Issues</span>
          </dt>
          <dd className="repo-stat-value">{formatNumber(repository.open_issues)}</dd>
        </div>

        <div className="repo-stat-card">
          <dt className="repo-stat-label">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
              className="repo-stat-icon"
            >
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
            <span>Licencia</span>
          </dt>
          <dd className="repo-stat-value repo-stat-text">
            {repository.license ? (
              <span>{repository.license}</span>
            ) : (
              <span className="repo-text-muted">Sin licencia declarada</span>
            )}
          </dd>
        </div>
      </dl>
    </div>
  );
};
