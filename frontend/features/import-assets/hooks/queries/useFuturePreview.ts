import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { FuturePreview, FuturePreviewRequest } from "@/types";

/** Prévia do futuro sem gravar nada; `request` nulo enquanto os controles não formam um pedido válido. */
export function useFuturePreview(request: FuturePreviewRequest | null, { enabled = true }: { enabled?: boolean } = {}) {
  return useQuery({
    queryKey: queryKeys.futurePreview(request ?? {}),
    queryFn: ({ signal }) =>
      apiFetch<FuturePreview>("/api/import-assets/future/preview", { method: "POST", body: request, signal }),
    enabled: enabled && request !== null,
    // A prévia anterior fica na tela, esmaecida, até a nova chegar
    placeholderData: keepPreviousData,
    // O erro da prévia tem o próprio "Tentar de novo"
    retry: false,
    // A prévia depende do que a base tem agora: cada abertura do diálogo gera de novo
    staleTime: 0,
    refetchOnWindowFocus: false,
  });
}
