import { describe, test, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { RepositoryActivityAnalysis } from './RepositoryActivityAnalysis';
import type { Activity } from '../types';

const mockActivity: Activity = {
  days: 30,
  since: '2024-04-01',
  until: '2024-04-30',
  total_commits: 124,
  total_issues: 18,
  total_pull_requests: 35,
  total_releases: 3,
  daily: [
    {
      date: '2024-04-20',
      commits: 15,
      issues: 2,
      pull_requests_opened: 3,
      pull_requests_closed: 2,
      releases: 1,
    },
    {
      date: '2024-04-05',
      commits: 8,
      issues: 1,
      pull_requests_opened: 2,
      pull_requests_closed: 1,
      releases: 0,
    },
    {
      date: '2024-04-12',
      commits: 22,
      issues: 4,
      pull_requests_opened: 5,
      pull_requests_closed: 3,
      releases: 0,
    },
  ],
};

describe('RepositoryActivityAnalysis Component', () => {
  test('1. Muestra el resumen global de commits (total_commits)', () => {
    const html = renderToStaticMarkup(<RepositoryActivityAnalysis activity={mockActivity} />);

    expect(html).toContain('Commits');
    expect(html).toContain('124');
  });

  test('2. Muestra el resumen global de issues (total_issues)', () => {
    const html = renderToStaticMarkup(<RepositoryActivityAnalysis activity={mockActivity} />);

    expect(html).toContain('Issues');
    expect(html).toContain('18');
  });

  test('3. Muestra el resumen global de pull requests (total_pull_requests)', () => {
    const html = renderToStaticMarkup(<RepositoryActivityAnalysis activity={mockActivity} />);

    expect(html).toContain('Pull Requests');
    expect(html).toContain('35');
  });

  test('4. Muestra el resumen global de releases (total_releases)', () => {
    const html = renderToStaticMarkup(<RepositoryActivityAnalysis activity={mockActivity} />);

    expect(html).toContain('Releases');
    expect(html).toContain('3');
  });

  test('5. Renderiza adecuadamente múltiples días de actividad', () => {
    const html = renderToStaticMarkup(<RepositoryActivityAnalysis activity={mockActivity} />);

    expect(html).toContain('Actividad del Repositorio');
    expect(html).toContain('Actividad Diaria Cronológica');
    expect(html).toContain('dateTime="2024-04-05"');
    expect(html).toContain('dateTime="2024-04-12"');
    expect(html).toContain('dateTime="2024-04-20"');
  });

  test('6. Ordena los días en estricto orden cronológico ascendente sin alterar el objeto original', () => {
    const html = renderToStaticMarkup(<RepositoryActivityAnalysis activity={mockActivity} />);

    const pos05 = html.indexOf('dateTime="2024-04-05"');
    const pos12 = html.indexOf('dateTime="2024-04-12"');
    const pos20 = html.indexOf('dateTime="2024-04-20"');

    expect(pos05).toBeGreaterThan(-1);
    expect(pos12).toBeGreaterThan(pos05);
    expect(pos20).toBeGreaterThan(pos12);

    // Verifica que el array original no fue mutado
    expect(mockActivity.daily[0].date).toBe('2024-04-20');
  });

  test('7. Renderiza correctamente un solo día de actividad', () => {
    const singleDayActivity: Activity = {
      days: 1,
      since: '2024-04-20',
      until: '2024-04-20',
      total_commits: 5,
      total_issues: 1,
      total_pull_requests: 2,
      total_releases: 0,
      daily: [
        {
          date: '2024-04-20',
          commits: 5,
          issues: 1,
          pull_requests_opened: 2,
          pull_requests_closed: 0,
          releases: 0,
        },
      ],
    };
    const html = renderToStaticMarkup(<RepositoryActivityAnalysis activity={singleDayActivity} />);

    expect(html).toContain('dateTime="2024-04-20"');
    expect(html).toContain('8'); // 5+1+2 = 8 eventos
  });

  test('8. Muestra estado vacío profesional cuando activity o daily están vacíos', () => {
    const emptyActivity: Activity = {
      days: 30,
      since: '2024-04-01',
      until: '2024-04-30',
      total_commits: 0,
      total_issues: 0,
      total_pull_requests: 0,
      total_releases: 0,
      daily: [],
    };
    const htmlEmpty = renderToStaticMarkup(<RepositoryActivityAnalysis activity={emptyActivity} />);
    expect(htmlEmpty).toContain('No se registró actividad diaria');

    const htmlNull = renderToStaticMarkup(<RepositoryActivityAnalysis activity={null} />);
    expect(htmlNull).toContain('No se registró actividad diaria');

    const htmlUndefined = renderToStaticMarkup(<RepositoryActivityAnalysis activity={undefined} />);
    expect(htmlUndefined).toContain('No se registró actividad diaria');
  });

  test('9. Maneja valores null o ausentes sin errores de renderizado', () => {
    const htmlNull = renderToStaticMarkup(<RepositoryActivityAnalysis activity={null} />);

    expect(htmlNull).toContain('<section class="activity-section"');
    expect(htmlNull).toContain('0');
    expect(htmlNull).not.toContain('NaN');
  });

  test('10. Muestra fechas válidas con time y formato legible UTC', () => {
    const html = renderToStaticMarkup(<RepositoryActivityAnalysis activity={mockActivity} />);

    expect(html).toContain('<time dateTime="2024-04-05"');
    expect(html).not.toContain('Invalid Date');
  });

  test('11. Ausencia absoluta de null, undefined o NaN en texto visible', () => {
    const partialActivity: Activity = {
      days: 7,
      since: '2024-01-01',
      until: '2024-01-07',
      total_commits: 0,
      total_issues: 0,
      total_pull_requests: 0,
      total_releases: 0,
      daily: [
        {
          date: '2024-01-01',
          commits: 0,
          issues: 0,
          pull_requests_opened: 0,
          pull_requests_closed: 0,
          releases: 0,
        },
      ],
    };
    const html = renderToStaticMarkup(<RepositoryActivityAnalysis activity={partialActivity} />);

    expect(html).not.toContain('>null<');
    expect(html).not.toContain('>undefined<');
    expect(html).not.toContain('NaN');
  });

  test('12. Estructura semántica accesible con section, header, h2, dl, dt, dd, ul, li, article, time', () => {
    const html = renderToStaticMarkup(<RepositoryActivityAnalysis activity={mockActivity} />);

    expect(html).toContain('<section class="activity-section"');
    expect(html).toContain('id="repository-activity-analysis"');
    expect(html).toContain('<header class="activity-header"');
    expect(html).toContain('<h2 id="activity-heading"');
    expect(html).toContain('<dl class="activity-stats-list"');
    expect(html).toContain('<dt');
    expect(html).toContain('<dd');
    expect(html).toContain('<ul class="activity-daily-list"');
    expect(html).toContain('<article class="activity-day-card"');
    expect(html).toContain('<time');
  });

  test('13. Soporta grandes números y datos extensos sin desbordar', () => {
    const bigActivity: Activity = {
      days: 90,
      since: '2023-01-01',
      until: '2023-03-31',
      total_commits: 999999,
      total_issues: 88888,
      total_pull_requests: 77777,
      total_releases: 6666,
      daily: [
        {
          date: '2023-01-15',
          commits: 54321,
          issues: 1234,
          pull_requests_opened: 2345,
          pull_requests_closed: 1987,
          releases: 12,
        },
      ],
    };
    const html = renderToStaticMarkup(<RepositoryActivityAnalysis activity={bigActivity} />);

    expect(html).toMatch(/999[.,]999/);
    expect(html).toMatch(/88[.,]888/);
    expect(html).toMatch(/54[.,]321/);
  });
});
