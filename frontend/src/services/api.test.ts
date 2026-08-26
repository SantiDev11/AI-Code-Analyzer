import { describe, test, expect, afterEach, vi } from 'vitest';
import { analyzeRepository, ApiError } from './api';

describe('API Service - analyzeRepository', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  test('construye la URL y retorna AnalysisResponse cuando la respuesta es 200 OK', async () => {
    const mockResponse = {
      repository: {
        name: 'httpx',
        full_name: 'encode/httpx',
        stars: 15000,
        forks: 1200,
      },
      quality: { tree_available: true },
      metrics: { total_files: 42 },
      cached: false,
    };

    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string | URL | Request) => {
        expect(url.toString()).toContain('/analyze/encode/httpx');
        return {
          ok: true,
          status: 200,
          json: async () => mockResponse,
        } as Response;
      })
    );

    const data = await analyzeRepository('encode', 'httpx');
    expect(data.repository.name).toBe('httpx');
    expect(data.repository.full_name).toBe('encode/httpx');
  });

  test('lanza ApiError 404 cuando el repositorio no existe', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => {
        return {
          ok: false,
          status: 404,
          json: async () => ({ detail: 'Repositorio no encontrado' }),
        } as Response;
      })
    );

    await expect(analyzeRepository('nonexistent', 'repo')).rejects.toThrow(ApiError);
    await expect(analyzeRepository('nonexistent', 'repo')).rejects.toMatchObject({
      status: 404,
      message: expect.stringContaining('Repositorio no encontrado'),
    });
  });

  test('lanza ApiError 429 ante limite de tasa excedido', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => {
        return {
          ok: false,
          status: 429,
          json: async () => ({ detail: 'Rate limit exceeded' }),
        } as Response;
      })
    );

    await expect(analyzeRepository('encode', 'httpx')).rejects.toMatchObject({
      status: 429,
      message: expect.stringContaining('Cuota de peticiones'),
    });
  });

  test('lanza ApiError 502/503 ante fallos del servicio de GitHub', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => {
        return {
          ok: false,
          status: 503,
          json: async () => ({ detail: 'Service Unavailable' }),
        } as Response;
      })
    );

    await expect(analyzeRepository('encode', 'httpx')).rejects.toMatchObject({
      status: 503,
      message: expect.stringContaining('no respondió a tiempo'),
    });
  });

  test('emplea ruta relativa y no inyecta tokens secretos en cabeceras', async () => {
    let capturedUrl = '';
    let capturedHeaders: Record<string, string> = {};

    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string | URL | Request, init?: RequestInit) => {
        capturedUrl = url.toString();
        capturedHeaders = (init?.headers as Record<string, string>) || {};
        return {
          ok: true,
          status: 200,
          json: async () => ({ repository: { name: 'demo' } }),
        } as Response;
      })
    );

    await analyzeRepository('user', 'project');

    // Debe llamar a /analyze/user/project
    expect(capturedUrl).toMatch(/\/analyze\/user\/project$/);
    // No debe enviar credenciales sensibles del backend
    expect(capturedHeaders['Authorization']).toBeUndefined();
    expect(capturedHeaders['X-GitHub-Token']).toBeUndefined();
    expect(capturedHeaders['X-AI-Key']).toBeUndefined();
  });
});
