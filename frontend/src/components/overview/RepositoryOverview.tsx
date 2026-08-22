import React from 'react';
import type { Repository } from '../../types';
import { RepositoryHeader } from './RepositoryHeader';
import { RepositoryStats } from './RepositoryStats';
import { RepositoryTopics } from './RepositoryTopics';

interface RepositoryOverviewProps {
  repository: Repository;
}

export const RepositoryOverview: React.FC<RepositoryOverviewProps> = ({ repository }) => {
  const createdAtFormatted = new Date(repository.created_at).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });

  const updatedAtFormatted = new Date(repository.updated_at).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });

  return (
    <section
      className="repo-overview-section"
      id="repository-overview"
      aria-labelledby="overview-main-heading"
    >
      <div className="analyzer-container">
        <div className="repo-overview-card">
          <span id="overview-main-heading" className="repo-section-badge">
            Resumen General del Repositorio
          </span>

          <RepositoryHeader repository={repository} />

          <RepositoryStats repository={repository} />

          <RepositoryTopics topics={repository.topics} />

          <footer className="repo-overview-footer">
            <dl className="repo-meta-list">
              <div className="repo-meta-item">
                <dt>Tamaño:</dt>
                <dd>{repository.size_kb.toLocaleString()} KB</dd>
              </div>
              <div className="repo-meta-item">
                <dt>Creado:</dt>
                <dd>{createdAtFormatted}</dd>
              </div>
              <div className="repo-meta-item">
                <dt>Última actualización:</dt>
                <dd>{updatedAtFormatted}</dd>
              </div>
            </dl>
          </footer>
        </div>
      </div>
    </section>
  );
};
