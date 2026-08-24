import React from 'react';
import type { AIAnalysis as AIAnalysisType, Concern, Recommendation, TechnicalOverview } from '../types';

interface AIAnalysisProps {
  aiAnalysis: AIAnalysisType | null | undefined;
}

type SeverityLevel = 'low' | 'medium' | 'high';
type PriorityLevel = 'low' | 'medium' | 'high';

const SEVERITY_CONFIG: Record<SeverityLevel, { label: string; className: string }> = {
  low: { label: 'Baja (Low)', className: 'is-low' },
  medium: { label: 'Media (Medium)', className: 'is-medium' },
  high: { label: 'Alta (High)', className: 'is-high' },
};

const PRIORITY_CONFIG: Record<PriorityLevel, { label: string; className: string }> = {
  low: { label: 'Baja (Low)', className: 'is-low' },
  medium: { label: 'Media (Medium)', className: 'is-medium' },
  high: { label: 'Alta (High)', className: 'is-high' },
};

const ConcernCard: React.FC<{ concern: Concern }> = ({ concern }) => {
  const severityKey = (concern.severity?.toLowerCase() as SeverityLevel) || 'low';
  const severityInfo = SEVERITY_CONFIG[severityKey] ?? SEVERITY_CONFIG.low;

  return (
    <li className="ai-concern-item">
      <article className="ai-concern-card">
        <header className="ai-card-header">
          <h4 className="ai-card-title">{concern.title}</h4>
          <span className={`ai-badge ${severityInfo.className}`} role="status">
            <span className="ai-badge-dot" aria-hidden="true" />
            <span>Severidad: {severityInfo.label}</span>
          </span>
        </header>
        <p className="ai-card-description">{concern.description}</p>
        {concern.evidence && (
          <div className="ai-evidence-box">
            <span className="ai-evidence-label">Evidencia detectada:</span>
            <p className="ai-evidence-text">{concern.evidence}</p>
          </div>
        )}
      </article>
    </li>
  );
};

const RecommendationCard: React.FC<{ recommendation: Recommendation }> = ({ recommendation }) => {
  const priorityKey = (recommendation.priority?.toLowerCase() as PriorityLevel) || 'low';
  const priorityInfo = PRIORITY_CONFIG[priorityKey] ?? PRIORITY_CONFIG.low;

  return (
    <li className="ai-recommendation-item">
      <article className="ai-recommendation-card">
        <header className="ai-card-header">
          <h4 className="ai-card-title">{recommendation.title}</h4>
          <span className={`ai-badge ${priorityInfo.className}`} role="status">
            <span className="ai-badge-dot" aria-hidden="true" />
            <span>Prioridad: {priorityInfo.label}</span>
          </span>
        </header>
        <p className="ai-card-description">{recommendation.description}</p>
      </article>
    </li>
  );
};

const TechnicalOverviewSection: React.FC<{ overview: TechnicalOverview }> = ({ overview }) => (
  <article className="ai-block ai-overview-block" aria-labelledby="ai-overview-heading">
    <h3 id="ai-overview-heading" className="ai-block-title">
      Visión Técnica General
    </h3>
    <dl className="ai-overview-list">
      <div className="ai-overview-item">
        <dt className="ai-overview-term">Arquitectura</dt>
        <dd className="ai-overview-desc">{overview.architecture}</dd>
      </div>
      <div className="ai-overview-item">
        <dt className="ai-overview-term">Stack Tecnológico</dt>
        <dd className="ai-overview-desc">{overview.stack}</dd>
      </div>
      <div className="ai-overview-item">
        <dt className="ai-overview-term">Ritmo de Actividad</dt>
        <dd className="ai-overview-desc">{overview.activity_summary}</dd>
      </div>
    </dl>
  </article>
);

const AIUnavailableSection: React.FC = () => (
  <section className="ai-section" id="ai-analysis" aria-labelledby="ai-heading">
    <div className="analyzer-container">
      <div className="ai-card ai-unavailable-card">
        <header className="ai-header">
          <span className="repo-section-badge">Inteligencia Artificial</span>
          <div className="ai-title-row">
            <h2 id="ai-heading" className="ai-title">
              Análisis Técnico con IA
            </h2>
          </div>
        </header>
        <div className="ai-empty" role="status">
          <div className="ai-unavailable-icon" aria-hidden="true">
            <svg
              width="28"
              height="28"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 2v4" />
              <path d="m4.93 4.93 2.83 2.83" />
              <path d="M2 12h4" />
              <path d="m4.93 19.07 2.83-2.83" />
              <path d="M12 22v-4" />
              <path d="m19.07 19.07-2.83-2.83" />
              <path d="M22 12h-4" />
              <path d="m19.07 4.93-2.83 2.83" />
            </svg>
          </div>
          <h3 className="ai-unavailable-title">AI analysis unavailable</h3>
          <p className="repo-text-muted">
            El análisis técnico estructurado con Inteligencia Artificial no está disponible
            actualmente para este repositorio.
          </p>
        </div>
      </div>
    </div>
  </section>
);

export const AIAnalysis: React.FC<AIAnalysisProps> = ({ aiAnalysis }) => {
  if (!aiAnalysis) {
    return <AIUnavailableSection />;
  }

  const strengths = aiAnalysis.strengths ?? [];
  const concerns = aiAnalysis.concerns ?? [];
  const recommendations = aiAnalysis.recommendations ?? [];
  const overview = aiAnalysis.technical_overview;

  return (
    <section className="ai-section" id="ai-analysis" aria-labelledby="ai-heading">
      <div className="analyzer-container">
        <div className="ai-card">
          <header className="ai-header">
            <span className="repo-section-badge">Inteligencia Artificial</span>
            <div className="ai-title-row">
              <h2 id="ai-heading" className="ai-title">
                Análisis Técnico con IA
              </h2>
            </div>
            <p className="ai-subtitle">
              Evaluación técnica integral fundamentada en evidencia objetiva recopilada del
              repositorio.
            </p>
          </header>

          {/* Resumen Ejecutivo Principal */}
          <article className="ai-summary-article" aria-labelledby="ai-summary-heading">
            <h3 id="ai-summary-heading" className="ai-summary-title">
              Resumen Ejecutivo
            </h3>
            <p className="ai-summary-text">{aiAnalysis.summary}</p>
          </article>

          {/* Puntos Fuertes */}
          {strengths.length > 0 && (
            <article className="ai-block" aria-labelledby="ai-strengths-heading">
              <h3 id="ai-strengths-heading" className="ai-block-title">
                Puntos Fuertes (Strengths)
              </h3>
              <ul className="ai-strengths-list" aria-label="Lista de fortalezas detectadas">
                {strengths.map((strength, index) => (
                  <li key={index} className="ai-strength-item">
                    <span className="ai-strength-bullet" aria-hidden="true">
                      ✓
                    </span>
                    <span className="ai-strength-text">{strength}</span>
                  </li>
                ))}
              </ul>
            </article>
          )}

          {/* Puntos de Atención / Concerns */}
          {concerns.length > 0 && (
            <article className="ai-block" aria-labelledby="ai-concerns-heading">
              <h3 id="ai-concerns-heading" className="ai-block-title">
                Puntos de Atención con Evidencia (Concerns)
              </h3>
              <ul className="ai-cards-grid" aria-label="Lista de puntos de atención">
                {concerns.map((concern, index) => (
                  <ConcernCard key={`${concern.title}-${index}`} concern={concern} />
                ))}
              </ul>
            </article>
          )}

          {/* Recomendaciones Técnicas */}
          {recommendations.length > 0 && (
            <article className="ai-block" aria-labelledby="ai-recommendations-heading">
              <h3 id="ai-recommendations-heading" className="ai-block-title">
                Recomendaciones Accionables
              </h3>
              <ul className="ai-cards-grid" aria-label="Lista de recomendaciones sugeridas">
                {recommendations.map((recommendation, index) => (
                  <RecommendationCard
                    key={`${recommendation.title}-${index}`}
                    recommendation={recommendation}
                  />
                ))}
              </ul>
            </article>
          )}

          {/* Visión Técnica General */}
          {overview && <TechnicalOverviewSection overview={overview} />}
        </div>
      </div>
    </section>
  );
};
