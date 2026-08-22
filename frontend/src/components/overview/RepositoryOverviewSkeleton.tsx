import React from 'react';

export const RepositoryOverviewSkeleton: React.FC = () => {
  return (
    <section
      className="repo-overview-section is-loading"
      aria-label="Cargando resumen del repositorio"
      aria-busy="true"
    >
      <div className="analyzer-container">
        <div className="repo-overview-card">
          <div className="repo-skeleton-header">
            <div className="repo-skeleton-title" />
            <div className="repo-skeleton-badge" />
          </div>
          <div className="repo-skeleton-desc" />
          <div className="repo-skeleton-desc short" />

          <div className="repo-skeleton-stats-grid">
            <div className="repo-skeleton-stat-box" />
            <div className="repo-skeleton-stat-box" />
            <div className="repo-skeleton-stat-box" />
            <div className="repo-skeleton-stat-box" />
          </div>
        </div>
      </div>
    </section>
  );
};
