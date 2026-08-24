import { describe, test, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { CodeQualityAnalysis } from './CodeQualityAnalysis';
import type { Quality } from '../types';

const mockQualityFull: Quality = {
  tree_available: true,
  tree_truncated: false,
  files_scanned: 150,
  tests: {
    detected: true,
    files: 12,
    directories: ['tests', 'tests/unit'],
  },
  documentation: {
    readme: true,
    contributing: true,
    docs_directory: true,
    files: ['README.md', 'CONTRIBUTING.md', 'docs/index.md'],
  },
  ci: {
    detected: true,
    files: ['.github/workflows/test.yml', '.github/workflows/lint.yml'],
  },
  linting: {
    detected: true,
    files: ['.flake8', 'ruff.toml'],
  },
  formatting: {
    detected: true,
    files: ['.editorconfig', '.prettierrc'],
  },
  type_checking: {
    detected: true,
    files: ['mypy.ini', 'tsconfig.json'],
  },
  dependencies: {
    detected: true,
    files: ['pyproject.toml', 'package.json'],
  },
  coverage: {
    configured: true,
    percentage: 94.5,
    files: ['.coveragerc'],
  },
  undetermined_config: ['pyproject.toml'],
};

describe('CodeQualityAnalysis Component', () => {
  test('1. Muestra señal de tests como "Detectado" con archivos y directorios', () => {
    const html = renderToStaticMarkup(<CodeQualityAnalysis quality={mockQualityFull} />);

    expect(html).toContain('Tests');
    expect(html).toContain('Detectado');
    expect(html).toContain('12');
    expect(html).toContain('tests/unit');
  });

  test('2. Muestra señal de tests como "No detectado"', () => {
    const quality: Quality = {
      ...mockQualityFull,
      tests: {
        detected: false,
        files: 0,
        directories: [],
      },
    };
    const html = renderToStaticMarkup(<CodeQualityAnalysis quality={quality} />);

    expect(html).toContain('Tests');
    expect(html).toContain('No detectado');
  });

  test('3. Muestra señal de tests como "No disponible" cuando detected es null', () => {
    const quality: Quality = {
      ...mockQualityFull,
      tests: {
        detected: null,
        files: 0,
        directories: [],
      },
    };
    const html = renderToStaticMarkup(<CodeQualityAnalysis quality={quality} />);

    expect(html).toContain('Tests');
    expect(html).toContain('No disponible');
  });

  test('4. Muestra señal de documentación detectada con detalles de README, CONTRIBUTING y docs/', () => {
    const html = renderToStaticMarkup(<CodeQualityAnalysis quality={mockQualityFull} />);

    expect(html).toContain('Documentación');
    expect(html).toContain('Detectado');
    expect(html).toContain('README:');
    expect(html).toContain('Presente');
    expect(html).toContain('CONTRIBUTING:');
    expect(html).toContain('Directorio docs/:');
  });

  test('5. Muestra documentación no detectada', () => {
    const quality: Quality = {
      ...mockQualityFull,
      documentation: {
        readme: false,
        contributing: false,
        docs_directory: false,
        files: [],
      },
    };
    const html = renderToStaticMarkup(<CodeQualityAnalysis quality={quality} />);

    expect(html).toContain('Documentación');
    expect(html).toContain('No detectado');
    expect(html).toContain('No encontrado');
  });

  test('6. Muestra cobertura con porcentaje numérico cuando está disponible', () => {
    const html = renderToStaticMarkup(<CodeQualityAnalysis quality={mockQualityFull} />);

    expect(html).toContain('Cobertura de Tests');
    expect(html).toContain('94.5%');
  });

  test('7. Muestra "Coverage unavailable" cuando percentage es null sin mostrar 0%', () => {
    const quality: Quality = {
      ...mockQualityFull,
      coverage: {
        configured: true,
        percentage: null,
        files: ['.coveragerc'],
      },
    };
    const html = renderToStaticMarkup(<CodeQualityAnalysis quality={quality} />);

    expect(html).toContain('Coverage unavailable');
    expect(html).not.toContain('0%');
  });

  test('8. Muestra Integración Continua (CI) detectada con archivos de workflow', () => {
    const html = renderToStaticMarkup(<CodeQualityAnalysis quality={mockQualityFull} />);

    expect(html).toContain('Integración Continua (CI)');
    expect(html).toContain('Detectado');
    expect(html).toContain('.github/workflows/test.yml');
  });

  test('9. Muestra Linters detectados con archivos de configuración', () => {
    const html = renderToStaticMarkup(<CodeQualityAnalysis quality={mockQualityFull} />);

    expect(html).toContain('Linters y Análisis Estático');
    expect(html).toContain('Detectado');
    expect(html).toContain('ruff.toml');
  });

  test('10. Muestra Formateadores de Código detectados', () => {
    const html = renderToStaticMarkup(<CodeQualityAnalysis quality={mockQualityFull} />);

    expect(html).toContain('Formateadores de Código');
    expect(html).toContain('Detectado');
    expect(html).toContain('.editorconfig');
  });

  test('11. Muestra Comprobación de Tipos (Type Checking) detectada', () => {
    const html = renderToStaticMarkup(<CodeQualityAnalysis quality={mockQualityFull} />);

    expect(html).toContain('Comprobación de Tipos');
    expect(html).toContain('Detectado');
    expect(html).toContain('mypy.ini');
  });

  test('12. Distingue con precisión valores null como "No disponible" sin convertirlos a false', () => {
    const qualityNullSignals: Quality = {
      tree_available: false,
      tree_truncated: true,
      files_scanned: 0,
      tests: { detected: null, files: 0, directories: [] },
      documentation: { readme: null, contributing: null, docs_directory: null, files: [] },
      ci: { detected: null, files: [] },
      linting: { detected: null, files: [] },
      formatting: { detected: null, files: [] },
      type_checking: { detected: null, files: [] },
      dependencies: { detected: null, files: [] },
      coverage: { configured: null, percentage: null, files: [] },
      undetermined_config: [],
    };
    const html = renderToStaticMarkup(<CodeQualityAnalysis quality={qualityNullSignals} />);

    expect(html).toContain('No disponible');
    expect(html).not.toContain('>null<');
    expect(html).not.toContain('>undefined<');
  });

  test('13. Ausencia absoluta de null, undefined o NaN en el contenido visible', () => {
    const html = renderToStaticMarkup(<CodeQualityAnalysis quality={mockQualityFull} />);

    expect(html).not.toContain('>null<');
    expect(html).not.toContain('>undefined<');
    expect(html).not.toContain('NaN');
  });

  test('14. Estructura semántica y accesible con section, header, h2, ul, li, article, dl, dt, dd', () => {
    const html = renderToStaticMarkup(<CodeQualityAnalysis quality={mockQualityFull} />);

    expect(html).toContain('<section class="quality-section"');
    expect(html).toContain('id="code-quality-analysis"');
    expect(html).toContain('<header class="quality-header"');
    expect(html).toContain('<h2 id="quality-heading"');
    expect(html).toContain('<ul class="quality-grid"');
    expect(html).toContain('<article class="quality-signal-card"');
    expect(html).toContain('<dl class="quality-signal-details"');
    expect(html).toContain('<dt');
    expect(html).toContain('<dd');
  });

  test('15. Maneja correctamente estado vacío cuando quality es null o undefined', () => {
    const htmlNull = renderToStaticMarkup(<CodeQualityAnalysis quality={null} />);
    expect(htmlNull).toContain('No hay información de calidad disponible');

    const htmlUndefined = renderToStaticMarkup(<CodeQualityAnalysis quality={undefined} />);
    expect(htmlUndefined).toContain('No hay información de calidad disponible');
  });
});
