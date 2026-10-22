import type { ZodType } from "zod";
import { handleApiResponse } from "@/shared/lib/utils/api";
import ApiError, { defaultErrorMessage, NETWORK_ERROR_STATUS } from "@/shared/lib/models/ApiError";

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
  // Só leituras têm timeout: uma compra enviada pode ter sido executada mesmo
  // se a conexão cair e não deve ser reenviada automaticamente.
  const readOnly = method === "GET" || path.endsWith("/order-preview");
  const requestSignal = readOnly
    ? AbortSignal.any([...(signal ? [signal] : []), AbortSignal.timeout(30_000)])
    : signal;

  let res: Response;
  try {
    res = await fetch(path, {
      method,
      credentials: "include",
      signal: requestSignal,
      headers: isFormData ? headers : { "Content-Type": "application/json", ...(headers ?? {}) },
      body: body === undefined ? undefined : isFormData ? body : JSON.stringify(body),
    });
    return await handleApiResponse<R>(res, responseSchema);
  } catch (err) {
    // Cancelamento segue como está; o resto é a requisição que não chegou ao servidor
    if (signal?.aborted) throw err;
    if (err instanceof ApiError) throw err;
    if (requestSignal?.aborted) throw new ApiError("O servidor demorou para responder. Tente novamente.", 408, null);
    throw new ApiError(defaultErrorMessage(NETWORK_ERROR_STATUS), NETWORK_ERROR_STATUS, null);
  }
}
