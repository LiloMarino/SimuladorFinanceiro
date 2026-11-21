import { keepPreviousData, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { FundIssuancePreview } from "@/types";
import { fundKeys } from "@/shared/hooks/fund-keys";
import { fetchPreviewOutcome, outcomeOfPreviewEvent, type PreviewOutcome } from "@/shared/lib/realtime/preview-outcome";

/**
 * O que a emissão de `quotas` cotas faz: caixa que entra e controle do gestor, se comprar ou não.
 * O servidor guarda o último pedido e entrega a prévia nova (ou o motivo da recusa) por `fund_issuance_preview:{id}`.
 */
export function useFundIssuancePreview(fundId: number, quotas: number) {
  const queryClient = useQueryClient();
  const queryKey = fundKeys.issuancePreview(fundId, quotas);

  useRealtime(
    `fund_issuance_preview:${fundId}`,
    (event) => {
      if (event.quotas !== quotas) return;
      void applyRealtime<PreviewOutcome<FundIssuancePreview>>(queryClient, queryKey, outcomeOfPreviewEvent(event));
    },
    quotas > 0,
  );

  const { data, ...query } = useQuery({
    queryKey,
    queryFn: ({ signal }) =>
      fetchPreviewOutcome<FundIssuancePreview>(`/api/funds/${fundId}/issuance/preview?quotas=${quotas}`, { signal }),
    enabled: quotas > 0,
    placeholderData: keepPreviousData,
    staleTime: 0,
  });

  return { ...query, preview: data?.preview ?? undefined, refused: data?.refused ?? null };
}
