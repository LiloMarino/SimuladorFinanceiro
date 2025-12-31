import { useState } from "react";
import { handleApiResponse } from "@/shared/lib/utils/api";
import type { ZodType } from "zod";
import ApiError from "@/shared/lib/models/ApiError";

interface UseFormDataMutationOptions<R = unknown> {
  readonly method?: "POST" | "PUT" | "DELETE";
  readonly responseSchema?: ZodType<R>;
  readonly onSuccess?: (data: R) => void;
  readonly onError?: (error: Error) => void;
}

/**
 * Converte um objeto em FormData.
 * File/Blob são preservados, o resto é convertido para string.
 */
function toFormData(obj: Record<string, string | number | boolean | File | Blob | null | undefined>): FormData {
  const formData = new FormData();
  for (const [key, value] of Object.entries(obj)) {
    if (value === undefined || value === null) continue;
    formData.append(key, value instanceof Blob ? value : String(value));
  }
  return formData;
}

/**
 * Hook para envio de FormData (arquivos, uploads, etc.)
 */
export function useFormDataMutation<R = unknown>(url: string, options?: Readonly<UseFormDataMutationOptions<R>>) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const { method = "POST", responseSchema, onSuccess, onError } = options ?? {};

  const mutate = async (
    payload: Record<string, string | number | boolean | File | Blob | null | undefined>
  ): Promise<R> => {
    setLoading(true);
    setError(null);

    try {
      const formData = toFormData(payload);

      const res = await fetch(url, {
        method,
        body: formData,
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
  };

  return { mutate, loading, error };
}
