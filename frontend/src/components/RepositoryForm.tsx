import React, { useState } from 'react';
import { analyzeRepository, ApiError } from '../services/api';
import type { AnalysisResponse, FormStatus } from '../types';

interface RepositoryFormProps {
  onAnalysisSuccess: (data: AnalysisResponse) => void;
  onAnalysisStart?: () => void;
}

export const RepositoryForm: React.FC<RepositoryFormProps> = ({
  onAnalysisSuccess,
  onAnalysisStart,
}) => {
  const [owner, setOwner] = useState<string>('');
  const [repo, setRepo] = useState<string>('');
  const [status, setStatus] = useState<FormStatus>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const ownerTrimmed = owner.trim();
  const repoTrimmed = repo.trim();

  // Validacion de formato de identificadores de GitHub
  const isOwnerValid = /^[a-zA-Z0-9_-]+$/.test(ownerTrimmed);
  const isRepoValid = /^[a-zA-Z0-9_.-]+$/.test(repoTrimmed);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (status === 'loading') {
      return;
    }

    if (!ownerTrimmed) {
      setStatus('error');
      setErrorMessage('Por favor, introduce el propietario u organización.');
      return;
    }

    if (!isOwnerValid) {
      setStatus('error');
      setErrorMessage('El nombre del propietario contiene caracteres no válidos.');
      return;
    }

    if (!repoTrimmed) {
      setStatus('error');
      setErrorMessage('Por favor, introduce el nombre del repositorio.');
      return;
    }

    if (!isRepoValid) {
      setStatus('error');
      setErrorMessage('El nombre del repositorio contiene caracteres no válidos.');
      return;
    }

    setStatus('loading');
    setErrorMessage(null);
    onAnalysisStart?.();

    try {
      const data = await analyzeRepository(ownerTrimmed, repoTrimmed);
      setStatus('success');
      onAnalysisSuccess(data);
    } catch (err) {
      setStatus('error');
      if (err instanceof ApiError) {
        setErrorMessage(err.message);
      } else if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage('Ocurrió un error inesperado al conectar con el servidor.');
      }
    }
  };

  const getOwnerInputClass = () => {
    if (status === 'error' && (!ownerTrimmed || !isOwnerValid)) {
      return 'analyzer-form-input is-invalid';
    }
    if (ownerTrimmed && isOwnerValid) {
      return 'analyzer-form-input is-valid';
    }
    return 'analyzer-form-input';
  };

  const getRepoInputClass = () => {
    if (status === 'error' && (!repoTrimmed || !isRepoValid)) {
      return 'analyzer-form-input is-invalid';
    }
    if (repoTrimmed && isRepoValid) {
      return 'analyzer-form-input is-valid';
    }
    return 'analyzer-form-input';
  };

  return (
    <section
      className="analyzer-hero-section"
      id="analyzer"
      aria-labelledby="hero-heading"
    >
      <div className="analyzer-container">
        <div className="analyzer-hero-intro">
          <h1 id="hero-heading" className="analyzer-hero-title">
            Inspección Técnica y Métricas Objetivas de GitHub
          </h1>
          <p className="analyzer-hero-description">
            Evalúa la arquitectura, señales de calidad de ingeniería, métricas cuantitativas
            y recibe un diagnóstico técnico fundamentado con IA sin ejecutar código de terceros.
          </p>
        </div>

        <div className="analyzer-form-card">
          <form className="analyzer-form" onSubmit={handleSubmit} noValidate>
            <div className="analyzer-form-grid">
              <div className="analyzer-form-group">
                <label htmlFor="owner-input" className="analyzer-form-label">
                  Propietario / Organización{' '}
                  <span className="analyzer-required-mark" aria-hidden="true">
                    *
                  </span>
                </label>
                <input
                  id="owner-input"
                  name="owner"
                  type="text"
                  className={getOwnerInputClass()}
                  placeholder="ej. encode"
                  value={owner}
                  disabled={status === 'loading'}
                  onChange={(e) => {
                    setOwner(e.target.value);
                    if (status !== 'idle') setStatus('idle');
                    setErrorMessage(null);
                  }}
                  aria-describedby="owner-helper"
                  aria-invalid={status === 'error' && (!ownerTrimmed || !isOwnerValid)}
                  autoComplete="off"
                  spellCheck="false"
                  required
                />
                <span id="owner-helper" className="analyzer-form-helper">
                  Usuario u organización en GitHub
                </span>
              </div>

              <div className="analyzer-form-group">
                <label htmlFor="repo-input" className="analyzer-form-label">
                  Repositorio{' '}
                  <span className="analyzer-required-mark" aria-hidden="true">
                    *
                  </span>
                </label>
                <input
                  id="repo-input"
                  name="repo"
                  type="text"
                  className={getRepoInputClass()}
                  placeholder="ej. httpx"
                  value={repo}
                  disabled={status === 'loading'}
                  onChange={(e) => {
                    setRepo(e.target.value);
                    if (status !== 'idle') setStatus('idle');
                    setErrorMessage(null);
                  }}
                  aria-describedby="repo-helper"
                  aria-invalid={status === 'error' && (!repoTrimmed || !isRepoValid)}
                  autoComplete="off"
                  spellCheck="false"
                  required
                />
                <span id="repo-helper" className="analyzer-form-helper">
                  Nombre exacto del repositorio público
                </span>
              </div>
            </div>

            {errorMessage && (
              <div className="analyzer-status-banner is-error" role="alert">
                <p>{errorMessage}</p>
              </div>
            )}

            {status === 'loading' && (
              <div className="analyzer-status-banner is-loading" role="status" aria-live="polite">
                <p>
                  Consultando GitHub API y calculando métricas para{' '}
                  <strong>
                    {ownerTrimmed}/{repoTrimmed}
                  </strong>
                  ...
                </p>
              </div>
            )}

            <div className="analyzer-form-actions">
              <button
                type="submit"
                className="analyzer-submit-button"
                disabled={status === 'loading'}
                aria-busy={status === 'loading'}
              >
                {status === 'loading' ? (
                  <>
                    <svg
                      className="analyzer-spinner"
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                    >
                      <circle cx="12" cy="12" r="10" strokeDasharray="32" strokeDashoffset="12" />
                    </svg>
                    <span>Analizando repositorio...</span>
                  </>
                ) : (
                  <>
                    <svg
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <circle cx="11" cy="11" r="8" />
                      <line x1="21" y1="21" x2="16.65" y2="16.65" />
                    </svg>
                    <span>Analyze Repository</span>
                  </>
                )}
              </button>
            </div>

            <div className="analyzer-quick-examples">
              <span className="analyzer-examples-label">Ejemplos rápidos:</span>
              <div className="analyzer-examples-list">
                {[
                  { o: 'encode', r: 'httpx' },
                  { o: 'fastapi', r: 'fastapi' },
                  { o: 'pallets', r: 'flask' },
                  { o: 'facebook', r: 'react' },
                ].map((sample) => (
                  <button
                    key={`${sample.o}/${sample.r}`}
                    type="button"
                    className="analyzer-example-pill"
                    disabled={status === 'loading'}
                    onClick={() => {
                      setOwner(sample.o);
                      setRepo(sample.r);
                      setStatus('idle');
                      setErrorMessage(null);
                    }}
                  >
                    {sample.o}/{sample.r}
                  </button>
                ))}
              </div>
            </div>
          </form>
        </div>
      </div>
    </section>
  );
};
