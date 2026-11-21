import { apiFetch, type ApiFetchInit } from "@/shared/lib/api/apiFetch";
import ApiError from "@/shared/lib/models/ApiError";

/** O que a chave de uma prévia guarda, vindo da leitura HTTP ou do aviso: a prévia ou o motivo da recusa. */
export type PreviewOutcome<T> = { preview: T | null; refused: string | null };

/** Status com que a API recusa uma prévia por regra (o servidor usa a mesma lista ao decidir o que vira `refused`). */
const RULE_REFUSAL_STATUS: readonly number[] = [409, 422];

/** O desfecho que o aviso entrega à chave da prévia. */
export const outcomeOfPreviewEvent = <T>({ preview, refused }: PreviewOutcome<T>): PreviewOutcome<T> => ({
  preview,
  refused,
});

/** A recusa de regra é dado da prévia, igual ao aviso; permissão, recurso inexistente, falha do servidor e da rede seguem como erro da consulta. */
export async function fetchPreviewOutcome<T>(path: string, init: ApiFetchInit<T> = {}): Promise<PreviewOutcome<T>> {
  try {
    return { preview: await apiFetch<T>(path, init), refused: null };
  } catch (failure) {
    if (failure instanceof ApiError && RULE_REFUSAL_STATUS.includes(failure.status)) {
      return { preview: null, refused: failure.message };
    }
    throw failure;
  }
}
