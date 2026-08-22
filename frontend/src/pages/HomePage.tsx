import React from 'react';
import { Header } from '../components/Header';
import { RepositoryForm } from '../components/RepositoryForm';
import { FeatureOverview } from '../components/FeatureOverview';
import { Footer } from '../components/Footer';

export const HomePage: React.FC = () => {
  return (
    <>
      <a href="#analyzer" className="analyzer-skip-link">
        Saltar al formulario de análisis
      </a>
      <Header />
      <main id="main-content">
        <RepositoryForm />
        <FeatureOverview />
      </main>
      <Footer />
    </>
  );
};
