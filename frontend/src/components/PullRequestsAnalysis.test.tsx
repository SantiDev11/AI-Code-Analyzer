import { describe, test, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { PullRequestsAnalysis } from './PullRequestsAnalysis';
import type { PullRequest } from '../types';

const mockPullRequests: PullRequest[] = [
  {
    number: 201,
    title: 'Add HTTP/2 multiplexing engine',
    state: 'closed',
    author: 'tomchristie',
    created_at: '2024-01-05T10:00:00Z',
    updated_at: '2024-01-08T12:00:00Z',
    closed_at: '2024-01-08T12:00:00Z',
    merged_at: '2024-01-08T12:00:00Z',
    source_branch: 'feature/http2-multiplex',
    target_branch: 'main',
    url: 'https://github.com/encode/httpx/pull/201',
  },
  {
    number: 202,
    title: 'Implement retry policy with exponential backoff',
    state: 'open',
    author: 'florimondmanca',
    created_at: '2024-01-12T14:00:00Z',
    updated_at: '2024-01-14T16:00:00Z',
    closed_at: null,
    merged_at: null,
    source_branch: 'feature/backoff-retry',
    target_branch: 'main',
    url: 'https://github.com/encode/httpx/pull/202',
  },
  {
    number: 203,
    title: 'Experimental alternate SSL backend (rejected)',
    state: 'closed',
    author: null,
    created_at: '2023-11-01T08:00:00Z',
    updated_at: '2023-11-03T09:00:00Z',
    closed_at: '2023-11-03T09:00:00Z',
    merged_at: null,
    source_branch: 'exp/alt-ssl',
    target_branch: 'master',
    url: 'https://github.com/encode/httpx/pull/203',
  },
];

describe('PullRequestsAnalysis Component', () => {
  test('1. Render con varios PRs estructurado en section y list', () => {
    const html = renderToStaticMarkup(
      <PullRequestsAnalysis
        pullRequests={mockPullRequests}
        pullRequestsCount={3}
        openPullRequestsCount={1}
        closedPullRequestsCount={2}
        mergedPullRequestsCount={1}
      />
    );

    expect(html).toContain('<section class="prs-section"');
    expect(html).toContain('id="pull-requests-analysis"');
    expect(html).toContain('Pull Requests');
    expect(html).toContain('Add HTTP/2 multiplexing engine');
    expect(html).toContain('Implement retry policy with exponential backoff');
  });

  test('2. Renderiza correctamente un solo PR', () => {
    const html = renderToStaticMarkup(
      <PullRequestsAnalysis
        pullRequests={[mockPullRequests[0]]}
        pullRequestsCount={1}
        openPullRequestsCount={0}
        closedPullRequestsCount={1}
        mergedPullRequestsCount={1}
      />
    );

    expect(html).toContain('#201');
    expect(html).toContain('Add HTTP/2 multiplexing engine');
  });

  test('3. Muestra el total de PRs (pull_requests_count)', () => {
    const html = renderToStaticMarkup(
      <PullRequestsAnalysis
        pullRequests={mockPullRequests}
        pullRequestsCount={50}
        openPullRequestsCount={10}
        closedPullRequestsCount={40}
        mergedPullRequestsCount={35}
      />
    );

    expect(html).toContain('Total en Muestra');
    expect(html).toContain('50');
  });

  test('4. Muestra el contador de abiertos (open_pull_requests_count)', () => {
    const html = renderToStaticMarkup(
      <PullRequestsAnalysis
        pullRequests={mockPullRequests}
        pullRequestsCount={50}
        openPullRequestsCount={10}
        closedPullRequestsCount={40}
        mergedPullRequestsCount={35}
      />
    );

    expect(html).toContain('Abiertos');
    expect(html).toContain('10');
  });

  test('5. Muestra el contador de cerrados (closed_pull_requests_count)', () => {
    const html = renderToStaticMarkup(
      <PullRequestsAnalysis
        pullRequests={mockPullRequests}
        pullRequestsCount={50}
        openPullRequestsCount={10}
        closedPullRequestsCount={40}
        mergedPullRequestsCount={35}
      />
    );

    expect(html).toContain('Cerrados');
    expect(html).toContain('40');
  });

  test('6. Muestra el contador de mergeados (merged_pull_requests_count)', () => {
    const html = renderToStaticMarkup(
      <PullRequestsAnalysis
        pullRequests={mockPullRequests}
        pullRequestsCount={50}
        openPullRequestsCount={10}
        closedPullRequestsCount={40}
        mergedPullRequestsCount={35}
      />
    );

    expect(html).toContain('Mergeados');
    expect(html).toContain('35');
  });

  test('7. Renderiza PR abierto con estado "Abierto"', () => {
    const html = renderToStaticMarkup(<PullRequestsAnalysis pullRequests={[mockPullRequests[1]]} />);

    expect(html).toContain('is-open');
    expect(html).toContain('Abierto');
  });

  test('8. Renderiza PR cerrado no mergeado con estado "Cerrado"', () => {
    const html = renderToStaticMarkup(<PullRequestsAnalysis pullRequests={[mockPullRequests[2]]} />);

    expect(html).toContain('is-closed');
    expect(html).toContain('Cerrado');
  });

  test('9. Renderiza PR mergeado con estado "Merged"', () => {
    const html = renderToStaticMarkup(<PullRequestsAnalysis pullRequests={[mockPullRequests[0]]} />);

    expect(html).toContain('is-merged');
    expect(html).toContain('Merged');
  });

  test('10. Distingue con precision un PR cerrado vs un PR mergeado', () => {
    const htmlMerged = renderToStaticMarkup(<PullRequestsAnalysis pullRequests={[mockPullRequests[0]]} />);
    const htmlClosed = renderToStaticMarkup(<PullRequestsAnalysis pullRequests={[mockPullRequests[2]]} />);

    expect(htmlMerged).toContain('is-merged');
    expect(htmlMerged).toContain('Merged');
    expect(htmlMerged).not.toContain('is-closed');

    expect(htmlClosed).toContain('is-closed');
    expect(htmlClosed).toContain('Cerrado');
    expect(htmlClosed).not.toContain('is-merged');
  });

  test('11. Muestra el autor cuando esta presente', () => {
    const html = renderToStaticMarkup(<PullRequestsAnalysis pullRequests={[mockPullRequests[0]]} />);

    expect(html).toContain('tomchristie');
  });

  test('12. Muestra fallback accesible cuando author es null', () => {
    const html = renderToStaticMarkup(<PullRequestsAnalysis pullRequests={[mockPullRequests[2]]} />);

    expect(html).toContain('Autor no identificado');
    expect(html).not.toContain('>null<');
    expect(html).not.toContain('>undefined<');
  });

  test('13. Muestra fecha de merge cuando merged_at esta presente', () => {
    const html = renderToStaticMarkup(<PullRequestsAnalysis pullRequests={[mockPullRequests[0]]} />);

    expect(html).toContain('Mergeado el');
    expect(html).toContain('dateTime="2024-01-08T12:00:00Z"');
  });

  test('14. No muestra fecha de merge cuando merged_at es null', () => {
    const html = renderToStaticMarkup(<PullRequestsAnalysis pullRequests={[mockPullRequests[1]]} />);

    expect(html).not.toContain('Mergeado el');
  });

  test('15. Renderiza enlace accesible a la URL oficial de GitHub del PR', () => {
    const html = renderToStaticMarkup(<PullRequestsAnalysis pullRequests={[mockPullRequests[0]]} />);

    expect(html).toContain('href="https://github.com/encode/httpx/pull/201"');
    expect(html).toContain('target="_blank"');
    expect(html).toContain('rel="noopener noreferrer"');
    expect(html).toContain('aria-label="Ver pull request número 201: Add HTTP/2 multiplexing engine en GitHub (se abre en nueva pestaña)"');
  });

  test('16. Muestra estado vacio profesional cuando no hay PRs', () => {
    const htmlEmpty = renderToStaticMarkup(<PullRequestsAnalysis pullRequests={[]} />);
    expect(htmlEmpty).toContain('No se encontraron pull requests recientes');

    const htmlNull = renderToStaticMarkup(<PullRequestsAnalysis pullRequests={null} />);
    expect(htmlNull).toContain('No se encontraron pull requests recientes');

    const htmlUndefined = renderToStaticMarkup(<PullRequestsAnalysis pullRequests={undefined} />);
    expect(htmlUndefined).toContain('No se encontraron pull requests recientes');
  });

  test('17. Ausencia absoluta de null, undefined o NaN en texto visible', () => {
    const edgePR: PullRequest = {
      number: 1,
      title: 'Edge title',
      state: 'open',
      author: null,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      closed_at: null,
      merged_at: null,
      source_branch: null,
      target_branch: null,
      url: 'https://github.com/owner/repo/pull/1',
    };
    const html = renderToStaticMarkup(<PullRequestsAnalysis pullRequests={[edgePR]} />);

    expect(html).not.toContain('>null<');
    expect(html).not.toContain('>undefined<');
    expect(html).not.toContain('NaN');
  });

  test('18. Cumple accesibilidad con estructura semantica dl, dt, dd, ul, li, article, time', () => {
    const html = renderToStaticMarkup(<PullRequestsAnalysis pullRequests={mockPullRequests} />);

    expect(html).toContain('<dl class="prs-stats-list"');
    expect(html).toContain('<dt');
    expect(html).toContain('<dd');
    expect(html).toContain('<ul class="prs-list"');
    expect(html).toContain('<article class="pr-entry"');
    expect(html).toContain('<time');
  });

  test('19. Renderiza titulos y ramas largas correctamente', () => {
    const longPR: PullRequest = {
      number: 999,
      title: 'A very long pull request title explaining intricate details about asynchronous connection multiplexing in deep architectures',
      state: 'open',
      author: 'contributor',
      created_at: '2024-02-01T00:00:00Z',
      updated_at: '2024-02-01T00:00:00Z',
      closed_at: null,
      merged_at: null,
      source_branch: 'feature/super-long-branch-name-with-many-sub-details',
      target_branch: 'release/v2.0-stabilization-branch',
      url: 'https://github.com/owner/repo/pull/999',
    };
    const html = renderToStaticMarkup(<PullRequestsAnalysis pullRequests={[longPR]} />);

    expect(html).toContain(longPR.title);
    expect(html).toContain('feature/super-long-branch-name-with-many-sub-details');
    expect(html).toContain('release/v2.0-stabilization-branch');
  });
});
