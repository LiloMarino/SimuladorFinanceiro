import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import type { FundBuybackPreview } from "@/types";
import { fundKeys } from "../fund-keys";

/** O custo, o ágio e o patrimônio por cota de quem fica, para `quantity` cotas a até `maxPrice` (decimal em string). */
export function useFundBuybackPreview(fundId: number, quantity: number, maxPrice: string) {
  return useQuery({
    queryKey: fundKeys.buybackPreview(fundId, quantity, maxPrice),
    queryFn: ({ signal }) =>
      apiFetch<FundBuybackPreview>(`/api/funds/${fundId}/buyback/preview?quantity=${quantity}&max_price=${maxPrice}`, {
        signal,
      }),
    enabled: quantity > 0 && Number(maxPrice) > 0,
    placeholderData: keepPreviousData,
  });
}
