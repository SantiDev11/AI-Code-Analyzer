import { describe, test, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { LanguagesAnalysis } from './LanguagesAnalysis';
import { formatBytes } from '../utils/format';

describe('LanguagesAnalysis Component', () => {
  test('1. Render con varios lenguajes estructurado en section y list', () => {
    const languages = {
      Python: 620000,
      TypeScript: 240000,
      JavaScript: 90000,
      CSS: 50000,
    };
    const html = renderToStaticMarkup(<LanguagesAnalysis languages={languages} />);

    expect(html).toContain('<section class="languages-section"');
    expect(html).toContain('id="languages-analysis"');
    expect(html).toContain('Languages');
    expect(html).toContain('Python');
    expect(html).toContain('TypeScript');
    expect(html).toContain('JavaScript');
    expect(html).toContain('CSS');
  });

  test('2. Orden descendente por bytes garantizado independientemente del orden de entrada', () => {
    const languages = {
      CSS: 1000,
      JavaScript: 5000,
      Python: 100000,
      HTML: 200,
    };
    const html = renderToStaticMarkup(<LanguagesAnalysis languages={languages} />);

    const pythonIdx = html.indexOf('Python');
    const jsIdx = html.indexOf('JavaScript');
    const cssIdx = html.indexOf('CSS');
    const htmlIdx = html.indexOf('HTML');

    expect(pythonIdx).toBeLessThan(jsIdx);
    expect(jsIdx).toBeLessThan(cssIdx);
    expect(cssIdx).toBeLessThan(htmlIdx);
  });

  test('3. Calcula porcentajes matematicamente correctos', () => {
    const languages = {
      TypeScript: 7500,
      JavaScript: 2500,
    };
    const html = renderToStaticMarkup(<LanguagesAnalysis languages={languages} />);

    expect(html).toContain('75.0%');
    expect(html).toContain('25.0%');
  });

  test('4. Formatea bytes de forma legible (B, KB, MB, etc.)', () => {
    expect(formatBytes(500)).toBe('500 B');
    expect(formatBytes(1024)).toBe('1 KB');
    expect(formatBytes(1048576)).toBe('1 MB');
    expect(formatBytes(1073741824)).toBe('1 GB');

    const languages = {
      Python: 1048576, // 1 MB
    };
    const html = renderToStaticMarkup(<LanguagesAnalysis languages={languages} />);
    expect(html).toContain('1 MB');
  });

  test('5. Soporta un solo lenguaje asignando 100.0%', () => {
    const languages = {
      Rust: 84000,
    };
    const html = renderToStaticMarkup(<LanguagesAnalysis languages={languages} />);

    expect(html).toContain('Rust');
    expect(html).toContain('100.0%');
  });

  test('6. Muestra un estado vacio profesional cuando languages esta vacio', () => {
    const htmlEmpty = renderToStaticMarkup(<LanguagesAnalysis languages={{}} />);
    expect(htmlEmpty).toContain('No se detectaron datos de lenguajes de programación');

    const htmlNull = renderToStaticMarkup(<LanguagesAnalysis languages={null} />);
    expect(htmlNull).toContain('No se detectaron datos de lenguajes de programación');

    const htmlUndefined = renderToStaticMarkup(<LanguagesAnalysis languages={undefined} />);
    expect(htmlUndefined).toContain('No se detectaron datos de lenguajes de programación');
  });

  test('7. Maneja total de bytes igual a cero sin romperse', () => {
    const languages = {
      Python: 0,
      Ruby: 0,
    };
    const html = renderToStaticMarkup(<LanguagesAnalysis languages={languages} />);

    expect(html).toContain('Python');
    expect(html).toContain('Ruby');
    expect(html).toContain('0.0%');
    expect(html).toContain('0 B');
  });

  test('8. Ausencia absoluta de NaN, Infinity o undefined en la salida renderizada', () => {
    const languages = {
      Python: 0,
      TypeScript: 100,
    };
    const html = renderToStaticMarkup(<LanguagesAnalysis languages={languages} />);

    expect(html).not.toContain('NaN');
    expect(html).not.toContain('Infinity');
    expect(html).not.toContain('>undefined<');
    expect(html).not.toContain('>null<');
  });

  test('9. Proporciona informacion textual accesible y roles semanticos', () => {
    const languages = {
      Go: 50000,
      HTML: 50000,
    };
    const html = renderToStaticMarkup(<LanguagesAnalysis languages={languages} />);

    expect(html).toContain('role="progressbar"');
    expect(html).toContain('role="img"');
    expect(html).toContain('aria-valuenow="50"');
    expect(html).toContain('aria-label="Porcentaje de Go"');
  });
});
