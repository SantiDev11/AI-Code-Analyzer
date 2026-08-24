import { describe, test, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { CodeMetricsAnalysis } from './CodeMetricsAnalysis';
import type { Metrics } from '../types';

const mockMetrics: Metrics = {
  tree_available: true,
  tree_truncated: false,
  total_files: 1240,
  total_directories: 186,
  source_files: 820,
  test_files: 213,
  documentation_files: 54,
  configuration_files: 37,
  file_extensions: {
    '.py': 420,
    '.ts': 310,
    '.md': 54,
    '.json': 37,
    '.css': 12,
  },
  largest_files: [
    { path: 'docs/assets/architecture-diagram.png', size_bytes: 5 * 1024 * 1024 },
    { path: 'app/services/github_client.py', size_bytes: 1536 },
    { path: 'frontend/src/styles/main.css', size_bytes: 96 * 1024 },
    { path: 'README.md', size_bytes: 512 },
  ],
  lines_of_code: null,
};

const emptyMetrics: Metrics = {
  tree_available: false,
  tree_truncated: false,
  total_files: 0,
  total_directories: 0,
  source_files: 0,
  test_files: 0,
  documentation_files: 0,
  configuration_files: 0,
  file_extensions: {},
  largest_files: [],
  lines_of_code: null,
};

describe('CodeMetricsAnalysis Component', () => {
  test('1. Renderiza las métricas básicas dentro de una section identificada', () => {
    const html = renderToStaticMarkup(<CodeMetricsAnalysis metrics={mockMetrics} />);

    expect(html).toContain('<section class="metrics-section"');
    expect(html).toContain('id="code-metrics-analysis"');
    expect(html).toContain('Métricas de Código');
    expect(html).toContain('Files');
    expect(html).toContain('Directories');
  });

  test('2. Muestra el total de archivos (total_files)', () => {
    const html = renderToStaticMarkup(<CodeMetricsAnalysis metrics={mockMetrics} />);

    expect(html).toContain('>Files</dt>');
    // El separador de miles depende del locale del entorno (1,240 / 1.240).
    expect(html).toMatch(/1[.,]240/);
  });

  test('3. Muestra el total de directorios (total_directories)', () => {
    const html = renderToStaticMarkup(<CodeMetricsAnalysis metrics={mockMetrics} />);

    expect(html).toContain('>Directories</dt>');
    expect(html).toContain('186');
  });

  test('4. Muestra los archivos de código fuente (source_files)', () => {
    const html = renderToStaticMarkup(<CodeMetricsAnalysis metrics={mockMetrics} />);

    expect(html).toContain('>Source Files</dt>');
    expect(html).toContain('820');
  });

  test('5. Muestra los archivos de test (test_files)', () => {
    const html = renderToStaticMarkup(<CodeMetricsAnalysis metrics={mockMetrics} />);

    expect(html).toContain('>Test Files</dt>');
    expect(html).toContain('213');
  });

  test('6. Muestra los archivos de documentación (documentation_files)', () => {
    const html = renderToStaticMarkup(<CodeMetricsAnalysis metrics={mockMetrics} />);

    expect(html).toContain('>Documentation Files</dt>');
    expect(html).toContain('54');
  });

  test('7. Muestra los archivos de configuración (configuration_files)', () => {
    const html = renderToStaticMarkup(<CodeMetricsAnalysis metrics={mockMetrics} />);

    expect(html).toContain('>Configuration Files</dt>');
    expect(html).toContain('37');
  });

  test('8. Muestra la distribución de extensiones con valor numérico visible', () => {
    const html = renderToStaticMarkup(<CodeMetricsAnalysis metrics={mockMetrics} />);

    expect(html).toContain('<code class="metrics-extension-name">.py</code>');
    expect(html).toContain('<code class="metrics-extension-name">.ts</code>');
    expect(html).toContain('420 archivos');
    expect(html).toContain('310 archivos');
  });

  test('9. Ordena las extensiones de mayor a menor', () => {
    const unordered: Metrics = {
      ...mockMetrics,
      file_extensions: { '.md': 5, '.py': 500, '.ts': 50 },
    };
    const html = renderToStaticMarkup(<CodeMetricsAnalysis metrics={unordered} />);

    const posPy = html.indexOf('>.py<');
    const posTs = html.indexOf('>.ts<');
    const posMd = html.indexOf('>.md<');

    expect(posPy).toBeGreaterThan(-1);
    expect(posPy).toBeLessThan(posTs);
    expect(posTs).toBeLessThan(posMd);
  });

  test('10. Muestra los archivos más pesados con su path en code', () => {
    const html = renderToStaticMarkup(<CodeMetricsAnalysis metrics={mockMetrics} />);

    expect(html).toContain('<code class="metrics-file-path">app/services/github_client.py</code>');
    expect(html).toContain('docs/assets/architecture-diagram.png');
    expect(html).toContain('<ul class="metrics-files-list"');
  });

  test('11. Ordena los archivos más pesados de mayor a menor tamaño', () => {
    const html = renderToStaticMarkup(<CodeMetricsAnalysis metrics={mockMetrics} />);

    const posPng = html.indexOf('docs/assets/architecture-diagram.png');
    const posCss = html.indexOf('frontend/src/styles/main.css');
    const posPy = html.indexOf('app/services/github_client.py');
    const posMd = html.indexOf('README.md');

    expect(posPng).toBeLessThan(posCss);
    expect(posCss).toBeLessThan(posPy);
    expect(posPy).toBeLessThan(posMd);
  });

  test('12. Formatea los tamaños en B, KB y MB legibles', () => {
    const html = renderToStaticMarkup(<CodeMetricsAnalysis metrics={mockMetrics} />);

    expect(html).toContain('5 MB');
    expect(html).toContain('96 KB');
    expect(html).toContain('1.5 KB');
    expect(html).toContain('512 B');
  });

  test('13. Con lines_of_code null no inventa un cero', () => {
    const html = renderToStaticMarkup(<CodeMetricsAnalysis metrics={mockMetrics} />);

    expect(html).toContain('Lines of code unavailable');
    expect(html).not.toContain('metrics-loc-value');
    expect(html).not.toContain('0 LOC');
  });

  test('13b. Con lines_of_code numérico muestra el valor real', () => {
    const withLoc: Metrics = { ...mockMetrics, lines_of_code: 84213 };
    const html = renderToStaticMarkup(<CodeMetricsAnalysis metrics={withLoc} />);

    expect(html).toMatch(/84[.,]213/);
    expect(html).toContain('LOC');
    expect(html).not.toContain('Lines of code unavailable');
  });

  test('14. Comunica el estado tree_available', () => {
    const htmlAvailable = renderToStaticMarkup(<CodeMetricsAnalysis metrics={mockMetrics} />);
    expect(htmlAvailable).toContain('Tree available');
    expect(htmlAvailable).not.toContain('Tree unavailable');

    const htmlUnavailable = renderToStaticMarkup(<CodeMetricsAnalysis metrics={emptyMetrics} />);
    expect(htmlUnavailable).toContain('Tree unavailable');
    expect(htmlUnavailable).toContain('El árbol de archivos no estuvo disponible');
  });

  test('15. Con tree_truncated advierte de que las métricas son una muestra parcial', () => {
    const truncated: Metrics = { ...mockMetrics, tree_truncated: true };
    const html = renderToStaticMarkup(<CodeMetricsAnalysis metrics={truncated} />);

    expect(html).toContain('Tree truncated');
    expect(html).toContain('muestra parcial del repositorio');

    const notTruncated = renderToStaticMarkup(<CodeMetricsAnalysis metrics={mockMetrics} />);
    expect(notTruncated).not.toContain('Tree truncated');
  });

  test('16. Métricas vacías, null o undefined se manejan con estados explícitos', () => {
    const htmlEmpty = renderToStaticMarkup(<CodeMetricsAnalysis metrics={emptyMetrics} />);
    expect(htmlEmpty).toContain('No se detectaron extensiones de archivo');
    expect(htmlEmpty).toContain('No se detectaron archivos destacados por tamaño');
    expect(htmlEmpty).not.toContain('<ul class="metrics-extensions-list"');
    expect(htmlEmpty).not.toContain('<ul class="metrics-files-list"');

    const htmlNull = renderToStaticMarkup(<CodeMetricsAnalysis metrics={null} />);
    expect(htmlNull).toContain('No hay métricas de código disponibles');

    const htmlUndefined = renderToStaticMarkup(<CodeMetricsAnalysis metrics={undefined} />);
    expect(htmlUndefined).toContain('No hay métricas de código disponibles');
  });

  test('17. Ausencia absoluta de null, undefined, NaN o Infinity en texto visible', () => {
    const html = renderToStaticMarkup(<CodeMetricsAnalysis metrics={mockMetrics} />);

    expect(html).not.toContain('>null<');
    expect(html).not.toContain('>undefined<');
    expect(html).not.toContain('NaN');
    expect(html).not.toContain('Infinity');

    const htmlEmpty = renderToStaticMarkup(<CodeMetricsAnalysis metrics={emptyMetrics} />);
    expect(htmlEmpty).not.toContain('NaN');
    expect(htmlEmpty).not.toContain('Infinity');
    expect(htmlEmpty).not.toContain('>undefined<');
  });

  test('18. Cumple accesibilidad con estructura semántica dl, dt, dd, ul, li, code', () => {
    const html = renderToStaticMarkup(<CodeMetricsAnalysis metrics={mockMetrics} />);

    expect(html).toContain('aria-labelledby="metrics-heading"');
    expect(html).toContain('<h2 id="metrics-heading"');
    expect(html).toContain('<dl class="metrics-stats-list"');
    expect(html).toContain('<dt');
    expect(html).toContain('<dd');
    expect(html).toContain('<ul class="metrics-extensions-list"');
    expect(html).toContain('<li class="metrics-extension-item"');
    expect(html).toContain('<article class="metrics-block"');
    expect(html).toContain('<code');
    // Las barras son decorativas: el valor numerico siempre esta como texto.
    expect(html).toContain('class="metrics-extension-track" aria-hidden="true"');
    expect(html).toContain('420 archivos');
  });

  test('19. Los paths y extensiones muy largos se renderizan completos', () => {
    const longPath =
      'packages/backend/src/infrastructure/adapters/persistence/repositories/generated/very_long_module_name_for_testing.py';
    const longMetrics: Metrics = {
      ...mockMetrics,
      file_extensions: { '.averyveryverylongcustomextensionname': 9 },
      largest_files: [{ path: longPath, size_bytes: 2048 }],
    };
    const html = renderToStaticMarkup(<CodeMetricsAnalysis metrics={longMetrics} />);

    expect(html).toContain(longPath);
    expect(html).toContain('.averyveryverylongcustomextensionname');
    expect(html).toContain('2 KB');
  });
});
