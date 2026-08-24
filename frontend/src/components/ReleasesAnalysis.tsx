import React from 'react';
import type { ReleaseDetail } from '../types';

interface ReleasesAnalysisProps {
  releases: ReleaseDetail[] | null | undefined;
  releasesCount?: number;
  publishedReleasesCount?: number;
  draftReleasesCount?: number;
  prereleasesCount?: number;
}

interface ReleaseItemProps {
  release: ReleaseDetail;
}

/** Longitud maxima de las notas antes de ofrecer el texto completo plegado. */
const BODY_PREVIEW_LENGTH = 240;

function formatReleaseDate(dateStr: string): string {
  try {
    const parsed = new Date(dateStr);
    if (isNaN(parsed.getTime())) {
      return dateStr;
    }
    return parsed.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      timeZone: 'UTC',
    });
  } catch {
    return dateStr;
  }
}

/**
 * `draft` y `prerelease` son ejes independientes: un borrador puede estar
 * marcado como version previa. El estado principal se resuelve por prioridad
 * y la version previa se senala aparte cuando ademas es borrador.
 */
type ReleaseState = 'draft' | 'prerelease' | 'published' | 'unpublished';

function resolveReleaseState(release: ReleaseDetail): ReleaseState {
  if (release.draft) {
    return 'draft';
  }
  if (release.prerelease) {
    return 'prerelease';
  }
  if (release.published_at) {
    return 'published';
  }
  return 'unpublished';
}

const STATE_LABEL: Record<ReleaseState, string> = {
  draft: 'Draft',
  prerelease: 'Prerelease',
  published: 'Published',
  unpublished: 'Sin publicar',
};

const STATE_CLASS: Record<ReleaseState, string> = {
  draft: 'is-draft',
  prerelease: 'is-prerelease',
  published: 'is-published',
  unpublished: 'is-unpublished',
};

const ReleaseItem: React.FC<ReleaseItemProps> = ({ release }) => {
  const state = resolveReleaseState(release);
  const titleText =
    release.name && release.name.trim().length > 0 ? release.name.trim() : release.tag_name;
  const authorName = release.author ? release.author.trim() : '';
  const displayAuthor = authorName.length > 0 ? authorName : 'Autor no identificado';
  const bodyText = release.body ? release.body.trim() : '';
  const hasBody = bodyText.length > 0;
  const isBodyLong = bodyText.length > BODY_PREVIEW_LENGTH;
  const bodyPreview = isBodyLong ? bodyText.slice(0, BODY_PREVIEW_LENGTH) + '…' : bodyText;
  const createdFormatted = formatReleaseDate(release.created_at);
  const publishedFormatted = release.published_at ? formatReleaseDate(release.published_at) : null;

  return (
    <li className="release-item">
      <article className="release-entry">
        <div className="release-state-col">
          <span className={`release-state-badge ${STATE_CLASS[state]}`} role="status">
            {STATE_LABEL[state]}
          </span>

          {/* Borrador y version previa conviven: se muestran por separado */}
          {release.draft && release.prerelease && (
            <span className="release-state-badge is-prerelease secondary">Prerelease</span>
          )}
        </div>

        <div className="release-content">
          <div className="release-main-row">
            <h3 className="release-title">
              <a
                href={release.url}
                target="_blank"
                rel="noopener noreferrer"
                className="release-link"
                aria-label={`Ver release ${titleText} (etiqueta ${release.tag_name}) en GitHub (se abre en nueva pestaña)`}
              >
                {titleText}
              </a>
            </h3>

            <code className="release-tag" title={`Etiqueta: ${release.tag_name}`}>
              {release.tag_name}
            </code>
          </div>

          {hasBody && (
            <div className="release-body-wrap">
              <p className="release-body">{bodyPreview}</p>
              {isBodyLong && (
                <details className="release-body-details">
                  <summary className="release-body-summary">Ver notas completas</summary>
                  <p className="release-body-full">{bodyText}</p>
                </details>
              )}
            </div>
          )}

          <footer className="release-meta">
            <span className="release-author">
              Por{' '}
              <strong
                className={release.author ? 'release-author-name' : 'release-author-unknown'}
              >
                {displayAuthor}
              </strong>
            </span>

            <span className="release-meta-separator" aria-hidden="true">
              •
            </span>

            <time
              dateTime={release.created_at}
              className="release-date"
              title={`Fecha de creación: ${release.created_at}`}
            >
              Creado el {createdFormatted}
            </time>

            {release.published_at && publishedFormatted ? (
              <>
                <span className="release-meta-separator" aria-hidden="true">
                  •
                </span>
                <time
                  dateTime={release.published_at}
                  className="release-date release-published-date"
                  title={`Fecha de publicación: ${release.published_at}`}
                >
                  Publicado el {publishedFormatted}
                </time>
              </>
            ) : (
              <>
                <span className="release-meta-separator" aria-hidden="true">
                  •
                </span>
                <span className="release-date release-unpublished-note">
                  Sin fecha de publicación
                </span>
              </>
            )}
          </footer>
        </div>
      </article>
    </li>
  );
};

export const ReleasesAnalysis: React.FC<ReleasesAnalysisProps> = ({
  releases,
  releasesCount,
  publishedReleasesCount,
  draftReleasesCount,
  prereleasesCount,
}) => {
  const items = releases ? [...releases] : [];
  const totalCount = releasesCount ?? items.length;
  const publishedCount = publishedReleasesCount ?? items.filter((release) => !release.draft).length;
  const draftCount = draftReleasesCount ?? items.filter((release) => release.draft).length;
  const prereleaseCount = prereleasesCount ?? items.filter((release) => release.prerelease).length;

  return (
    <section className="releases-section" id="releases-analysis" aria-labelledby="releases-heading">
      <div className="analyzer-container">
        <div className="releases-card">
          <header className="releases-header">
            <span className="repo-section-badge">Versiones y Entregas</span>
            <div className="releases-title-row">
              <h2 id="releases-heading" className="releases-title">
                Releases
              </h2>
            </div>
            <p className="releases-subtitle">
              Historial reciente de versiones publicadas, borradores sin publicar y versiones
              previas.
            </p>
          </header>

          {/* Resumen metrico semantico dl/dt/dd */}
          <div className="releases-stats-container">
            <dl className="releases-stats-list">
              <div className="releases-stat-card">
                <dt className="releases-stat-label">Total Releases</dt>
                <dd className="releases-stat-value">{totalCount.toLocaleString()}</dd>
              </div>

              <div className="releases-stat-card">
                <dt className="releases-stat-label">
                  <span className="releases-status-dot published" aria-hidden="true" />
                  <span>Published</span>
                </dt>
                <dd className="releases-stat-value published-text">
                  {publishedCount.toLocaleString()}
                </dd>
              </div>

              <div className="releases-stat-card">
                <dt className="releases-stat-label">
                  <span className="releases-status-dot draft" aria-hidden="true" />
                  <span>Draft</span>
                </dt>
                <dd className="releases-stat-value draft-text">{draftCount.toLocaleString()}</dd>
              </div>

              <div className="releases-stat-card">
                <dt className="releases-stat-label">
                  <span className="releases-status-dot prerelease" aria-hidden="true" />
                  <span>Prereleases</span>
                </dt>
                <dd className="releases-stat-value prerelease-text">
                  {prereleaseCount.toLocaleString()}
                </dd>
              </div>
            </dl>
          </div>

          {items.length === 0 ? (
            <div className="releases-empty" role="status">
              <p className="repo-text-muted">No se encontraron releases en este repositorio.</p>
            </div>
          ) : (
            <ul className="releases-list" aria-label="Lista de releases del repositorio">
              {items.map((release, index) => (
                <ReleaseItem key={`${release.id}-${index}`} release={release} />
              ))}
            </ul>
          )}
        </div>
      </div>
    </section>
  );
};
