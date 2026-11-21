import { keepPreviousData, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtime } from "@/shared/lib/realtime/apply-realtime";
import type { FundDirectedIssuancePreview } from "@/types";
import { fundKeys } from "@/shared/hooks/fund-keys";
import { fetchPreviewOutcome, outcomeOfPreviewEvent, type PreviewOutcome } from "@/shared/lib/realtime/preview-outcome";

/**
 * O que a emissão dirigida de `quotas` cotas faz, vista por quem consulta como comprador: preço, custo, teto e participação.
 * O servidor guarda o último pedido e entrega a prévia nova por `fund_directed_preview:{id}`.
 */
export function useFundDirectedIssuancePreview(fundId: number, quotas: number, { enabled = true } = {}) {
  const queryClient = useQueryClient();
  const queryKey = fundKeys.directedPreview(fundId, quotas);
  const active = enabled && quotas > 0;

  useRealtime(
    `fund_directed_preview:${fundId}`,
    (event) => {
      if (event.quotas !== quotas) return;
      void applyRealtime<PreviewOutcome<FundDirectedIssuancePreview>>(
        queryClient,
        queryKey,
        outcomeOfPreviewEvent(event),
      );
    },
    active,
  );

  const { data, ...query } = useQuery({
    queryKey,
    queryFn: ({ signal }) =>
      fetchPreviewOutcome<FundDirectedIssuancePreview>(
        `/api/funds/${fundId}/directed-issuance/preview?quotas=${quotas}`,
        { signal },
      ),
    enabled: active,
    placeholderData: keepPreviousData,
    staleTime: 0,
  });

  return { ...query, preview: data?.preview ?? undefined, refused: data?.refused ?? null };
}
