import { test, describe, after } from 'node:test';
import assert from 'node:assert/strict';
import { analyzeRepository, ApiError } from './api.ts';

describe('API Service - analyzeRepository', () => {
  const originalFetch = globalThis.fetch;

  after(() => {
    globalThis.fetch = originalFetch;
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

    globalThis.fetch = (async (url: string | URL | Request) => {
      assert.ok(url.toString().includes('/analyze/encode/httpx'));
      return {
        ok: true,
        status: 200,
        json: async () => mockResponse,
      } as Response;
    }) as typeof fetch;

    const data = await analyzeRepository('encode', 'httpx');
    assert.equal(data.repository.name, 'httpx');
    assert.equal(data.repository.full_name, 'encode/httpx');
  });

  test('lanza ApiError 404 cuando el repositorio no existe', async () => {
    globalThis.fetch = (async () => {
      return {
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Repositorio no encontrado' }),
      } as Response;
    }) as typeof fetch;

    await assert.rejects(
      async () => {
        await analyzeRepository('nonexistent', 'repo');
      },
      (err: unknown) => {
        const apiError = err as ApiError;
        assert.ok(apiError instanceof ApiError);
        assert.equal(apiError.status, 404);
        assert.ok(apiError.message.includes('Repositorio no encontrado'));
        return true;
      }
    );
  });

  test('lanza ApiError 429 ante limite de tasa excedido', async () => {
    globalThis.fetch = (async () => {
      return {
        ok: false,
        status: 429,
        json: async () => ({ detail: 'Rate limit exceeded' }),
      } as Response;
    }) as typeof fetch;

    await assert.rejects(
      async () => {
        await analyzeRepository('encode', 'httpx');
      },
      (err: unknown) => {
        const apiError = err as ApiError;
        assert.ok(apiError instanceof ApiError);
        assert.equal(apiError.status, 429);
        assert.ok(apiError.message.includes('Cuota de peticiones'));
        return true;
      }
    );
  });

  test('lanza ApiError 502/503 ante fallos del servicio de GitHub', async () => {
    globalThis.fetch = (async () => {
      return {
        ok: false,
        status: 503,
        json: async () => ({ detail: 'Service Unavailable' }),
      } as Response;
    }) as typeof fetch;

    await assert.rejects(
      async () => {
        await analyzeRepository('encode', 'httpx');
      },
      (err: unknown) => {
        const apiError = err as ApiError;
        assert.ok(apiError instanceof ApiError);
        assert.equal(apiError.status, 503);
        assert.ok(apiError.message.includes('no respondió a tiempo'));
        return true;
      }
    );
  });
});
