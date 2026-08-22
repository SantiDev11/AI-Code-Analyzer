import React, { useState } from 'react';
import { Header } from '../components/Header';
import { RepositoryForm } from '../components/RepositoryForm';
import { FeatureOverview } from '../components/FeatureOverview';
import { Footer } from '../components/Footer';
import { RepositoryOverview } from '../components/overview/RepositoryOverview';
import { RepositoryOverviewSkeleton } from '../components/overview/RepositoryOverviewSkeleton';
import { LanguagesAnalysis } from '../components/LanguagesAnalysis';
import type { AnalysisResponse } from '../types';

export const HomePage: React.FC = () => {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleAnalysisSuccess = (data: AnalysisResponse) => {
    setAnalysisResult(data);
    setIsLoading(false);
  };

  const handleAnalysisStart = () => {
    setAnalysisResult(null);
    setIsLoading(true);
  };

  return (
    <>
      <a href="#analyzer" className="analyzer-skip-link">
        Saltar al formulario de análisis
      </a>
      <Header />
      <main id="main-content">
        <RepositoryForm
          onAnalysisSuccess={handleAnalysisSuccess}
          onAnalysisStart={handleAnalysisStart}
        />

        {isLoading && <RepositoryOverviewSkeleton />}

        {analysisResult && (
          <>
            <RepositoryOverview repository={analysisResult.repository} />
            <LanguagesAnalysis languages={analysisResult.languages} />
          </>
        )}

        <FeatureOverview />
      </main>
      <Footer />
    </>
  );
};
