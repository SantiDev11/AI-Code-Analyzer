/**
 * Tipos fundamentales para el frontend de AI-Code-Analyzer.
 */

export type FormStatus = 'idle' | 'valid' | 'invalid' | 'loading' | 'error';

export interface FormState {
  owner: string;
  repo: string;
  status: FormStatus;
  errorMessage: string | null;
}

export interface FeatureItem {
  id: string;
  title: string;
  description: string;
  badge: string;
}
