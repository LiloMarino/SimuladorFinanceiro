import { useState } from "react";
import type { ZodType } from "zod";

interface UseFetchApiOptions<T> {
  headers?: Record<string, string>;
  responseSchema?: ZodType<T>;
}

/**
 * Hook para **consultas pontuais** (GET).
 * 
 * 👉 Use quando precisar buscar dados sob demanda.
 */
export function useQueryApi<T = unknown>(
  url: string,
  options?: UseFetchApiOptions<T>
) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchData = async (): Promise<T> => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(url, {
        headers: { "Content-Type": "application/json", ...(options?.headers || {}) },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const json = await res.json();
      if (options?.responseSchema) {
        const parsed = options.responseSchema.parse(json);
        setData(parsed);
        return parsed;
      }

      setData(json);
      return json;
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { data, error, loading, fetchData };
}
