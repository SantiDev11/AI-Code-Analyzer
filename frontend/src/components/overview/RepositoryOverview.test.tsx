import { describe, test, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { RepositoryOverview } from './RepositoryOverview';
import type { Repository } from '../../types';

const createMockRepository = (overrides: Partial<Repository> = {}): Repository => ({
  name: 'httpx',
  full_name: 'encode/httpx',
  description: 'A next-generation HTTP client for Python.',
  stars: 15420,
  forks: 1250,
  open_issues: 42,
  created_at: '2019-08-10T12:00:00Z',
  updated_at: '2024-01-15T18:30:00Z',
  primary_language: 'Python',
  url: 'https://github.com/encode/httpx',
  license: 'BSD-3-Clause',
  topics: ['python', 'http-client', 'asyncio'],
  size_kb: 4500,
  is_archived: false,
  default_branch: 'master',
  ...overrides,
});

describe('RepositoryOverview Component', () => {
  test('1. Render exitoso del contenedor semantico section y card', () => {
    const repo = createMockRepository();
    const html = renderToStaticMarkup(<RepositoryOverview repository={repo} />);

    expect(html).toContain('<section class="repo-overview-section"');
    expect(html).toContain('id="repository-overview"');
    expect(html).toContain('Resumen General del Repositorio');
  });

  test('2. Muestra el nombre y enlace al repositorio', () => {
    const repo = createMockRepository({
      full_name: 'encode/httpx',
      url: 'https://github.com/encode/httpx',
    });
    const html = renderToStaticMarkup(<RepositoryOverview repository={repo} />);

    expect(html).toContain('encode/httpx');
    expect(html).toContain('href="https://github.com/encode/httpx"');
    expect(html).toContain('target="_blank"');
  });

  test('3. Muestra la descripcion del repositorio', () => {
    const repo = createMockRepository({
      description: 'Cliente HTTP de última generación para Python.',
    });
    const html = renderToStaticMarkup(<RepositoryOverview repository={repo} />);

    expect(html).toContain('Cliente HTTP de última generación para Python.');
  });

  test('4. Muestra las estrellas formateadas', () => {
    const repo = createMockRepository({ stars: 15420 });
    const html = renderToStaticMarkup(<RepositoryOverview repository={repo} />);

    expect(html).toContain('Stars');
    expect(html).toContain('15');
  });

  test('5. Muestra los forks formateados', () => {
    const repo = createMockRepository({ forks: 1250 });
    const html = renderToStaticMarkup(<RepositoryOverview repository={repo} />);

    expect(html).toContain('Forks');
    expect(html).toContain('1');
  });

  test('6. Muestra los open issues', () => {
    const repo = createMockRepository({ open_issues: 42 });
    const html = renderToStaticMarkup(<RepositoryOverview repository={repo} />);

    expect(html).toContain('Open Issues');
    expect(html).toContain('42');
  });

  test('7. Muestra la rama por defecto real sin asumir main', () => {
    const repo = createMockRepository({ default_branch: 'develop' });
    const html = renderToStaticMarkup(<RepositoryOverview repository={repo} />);

    expect(html).toContain('develop');
  });

  test('8. Muestra los topics de forma individual', () => {
    const repo = createMockRepository({
      topics: ['fastapi', 'rest-api', 'testing'],
    });
    const html = renderToStaticMarkup(<RepositoryOverview repository={repo} />);

    expect(html).toContain('fastapi');
    expect(html).toContain('rest-api');
    expect(html).toContain('testing');
  });

  test('9. Muestra la licencia del repositorio', () => {
    const repo = createMockRepository({ license: 'MIT' });
    const html = renderToStaticMarkup(<RepositoryOverview repository={repo} />);

    expect(html).toContain('Licencia');
    expect(html).toContain('MIT');
  });

  test('10. Muestra estado vacio discreto cuando topics esta vacio', () => {
    const repo = createMockRepository({ topics: [] });
    const html = renderToStaticMarkup(<RepositoryOverview repository={repo} />);

    expect(html).toContain('No se han configurado etiquetas temáticas');
  });

  test('11. Maneja valores null correctamente (descripcion, licencia, lenguaje)', () => {
    const repo = createMockRepository({
      description: null,
      license: null,
      primary_language: null,
      topics: [],
    });
    const html = renderToStaticMarkup(<RepositoryOverview repository={repo} />);

    expect(html).toContain('Sin descripción proporcionada en GitHub.');
    expect(html).toContain('Sin licencia declarada');
    // No debe imprimir texto crudo 'null' ni 'undefined'
    expect(html).not.toContain('>null<');
    expect(html).not.toContain('>undefined<');
  });
});
