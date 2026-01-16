import { ApiErrorSchema } from "@/shared/lib/schemas/api";
import type { ZodType } from "zod";
import ApiError from "../models/ApiError";

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
 * Valida erros com schema Zod e retorna conteúdo direto em sucesso.
 */
export async function handleApiResponse<R>(res: Response, responseSchema?: ZodType<R>): Promise<R> {
  let json: unknown = null;

  try {
    json = await res.json();
  } catch {
    // Pode acontecer em respostas sem corpo (ex: 204 No Content)
    if (res.ok) {
      // Retorna undefined para casos sem payload
      return undefined as R;
    }

    // Se não tem corpo mas é erro, usa status code
    throw new ApiError(getHttpStatusText(res.status), res.status, null);
  }

  if (!res.ok) {
    // Valida schema de erro
    const errorData = ApiErrorSchema.safeParse(json);
    const message = errorData.success ? errorData.data.message : getHttpStatusText(res.status);

    throw new ApiError(message, res.status, json);
  }

  // Retorna o conteúdo diretamente
  return responseSchema ? responseSchema.parse(json) : (json as R);
}
