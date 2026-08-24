import { describe, test, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { readFileSync } from 'fs';
import { resolve } from 'path';
import { AIAnalysis } from './AIAnalysis';
import type { AIAnalysis as AIAnalysisType } from '../types';

const mockAIAnalysis: AIAnalysisType = {
  summary:
    'FastAPI es un framework web maduro, altamente probado y con activa mantención por parte de la comunidad.',
  strengths: [
    'Suite de pruebas robusta con alta cobertura.',
    'Documentación exhaustiva en múltiples idiomas.',
    'Tipado estricto con validación basada en Pydantic.',
  ],
  concerns: [
    {
      title: 'Configuración de cobertura no detectada en raíz',
      description: 'No se identificó archivo .coveragerc explícito en el árbol raíz.',
      severity: 'low',
      evidence: 'CoverageSignal detected=False en archivos analizados.',
    },
    {
      title: 'Dependencias obsoletas en ramas secundarias',
      description: 'Se detectaron versiones fijadas sin actualizar en dependencias opcionales.',
      severity: 'medium',
      evidence: 'pyproject.toml contiene dependencias fijadas hace más de 180 días.',
    },
    {
      title: 'Archivos críticos sin linters activos',
      description: 'El flujo de CI no ejecuta comprobación de tipos sobre scripts auxiliares.',
      severity: 'high',
      evidence: 'Directorio scripts/ no está incluido en mypy.ini.',
    },
  ],
  recommendations: [
    {
      title: 'Asegurar reporte público de cobertura',
      description: 'Integrar reporte de Codecov en el flujo de CI para visibilidad pública.',
      priority: 'low',
    },
    {
      title: 'Automatizar escaneo de dependencias',
      description: 'Configurar Dependabot o Renovate para gestionar actualizaciones seguras.',
      priority: 'medium',
    },
    {
      title: 'Extender type checking a scripts',
      description: 'Incluir carpeta scripts/ en la configuración de mypy para evitar regresiones.',
      priority: 'high',
    },
  ],
  technical_overview: {
    architecture: 'Framework modular basado en Starlette y validación de tipos con Pydantic.',
    stack: 'Python, Starlette, Pydantic, Uvicorn, pytest.',
    activity_summary: 'Ritmo activo constante con releases periódicos y gestión activa de PRs.',
  },
};

describe('AIAnalysis Component', () => {
  test('1. Renderiza correctamente con un ai_analysis válido', () => {
    const html = renderToStaticMarkup(<AIAnalysis aiAnalysis={mockAIAnalysis} />);

    expect(html).toContain('<section class="ai-section"');
    expect(html).toContain('id="ai-analysis"');
    expect(html).toContain('Análisis Técnico con IA');
  });

  test('2. Muestra el resumen ejecutivo principal (summary)', () => {
    const html = renderToStaticMarkup(<AIAnalysis aiAnalysis={mockAIAnalysis} />);

    expect(html).toContain('Resumen Ejecutivo');
    expect(html).toContain(mockAIAnalysis.summary);
  });

  test('3. Muestra la lista de puntos fuertes (strengths)', () => {
    const html = renderToStaticMarkup(<AIAnalysis aiAnalysis={mockAIAnalysis} />);

    expect(html).toContain('Puntos Fuertes (Strengths)');
    expect(html).toContain('Suite de pruebas robusta con alta cobertura.');
    expect(html).toContain('Tipado estricto con validación basada en Pydantic.');
  });

  test('4. Muestra la sección de puntos de atención (concerns)', () => {
    const html = renderToStaticMarkup(<AIAnalysis aiAnalysis={mockAIAnalysis} />);

    expect(html).toContain('Puntos de Atención con Evidencia (Concerns)');
    expect(html).toContain('Configuración de cobertura no detectada en raíz');
  });

  test('5. Distingue visual y textualmente la severidad Low (Baja)', () => {
    const html = renderToStaticMarkup(<AIAnalysis aiAnalysis={mockAIAnalysis} />);

    expect(html).toContain('is-low');
    expect(html).toContain('Severidad: Baja (Low)');
  });

  test('6. Distingue visual y textualmente la severidad Medium (Media)', () => {
    const html = renderToStaticMarkup(<AIAnalysis aiAnalysis={mockAIAnalysis} />);

    expect(html).toContain('is-medium');
    expect(html).toContain('Severidad: Media (Medium)');
  });

  test('7. Distingue visual y textualmente la severidad High (Alta)', () => {
    const html = renderToStaticMarkup(<AIAnalysis aiAnalysis={mockAIAnalysis} />);

    expect(html).toContain('is-high');
    expect(html).toContain('Severidad: Alta (High)');
  });

  test('8. Muestra la evidencia detectada en cada concern', () => {
    const html = renderToStaticMarkup(<AIAnalysis aiAnalysis={mockAIAnalysis} />);

    expect(html).toContain('Evidencia detectada:');
    expect(html).toContain('CoverageSignal detected=False en archivos analizados.');
    expect(html).toContain('Directorio scripts/ no está incluido en mypy.ini.');
  });

  test('9. Muestra la lista de recomendaciones accionables', () => {
    const html = renderToStaticMarkup(<AIAnalysis aiAnalysis={mockAIAnalysis} />);

    expect(html).toContain('Recomendaciones Accionables');
    expect(html).toContain('Asegurar reporte público de cobertura');
    expect(html).toContain('Automatizar escaneo de dependencias');
  });

  test('10. Distingue visual y textualmente la prioridad Low (Baja)', () => {
    const html = renderToStaticMarkup(<AIAnalysis aiAnalysis={mockAIAnalysis} />);

    expect(html).toContain('Prioridad: Baja (Low)');
  });

  test('11. Distingue visual y textualmente la prioridad Medium (Media)', () => {
    const html = renderToStaticMarkup(<AIAnalysis aiAnalysis={mockAIAnalysis} />);

    expect(html).toContain('Prioridad: Media (Medium)');
  });

  test('12. Distingue visual y textualmente la prioridad High (Alta)', () => {
    const html = renderToStaticMarkup(<AIAnalysis aiAnalysis={mockAIAnalysis} />);

    expect(html).toContain('Prioridad: Alta (High)');
  });

  test('13. Muestra la visión técnica general (architecture, stack, activity_summary)', () => {
    const html = renderToStaticMarkup(<AIAnalysis aiAnalysis={mockAIAnalysis} />);

    expect(html).toContain('Visión Técnica General');
    expect(html).toContain('Arquitectura');
    expect(html).toContain(mockAIAnalysis.technical_overview.architecture);
    expect(html).toContain('Stack Tecnológico');
    expect(html).toContain(mockAIAnalysis.technical_overview.stack);
    expect(html).toContain('Ritmo de Actividad');
    expect(html).toContain(mockAIAnalysis.technical_overview.activity_summary);
  });

  test('14. Muestra estado profesional cuando ai_analysis es null o undefined', () => {
    const htmlNull = renderToStaticMarkup(<AIAnalysis aiAnalysis={null} />);
    expect(htmlNull).toContain('AI analysis unavailable');
    expect(htmlNull).toContain('no está disponible actualmente');
    expect(htmlNull).not.toContain('500');
    expect(htmlNull).not.toContain('Internal Error');

    const htmlUndefined = renderToStaticMarkup(<AIAnalysis aiAnalysis={undefined} />);
    expect(htmlUndefined).toContain('AI analysis unavailable');
  });

  test('15. Ausencia absoluta de null, undefined o NaN en el contenido visible', () => {
    const html = renderToStaticMarkup(<AIAnalysis aiAnalysis={mockAIAnalysis} />);

    expect(html).not.toContain('>null<');
    expect(html).not.toContain('>undefined<');
    expect(html).not.toContain('NaN');
  });

  test('16. Cumple accesibilidad y jerarquía semántica con section, header, h2, h3, h4, article, dl, dt, dd, ul, li', () => {
    const html = renderToStaticMarkup(<AIAnalysis aiAnalysis={mockAIAnalysis} />);

    expect(html).toContain('<section class="ai-section"');
    expect(html).toContain('id="ai-analysis"');
    expect(html).toContain('<header class="ai-header"');
    expect(html).toContain('<h2 id="ai-heading"');
    expect(html).toContain('<h3');
    expect(html).toContain('<h4');
    expect(html).toContain('<article');
    expect(html).toContain('<dl');
    expect(html).toContain('<dt');
    expect(html).toContain('<dd');
    expect(html).toContain('<ul');
    expect(html).toContain('<li');
  });

  test('17. Soporta textos largos de IA sin romper estructura', () => {
    const longAnalysis: AIAnalysisType = {
      summary:
        'A'.repeat(500) + ' Detailed summary about multifaceted codebases with intricate nuances.',
      strengths: ['B'.repeat(300)],
      concerns: [
        {
          title: 'C'.repeat(120),
          description: 'D'.repeat(400),
          severity: 'high',
          evidence: 'E'.repeat(300),
        },
      ],
      recommendations: [
        {
          title: 'F'.repeat(120),
          description: 'G'.repeat(400),
          priority: 'high',
        },
      ],
      technical_overview: {
        architecture: 'H'.repeat(300),
        stack: 'I'.repeat(300),
        activity_summary: 'J'.repeat(300),
      },
    };

    const html = renderToStaticMarkup(<AIAnalysis aiAnalysis={longAnalysis} />);

    expect(html).toContain('A'.repeat(500));
    expect(html).toContain('C'.repeat(120));
    expect(html).toContain('E'.repeat(300));
  });

  test('18. Verifica que NO se utiliza dangerouslySetInnerHTML en el código fuente del componente', () => {
    const filePath = resolve(__dirname, './AIAnalysis.tsx');
    const sourceCode = readFileSync(filePath, 'utf-8');

    expect(sourceCode).not.toContain('dangerouslySetInnerHTML');
  });
});
