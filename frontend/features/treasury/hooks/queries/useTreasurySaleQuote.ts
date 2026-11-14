import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useDebounce } from "use-debounce";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { TreasurySaleQuote } from "@/types";

/** A venda de `gross` reais do título hoje, a mercado: IOF, IR, líquido e a comparação com esperar o vencimento. */
export function useTreasurySaleQuote(id: string, gross: string, currentDate: string) {
  const [debouncedGross] = useDebounce(gross || "0", 300);

  return useQuery({
    queryKey: queryKeys.treasurySaleQuote(id, debouncedGross, currentDate),
    queryFn: ({ signal }) =>
      apiFetch<TreasurySaleQuote>(`/api/treasury/${id}/quote?gross=${encodeURIComponent(debouncedGross)}`, {
        signal,
        activeAccount: true,
      }),
    placeholderData: keepPreviousData,
  });
}
