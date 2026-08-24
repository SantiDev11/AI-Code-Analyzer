import { describe, test, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { ReleasesAnalysis } from './ReleasesAnalysis';
import type { ReleaseDetail } from '../types';

const publishedRelease: ReleaseDetail = {
  id: 178123456,
  tag_name: '0.115.0',
  name: 'FastAPI 0.115.0',
  body: 'Correcciones menores y mejoras de rendimiento.',
  draft: false,
  prerelease: false,
  created_at: '2024-04-20T09:30:00Z',
  published_at: '2024-04-20T10:00:00Z',
  author: 'tiangolo',
  url: 'https://github.com/fastapi/fastapi/releases/tag/0.115.0',
};

const draftRelease: ReleaseDetail = {
  id: 178123457,
  tag_name: 'v2.0.0-wip',
  name: null,
  body: null,
  draft: true,
  prerelease: false,
  created_at: '2024-05-01T08:00:00Z',
  published_at: null,
  author: null,
  url: 'https://github.com/fastapi/fastapi/releases/tag/v2.0.0-wip',
};

const prerelease: ReleaseDetail = {
  id: 178123458,
  tag_name: 'v1.9.0-rc1',
  name: 'Release candidate 1',
  body: 'Version previa para pruebas de integracion.',
  draft: false,
  prerelease: true,
  created_at: '2024-03-10T11:00:00Z',
  published_at: '2024-03-10T12:00:00Z',
  author: 'maintainer',
  url: 'https://github.com/fastapi/fastapi/releases/tag/v1.9.0-rc1',
};

const mockReleases: ReleaseDetail[] = [publishedRelease, draftRelease, prerelease];

describe('ReleasesAnalysis Component', () => {
  test('1. Render con varios releases estructurado en section y list', () => {
    const html = renderToStaticMarkup(
      <ReleasesAnalysis
        releases={mockReleases}
        releasesCount={3}
        publishedReleasesCount={2}
        draftReleasesCount={1}
        prereleasesCount={1}
      />
    );

    expect(html).toContain('<section class="releases-section"');
    expect(html).toContain('id="releases-analysis"');
    expect(html).toContain('Releases');
    expect(html).toContain('FastAPI 0.115.0');
    expect(html).toContain('Release candidate 1');
    expect(html).toContain('v2.0.0-wip');
  });

  test('2. Renderiza correctamente un solo release', () => {
    const html = renderToStaticMarkup(
      <ReleasesAnalysis
        releases={[publishedRelease]}
        releasesCount={1}
        publishedReleasesCount={1}
        draftReleasesCount={0}
        prereleasesCount={0}
      />
    );

    expect(html).toContain('FastAPI 0.115.0');
    expect(html).toContain('0.115.0');
    expect((html.match(/<article class="release-entry"/g) || []).length).toBe(1);
  });

  test('3. Muestra el contador total del backend (releases_count)', () => {
    const html = renderToStaticMarkup(
      <ReleasesAnalysis
        releases={mockReleases}
        releasesCount={42}
        publishedReleasesCount={30}
        draftReleasesCount={5}
        prereleasesCount={7}
      />
    );

    expect(html).toContain('Total Releases');
    expect(html).toContain('>42<');
  });

  test('4. Muestra el contador de publicados (published_releases_count)', () => {
    const html = renderToStaticMarkup(
      <ReleasesAnalysis
        releases={mockReleases}
        releasesCount={42}
        publishedReleasesCount={30}
        draftReleasesCount={5}
        prereleasesCount={7}
      />
    );

    expect(html).toContain('Published');
    expect(html).toContain('class="releases-stat-value published-text">30<');
  });

  test('5. Muestra el contador de borradores (draft_releases_count)', () => {
    const html = renderToStaticMarkup(
      <ReleasesAnalysis
        releases={mockReleases}
        releasesCount={42}
        publishedReleasesCount={30}
        draftReleasesCount={5}
        prereleasesCount={7}
      />
    );

    expect(html).toContain('Draft');
    expect(html).toContain('class="releases-stat-value draft-text">5<');
  });

  test('6. Muestra el contador de versiones previas (prereleases_count)', () => {
    const html = renderToStaticMarkup(
      <ReleasesAnalysis
        releases={mockReleases}
        releasesCount={42}
        publishedReleasesCount={30}
        draftReleasesCount={5}
        prereleasesCount={7}
      />
    );

    expect(html).toContain('Prereleases');
    expect(html).toContain('class="releases-stat-value prerelease-text">7<');
  });

  test('7. Un release publicado se marca como Published con texto, no solo color', () => {
    const html = renderToStaticMarkup(<ReleasesAnalysis releases={[publishedRelease]} />);

    expect(html).toContain('release-state-badge is-published');
    expect(html).toContain('>Published</span>');
  });

  test('8. Un borrador se marca como Draft', () => {
    const html = renderToStaticMarkup(<ReleasesAnalysis releases={[draftRelease]} />);

    expect(html).toContain('release-state-badge is-draft');
    expect(html).toContain('>Draft</span>');
    expect(html).not.toContain('release-state-badge is-published');
  });

  test('9. Una version previa publicada se marca como Prerelease', () => {
    const html = renderToStaticMarkup(<ReleasesAnalysis releases={[prerelease]} />);

    expect(html).toContain('release-state-badge is-prerelease');
    expect(html).toContain('>Prerelease</span>');
    expect(html).not.toContain('release-state-badge is-draft');
  });

  test('10. Draft y prerelease son ejes independientes, no se mezclan', () => {
    const draftAndPrerelease: ReleaseDetail = {
      ...draftRelease,
      id: 999,
      prerelease: true,
    };
    const html = renderToStaticMarkup(<ReleasesAnalysis releases={[draftAndPrerelease]} />);

    expect(html).toContain('>Draft</span>');
    expect(html).toContain('>Prerelease</span>');
    expect(html).toContain('release-state-badge is-prerelease secondary');
  });

  test('11. Muestra el nombre del release cuando existe', () => {
    const html = renderToStaticMarkup(<ReleasesAnalysis releases={[publishedRelease]} />);

    expect(html).toContain('FastAPI 0.115.0');
    expect(html).toContain('<code class="release-tag"');
  });

  test('12. Usa tag_name como fallback cuando name es null o vacio', () => {
    const htmlNull = renderToStaticMarkup(<ReleasesAnalysis releases={[draftRelease]} />);
    expect(htmlNull).toContain('v2.0.0-wip');
    expect(htmlNull).not.toContain('>null<');

    const emptyName: ReleaseDetail = { ...publishedRelease, name: '   ' };
    const htmlEmpty = renderToStaticMarkup(<ReleasesAnalysis releases={[emptyName]} />);
    expect(htmlEmpty).toContain('0.115.0');
    expect(htmlEmpty).not.toContain('release-link"></a>');
  });

  test('13. Muestra la fecha de creacion con etiqueta time', () => {
    const html = renderToStaticMarkup(<ReleasesAnalysis releases={[publishedRelease]} />);

    expect(html).toMatch(/datetime="2024-04-20T09:30:00Z"/i);
    expect(html).toContain('Creado el');
  });

  test('14. Muestra la fecha de publicacion cuando existe', () => {
    const html = renderToStaticMarkup(<ReleasesAnalysis releases={[publishedRelease]} />);

    expect(html).toMatch(/datetime="2024-04-20T10:00:00Z"/i);
    expect(html).toContain('Publicado el');
    expect(html).toContain('release-published-date');
  });

  test('15. Con published_at null no inventa fecha de publicacion', () => {
    const html = renderToStaticMarkup(<ReleasesAnalysis releases={[draftRelease]} />);

    expect(html).not.toContain('Publicado el');
    expect(html).not.toContain('Invalid Date');
    expect(html).toContain('Sin fecha de publicación');
  });

  test('16. Muestra el autor cuando existe', () => {
    const html = renderToStaticMarkup(<ReleasesAnalysis releases={[publishedRelease]} />);

    expect(html).toContain('tiangolo');
    expect(html).toContain('release-author-name');
  });

  test('17. Con autor null muestra el texto de respaldo', () => {
    const html = renderToStaticMarkup(<ReleasesAnalysis releases={[draftRelease]} />);

    expect(html).toContain('Autor no identificado');
    expect(html).toContain('release-author-unknown');
  });

  test('18. Enlaza a GitHub de forma segura y accesible por teclado', () => {
    const html = renderToStaticMarkup(<ReleasesAnalysis releases={[publishedRelease]} />);

    expect(html).toContain('href="https://github.com/fastapi/fastapi/releases/tag/0.115.0"');
    expect(html).toContain('target="_blank"');
    expect(html).toContain('rel="noopener noreferrer"');
  });

  test('19. Muestra el body como texto plano, sin HTML arbitrario', () => {
    const htmlRelease: ReleaseDetail = {
      ...publishedRelease,
      body: 'Notas con <script>alert(1)</script> y <b>marcado</b>.',
    };
    const html = renderToStaticMarkup(<ReleasesAnalysis releases={[htmlRelease]} />);

    expect(html).toContain('&lt;script&gt;');
    expect(html).not.toContain('<script>alert(1)</script>');
    expect(html).not.toContain('<b>marcado</b>');
  });

  test('20. Sin body no renderiza el bloque de notas', () => {
    const html = renderToStaticMarkup(<ReleasesAnalysis releases={[draftRelease]} />);

    expect(html).not.toContain('release-body-wrap');

    const emptyBody: ReleaseDetail = { ...publishedRelease, body: '   ' };
    const htmlEmpty = renderToStaticMarkup(<ReleasesAnalysis releases={[emptyBody]} />);
    expect(htmlEmpty).not.toContain('release-body-wrap');
  });

  test('21. Lista vacia, null o undefined muestran estado vacio explicito', () => {
    const htmlEmpty = renderToStaticMarkup(
      <ReleasesAnalysis
        releases={[]}
        releasesCount={0}
        publishedReleasesCount={0}
        draftReleasesCount={0}
        prereleasesCount={0}
      />
    );
    expect(htmlEmpty).toContain('No se encontraron releases en este repositorio.');
    expect(htmlEmpty).not.toContain('<ul class="releases-list"');

    const htmlNull = renderToStaticMarkup(<ReleasesAnalysis releases={null} />);
    expect(htmlNull).toContain('No se encontraron releases en este repositorio.');

    const htmlUndefined = renderToStaticMarkup(<ReleasesAnalysis releases={undefined} />);
    expect(htmlUndefined).toContain('No se encontraron releases en este repositorio.');
  });

  test('22. Ausencia absoluta de null, undefined o NaN en texto visible', () => {
    const edgeRelease: ReleaseDetail = {
      id: 1,
      tag_name: 'v0.0.1',
      name: null,
      body: null,
      draft: false,
      prerelease: false,
      created_at: '2024-01-01T00:00:00Z',
      published_at: null,
      author: null,
      url: 'https://github.com/owner/repo/releases/tag/v0.0.1',
    };
    const html = renderToStaticMarkup(<ReleasesAnalysis releases={[edgeRelease]} />);

    expect(html).not.toContain('>null<');
    expect(html).not.toContain('>undefined<');
    expect(html).not.toContain('NaN');
    expect(html).toContain('Sin publicar');
  });

  test('23. Cumple accesibilidad con estructura semantica dl, dt, dd, ul, li, article, time', () => {
    const html = renderToStaticMarkup(<ReleasesAnalysis releases={mockReleases} />);

    expect(html).toContain('<dl class="releases-stats-list"');
    expect(html).toContain('<dt');
    expect(html).toContain('<dd');
    expect(html).toContain('<ul class="releases-list"');
    expect(html).toContain('<li class="release-item"');
    expect(html).toContain('<article class="release-entry"');
    expect(html).toContain('<time');
    expect(html).toContain('aria-labelledby="releases-heading"');
    expect(html).toContain('<h2 id="releases-heading"');
  });

  test('24. Contenido largo se trunca de forma accesible sin perder el texto', () => {
    const longRelease: ReleaseDetail = {
      id: 500,
      tag_name: 'v3.0.0-super-long-release-candidate-tag-name-for-testing',
      name: 'Una versión con un título extremadamente largo que describe muchísimos cambios internos de arquitectura',
      body: 'Nota de version muy larga. '.repeat(40),
      draft: false,
      prerelease: false,
      created_at: '2024-06-01T00:00:00Z',
      published_at: '2024-06-01T01:00:00Z',
      author: 'release-bot',
      url: 'https://github.com/owner/repo/releases/tag/v3.0.0',
    };
    const html = renderToStaticMarkup(<ReleasesAnalysis releases={[longRelease]} />);

    expect(html).toContain(longRelease.name as string);
    expect(html).toContain('v3.0.0-super-long-release-candidate-tag-name-for-testing');
    expect(html).toContain('…');
    expect(html).toContain('<details class="release-body-details"');
    expect(html).toContain('Ver notas completas');
  });
});
