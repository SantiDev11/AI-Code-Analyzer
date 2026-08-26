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
          <div className="ai-header-top">
            <span className="repo-section-badge ai-badge-accent">Inteligencia Artificial</span>
            <span className="ai-roadmap-pill">EN PROCESO • Próximamente</span>
          </div>
          <div className="ai-title-row">
            <h2 id="ai-heading" className="ai-title">
              Análisis Técnico con IA
            </h2>
          </div>
        </header>
        <div className="ai-empty ai-roadmap-container" role="status">
          <div className="ai-roadmap-icon" aria-hidden="true">
            <svg
              width="36"
              height="36"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 2a10 10 0 1 0 10 10H12V2z" />
              <path d="M12 2a10 10 0 0 1 10 10" />
              <circle cx="12" cy="12" r="4" />
            </svg>
          </div>
          <h3 className="ai-unavailable-title">AI analysis unavailable</h3>
          <p className="ai-roadmap-desc">
            El motor de análisis técnico asistido por Inteligencia Artificial no está disponible actualmente para este repositorio y se encuentra en desarrollo activo en el roadmap del proyecto.
          </p>
          <div className="ai-roadmap-features-preview">
            <div className="ai-roadmap-feature-chip">
              <span className="ai-roadmap-feature-dot" />
              <span>Resumen Ejecutivo Automatizado</span>
            </div>
            <div className="ai-roadmap-feature-chip">
              <span className="ai-roadmap-feature-dot" />
              <span>Detección de Fortalezas & Riesgos</span>
            </div>
            <div className="ai-roadmap-feature-chip">
              <span className="ai-roadmap-feature-dot" />
              <span>Recomendaciones Accionables de Arquitectura</span>
            </div>
          </div>
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
            <div className="ai-header-top">
              <span className="repo-section-badge ai-badge-accent">Inteligencia Artificial</span>
              <span className="ai-roadmap-pill">EN PROCESO • Próximamente</span>
            </div>
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

