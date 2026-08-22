import { describe, test, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { IssuesAnalysis } from './IssuesAnalysis';
import type { Issue } from '../types';

const mockIssues: Issue[] = [
  {
    number: 101,
    title: 'Support HTTP/3 protocol negotiation',
    state: 'open',
    author: 'octocat',
    created_at: '2024-01-10T12:00:00Z',
    updated_at: '2024-01-15T15:30:00Z',
    url: 'https://github.com/encode/httpx/issues/101',
  },
  {
    number: 99,
    title: 'Fix memory leak in connection pool under high concurrency load',
    state: 'closed',
    author: null,
    created_at: '2023-12-01T08:00:00Z',
    updated_at: '2023-12-05T10:00:00Z',
    url: 'https://github.com/encode/httpx/issues/99',
  },
  {
    number: 95,
    title: 'Add support for custom SSL context options',
    state: 'open',
    author: 'florimondmanca',
    created_at: '2023-11-20T09:00:00Z',
    updated_at: '2023-11-22T11:00:00Z',
    url: 'https://github.com/encode/httpx/issues/95',
  },
];

describe('IssuesAnalysis Component', () => {
  test('1. Render con varios issues estructurado en section y list', () => {
    const html = renderToStaticMarkup(
      <IssuesAnalysis
        issues={mockIssues}
        issuesCount={3}
        openIssuesCount={2}
        closedIssuesCount={1}
      />
    );

    expect(html).toContain('<section class="issues-section"');
    expect(html).toContain('id="issues-analysis"');
    expect(html).toContain('Issues');
    expect(html).toContain('Support HTTP/3 protocol negotiation');
    expect(html).toContain('Fix memory leak in connection pool');
  });

  test('2. Renderiza correctamente un solo issue', () => {
    const html = renderToStaticMarkup(
      <IssuesAnalysis
        issues={[mockIssues[0]]}
        issuesCount={1}
        openIssuesCount={1}
        closedIssuesCount={0}
      />
    );

    expect(html).toContain('#101');
    expect(html).toContain('Support HTTP/3 protocol negotiation');
  });

  test('3. Muestra el total de issues exacto (issues_count)', () => {
    const html = renderToStaticMarkup(
      <IssuesAnalysis
        issues={mockIssues}
        issuesCount={42}
        openIssuesCount={30}
        closedIssuesCount={12}
      />
    );

    expect(html).toContain('Total en Muestra');
    expect(html).toContain('42');
  });

  test('4. Muestra el recuento de issues abiertos (open_issues_count)', () => {
    const html = renderToStaticMarkup(
      <IssuesAnalysis
        issues={mockIssues}
        issuesCount={42}
        openIssuesCount={30}
        closedIssuesCount={12}
      />
    );

    expect(html).toContain('Abiertos');
    expect(html).toContain('30');
  });

  test('5. Muestra el recuento de issues cerrados (closed_issues_count)', () => {
    const html = renderToStaticMarkup(
      <IssuesAnalysis
        issues={mockIssues}
        issuesCount={42}
        openIssuesCount={30}
        closedIssuesCount={12}
      />
    );

    expect(html).toContain('Cerrados');
    expect(html).toContain('12');
  });

  test('6. Distingue visual y textualmente un issue abierto (state = "open")', () => {
    const html = renderToStaticMarkup(<IssuesAnalysis issues={[mockIssues[0]]} />);

    expect(html).toContain('is-open');
    expect(html).toContain('Abierto');
  });

  test('7. Distingue visual y textualmente un issue cerrado (state = "closed")', () => {
    const html = renderToStaticMarkup(<IssuesAnalysis issues={[mockIssues[1]]} />);

    expect(html).toContain('is-closed');
    expect(html).toContain('Cerrado');
  });

  test('8. Muestra el autor del issue cuando esta presente', () => {
    const html = renderToStaticMarkup(<IssuesAnalysis issues={[mockIssues[0]]} />);

    expect(html).toContain('octocat');
  });

  test('9. Muestra fallback accesible ("Autor no identificado") cuando author es null', () => {
    const html = renderToStaticMarkup(<IssuesAnalysis issues={[mockIssues[1]]} />);

    expect(html).toContain('Autor no identificado');
    expect(html).not.toContain('>null<');
    expect(html).not.toContain('>undefined<');
  });

  test('10. Muestra la fecha de creacion formateada en elemento time', () => {
    const html = renderToStaticMarkup(<IssuesAnalysis issues={[mockIssues[0]]} />);

    expect(html).toContain('Creado el');
    expect(html).toContain('2024');
    expect(html).toContain('dateTime="2024-01-10T12:00:00Z"');
  });

  test('11. Muestra la fecha de actualizacion formateada en elemento time', () => {
    const html = renderToStaticMarkup(<IssuesAnalysis issues={[mockIssues[0]]} />);

    expect(html).toContain('Actualizado el');
    expect(html).toContain('dateTime="2024-01-15T15:30:00Z"');
  });

  test('12. Renderiza enlace accesible a la URL oficial de GitHub del issue', () => {
    const html = renderToStaticMarkup(<IssuesAnalysis issues={[mockIssues[0]]} />);

    expect(html).toContain('href="https://github.com/encode/httpx/issues/101"');
    expect(html).toContain('target="_blank"');
    expect(html).toContain('rel="noopener noreferrer"');
    expect(html).toContain('aria-label="Ver issue número 101: Support HTTP/3 protocol negotiation en GitHub (se abre en nueva pestaña)"');
  });

  test('13. Muestra estado vacio profesional cuando no hay issues', () => {
    const htmlEmpty = renderToStaticMarkup(<IssuesAnalysis issues={[]} />);
    expect(htmlEmpty).toContain('No se encontraron issues recientes');

    const htmlNull = renderToStaticMarkup(<IssuesAnalysis issues={null} />);
    expect(htmlNull).toContain('No se encontraron issues recientes');

    const htmlUndefined = renderToStaticMarkup(<IssuesAnalysis issues={undefined} />);
    expect(htmlUndefined).toContain('No se encontraron issues recientes');
  });

  test('14. Ausencia absoluta de null, undefined o NaN visibles', () => {
    const edgeIssue: Issue = {
      number: 1,
      title: 'Sample title',
      state: 'open',
      author: null,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-02T00:00:00Z',
      url: 'https://github.com/owner/repo/issues/1',
    };
    const html = renderToStaticMarkup(<IssuesAnalysis issues={[edgeIssue]} />);

    expect(html).not.toContain('>null<');
    expect(html).not.toContain('>undefined<');
    expect(html).not.toContain('NaN');
  });

  test('15. Cumple accesibilidad basica y marcado semantico (dl, dt, dd, ul, li, article, time)', () => {
    const html = renderToStaticMarkup(<IssuesAnalysis issues={mockIssues} />);

    expect(html).toContain('<dl class="issues-stats-list"');
    expect(html).toContain('<dt');
    expect(html).toContain('<dd');
    expect(html).toContain('<ul class="issues-list"');
    expect(html).toContain('<article class="issue-entry"');
    expect(html).toContain('<time');
  });

  test('16. Soporta titulos largos sin desbordamiento', () => {
    const longTitle =
      'Feature request: investigate adding full native support for WebSockets and server-sent events with resilient automatic reconnection protocols across all asynchronous backend engines';
    const longIssue: Issue = {
      number: 200,
      title: longTitle,
      state: 'open',
      author: 'contributor',
      created_at: '2024-02-01T00:00:00Z',
      updated_at: '2024-02-01T00:00:00Z',
      url: 'https://github.com/owner/repo/issues/200',
    };
    const html = renderToStaticMarkup(<IssuesAnalysis issues={[longIssue]} />);

    expect(html).toContain(longTitle);
  });
});
