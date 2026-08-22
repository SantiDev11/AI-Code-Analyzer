import React from 'react';

interface RepositoryTopicsProps {
  topics: string[];
}

export const RepositoryTopics: React.FC<RepositoryTopicsProps> = ({ topics }) => {
  if (!topics || topics.length === 0) {
    return (
      <div className="repo-topics-empty" aria-label="Temas del repositorio">
        <p className="repo-text-muted">No se han configurado etiquetas temáticas (topics) en este repositorio.</p>
      </div>
    );
  }

  return (
    <div className="repo-topics-wrapper" aria-label="Etiquetas temáticas del repositorio">
      <h3 className="repo-topics-heading">Topics</h3>
      <ul className="repo-topics-list">
        {topics.map((topic) => (
          <li key={topic} className="repo-topic-item">
            <span className="repo-topic-tag">{topic}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};
