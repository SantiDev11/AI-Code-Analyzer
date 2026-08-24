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
            <ContributorsAnalysis
              contributors={analysisResult.contributors}
              contributorsCount={analysisResult.contributors_count}
            />
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
            <RepositoryActivityAnalysis activity={analysisResult.activity} />
          </>
        )}

        <FeatureOverview />
      </main>
      <Footer />
    </>
  );
};
