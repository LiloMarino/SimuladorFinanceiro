import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { FundDirectedIssuancePreview } from "@/types";
import { fundKeys } from "@/shared/hooks/fund-keys";

/** O que a emissão dirigida de `quotas` cotas faz, vista por quem consulta como comprador: preço, custo, teto e participação. */
export function useFundDirectedIssuancePreview(fundId: number, quotas: number, { enabled = true } = {}) {
  return useQuery({
    queryKey: fundKeys.directedPreview(fundId, quotas),
    queryFn: ({ signal }) =>
      apiFetch<FundDirectedIssuancePreview>(`/api/funds/${fundId}/directed-issuance/preview?quotas=${quotas}`, {
        signal,
      }),
    enabled: enabled && quotas > 0,
    placeholderData: keepPreviousData,
  });
}
