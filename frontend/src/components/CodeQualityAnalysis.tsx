import React from 'react';
import { formatNumber } from '../utils/format';
import type {
  Quality,
  QualitySignal,
  TestsSignal,
  DocumentationSignal,
  CoverageSignal,
} from '../types';

interface CodeQualityAnalysisProps {
  quality: Quality | null | undefined;
}

type SignalStatus = 'detected' | 'not_detected' | 'unknown';

function resolveStatus(value: boolean | null | undefined): SignalStatus {
  if (value === true) return 'detected';
  if (value === false) return 'not_detected';
  return 'unknown';
}

const STATUS_LABELS: Record<SignalStatus, string> = {
  detected: 'Detectado',
  not_detected: 'No detectado',
  unknown: 'No disponible',
};

const STATUS_CLASSES: Record<SignalStatus, string> = {
  detected: 'is-detected',
  not_detected: 'is-not-detected',
  unknown: 'is-unknown',
};

const StatusBadge: React.FC<{ status: SignalStatus; label?: string }> = ({ status, label }) => {
  const displayLabel = label ?? STATUS_LABELS[status];
  return (
    <span className={`quality-status-badge ${STATUS_CLASSES[status]}`} role="status">
      <span className={`quality-status-dot ${STATUS_CLASSES[status]}`} aria-hidden="true" />
      <span>{displayLabel}</span>
    </span>
  );
};

export const CodeQualityAnalysis: React.FC<CodeQualityAnalysisProps> = ({ quality }) => {
  if (!quality) {
    return (
      <section
        className="quality-section"
        id="code-quality-analysis"
        aria-labelledby="quality-heading"
      >
        <div className="analyzer-container">
          <div className="quality-card">
            <header className="quality-header">
              <span className="repo-section-badge">Salud y Estándares</span>
              <div className="quality-title-row">
                <h2 id="quality-heading" className="quality-title">
                  Calidad de Código
                </h2>
              </div>
            </header>
            <div className="quality-empty" role="status">
              <p className="repo-text-muted">
                No hay información de calidad disponible para este repositorio.
              </p>
            </div>
          </div>
        </div>
      </section>
    );
  }

  const tests: TestsSignal | undefined = quality.tests;
  const docs: DocumentationSignal | undefined = quality.documentation;
  const coverage: CoverageSignal | undefined = quality.coverage;
  const ci: QualitySignal | undefined = quality.ci;
  const linting: QualitySignal | undefined = quality.linting;
  const formatting: QualitySignal | undefined = quality.formatting;
  const typeChecking: QualitySignal | undefined = quality.type_checking;
  const dependencies: QualitySignal | undefined = quality.dependencies;

  const testsStatus = resolveStatus(tests?.detected);
  const docsStatus = resolveStatus(
    docs ? (docs.readme || docs.contributing || docs.docs_directory ? true : docs.readme === false && docs.contributing === false && docs.docs_directory === false ? false : null) : null
  );
  const coverageStatus = resolveStatus(coverage?.configured);
  const ciStatus = resolveStatus(ci?.detected);
  const lintingStatus = resolveStatus(linting?.detected);
  const formattingStatus = resolveStatus(formatting?.detected);
  const typeCheckingStatus = resolveStatus(typeChecking?.detected);
  const dependenciesStatus = resolveStatus(dependencies?.detected);

  const totalSignals = 8;
  const detectedCount = [
    testsStatus === 'detected',
    docsStatus === 'detected',
    coverageStatus === 'detected',
    ciStatus === 'detected',
    lintingStatus === 'detected',
    formattingStatus === 'detected',
    typeCheckingStatus === 'detected',
    dependenciesStatus === 'detected',
  ].filter(Boolean).length;

  return (
    <section
      className="quality-section"
      id="code-quality-analysis"
      aria-labelledby="quality-heading"
    >
      <div className="analyzer-container">
        <div className="quality-card">
          <header className="quality-header">
            <div className="quality-header-top">
              <span className="repo-section-badge">Salud y Estándares</span>
              <div className="quality-summary-pill" aria-label={`${detectedCount} de ${totalSignals} estándares detectados`}>
                <span className="quality-summary-count">{detectedCount}/{totalSignals}</span>
                <span className="quality-summary-text">Señales Detectadas</span>
              </div>
            </div>
            <div className="quality-title-row">
              <h2 id="quality-heading" className="quality-title">
                Calidad de Código
              </h2>
            </div>
            <p className="quality-subtitle">
              Señales objetivas de configuración, pruebas, documentación y automatización deducidas del árbol de archivos ({formatNumber(quality.files_scanned)} archivos analizados).
            </p>
          </header>

          <ul className="quality-grid" aria-label="Señales de calidad del código">
            {/* 1. Tests */}
            <li className="quality-grid-item">
              <article className="quality-signal-card">
                <header className="quality-signal-header">
                  <div className="quality-signal-title-group">
                    <span className="quality-signal-icon" aria-hidden="true">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                        <polyline points="14 2 14 8 20 8"/>
                        <path d="m9 15 2 2 4-4"/>
                      </svg>
                    </span>
                    <h3 className="quality-signal-title">Tests</h3>
                  </div>
                  <StatusBadge status={testsStatus} />
                </header>
                <div className="quality-signal-body">
                  {tests ? (
                    <dl className="quality-signal-details">
                      <div className="quality-detail-row">
                        <dt className="quality-detail-label">Archivos de test:</dt>
                        <dd className="quality-detail-value">{formatNumber(tests.files)}</dd>
                      </div>
                      {tests.directories && tests.directories.length > 0 && (
                        <div className="quality-detail-row">
                          <dt className="quality-detail-label">Directorios:</dt>
                          <dd className="quality-detail-value">
                            <ul className="quality-files-list" aria-label="Directorios de tests">
                              {tests.directories.map((dir, idx) => (
                                <li key={idx}>
                                  <code className="quality-file-tag">{dir}</code>
                                </li>
                              ))}
                            </ul>
                          </dd>
                        </div>
                      )}
                    </dl>
                  ) : (
                    <p className="quality-signal-desc repo-text-muted">No disponible</p>
                  )}
                </div>
              </article>
            </li>

            {/* 2. Documentación */}
            <li className="quality-grid-item">
              <article className="quality-signal-card">
                <header className="quality-signal-header">
                  <div className="quality-signal-title-group">
                    <span className="quality-signal-icon" aria-hidden="true">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"/>
                        <path d="M6 6h10"/>
                        <path d="M6 10h10"/>
                      </svg>
                    </span>
                    <h3 className="quality-signal-title">Documentación</h3>
                  </div>
                  <StatusBadge status={docsStatus} />
                </header>
                <div className="quality-signal-body">
                  {docs ? (
                    <dl className="quality-signal-details">
                      <div className="quality-detail-row">
                        <dt className="quality-detail-label">README:</dt>
                        <dd className="quality-detail-value">
                          {docs.readme === true ? 'Presente' : docs.readme === false ? 'No encontrado' : 'No disponible'}
                        </dd>
                      </div>
                      <div className="quality-detail-row">
                        <dt className="quality-detail-label">CONTRIBUTING:</dt>
                        <dd className="quality-detail-value">
                          {docs.contributing === true ? 'Presente' : docs.contributing === false ? 'No encontrado' : 'No disponible'}
                        </dd>
                      </div>
                      <div className="quality-detail-row">
                        <dt className="quality-detail-label">Directorio docs/:</dt>
                        <dd className="quality-detail-value">
                          {docs.docs_directory === true ? 'Presente' : docs.docs_directory === false ? 'No encontrado' : 'No disponible'}
                        </dd>
                      </div>
                      {docs.files && docs.files.length > 0 && (
                        <div className="quality-detail-row">
                          <dt className="quality-detail-label">Archivos:</dt>
                          <dd className="quality-detail-value">
                            <ul className="quality-files-list" aria-label="Archivos de documentación">
                              {docs.files.map((file, idx) => (
                                <li key={idx}>
                                  <code className="quality-file-tag">{file}</code>
                                </li>
                              ))}
                            </ul>
                          </dd>
                        </div>
                      )}
                    </dl>
                  ) : (
                    <p className="quality-signal-desc repo-text-muted">No disponible</p>
                  )}
                </div>
              </article>
            </li>

            {/* 3. Coverage */}
            <li className="quality-grid-item">
              <article className="quality-signal-card">
                <header className="quality-signal-header">
                  <div className="quality-signal-title-group">
                    <span className="quality-signal-icon" aria-hidden="true">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                        <path d="m9 12 2 2 4-4"/>
                      </svg>
                    </span>
                    <h3 className="quality-signal-title">Cobertura de Tests</h3>
                  </div>
                  <StatusBadge status={coverageStatus} />
                </header>
                <div className="quality-signal-body">
                  {coverage ? (
                    <dl className="quality-signal-details">
                      <div className="quality-detail-row">
                        <dt className="quality-detail-label">Porcentaje:</dt>
                        <dd className="quality-detail-value">
                          {coverage.percentage !== null && coverage.percentage !== undefined
                            ? `${coverage.percentage}%`
                            : 'Coverage unavailable'}
                        </dd>
                      </div>
                      {coverage.files && coverage.files.length > 0 && (
                        <div className="quality-detail-row">
                          <dt className="quality-detail-label">Configuración:</dt>
                          <dd className="quality-detail-value">
                            <ul className="quality-files-list" aria-label="Archivos de configuración de cobertura">
                              {coverage.files.map((file, idx) => (
                                <li key={idx}>
                                  <code className="quality-file-tag">{file}</code>
                                </li>
                              ))}
                            </ul>
                          </dd>
                        </div>
                      )}
                    </dl>
                  ) : (
                    <p className="quality-signal-desc repo-text-muted">No disponible</p>
                  )}
                </div>
              </article>
            </li>

            {/* 4. CI */}
            <li className="quality-grid-item">
              <article className="quality-signal-card">
                <header className="quality-signal-header">
                  <div className="quality-signal-title-group">
                    <span className="quality-signal-icon" aria-hidden="true">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="12" cy="12" r="10"/>
                        <polyline points="12 6 12 12 16 14"/>
                      </svg>
                    </span>
                    <h3 className="quality-signal-title">Integración Continua (CI)</h3>
                  </div>
                  <StatusBadge status={ciStatus} />
                </header>
                <div className="quality-signal-body">
                  {ci && ci.files && ci.files.length > 0 ? (
                    <dl className="quality-signal-details">
                      <div className="quality-detail-row">
                        <dt className="quality-detail-label">Flujos detectados:</dt>
                        <dd className="quality-detail-value">
                          <ul className="quality-files-list" aria-label="Archivos de CI">
                            {ci.files.map((file, idx) => (
                              <li key={idx}>
                                <code className="quality-file-tag">{file}</code>
                              </li>
                            ))}
                          </ul>
                        </dd>
                      </div>
                    </dl>
                  ) : (
                    <p className="quality-signal-desc repo-text-muted">
                      {ciStatus === 'detected'
                        ? 'Configuración CI detectada'
                        : ciStatus === 'not_detected'
                        ? 'No se detectaron flujos de CI'
                        : 'No disponible'}
                    </p>
                  )}
                </div>
              </article>
            </li>

            {/* 5. Linting */}
            <li className="quality-grid-item">
              <article className="quality-signal-card">
                <header className="quality-signal-header">
                  <div className="quality-signal-title-group">
                    <span className="quality-signal-icon" aria-hidden="true">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                      </svg>
                    </span>
                    <h3 className="quality-signal-title">Linters y Análisis Estático</h3>
                  </div>
                  <StatusBadge status={lintingStatus} />
                </header>
                <div className="quality-signal-body">
                  {linting && linting.files && linting.files.length > 0 ? (
                    <dl className="quality-signal-details">
                      <div className="quality-detail-row">
                        <dt className="quality-detail-label">Herramientas:</dt>
                        <dd className="quality-detail-value">
                          <ul className="quality-files-list" aria-label="Archivos de linters">
                            {linting.files.map((file, idx) => (
                              <li key={idx}>
                                <code className="quality-file-tag">{file}</code>
                              </li>
                            ))}
                          </ul>
                        </dd>
                      </div>
                    </dl>
                  ) : (
                    <p className="quality-signal-desc repo-text-muted">
                      {lintingStatus === 'detected'
                        ? 'Herramientas de linting detectadas'
                        : lintingStatus === 'not_detected'
                        ? 'No se detectaron configuraciones de linter'
                        : 'No disponible'}
                    </p>
                  )}
                </div>
              </article>
            </li>

            {/* 6. Formatting */}
            <li className="quality-grid-item">
              <article className="quality-signal-card">
                <header className="quality-signal-header">
                  <div className="quality-signal-title-group">
                    <span className="quality-signal-icon" aria-hidden="true">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="4 7 4 4 20 4 20 7"/>
                        <line x1="9" y1="20" x2="15" y2="20"/>
                        <line x1="12" y1="4" x2="12" y2="20"/>
                      </svg>
                    </span>
                    <h3 className="quality-signal-title">Formateadores de Código</h3>
                  </div>
                  <StatusBadge status={formattingStatus} />
                </header>
                <div className="quality-signal-body">
                  {formatting && formatting.files && formatting.files.length > 0 ? (
                    <dl className="quality-signal-details">
                      <div className="quality-detail-row">
                        <dt className="quality-detail-label">Configuración:</dt>
                        <dd className="quality-detail-value">
                          <ul className="quality-files-list" aria-label="Archivos de formateo">
                            {formatting.files.map((file, idx) => (
                              <li key={idx}>
                                <code className="quality-file-tag">{file}</code>
                              </li>
                            ))}
                          </ul>
                        </dd>
                      </div>
                    </dl>
                  ) : (
                    <p className="quality-signal-desc repo-text-muted">
                      {formattingStatus === 'detected'
                        ? 'Formateadores configurados'
                        : formattingStatus === 'not_detected'
                        ? 'No se detectaron herramientas de formateo'
                        : 'No disponible'}
                    </p>
                  )}
                </div>
              </article>
            </li>

            {/* 7. Type Checking */}
            <li className="quality-grid-item">
              <article className="quality-signal-card">
                <header className="quality-signal-header">
                  <div className="quality-signal-title-group">
                    <span className="quality-signal-icon" aria-hidden="true">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="16 18 22 12 16 6"/>
                        <polyline points="8 6 2 12 8 18"/>
                      </svg>
                    </span>
                    <h3 className="quality-signal-title">Comprobación de Tipos</h3>
                  </div>
                  <StatusBadge status={typeCheckingStatus} />
                </header>
                <div className="quality-signal-body">
                  {typeChecking && typeChecking.files && typeChecking.files.length > 0 ? (
                    <dl className="quality-signal-details">
                      <div className="quality-detail-row">
                        <dt className="quality-detail-label">Archivos:</dt>
                        <dd className="quality-detail-value">
                          <ul className="quality-files-list" aria-label="Archivos de comprobación de tipos">
                            {typeChecking.files.map((file, idx) => (
                              <li key={idx}>
                                <code className="quality-file-tag">{file}</code>
                              </li>
                            ))}
                          </ul>
                        </dd>
                      </div>
                    </dl>
                  ) : (
                    <p className="quality-signal-desc repo-text-muted">
                      {typeCheckingStatus === 'detected'
                        ? 'Comprobadores de tipos detectados'
                        : typeCheckingStatus === 'not_detected'
                        ? 'No se detectó configuración de tipos'
                        : 'No disponible'}
                    </p>
                  )}
                </div>
              </article>
            </li>

            {/* 8. Dependencias */}
            <li className="quality-grid-item">
              <article className="quality-signal-card">
                <header className="quality-signal-header">
                  <div className="quality-signal-title-group">
                    <span className="quality-signal-icon" aria-hidden="true">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="m7.5 4.27 9 5.15"/>
                        <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/>
                        <path d="m3.3 7 8.7 5 8.7-5"/>
                        <path d="M12 22V12"/>
                      </svg>
                    </span>
                    <h3 className="quality-signal-title">Gestión de Dependencias</h3>
                  </div>
                  <StatusBadge status={dependenciesStatus} />
                </header>
                <div className="quality-signal-body">
                  {dependencies && dependencies.files && dependencies.files.length > 0 ? (
                    <dl className="quality-signal-details">
                      <div className="quality-detail-row">
                        <dt className="quality-detail-label">Gestores:</dt>
                        <dd className="quality-detail-value">
                          <ul className="quality-files-list" aria-label="Archivos de dependencias">
                            {dependencies.files.map((file, idx) => (
                              <li key={idx}>
                                <code className="quality-file-tag">{file}</code>
                              </li>
                            ))}
                          </ul>
                        </dd>
                      </div>
                    </dl>
                  ) : (
                    <p className="quality-signal-desc repo-text-muted">
                      {dependenciesStatus === 'detected'
                        ? 'Archivos de dependencias detectados'
                        : dependenciesStatus === 'not_detected'
                        ? 'No se detectaron manifiestos de dependencias'
                        : 'No disponible'}
                    </p>
                  )}
                </div>
              </article>
            </li>
          </ul>
        </div>
      </div>
    </section>
  );
};

