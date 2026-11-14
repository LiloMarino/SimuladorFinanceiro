import { useQuery, useQueryClient } from "@tanstack/react-query";
import type { Order } from "@/types";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";

export function usePendingOrders(ticker: string | undefined) {
  const queryClient = useQueryClient();
  const queryKey = queryKeys.variableIncomeOrders(ticker ?? "");

  const { data, isLoading, error, refetch } = useQuery({
    queryKey,
    queryFn: ({ signal }) => apiFetch<Order[]>(`/api/variable-income/${ticker}/orders`, { signal }),
    enabled: !!ticker,
  });

  // O backend entrega o livro na ordem de prioridade do casamento: o evento de ordem recarrega a lista
  const reload = () => void queryClient.invalidateQueries({ queryKey });

  useRealtime(`order_added:${ticker}`, reload, !!ticker);
  useRealtime(`order_updated:${ticker}`, reload, !!ticker);

  useRealtime(
    `order_book_snapshot:${ticker}`,
    ({ orders }) => {
      queryClient.setQueryData(queryKey, orders);
    },
    !!ticker,
  );

  return { orders: data ?? [], isLoading, error, refetch };
}
