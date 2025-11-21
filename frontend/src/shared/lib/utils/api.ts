import { ApiResponseSchema } from "@/shared/lib/schemas/api";
import type { ZodType } from "zod";

/**
 * Retorna o nome amigável padrão para um código HTTP.
 */
function getHttpStatusText(status: number): string {
  const statuses: Record<number, string> = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    408: "Request Timeout",
    409: "Conflict",
    413: "Payload Too Large",
    415: "Unsupported Media Type",
    422: "Unprocessable Entity",
    429: "Too Many Requests",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
  };
  return statuses[status] ?? "Unknown Error";
}

/**
 * Centraliza o parsing e tratamento de respostas da API.
 * Inclui mensagens padronizadas com código HTTP e descrição legível.
 */
export async function handleApiResponse<R>(res: Response, responseSchema?: ZodType<R>): Promise<R> {
  let json: unknown = null;

  try {
    json = await res.json();
  } catch {
    // Pode acontecer em respostas sem corpo (ex: 204 No Content)
  }

  if (!res.ok) {
    const message =
      (json as Record<string, unknown> | null)?.message ?? getHttpStatusText(res.status) ?? "Unexpected error";
    throw new Error(`${message} (${res.status} – ${getHttpStatusText(res.status)})`);
  }

  const parsed = ApiResponseSchema.parse(json);
  return responseSchema ? responseSchema.parse(parsed.data) : parsed.data;
}
