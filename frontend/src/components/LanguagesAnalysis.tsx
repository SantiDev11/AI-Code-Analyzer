import React from 'react';
import { formatBytes } from '../utils/format';

interface LanguagesAnalysisProps {
  languages: Record<string, number> | null | undefined;
}

interface LanguageItem {
  name: string;
  bytes: number;
  percentage: number;
  formattedBytes: string;
  formattedPercentage: string;
}

// Colores tecnicos predefinidos para lenguajes comunes de GitHub
const LANGUAGE_COLORS: Record<string, string> = {
  Python: '#3572A5',
  TypeScript: '#3178C6',
  JavaScript: '#F7DF1E',
  HTML: '#E34C26',
  CSS: '#563D7C',
  Rust: '#DEA584',
  Go: '#00ADD8',
  Java: '#B07219',
  'C++': '#F34B7D',
  C: '#555555',
  'C#': '#178600',
  PHP: '#4F5D95',
  Ruby: '#701516',
  Shell: '#89E051',
  Kotlin: '#A97BFF',
  Swift: '#F05138',
  Dart: '#00B4AB',
};

const DEFAULT_COLOR_PALETTE = [
  '#2f81f7',
  '#3fb950',
  '#d29922',
  '#db61a2',
  '#a371f7',
  '#79c0ff',
  '#56d364',
  '#e3b341',
];

function getLanguageColor(name: string, index: number): string {
  if (LANGUAGE_COLORS[name]) {
    return LANGUAGE_COLORS[name];
  }
  return DEFAULT_COLOR_PALETTE[index % DEFAULT_COLOR_PALETTE.length];
}

export const LanguagesAnalysis: React.FC<LanguagesAnalysisProps> = ({ languages }) => {
  // Manejo de casos nulos, indefinidos o vacios
  const entries = languages ? Object.entries(languages) : [];

  // Filtrar entradas invalidas o con bytes menores a 0
  const validEntries = entries.filter(
    ([, bytes]) => typeof bytes === 'number' && Number.isFinite(bytes) && bytes >= 0
  );

  // Ordenar siempre de mayor a menor cantidad de bytes
  validEntries.sort((a, b) => b[1] - a[1]);

  const totalBytes = validEntries.reduce((acc, [, bytes]) => acc + bytes, 0);

  const items: LanguageItem[] = validEntries.map(([name, bytes]) => {
    let percentage = 0;
    if (totalBytes > 0) {
      percentage = (bytes / totalBytes) * 100;
    }

    // Formatear porcentaje evitando NaN/Infinity
    const safePercentage = Number.isFinite(percentage) ? percentage : 0;
    const formattedPercentage =
      safePercentage > 0 && safePercentage < 0.1
        ? '< 0.1%'
        : `${safePercentage.toFixed(1)}%`;

    return {
      name,
      bytes,
      percentage: safePercentage,
      formattedBytes: formatBytes(bytes),
      formattedPercentage,
    };
  });

  return (
    <section
      className="languages-section"
      id="languages-analysis"
      aria-labelledby="languages-heading"
    >
      <div className="analyzer-container">
        <div className="languages-card">
          <header className="languages-header">
            <span className="repo-section-badge">Distribución de Código</span>
            <div className="languages-title-row">
              <h2 id="languages-heading" className="languages-title">
                Languages
              </h2>
              {totalBytes > 0 && (
                <span className="languages-total-bytes">
                  Total escaneado: <strong>{formatBytes(totalBytes)}</strong>
                </span>
              )}
            </div>
            <p className="languages-subtitle">
              Desglose cuantitativo del volumen de código por lenguaje detectado en el repositorio.
            </p>
          </header>

          {items.length === 0 ? (
            <div className="languages-empty" role="status">
              <p className="repo-text-muted">
                No se detectaron datos de lenguajes de programación en este repositorio.
              </p>
            </div>
          ) : (
            <div className="languages-content">
              {/* Barra horizontal visual agregada */}
              <div
                className="languages-stacked-bar"
                role="img"
                aria-label={`Distribución de lenguajes: ${items.map((i) => `${i.name} ${i.formattedPercentage}`).join(', ')}`}
              >
                {items.map((item, index) => {
                  const color = getLanguageColor(item.name, index);
                  return (
                    <div
                      key={item.name}
                      className="languages-bar-segment"
                      style={{
                        width: `${item.percentage}%`,
                        backgroundColor: color,
                      }}
                      title={`${item.name}: ${item.formattedPercentage} (${item.formattedBytes})`}
                    />
                  );
                })}
              </div>

              {/* Lista detallada semantica con barras individuales */}
              <ul className="languages-list" aria-label="Lista detallada de lenguajes">
                {items.map((item, index) => {
                  const color = getLanguageColor(item.name, index);
                  return (
                    <li key={item.name} className="languages-item">
                      <div className="languages-item-header">
                        <div className="languages-item-name-wrap">
                          <span
                            className="languages-dot"
                            style={{ backgroundColor: color }}
                            aria-hidden="true"
                          />
                          <span className="languages-item-name">{item.name}</span>
                        </div>
                        <div className="languages-item-stats">
                          <span className="languages-item-percent">
                            {item.formattedPercentage}
                          </span>
                          <span className="languages-item-bytes">
                            {item.formattedBytes}
                          </span>
                        </div>
                      </div>

                      {/* Barra de progreso individual para este lenguaje */}
                      <div
                        className="languages-progress-track"
                        role="progressbar"
                        aria-valuenow={Math.round(item.percentage)}
                        aria-valuemin={0}
                        aria-valuemax={100}
                        aria-label={`Porcentaje de ${item.name}`}
                      >
                        <div
                          className="languages-progress-fill"
                          style={{
                            width: `${Math.max(item.percentage, 0.5)}%`,
                            backgroundColor: color,
                          }}
                        />
                      </div>
                    </li>
                  );
                })}
              </ul>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};
