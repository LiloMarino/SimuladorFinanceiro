import { useCallback, useEffect, useState } from "react";
import { handleApiResponse } from "@/shared/lib/utils/api";
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
  const { headers, responseSchema, initialFetch = true } = options ?? {};

  const query = useCallback(async (): Promise<R> => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(url, {
        headers: { "Content-Type": "application/json", ...(headers ?? {}) },
        credentials: "include",
      });

      const validatedData = await handleApiResponse<R>(res, responseSchema);
      setData(validatedData);
      return validatedData;
    } catch (err) {
      const e = err instanceof Error ? err : new Error(String(err));
      setError(e);
      throw e;
    } finally {
      setLoading(false);
    }
  }, [url, headers, responseSchema]);

  useEffect(() => {
    if (initialFetch) {
      void query();
    }
  }, [query, initialFetch]);

  return { data, setData, error, loading, query };
}
