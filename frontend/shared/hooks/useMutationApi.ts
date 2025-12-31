import { useCallback, useState } from "react";
import { handleApiResponse } from "@/shared/lib/utils/api";
import type { ZodType } from "zod";
import ApiError from "@/shared/lib/models/ApiError";

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
  const [error, setError] = useState<ApiError | null>(null);
  const { method = "POST", headers, bodySchema, responseSchema, onSuccess, onError } = options ?? {};

  const mutate = useCallback(
    async (body: B): Promise<R> => {
      setLoading(true);
      setError(null);

      try {
        // Valida o body se houver schema
        const validatedBody = bodySchema?.parse(body) ?? body;

        const res = await fetch(url, {
          method,
          headers: { "Content-Type": "application/json", ...(headers ?? {}) },
          credentials: "include",
          body: JSON.stringify(validatedBody),
        });

        const data = await handleApiResponse<R>(res, responseSchema);
        onSuccess?.(data);
        return data;
      } catch (err) {
        const apiError = err instanceof ApiError ? err : new ApiError("Unexpected error", 0, err);
        setError(apiError);
        onError?.(apiError);
        throw apiError;
      } finally {
        setLoading(false);
      }
    },
    [url, method, headers, bodySchema, responseSchema, onSuccess, onError]
  );

  return { mutate, loading, error };
}
