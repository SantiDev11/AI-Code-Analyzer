import React from 'react';
import type { FeatureItem } from '../types';

const FEATURES: FeatureItem[] = [
  {
    id: 'repository',
    title: 'Repository Metadata',
    badge: 'Metadata',
    description:
      'Extracción de metadatos oficiales: estrellas, forks, licencia SPDX, rama por defecto, topics y estado de archivado.',
  },
  {
    id: 'languages',
    title: 'Languages Breakdown',
    badge: 'Stack',
    description:
      'Distribución precisa del volumen de código en bytes por lenguaje detectado por lingüística en el repositorio.',
  },
  {
    id: 'contributors',
    title: 'Contributors & Impact',
    badge: 'Community',
    description:
      'Identificación del equipo de desarrollo, ranking de commits atribuidos y enlaces directos a perfiles verificados.',
  },
  {
    id: 'commits',
    title: 'Recent Commits',
    badge: 'History',
    description:
      'Auditoría de los últimos commits de la rama principal: hash SHA, mensajes de cambio, autoría y marcas temporales.',
  },
  {
    id: 'issues',
    title: 'Issues Tracking',
    badge: 'Workflow',
    description:
      'Muestreo de issues reales descartando pull requests, con recuento clasificado de abiertos y cerrados.',
  },
  {
    id: 'pull_requests',
    title: 'Pull Requests & Merges',
    badge: 'Collaboration',
    description:
      'Seguimiento de propuestas de cambio: estados abiertos, cerrados, mergeados, fechas y ramas de integración.',
  },
  {
    id: 'releases',
    title: 'Releases & Versioning',
    badge: 'Delivery',
    description:
      'Historial ordenado de versiones distinguiendo publicaciones oficiales, borradores internos y prereleases.',
  },
  {
    id: 'activity',
    title: 'Temporal Activity (UTC)',
    badge: 'Pace',
    description:
      'Línea de tiempo diaria calculada en días naturales UTC sin consumo adicional de cuota en la API de GitHub.',
  },
  {
    id: 'quality',
    title: 'Code Quality Signals',
    badge: 'Engineering',
    description:
      'Detección objetiva de suites de testing, documentación, workflows de CI/CD, linters, formatters y tipado estático.',
  },
  {
    id: 'metrics',
    title: 'Code Metrics & File Tree',
    badge: 'Metrics',
    description:
      'Conteo jerárquico de directorios, clasificación (fuente, tests, configs, docs), extensiones y top de archivos más pesados.',
  },
  {
    id: 'ai_analysis',
    title: 'AI Technical Analysis',
    badge: 'Intelligence',
    description:
      'Diagnóstico fundamentado estrictamente en evidencia real: resumen ejecutivo, fortalezas, aspectos de atención y recomendaciones accionables.',
  },
];

export const FeatureOverview: React.FC = () => {
  return (
    <section
      className="analyzer-features-section"
      id="features"
      aria-labelledby="features-heading"
    >
      <div className="analyzer-container">
        <header className="analyzer-features-header">
          <h2 id="features-heading" className="analyzer-section-title">
            Capacidades de Inspección Multidimensional
          </h2>
          <p className="analyzer-section-subtitle">
            11 módulos especializados diseñados para proporcionar visibilidad técnica total
            sin descargar dependencias ni ejecutar código ajeno.
          </p>
        </header>

        <div className="analyzer-features-grid">
          {FEATURES.map((feature) => (
            <article key={feature.id} className="analyzer-feature-card">
              <header className="analyzer-feature-header">
                <h3 className="analyzer-feature-title">{feature.title}</h3>
                <span className="analyzer-feature-badge">{feature.badge}</span>
              </header>
              <p className="analyzer-feature-desc">{feature.description}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
};
