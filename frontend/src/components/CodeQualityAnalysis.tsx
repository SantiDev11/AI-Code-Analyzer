import React from 'react';
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
            <p className="quality-subtitle">
              Señales objetivas de configuración, pruebas, documentación y automatización deducidas del árbol de archivos ({quality.files_scanned.toLocaleString()} archivos analizados).
            </p>
          </header>

          <ul className="quality-grid" aria-label="Señales de calidad del código">
            {/* 1. Tests */}
            <li className="quality-grid-item">
              <article className="quality-signal-card">
                <header className="quality-signal-header">
                  <h3 className="quality-signal-title">Tests</h3>
                  <StatusBadge status={testsStatus} />
                </header>
                <div className="quality-signal-body">
                  {tests ? (
                    <dl className="quality-signal-details">
                      <div className="quality-detail-row">
                        <dt className="quality-detail-label">Archivos de test:</dt>
                        <dd className="quality-detail-value">{tests.files.toLocaleString()}</dd>
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
                  <h3 className="quality-signal-title">Documentación</h3>
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
                  <h3 className="quality-signal-title">Cobertura de Tests</h3>
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
                  <h3 className="quality-signal-title">Integración Continua (CI)</h3>
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
                  <h3 className="quality-signal-title">Linters y Análisis Estático</h3>
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
                  <h3 className="quality-signal-title">Formateadores de Código</h3>
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
                  <h3 className="quality-signal-title">Comprobación de Tipos</h3>
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
                  <h3 className="quality-signal-title">Gestión de Dependencias</h3>
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
