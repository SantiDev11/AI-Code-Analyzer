import { describe, test, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { RecentCommitsAnalysis } from './RecentCommitsAnalysis';
import type { Commit } from '../types';

const mockCommits: Commit[] = [
  {
    sha: 'a1b2c3d',
    message: 'feat: add streaming response support',
    author: 'tomchristie',
    date: '2024-02-20T14:30:00Z',
    url: 'https://github.com/encode/httpx/commit/a1b2c3d',
  },
  {
    sha: 'e4f5g6h',
    message: 'fix: resolve connection pool leak under high concurrency',
    author: 'florimondmanca',
    date: '2024-02-18T09:15:00Z',
    url: 'https://github.com/encode/httpx/commit/e4f5g6h',
  },
  {
    sha: 'i7j8k9l',
    message: 'docs: update quickstart guide with async examples',
    author: null,
    date: '2024-02-15T18:45:00Z',
    url: 'https://github.com/encode/httpx/commit/i7j8k9l',
  },
];

describe('RecentCommitsAnalysis Component', () => {
  test('1. Render con varios commits estructurado en section y timeline', () => {
    const html = renderToStaticMarkup(<RecentCommitsAnalysis commits={mockCommits} />);

    expect(html).toContain('<section class="commits-section"');
    expect(html).toContain('id="recent-commits-analysis"');
    expect(html).toContain('Recent Commits');
    expect(html).toContain('Mostrando <strong>3</strong> commits');
  });

  test('2. Renderiza correctamente un solo commit', () => {
    const html = renderToStaticMarkup(<RecentCommitsAnalysis commits={[mockCommits[0]]} />);

    expect(html).toContain('a1b2c3d');
    expect(html).toContain('feat: add streaming response support');
    expect(html).toContain('Mostrando <strong>1</strong> commits');
  });

  test('3. Respeta el orden cronologico de commits recibido', () => {
    const html = renderToStaticMarkup(<RecentCommitsAnalysis commits={mockCommits} />);

    const firstShaIdx = html.indexOf('a1b2c3d');
    const secondShaIdx = html.indexOf('e4f5g6h');
    const thirdShaIdx = html.indexOf('i7j8k9l');

    expect(firstShaIdx).toBeLessThan(secondShaIdx);
    expect(secondShaIdx).toBeLessThan(thirdShaIdx);
  });

  test('4. Muestra el mensaje del commit', () => {
    const html = renderToStaticMarkup(<RecentCommitsAnalysis commits={[mockCommits[0]]} />);

    expect(html).toContain('feat: add streaming response support');
  });

  test('5. Muestra el SHA recortado de 7 caracteres', () => {
    const html = renderToStaticMarkup(<RecentCommitsAnalysis commits={[mockCommits[0]]} />);

    expect(html).toContain('<code>a1b2c3d</code>');
  });

  test('6. Muestra el autor del commit cuando existe', () => {
    const html = renderToStaticMarkup(<RecentCommitsAnalysis commits={[mockCommits[0]]} />);

    expect(html).toContain('tomchristie');
  });

  test('7. Maneja author = null con fallback amigable ("Autor no identificado")', () => {
    const html = renderToStaticMarkup(<RecentCommitsAnalysis commits={[mockCommits[2]]} />);

    expect(html).toContain('Autor no identificado');
    expect(html).not.toContain('>null<');
    expect(html).not.toContain('>undefined<');
  });

  test('8. Formatea la fecha en UTC de forma legible', () => {
    const html = renderToStaticMarkup(<RecentCommitsAnalysis commits={[mockCommits[0]]} />);

    expect(html).toContain('2024');
    expect(html).toContain('UTC');
    expect(html).toContain('dateTime="2024-02-20T14:30:00Z"');
  });

  test('9. Renderiza enlace accesible a GitHub para cada commit', () => {
    const html = renderToStaticMarkup(<RecentCommitsAnalysis commits={[mockCommits[0]]} />);

    expect(html).toContain('href="https://github.com/encode/httpx/commit/a1b2c3d"');
    expect(html).toContain('target="_blank"');
    expect(html).toContain('rel="noopener noreferrer"');
    expect(html).toContain('aria-label="Ver commit a1b2c3d en GitHub (se abre en nueva pestaña)"');
  });

  test('10. Muestra estado vacio profesional cuando no hay commits', () => {
    const htmlEmpty = renderToStaticMarkup(<RecentCommitsAnalysis commits={[]} />);
    expect(htmlEmpty).toContain('No hay commits recientes disponibles');

    const htmlNull = renderToStaticMarkup(<RecentCommitsAnalysis commits={null} />);
    expect(htmlNull).toContain('No hay commits recientes disponibles');

    const htmlUndefined = renderToStaticMarkup(<RecentCommitsAnalysis commits={undefined} />);
    expect(htmlUndefined).toContain('No hay commits recientes disponibles');
  });

  test('11. Ausencia absoluta de null, undefined o NaN en texto visible', () => {
    const edgeCommit: Commit = {
      sha: '1234567',
      message: '',
      author: null,
      date: '2024-01-01T00:00:00Z',
      url: 'https://github.com/owner/repo/commit/1234567',
    };
    const html = renderToStaticMarkup(<RecentCommitsAnalysis commits={[edgeCommit]} />);

    expect(html).not.toContain('>null<');
    expect(html).not.toContain('>undefined<');
    expect(html).not.toContain('NaN');
  });

  test('12. Cumple accesibilidad con elementos semanticos ol, li, article, time, code', () => {
    const html = renderToStaticMarkup(<RecentCommitsAnalysis commits={mockCommits} />);

    expect(html).toContain('<ol class="commits-timeline"');
    expect(html).toContain('aria-label="Historial de commits recientes"');
    expect(html).toContain('<article class="commit-entry">');
    expect(html).toContain('<time');
    expect(html).toContain('<code>');
  });

  test('13. Soporta mensajes largos sin romper el marcado', () => {
    const longMessage =
      'refactor(core): overhaul entire internal transport layer to support HTTP/2 and HTTP/3 multiplexing while preserving backwards compatibility with legacy connection pools';
    const longCommit: Commit = {
      sha: '9999999',
      message: longMessage,
      author: 'architect',
      date: '2024-02-22T10:00:00Z',
      url: 'https://github.com/owner/repo/commit/9999999',
    };
    const html = renderToStaticMarkup(<RecentCommitsAnalysis commits={[longCommit]} />);

    expect(html).toContain(longMessage);
    expect(html).toContain('title="refactor(core)');
  });
});
