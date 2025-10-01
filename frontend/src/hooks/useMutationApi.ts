import { useState } from "react";
import type { ZodType } from "zod";

interface UseMutationApiOptions<T, B> {
  method?: "POST" | "PUT" | "DELETE";
  headers?: Record<string, string>;
  bodySchema?: ZodType<B>; // Schema para validar o body
  responseSchema?: ZodType<T>; // Schema para validar a resposta
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
}

export function useMutationApi<T, B = unknown>(
  url: string,
  options?: UseMutationApiOptions<T, B>
) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const mutate = async (body: B): Promise<T> => {
    setLoading(true);
    setError(null);

    try {
      // Valida o body antes de enviar
      const validatedBody = options?.bodySchema?.parse(body) ?? body;

      const res = await fetch(url, {
        method: options?.method || "POST",
        headers: { "Content-Type": "application/json", ...(options?.headers || {}) },
        body: JSON.stringify(validatedBody),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();

      const data = options?.responseSchema?.parse(json) ?? (json as T);
      options?.onSuccess?.(data);

      return data;
    } catch (err) {
      const e = err as Error;
      setError(e);
      options?.onError?.(e);
      throw e;
    } finally {
      setLoading(false);
    }
  };

  return { mutate, loading, error };
}
