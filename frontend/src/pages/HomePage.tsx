import React, { useState } from 'react';
import { Header } from '../components/Header';
import { RepositoryForm } from '../components/RepositoryForm';
import { FeatureOverview } from '../components/FeatureOverview';
import { Footer } from '../components/Footer';
import type { AnalysisResponse } from '../types';

export const HomePage: React.FC = () => {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);

  const handleAnalysisSuccess = (data: AnalysisResponse) => {
    setAnalysisResult(data);
  };

  const handleAnalysisStart = () => {
    setAnalysisResult(null);
  };

  return (
    <>
      <a href="#analyzer" className="analyzer-skip-link">
        Saltar al formulario de análisis
      </a>
      <Header />
      <main id="main-content">
        <RepositoryForm
          onAnalysisSuccess={handleAnalysisSuccess}
          onAnalysisStart={handleAnalysisStart}
        />

        {analysisResult && (
          <section
            className="analyzer-container"
            style={{ paddingTop: '2rem', paddingBottom: '2rem' }}
            aria-labelledby="success-summary-heading"
          >
            <div
              className="analyzer-form-card"
              style={{ borderColor: 'var(--color-success)' }}
              role="region"
              aria-live="polite"
            >
              <header style={{ marginBottom: '1rem' }}>
                <span className="analyzer-badge" style={{ color: 'var(--color-success)', borderColor: 'var(--color-success)' }}>
                  ✓ Análisis Recibido Exitosamente
                </span>
                <h2 id="success-summary-heading" style={{ fontSize: '1.5rem', marginTop: '0.5rem', color: 'var(--color-text-primary)' }}>
                  {analysisResult.repository.full_name}
                </h2>
                <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9375rem', marginTop: '0.25rem' }}>
                  {analysisResult.repository.description || 'Sin descripción proporcionada'}
                </p>
              </header>

              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                  gap: '1rem',
                  paddingTop: '1rem',
                  borderTop: '1px solid var(--color-border)',
                }}
              >
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Lenguaje Principal</span>
                  <p style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>{analysisResult.repository.primary_language || 'N/A'}</p>
                </div>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Estrellas</span>
                  <p style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>{analysisResult.repository.stars.toLocaleString()}</p>
                </div>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Archivos Escaneados</span>
                  <p style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>{analysisResult.metrics.total_files}</p>
                </div>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Tests Detectados</span>
                  <p style={{ fontWeight: 600, color: analysisResult.quality.tests.detected ? 'var(--color-success)' : 'var(--color-text-muted)' }}>
                    {analysisResult.quality.tests.detected ? `Sí (${analysisResult.quality.tests.files} archivos)` : 'No detectados'}
                  </p>
                </div>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>AI Analysis</span>
                  <p style={{ fontWeight: 600, color: analysisResult.ai_analysis ? 'var(--color-accent)' : 'var(--color-text-muted)' }}>
                    {analysisResult.ai_analysis ? 'Disponible (Estructurado)' : 'No configurado'}
                  </p>
                </div>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Origen de Datos</span>
                  <p style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>
                    {analysisResult.cached ? 'Caché en memoria' : 'GitHub REST API en vivo'}
                  </p>
                </div>
              </div>
            </div>
          </section>
        )}

        <FeatureOverview />
      </main>
      <Footer />
    </>
  );
};
