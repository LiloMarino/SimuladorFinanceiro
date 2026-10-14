import { ApiErrorSchema } from "@/shared/lib/schemas/api";
import type { ZodType } from "zod";
import ApiError, { defaultErrorMessage } from "../models/ApiError";

/**
 * Centraliza o parsing e tratamento de respostas da API.
 * Valida erros com schema Zod e retorna conteúdo direto em sucesso.
 */
export async function handleApiResponse<R>(res: Response, responseSchema?: ZodType<R>): Promise<R> {
  let json: unknown;

  try {
    json = await res.json();
  } catch {
    // Pode acontecer em respostas sem corpo (ex: 204 No Content)
    if (res.ok) {
      // Retorna undefined para casos sem payload
      return undefined as R;
    }

    // Se não tem corpo mas é erro, usa status code
    throw new ApiError(defaultErrorMessage(res.status), res.status, null);
  }

  if (!res.ok) {
    // Valida schema de erro
    const errorData = ApiErrorSchema.safeParse(json);
    const message = errorData.success ? errorData.data.message : defaultErrorMessage(res.status);

    throw new ApiError(message, res.status, json);
  }

  // Retorna o conteúdo diretamente
  return responseSchema ? responseSchema.parse(json) : (json as R);
}
