import React, { useEffect } from 'react';

interface ProjectHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoadSelfDemo?: () => void;
}

interface Milestone {
  phase: string;
  title: string;
  badge: string;
  badgeType: 'success' | 'accent' | 'info' | 'warning';
  description: string;
  commits: string[];
  deliverables: string[];
}

const MILESTONES: Milestone[] = [
  {
    phase: 'Fase 1',
    title: 'Arquitectura Base y Núcleo de la API',
    badge: 'Backend Core',
    badgeType: 'accent',
    description: 'Creación del servicio backend con FastAPI, cliente asíncrono para la GitHub REST API, sistema de caché en memoria con TTL y validación estricta con Pydantic.',
    commits: ['545b3fb (MVP FastAPI)', 'e6a384f (Caché en memoria)', 'abd42da (Licencia, topics, releases)', '45876b3 (Full name y metadatos)'],
    deliverables: ['Endpoint /analyze/{owner}/{repo}', 'Manejo de Rate Limit 429', 'Caché con expiración configurable'],
  },
  {
    phase: 'Fase 2',
    title: 'Análisis de Actividad, Commits, Issues y PRs',
    badge: 'Git Analytics',
    badgeType: 'info',
    description: 'Implementación del muestreo y cálculo estadístico de contribuciones de colaboradores, historial de commits recientes, desglose de issues abiertas/cerradas y pull requests.',
    commits: ['7ab3a92 (Contributors)', '72bc3fa (Recent Commits)', 'fdb2b5a (Issues)', '504ba8a (Pull Requests)', '67201cb (Releases)'],
    deliverables: ['Muestreo de commits', 'Clasificación de issues y PRs', 'Detección de versiones y pre-releases'],
  },
  {
    phase: 'Fase 3',
    title: 'Ritmo Temporal (Activity) y Git Tree',
    badge: 'Deep Inspection',
    badgeType: 'warning',
    description: 'Cálculo de actividad temporal diaria en días naturales (UTC) y exploración del Git Tree de la rama por defecto sin clonar repositorios en disco.',
    commits: ['b1421f3 (Activity Analysis)', 'ff86f22 (Code Metrics)', 'cd408c2 (AI Contract Base)'],
    deliverables: ['Distribución diaria de eventos (90 días)', 'Conteo jerárquico de archivos y directorios', 'Mapeo de extensiones'],
  },
  {
    phase: 'Fase 4',
    title: 'Estándares de Calidad e Ingeniería (Quality Signals)',
    badge: 'Code Quality',
    badgeType: 'success',
    description: 'Deducción en memoria de 8 señales objetivas de ingeniería de software a partir de la estructura de archivos: Tests, Documentación, CI/CD, Linters, Formateo, Tipado, Dependencias y Cobertura.',
    commits: ['8c4c29c (Quality signals)', '3437188 (Documentación y contrato API)'],
    deliverables: ['8 detectores automáticos de configuración', 'Soporte para múltiples linters y herramientas', 'Ausencia de falsos negativos'],
  },
  {
    phase: 'Fase 5',
    title: 'Frontend React + TypeScript + Vite',
    badge: 'SPA Frontend',
    badgeType: 'accent',
    description: 'Creación de la interfaz de usuario moderna con React 18, TypeScript estricto, suite de pruebas unitarias con Vitest y diseño accesible basado en HTML5 semántico.',
    commits: ['0f1e83b (Frontend Foundation)', 'b81768f (Componentes de análisis)', 'c91976e (Estilos y métricas)'],
    deliverables: ['13 componentes modulares', '180 pruebas unitarias con Vitest', 'Formulario con validación en vivo'],
  },
  {
    phase: 'Fase 6',
    title: 'Contenedores Docker y Pipeline de CI/CD',
    badge: 'DevOps & CI',
    badgeType: 'info',
    description: 'Automatización completa de integración continua con GitHub Actions (pytest + vitest + tsc + docker build) y configuración de compose multicontenedor.',
    commits: ['16dec33 (Actualizar Docker)', '114ee1e (GitHub Actions CI)', 'bf29beb (Configuración de producción)'],
    deliverables: ['Pipeline de 3 jobs paralelos', 'Validación estricta en cada push', 'Pruebas simuladas con cero secretos'],
  },
  {
    phase: 'Fase 7',
    title: 'Unificación en Servicio Único & Rediseño SaaS Dashboard',
    badge: 'Full-Stack V1.0',
    badgeType: 'success',
    description: 'Unificación de FastAPI y React en un solo servicio desplegable vía Docker multi-stage (Node 22 + Python 3.12), client-side routing SPA y rediseño visual moderno Developer Intelligence.',
    commits: ['dd28e2a (Unificación de arquitectura)', 'a209e7d (Proyecto final)', '80bffd0 (Actualización visual Deep Slate)'],
    deliverables: ['Un solo puerto/URL pública', 'Deep Slate Design System', 'Roadmap de IA integrado'],
  },
];

export const ProjectHistoryModal: React.FC<ProjectHistoryModalProps> = ({
  isOpen,
  onClose,
  onLoadSelfDemo,
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="demo-modal-overlay" onClick={onClose} role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div className="demo-modal-container" onClick={(e) => e.stopPropagation()}>
        <header className="demo-modal-header">
          <div className="demo-modal-header-text">
            <div className="demo-modal-tags">
              <span className="demo-badge-version">v0.1.0 DEMO</span>
              <span className="demo-badge-status">Evolución & Changelog</span>
            </div>
            <h2 id="modal-title" className="demo-modal-title">
              Historial de Desarrollo del Proyecto
            </h2>
            <p className="demo-modal-subtitle">
              Recorrido cronológico de todas las fases, commits y capacidades construidas desde el inicio del proyecto hasta hoy.
            </p>
          </div>
          <button type="button" className="demo-modal-close" onClick={onClose} aria-label="Cerrar ventana">
            ✕
          </button>
        </header>

        <div className="demo-modal-content">
          {onLoadSelfDemo && (
            <div className="demo-cta-card">
              <div className="demo-cta-info">
                <span className="demo-cta-tag">Auto-Demostración</span>
                <h3 className="demo-cta-title">Analizar este propio repositorio</h3>
                <p className="demo-cta-desc">
                  Ejecuta el análisis técnico completo sobre <strong>SantiDev11/AI-Code-Analyzer</strong> para ver todas las métricas, señales de calidad y actividad en acción.
                </p>
              </div>
              <button
                type="button"
                className="demo-cta-button"
                onClick={() => {
                  onClose();
                  onLoadSelfDemo();
                }}
              >
                <span>Analizar Proyecto Demo</span>
                <span aria-hidden="true">➔</span>
              </button>
            </div>
          )}

          <div className="demo-timeline">
            {MILESTONES.map((milestone, idx) => (
              <article key={idx} className="demo-timeline-item">
                <div className="demo-timeline-marker">
                  <span className="demo-marker-dot" />
                  <span className="demo-marker-line" />
                </div>
                <div className="demo-timeline-card">
                  <header className="demo-timeline-header">
                    <div className="demo-timeline-phase-group">
                      <span className="demo-phase-label">{milestone.phase}</span>
                      <h4 className="demo-timeline-title">{milestone.title}</h4>
                    </div>
                    <span className={`demo-type-pill is-${milestone.badgeType}`}>
                      {milestone.badge}
                    </span>
                  </header>

                  <p className="demo-timeline-description">{milestone.description}</p>

                  <div className="demo-timeline-details">
                    <div className="demo-details-col">
                      <span className="demo-details-title">Commits & Hitos:</span>
                      <ul className="demo-commits-list">
                        {milestone.commits.map((commit, cIdx) => (
                          <li key={cIdx} className="demo-commit-tag">
                            <code>{commit}</code>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="demo-details-col">
                      <span className="demo-details-title">Entregables Clave:</span>
                      <ul className="demo-deliverables-list">
                        {milestone.deliverables.map((item, dIdx) => (
                          <li key={dIdx}>✓ {item}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </div>

        <footer className="demo-modal-footer">
          <div className="demo-footer-info">
            <span>Repositorio Público: <strong>SantiDev11/AI-Code-Analyzer</strong></span>
          </div>
          <button type="button" className="demo-footer-close-button" onClick={onClose}>
            Cerrar
          </button>
        </footer>
      </div>
    </div>
  );
};
