import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { FundIssuancePreview } from "@/types";
import { fundKeys } from "../fund-keys";

/** O que a emissão de `quotas` cotas faz: caixa que entra e controle do gestor, se comprar ou não. */
export function useFundIssuancePreview(fundId: number, quotas: number) {
  return useQuery({
    queryKey: fundKeys.issuancePreview(fundId, quotas),
    queryFn: ({ signal }) =>
      apiFetch<FundIssuancePreview>(`/api/funds/${fundId}/issuance/preview?quotas=${quotas}`, { signal }),
    enabled: quotas > 0,
    placeholderData: keepPreviousData,
  });
}
