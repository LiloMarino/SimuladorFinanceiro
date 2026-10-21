import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { PriceImpactPreview } from "@/types";

/** Curva do impacto de uma compra no preço, para o exemplo da simulação. */
export function usePriceImpactPreview(k: number, decayDays: number, { enabled }: { enabled: boolean }) {
  return useQuery({
    queryKey: queryKeys.priceImpactPreview(k, decayDays),
    queryFn: ({ signal }) =>
      apiFetch<PriceImpactPreview>(`/api/simulation/price-impact-preview?k=${k}&decay_days=${decayDays}`, { signal }),
    enabled,
  });
}
