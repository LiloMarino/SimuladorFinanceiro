import { useQuery, useQueryClient } from "@tanstack/react-query";
import type { Order } from "@/types";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { applyRealtime, applyRealtimeDelta } from "@/shared/lib/realtime/apply-realtime";
import { applyOrderEvent } from "../../lib/order-book";

export function usePendingOrders(ticker: string | undefined) {
  const queryClient = useQueryClient();
  const queryKey = queryKeys.variableIncomeOrders(ticker ?? "");

  const { data, isLoading, error, refetch } = useQuery({
    queryKey,
    queryFn: ({ signal }) => apiFetch<Order[]>(`/api/variable-income/${ticker}/orders`, { signal }),
    enabled: !!ticker,
  });

  // O aviso traz a ordem: entra no livro na posição que o casamento dá a ela
  const applyOrder = ({ order }: { order: Order }) =>
    void applyRealtimeDelta<Order[]>(queryClient, queryKey, (current) => applyOrderEvent(current, order));

  useRealtime(`order_added:${ticker}`, applyOrder, !!ticker);
  useRealtime(`order_updated:${ticker}`, applyOrder, !!ticker);

  useRealtime(
    `order_book_snapshot:${ticker}`,
    ({ orders }) => {
      void applyRealtime<Order[]>(queryClient, queryKey, orders);
    },
    !!ticker,
  );

  return { orders: data ?? [], isLoading, error, refetch };
}
