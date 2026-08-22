import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="analyzer-footer">
      <div className="analyzer-container analyzer-footer-content">
        <div className="analyzer-footer-brand">
          <p className="analyzer-footer-name">AI-Code-Analyzer</p>
          <p className="analyzer-footer-copy">
            Plataforma de análisis estático, métricas y diagnóstico de repositorios GitHub.
          </p>
        </div>

        <p className="analyzer-footer-notice">
          Datos procesados mediante la{' '}
          <a
            href="https://docs.github.com/rest"
            target="_blank"
            rel="noreferrer"
          >
            GitHub REST API
          </a>
          . No se ejecuta código ni se descargan dependencias de repositorios analizados.
        </p>
      </div>
    </footer>
  );
};
