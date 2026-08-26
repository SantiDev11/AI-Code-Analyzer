import React, { useState } from 'react';
import { Header } from '../components/Header';
import { RepositoryForm } from '../components/RepositoryForm';
import { FeatureOverview } from '../components/FeatureOverview';
import { Footer } from '../components/Footer';
import { RepositoryOverview } from '../components/overview/RepositoryOverview';
import { RepositoryOverviewSkeleton } from '../components/overview/RepositoryOverviewSkeleton';
import { LanguagesAnalysis } from '../components/LanguagesAnalysis';
import { ContributorsAnalysis } from '../components/ContributorsAnalysis';
import { RecentCommitsAnalysis } from '../components/RecentCommitsAnalysis';
import { IssuesAnalysis } from '../components/IssuesAnalysis';
import { PullRequestsAnalysis } from '../components/PullRequestsAnalysis';
import { ReleasesAnalysis } from '../components/ReleasesAnalysis';
import { RepositoryActivityAnalysis } from '../components/RepositoryActivityAnalysis';
import { CodeQualityAnalysis } from '../components/CodeQualityAnalysis';
import { CodeMetricsAnalysis } from '../components/CodeMetricsAnalysis';
import { AIAnalysis } from '../components/AIAnalysis';
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
            {/* Quick Navigation Sticky Bar */}
            <nav className="analyzer-quicknav" aria-label="Navegación rápida de secciones">
              <div className="analyzer-container">
                <ul className="analyzer-quicknav-list">
                  <li>
                    <a href="#repository-overview" className="analyzer-quicknav-link">
                      <span className="quicknav-icon">📊</span> Resumen
                    </a>
                  </li>
                  <li>
                    <a href="#code-quality-analysis" className="analyzer-quicknav-link">
                      <span className="quicknav-icon">🛡️</span> Calidad
                    </a>
                  </li>
                  <li>
                    <a href="#code-metrics-analysis" className="analyzer-quicknav-link">
                      <span className="quicknav-icon">📈</span> Métricas
                    </a>
                  </li>
                  <li>
                    <a href="#repository-activity-analysis" className="analyzer-quicknav-link">
                      <span className="quicknav-icon">⚡</span> Actividad
                    </a>
                  </li>
                  <li>
                    <a href="#languages-analysis" className="analyzer-quicknav-link">
                      <span className="quicknav-icon">🌐</span> Lenguajes
                    </a>
                  </li>
                  <li>
                    <a href="#recent-commits-analysis" className="analyzer-quicknav-link">
                      <span className="quicknav-icon">📦</span> Commits & PRs
                    </a>
                  </li>
                  <li>
                    <a href="#ai-analysis" className="analyzer-quicknav-link">
                      <span className="quicknav-icon">🤖</span> IA (Roadmap)
                    </a>
                  </li>
                </ul>
              </div>
            </nav>

            {/* 1. Repository Overview */}
            <RepositoryOverview repository={analysisResult.repository} />

            {/* 2. Estándares de Calidad */}
            <CodeQualityAnalysis quality={analysisResult.quality} />

            {/* 3. Métricas Cuantitativas de Código */}
            <CodeMetricsAnalysis metrics={analysisResult.metrics} />

            {/* 4. Actividad Temporal Diaria */}
            <RepositoryActivityAnalysis activity={analysisResult.activity} />

            {/* 5. Lenguajes y Colaboradores */}
            <LanguagesAnalysis languages={analysisResult.languages} />
            <ContributorsAnalysis
              contributors={analysisResult.contributors}
              contributorsCount={analysisResult.contributors_count}
            />

            {/* 6. Git Flow: Commits, Issues, PRs y Releases */}
            <RecentCommitsAnalysis commits={analysisResult.recent_commits} />
            <IssuesAnalysis
              issues={analysisResult.issues}
              issuesCount={analysisResult.issues_count}
              openIssuesCount={analysisResult.open_issues_count}
              closedIssuesCount={analysisResult.closed_issues_count}
            />
            <PullRequestsAnalysis
              pullRequests={analysisResult.pull_requests}
              pullRequestsCount={analysisResult.pull_requests_count}
              openPullRequestsCount={analysisResult.open_pull_requests_count}
              closedPullRequestsCount={analysisResult.closed_pull_requests_count}
              mergedPullRequestsCount={analysisResult.merged_pull_requests_count}
            />
            <ReleasesAnalysis
              releases={analysisResult.releases}
              releasesCount={analysisResult.releases_count}
              publishedReleasesCount={analysisResult.published_releases_count}
              draftReleasesCount={analysisResult.draft_releases_count}
              prereleasesCount={analysisResult.prereleases_count}
            />

            {/* 7. Inteligencia Artificial */}
            <AIAnalysis aiAnalysis={analysisResult.ai_analysis} />
          </>
        )}

        <FeatureOverview />
      </main>
      <Footer />
    </>
  );
};
