import { useState } from "react";
import { ApiResponseSchema } from "@/lib/schemas/api";
import type { ZodType } from "zod";

interface UseFormDataMutationOptions<R = unknown> {
  readonly method?: "POST" | "PUT" | "DELETE";
  readonly responseSchema?: ZodType<R>;
  readonly onSuccess?: (data: R) => void;
  readonly onError?: (error: Error) => void;
}

/**
 * Hook para enviar FormData (arquivos, uploads, etc.)
 */
export function useFormDataMutation<R = unknown>(url: string, options?: Readonly<UseFormDataMutationOptions<R>>) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const mutate = async (formData: FormData): Promise<R> => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(url, {
        method: options?.method || "POST",
        body: formData,
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      const parsed = ApiResponseSchema.parse(json);
      const data: R = options?.responseSchema ? options.responseSchema.parse(parsed.data) : parsed.data;
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
