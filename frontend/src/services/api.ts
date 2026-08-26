import type { AnalysisOptions, AnalysisResponse } from '../types';

export class ApiError extends Error {
  readonly status: number;
  readonly detail?: string;

  constructor(message: string, status: number, detail?: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

/**
 * Obtiene la URL base de la API desde las variables de entorno de Vite.
 * Si no esta definida, utiliza string vacio para que las peticiones se resuelvan
 * de forma relativa al host o mediante el proxy de Vite en desarrollo.
 */
function getApiBaseUrl(): string {
  const envUrl =
    typeof import.meta !== 'undefined' && import.meta.env
      ? import.meta.env.VITE_API_BASE_URL
      : undefined;
  if (typeof envUrl === 'string' && envUrl.trim().length > 0) {
    return envUrl.trim().replace(/\/+$/, '');
  }
  return '';
}

/**
 * Mapea los codigos de estado HTTP devueltos por el backend a mensajes claros y amigables.
 */
function mapHttpError(status: number, serverDetail?: string): string {
  if (serverDetail && typeof serverDetail === 'string' && serverDetail.trim().length > 0) {
    // Si el servidor envio un detalle util de excepcion de dominio
    if (status === 404) {
      return `Repositorio no encontrado: ${serverDetail}`;
    }
  }

  switch (status) {
    case 404:
      return 'Repositorio no encontrado o es privado.';
    case 429:
      return 'Cuota de peticiones de la GitHub API agotada. Inténtalo más tarde.';
    case 502:
      return 'Respuesta inesperada al conectar con GitHub.';
    case 503:
      return 'El servicio de GitHub no respondió a tiempo (timeout o fallo de red).';
    case 500:
      return 'Error interno del servidor al procesar el análisis.';
    default:
      return `Error en la solicitud de análisis (código HTTP ${status}).`;
  }
}

/**
 * Consulta el endpoint GET /analyze/{owner}/{repo} del backend.
 */
export async function analyzeRepository(
  owner: string,
  repo: string,
  options?: AnalysisOptions
): Promise<AnalysisResponse> {
  const baseUrl = getApiBaseUrl();
  const encodedOwner = encodeURIComponent(owner.trim());
  const encodedRepo = encodeURIComponent(repo.trim());

  // En arquitectura unificada las peticiones son relativas al mismo origen (/analyze/...)
  const path = `${baseUrl}/analyze/${encodedOwner}/${encodedRepo}`;
  const origin =
    typeof window !== 'undefined' && window.location ? window.location.origin : 'http://localhost:8000';
  const url = new URL(path, origin);

  if (options?.commits !== undefined) {
    url.searchParams.set('commits', options.commits.toString());
  }
  if (options?.issues !== undefined) {
    url.searchParams.set('issues', options.issues.toString());
  }
  if (options?.pulls !== undefined) {
    url.searchParams.set('pulls', options.pulls.toString());
  }
  if (options?.releases !== undefined) {
    url.searchParams.set('releases', options.releases.toString());
  }
  if (options?.activityDays !== undefined) {
    url.searchParams.set('activity_days', options.activityDays.toString());
  }

  let response: Response;
  try {
    response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    });
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : 'Error de conexión';
    throw new ApiError(
      `No se pudo conectar con el servidor de análisis (${errorMsg}).`,
      0
    );
  }

  if (!response.ok) {
    let serverDetail: string | undefined;
    try {
      const errBody = await response.json();
      if (errBody && typeof errBody.detail === 'string') {
        serverDetail = errBody.detail;
      }
    } catch {
      // Si la respuesta de error no es JSON valido, se usa el mensaje por defecto
    }

    const message = mapHttpError(response.status, serverDetail);
    throw new ApiError(message, response.status, serverDetail);
  }

  try {
    const data: AnalysisResponse = await response.json();
    return data;
  } catch (err) {
    throw new ApiError(
      'La respuesta recibida del servidor no tiene un formato JSON válido.',
      response.status
    );
  }
}
