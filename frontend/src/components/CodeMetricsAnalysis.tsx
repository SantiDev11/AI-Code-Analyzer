import React from 'react';
import type { Metrics, LargeFile } from '../types';
import { formatBytes, formatNumber } from '../utils/format';

interface CodeMetricsAnalysisProps {
  metrics: Metrics | null | undefined;
}

interface MetricCardProps {
  label: string;
  value: string;
  hint?: string;
}

interface ExtensionItem {
  extension: string;
  count: number;
  percentage: number;
}

/** Cuantas extensiones se listan como maximo antes de agrupar el resto. */
const MAX_EXTENSIONS = 12;

/** Cuantos archivos pesados se listan como maximo. */
const MAX_LARGEST_FILES = 10;

/**
 * Convierte un recuento del backend en texto seguro: nunca NaN, Infinity,
 * null ni undefined llegan a la interfaz.
 */
function formatCount(value: number | null | undefined): string {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    return 'No disponible';
  }
  return formatNumber(Math.trunc(value));
}

function safeNumber(value: number | null | undefined): number {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    return 0;
  }
  return value;
}

const MetricCard: React.FC<MetricCardProps> = ({ label, value, hint }) => (
  <div className="metrics-stat-card">
    <dt className="metrics-stat-label">{label}</dt>
    <dd className="metrics-stat-value">
      {value}
      {hint ? <span className="metrics-stat-hint">{hint}</span> : null}
    </dd>
  </div>
);

const LargestFileList: React.FC<{ files: LargeFile[] }> = ({ files }) => {
  // El backend no garantiza el orden: se ordena de mayor a menor por tamano.
  const sorted = [...files].sort((a, b) => safeNumber(b.size_bytes) - safeNumber(a.size_bytes));
  const visible = sorted.slice(0, MAX_LARGEST_FILES);

  return (
    <ul className="metrics-files-list" aria-label="Archivos más pesados del repositorio">
      {visible.map((file, index) => (
        <li className="metrics-file-item" key={`${file.path}-${index}`}>
          <code className="metrics-file-path">{file.path}</code>
          <span className="metrics-file-size">{formatBytes(safeNumber(file.size_bytes))}</span>
        </li>
      ))}
    </ul>
  );
};

const MetricsEmptySection: React.FC = () => (
  <section className="metrics-section" id="code-metrics-analysis" aria-labelledby="metrics-heading">
    <div className="analyzer-container">
      <div className="metrics-card">
        <header className="metrics-header">
          <span className="repo-section-badge">Estructura y Volumen</span>
          <div className="metrics-title-row">
            <h2 id="metrics-heading" className="metrics-title">
              Métricas de Código
            </h2>
          </div>
        </header>
        <div className="metrics-empty" role="status">
          <p className="repo-text-muted">
            No hay métricas de código disponibles para este repositorio.
          </p>
        </div>
      </div>
    </div>
  </section>
);

export const CodeMetricsAnalysis: React.FC<CodeMetricsAnalysisProps> = ({ metrics }) => {
  if (!metrics) {
    return <MetricsEmptySection />;
  }

  const treeAvailable = metrics.tree_available === true;
  const treeTruncated = metrics.tree_truncated === true;

  const extensionEntries = metrics.file_extensions ? Object.entries(metrics.file_extensions) : [];
  const validExtensions = extensionEntries.filter(
    ([, count]) => typeof count === 'number' && Number.isFinite(count) && count > 0
  );
  validExtensions.sort((a, b) => b[1] - a[1]);

  const maxExtensionCount = validExtensions.length > 0 ? validExtensions[0][1] : 0;
  const extensionItems: ExtensionItem[] = validExtensions
    .slice(0, MAX_EXTENSIONS)
    .map(([extension, count]) => ({
      extension,
      count,
      percentage: maxExtensionCount > 0 ? (count / maxExtensionCount) * 100 : 0,
    }));
  const hiddenExtensions = Math.max(validExtensions.length - extensionItems.length, 0);

  const largestFiles = metrics.largest_files ?? [];
  const hasLargestFiles = largestFiles.length > 0;
  const hiddenLargestFiles = Math.max(largestFiles.length - MAX_LARGEST_FILES, 0);

  // lines_of_code es null cuando no se puede calcular: no se convierte en cero.
  const linesOfCodeAvailable =
    typeof metrics.lines_of_code === 'number' && Number.isFinite(metrics.lines_of_code);

  return (
    <section
      className="metrics-section"
      id="code-metrics-analysis"
      aria-labelledby="metrics-heading"
    >
      <div className="analyzer-container">
        <div className="metrics-card">
          <header className="metrics-header">
            <span className="repo-section-badge">Estructura y Volumen</span>
            <div className="metrics-title-row">
              <h2 id="metrics-heading" className="metrics-title">
                Métricas de Código
              </h2>
              <div className="metrics-tree-badges">
                <span
                  className={`metrics-tree-badge ${treeAvailable ? 'is-available' : 'is-unavailable'}`}
                  role="status"
                >
                  {treeAvailable ? 'Tree available' : 'Tree unavailable'}
                </span>
                {treeTruncated ? (
                  <span className="metrics-tree-badge is-truncated" role="status">
                    Tree truncated
                  </span>
                ) : null}
              </div>
            </div>
            <p className="metrics-subtitle">
              Recuentos objetivos de archivos, directorios y tamaños obtenidos del árbol de archivos
              del repositorio.
            </p>
          </header>

          {!treeAvailable ? (
            <p className="metrics-notice is-warning" role="status">
              El árbol de archivos no estuvo disponible: los recuentos que se muestran pueden ser
              incompletos o iguales a cero.
            </p>
          ) : null}

          {treeTruncated ? (
            <p className="metrics-notice is-warning" role="status">
              GitHub truncó el árbol de archivos por superar su límite de elementos. Estas métricas
              describen una muestra parcial del repositorio, no su totalidad.
            </p>
          ) : null}

          {/* Resumen metrico semantico dl/dt/dd */}
          <div className="metrics-stats-container">
            <dl className="metrics-stats-list">
              <MetricCard label="Files" value={formatCount(metrics.total_files)} />
              <MetricCard label="Directories" value={formatCount(metrics.total_directories)} />
              <MetricCard label="Source Files" value={formatCount(metrics.source_files)} />
              <MetricCard label="Test Files" value={formatCount(metrics.test_files)} />
              <MetricCard
                label="Documentation Files"
                value={formatCount(metrics.documentation_files)}
              />
              <MetricCard
                label="Configuration Files"
                value={formatCount(metrics.configuration_files)}
              />
            </dl>
          </div>

          {/* Lineas de codigo: null no es cero */}
          <article className="metrics-block" aria-labelledby="metrics-loc-heading">
            <h3 id="metrics-loc-heading" className="metrics-block-title">
              Líneas de código
            </h3>
            {linesOfCodeAvailable ? (
              <p className="metrics-loc-value">
                {formatCount(metrics.lines_of_code)} <span className="metrics-loc-unit">LOC</span>
              </p>
            ) : (
              <p className="metrics-loc-unavailable">
                Lines of code unavailable — no se calculan sin descargar el contenido completo del
                repositorio.
              </p>
            )}
          </article>

          {/* Distribucion por extension */}
          <article className="metrics-block" aria-labelledby="metrics-extensions-heading">
            <h3 id="metrics-extensions-heading" className="metrics-block-title">
              Distribución por extensión
            </h3>
            {extensionItems.length === 0 ? (
              <p className="repo-text-muted" role="status">
                No se detectaron extensiones de archivo en este repositorio.
              </p>
            ) : (
              <>
                <ul
                  className="metrics-extensions-list"
                  aria-label="Distribución de archivos por extensión"
                >
                  {extensionItems.map((item) => (
                    <li className="metrics-extension-item" key={item.extension}>
                      <span className="metrics-extension-head">
                        <code className="metrics-extension-name">{item.extension}</code>
                        <span className="metrics-extension-count">
                          {formatCount(item.count)} archivos
                        </span>
                      </span>
                      <span className="metrics-extension-track" aria-hidden="true">
                        <span
                          className="metrics-extension-fill"
                          style={{ width: `${item.percentage.toFixed(1)}%` }}
                        />
                      </span>
                    </li>
                  ))}
                </ul>
                {hiddenExtensions > 0 ? (
                  <p className="metrics-list-note">
                    Se muestran las {extensionItems.length} extensiones más frecuentes de{' '}
                    {formatCount(validExtensions.length)} detectadas.
                  </p>
                ) : null}
              </>
            )}
          </article>

          {/* Archivos mas pesados */}
          <article className="metrics-block" aria-labelledby="metrics-largest-heading">
            <h3 id="metrics-largest-heading" className="metrics-block-title">
              Archivos más pesados
            </h3>
            {!hasLargestFiles ? (
              <p className="repo-text-muted" role="status">
                No se detectaron archivos destacados por tamaño en este repositorio.
              </p>
            ) : (
              <>
                <LargestFileList files={largestFiles} />
                {hiddenLargestFiles > 0 ? (
                  <p className="metrics-list-note">
                    Se muestran los {MAX_LARGEST_FILES} archivos más pesados de{' '}
                    {formatCount(largestFiles.length)} registrados.
                  </p>
                ) : null}
              </>
            )}
          </article>
        </div>
      </div>
    </section>
  );
};
