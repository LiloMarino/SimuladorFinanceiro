import type { ZodType } from "zod";
import { handleApiResponse } from "@/shared/lib/utils/api";

export interface ApiFetchInit<R = unknown> {
  readonly method?: "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
  readonly body?: unknown;
  readonly headers?: Record<string, string>;
  readonly responseSchema?: ZodType<R>;
  readonly signal?: AbortSignal;
}

/**
 * Fetch + handleApiResponse num único ponto, usado dentro de todo
 * queryFn/mutationFn do TanStack Query. `body` pode ser um objeto
 * serializável (vira JSON) ou uma instância de FormData (enviada crua).
 */
export async function apiFetch<R = unknown>(path: string, init: ApiFetchInit<R> = {}): Promise<R> {
  const { method = "GET", body, headers, responseSchema, signal } = init;
  const isFormData = body instanceof FormData;

  const res = await fetch(path, {
    method,
    credentials: "include",
    signal,
    headers: isFormData ? headers : { "Content-Type": "application/json", ...(headers ?? {}) },
    body: body === undefined ? undefined : isFormData ? body : JSON.stringify(body),
  });

  return handleApiResponse<R>(res, responseSchema);
}
