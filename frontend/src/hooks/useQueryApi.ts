import { ApiResponseSchema } from "@/schemas/api";
import { useCallback, useEffect, useState } from "react";
import type { ZodType } from "zod";

interface UseFetchApiOptions<T> {
  readonly headers?: Record<string, string>;
  readonly responseSchema?: ZodType<T>;
  readonly initialFetch?: boolean;
}

/**
 * Hook para **consultas pontuais** (GET).
 *
 * 👉 Use quando precisar buscar dados sob demanda
 *     ou automaticamente ao montar o componente (`autoFetch`).
 */
export function useQueryApi<T = unknown>(url: string, options?: Readonly<UseFetchApiOptions<T>>) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchData = useCallback(async (): Promise<T> => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(url, {
        headers: { "Content-Type": "application/json", ...(options?.headers || {}) },
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const json = await res.json();
      const response = ApiResponseSchema.parse(json);
      const validatedData: T = options?.responseSchema ? options.responseSchema.parse(response.data) : response.data;

      setData(validatedData);
      return validatedData;
    } catch (err) {
      const e = err as Error;
      setError(e);
      throw e;
    } finally {
      setLoading(false);
    }
  }, [url, options?.headers, options?.responseSchema]);

  useEffect(() => {
    if (options?.initialFetch) {
      void fetchData();
    }
  }, [fetchData, options?.initialFetch]);

  return { data, setData, error, loading, fetchData };
}
