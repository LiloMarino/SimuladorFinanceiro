import { useCallback, useEffect, useState } from "react";
import { handleApiResponse } from "@/lib/utils/api";
import type { ZodType } from "zod";

interface UseQueryApiOptions<R> {
  readonly headers?: Record<string, string>;
  readonly responseSchema?: ZodType<R>;
  readonly initialFetch?: boolean;
}

/**
 * Hook para **consultas pontuais** (GET).
 *
 * 👉 Use quando precisar buscar dados sob demanda
 *     ou automaticamente ao montar o componente (`initialFetch`).
 */
export function useQueryApi<R = unknown>(url: string, options?: Readonly<UseQueryApiOptions<R>>) {
  const [data, setData] = useState<R | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(false);

  const query = useCallback(async (): Promise<R> => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(url, {
        headers: { "Content-Type": "application/json", ...(options?.headers || {}) },
      });

      const validatedData = await handleApiResponse<R>(res, options?.responseSchema);
      setData(validatedData);
      return validatedData;
    } catch (err) {
      const e = err instanceof Error ? err : new Error(String(err));
      setError(e);
      throw e;
    } finally {
      setLoading(false);
    }
  }, [url, options?.headers, options?.responseSchema]);

  useEffect(() => {
    if (options?.initialFetch ?? true) {
      void query();
    }
  }, [query, options?.initialFetch]);

  return { data, setData, error, loading, query };
}
