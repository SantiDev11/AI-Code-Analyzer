import { describe, test, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { ContributorsAnalysis } from './ContributorsAnalysis';
import type { Contributor } from '../types';

const mockContributors: Contributor[] = [
  {
    username: 'tomchristie',
    contributions: 1420,
    avatar_url: 'https://avatars.githubusercontent.com/u/647318',
    profile_url: 'https://github.com/tomchristie',
  },
  {
    username: 'florimondmanca',
    contributions: 890,
    avatar_url: 'https://avatars.githubusercontent.com/u/15911462',
    profile_url: 'https://github.com/florimondmanca',
  },
  {
    username: 'sethmlarson',
    contributions: 320,
    avatar_url: 'https://avatars.githubusercontent.com/u/1851900',
    profile_url: 'https://github.com/sethmlarson',
  },
];

describe('ContributorsAnalysis Component', () => {
  test('1. Render con multiples contributors estructurado en section y cards', () => {
    const html = renderToStaticMarkup(
      <ContributorsAnalysis contributors={mockContributors} contributorsCount={3} />
    );

    expect(html).toContain('<section class="contributors-section"');
    expect(html).toContain('id="contributors-analysis"');
    expect(html).toContain('Contributors');
    expect(html).toContain('tomchristie');
    expect(html).toContain('florimondmanca');
    expect(html).toContain('sethmlarson');
  });

  test('2. Ordena estrictamente de mayor a menor numero de contribuciones', () => {
    // Proporcionar lista desordenada
    const unordered: Contributor[] = [
      {
        username: 'third',
        contributions: 50,
        avatar_url: 'https://example.com/3.png',
        profile_url: 'https://github.com/third',
      },
      {
        username: 'first',
        contributions: 500,
        avatar_url: 'https://example.com/1.png',
        profile_url: 'https://github.com/first',
      },
      {
        username: 'second',
        contributions: 200,
        avatar_url: 'https://example.com/2.png',
        profile_url: 'https://github.com/second',
      },
    ];

    const html = renderToStaticMarkup(<ContributorsAnalysis contributors={unordered} />);

    const firstIdx = html.indexOf('first');
    const secondIdx = html.indexOf('second');
    const thirdIdx = html.indexOf('third');

    expect(firstIdx).toBeLessThan(secondIdx);
    expect(secondIdx).toBeLessThan(thirdIdx);
  });

  test('3. Soporta un solo contributor con singularidad gramatical adecuada', () => {
    const single: Contributor[] = [
      {
        username: 'solodev',
        contributions: 1,
        avatar_url: 'https://example.com/avatar.png',
        profile_url: 'https://github.com/solodev',
      },
    ];

    const html = renderToStaticMarkup(<ContributorsAnalysis contributors={single} />);

    expect(html).toContain('solodev');
    expect(html).toContain('1');
    expect(html).toContain('commit atribuido');
  });

  test('4. Muestra estado vacio cuando la lista esta vacia o es null/undefined', () => {
    const htmlEmpty = renderToStaticMarkup(<ContributorsAnalysis contributors={[]} />);
    expect(htmlEmpty).toContain('No se encontraron datos de contribuidores');

    const htmlNull = renderToStaticMarkup(<ContributorsAnalysis contributors={null} />);
    expect(htmlNull).toContain('No se encontraron datos de contribuidores');

    const htmlUndefined = renderToStaticMarkup(<ContributorsAnalysis contributors={undefined} />);
    expect(htmlUndefined).toContain('No se encontraron datos de contribuidores');
  });

  test('5. Renderiza avatar con alt y src cuando esta disponible', () => {
    const html = renderToStaticMarkup(
      <ContributorsAnalysis contributors={[mockContributors[0]]} />
    );

    expect(html).toContain('img');
    expect(html).toContain('src="https://avatars.githubusercontent.com/u/647318"');
    expect(html).toContain('alt="Avatar de tomchristie"');
  });

  test('6. Muestra fallback visual con inicial cuando el avatar_url esta ausente', () => {
    const withoutAvatar: Contributor[] = [
      {
        username: 'ghostuser',
        contributions: 42,
        avatar_url: '',
        profile_url: 'https://github.com/ghostuser',
      },
    ];

    const html = renderToStaticMarkup(<ContributorsAnalysis contributors={withoutAvatar} />);

    expect(html).toContain('class="contributor-avatar-fallback"');
    expect(html).toContain('G'); // Inicial mayuscula
  });

  test('7. Cumple accesibilidad con enlaces a perfiles y descripciones de puesto', () => {
    const html = renderToStaticMarkup(
      <ContributorsAnalysis contributors={mockContributors} />
    );

    expect(html).toContain('aria-label="Puesto número 1"');
    expect(html).toContain('aria-label="Lista de principales contribuidores"');
    expect(html).toContain('href="https://github.com/tomchristie"');
    expect(html).toContain('target="_blank"');
    expect(html).toContain('rel="noopener noreferrer"');
  });

  test('8. Ausencia absoluta de undefined, null o NaN visibles', () => {
    const edgeCaseContributors: Contributor[] = [
      {
        username: 'edgeuser',
        contributions: 0,
        avatar_url: '',
        profile_url: '',
      },
    ];

    const html = renderToStaticMarkup(
      <ContributorsAnalysis contributors={edgeCaseContributors} />
    );

    expect(html).not.toContain('NaN');
    expect(html).not.toContain('>undefined<');
    expect(html).not.toContain('>null<');
  });
});
