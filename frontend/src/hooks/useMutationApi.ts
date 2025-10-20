import { ApiResponseSchema } from "@/lib/schemas/api";
import { useState } from "react";
import type { ZodType } from "zod";

interface UseMutationApiOptions<R = unknown, B = unknown> {
  readonly method?: "POST" | "PUT" | "DELETE";
  readonly headers?: Record<string, string>;
  readonly bodySchema?: ZodType<B>; // Schema para validar o body
  readonly responseSchema?: ZodType<R>; // Schema para validar a resposta
  readonly onSuccess?: (data: R) => void;
  readonly onError?: (error: Error) => void;
}

/**
 * Hook para **ações de escrita** (POST/PUT/DELETE).
 *
 * 👉 Use quando precisar enviar dados ou alterar estado no backend.
 */
export function useMutationApi<R = unknown, B = unknown>(url: string, options?: Readonly<UseMutationApiOptions<R, B>>) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const mutate = async (body: B): Promise<R> => {
    setLoading(true);
    setError(null);

    try {
      // Valida o body se houver schema
      const validatedBody = options?.bodySchema?.parse(body) ?? body;

      const res = await fetch(url, {
        method: options?.method || "POST",
        headers: { "Content-Type": "application/json", ...(options?.headers || {}) },
        body: JSON.stringify(validatedBody),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      const response = ApiResponseSchema.parse(json);
      const data: R = options?.responseSchema ? options.responseSchema.parse(response.data) : response.data;
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
