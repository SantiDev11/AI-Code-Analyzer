/**
 * Tipos y modelos de datos del contrato publico de AI-Code-Analyzer.
 *
 * Reflejan fielmente los modelos Pydantic definidos en app/schemas/repository.py.
 */

export interface Repository {
  name: string;
  full_name: string;
  description: string | null;
  stars: number;
  forks: number;
  open_issues: number;
  created_at: string;
  updated_at: string;
  primary_language: string | null;
  url: string;
  license: string | null;
  topics: string[];
  size_kb: number;
  is_archived: boolean;
  default_branch: string;
}

export interface Contributor {
  username: string;
  contributions: number;
  avatar_url: string;
  profile_url: string;
}

export interface Release {
  tag: string;
  name: string | null;
  published_at: string;
  url: string;
}

export interface Issue {
  number: number;
  title: string;
  state: 'open' | 'closed';
  author: string | null;
  created_at: string;
  updated_at: string;
  url: string;
}

export interface Commit {
  sha: string;
  message: string;
  author: string | null;
  date: string;
  url: string;
}

export interface PullRequest {
  number: number;
  title: string;
  state: 'open' | 'closed';
  author: string | null;
  created_at: string;
  updated_at: string;
  closed_at: string | null;
  merged_at: string | null;
  source_branch: string | null;
  target_branch: string | null;
  url: string;
}

export interface ReleaseDetail {
  id: number;
  tag_name: string;
  name: string | null;
  body: string | null;
  draft: boolean;
  prerelease: boolean;
  created_at: string;
  published_at: string | null;
  author: string | null;
  url: string;
}

export interface DailyActivity {
  date: string;
  commits: number;
  issues: number;
  pull_requests_opened: number;
  pull_requests_closed: number;
  releases: number;
}

export interface Activity {
  days: number;
  since: string;
  until: string;
  total_commits: number;
  total_issues: number;
  total_pull_requests: number;
  total_releases: number;
  daily: DailyActivity[];
}

export interface QualitySignal {
  detected: boolean | null;
  files: string[];
}

export interface TestsSignal {
  detected: boolean | null;
  files: number;
  directories: string[];
}

export interface DocumentationSignal {
  readme: boolean | null;
  contributing: boolean | null;
  docs_directory: boolean | null;
  files: string[];
}

export interface CoverageSignal {
  configured: boolean | null;
  percentage: number | null;
  files: string[];
}

export interface Quality {
  tree_available: boolean;
  tree_truncated: boolean;
  files_scanned: number;
  tests: TestsSignal;
  documentation: DocumentationSignal;
  ci: QualitySignal;
  linting: QualitySignal;
  formatting: QualitySignal;
  type_checking: QualitySignal;
  dependencies: QualitySignal;
  coverage: CoverageSignal;
  undetermined_config: string[];
}

export interface LargeFile {
  path: string;
  size_bytes: number;
}

export interface Metrics {
  tree_available: boolean;
  tree_truncated: boolean;
  total_files: number;
  total_directories: number;
  source_files: number;
  test_files: number;
  documentation_files: number;
  configuration_files: number;
  file_extensions: Record<string, number>;
  largest_files: LargeFile[];
  lines_of_code: number | null;
}

export interface Concern {
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  evidence: string;
}

export interface Recommendation {
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
}

export interface TechnicalOverview {
  architecture: string;
  stack: string;
  activity_summary: string;
}

export interface AIAnalysis {
  summary: string;
  strengths: string[];
  concerns: Concern[];
  recommendations: Recommendation[];
  technical_overview: TechnicalOverview;
}

export interface AnalysisResponse {
  repository: Repository;
  languages: Record<string, number>;
  contributors: Contributor[];
  contributors_count: number;
  latest_release: Release | null;
  recent_commits: Commit[];
  issues: Issue[];
  issues_count: number;
  open_issues_count: number;
  closed_issues_count: number;
  pull_requests: PullRequest[];
  pull_requests_count: number;
  open_pull_requests_count: number;
  closed_pull_requests_count: number;
  merged_pull_requests_count: number;
  releases: ReleaseDetail[];
  releases_count: number;
  published_releases_count: number;
  draft_releases_count: number;
  prereleases_count: number;
  activity: Activity;
  quality: Quality;
  metrics: Metrics;
  ai_analysis: AIAnalysis | null;
  cached: boolean;
}

/**
 * Estados y tipos de interfaz de usuario.
 */
export type FormStatus = 'idle' | 'loading' | 'success' | 'error';

export interface AnalysisOptions {
  commits?: number;
  issues?: number;
  pulls?: number;
  releases?: number;
  activityDays?: number;
}

export interface FeatureItem {
  id: string;
  title: string;
  description: string;
  badge: string;
}
