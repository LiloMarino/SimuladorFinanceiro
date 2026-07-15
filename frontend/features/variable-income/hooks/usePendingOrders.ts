import { useQueryClient } from "@tanstack/react-query";
import type { Order } from "@/types";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRealtime } from "@/shared/hooks/useRealtime";

export function usePendingOrders(ticker: string | undefined) {
    const queryClient = useQueryClient();

    const { data: pendingOrders } = useApiQuery({
        queryKey: queryKeys.variableIncomeOrders(ticker ?? ""),
        queryFn: ({ signal }) => apiFetch<Order[]>(`/api/variable-income/${ticker}/orders`, { signal }),
        enabled: !!ticker,
    });

    const setPendingOrders = (updater: Order[] | ((prev: Order[] | undefined) => Order[])) => {
        queryClient.setQueryData(queryKeys.variableIncomeOrders(ticker ?? ""), updater);
    };

    useRealtime(
        `order_added:${ticker}`,
        ({ order }) => {
            setPendingOrders((prev) => {
                if (!prev) return [order];

                if (prev.some((o) => o.id === order.id)) {
                    return prev;
                }

                return [...prev, order];
            });
        },
        !!ticker,
    );

    useRealtime(
        `order_updated:${ticker}`,
        ({ order }) => {
            setPendingOrders((prev) => {
                if (!prev) return [order];
                return prev.map((o) => (o.id === order.id ? order : o));
            });
        },
        !!ticker,
    );

    useRealtime(
        `order_book_snapshot:${ticker}`,
        ({ orders }) => {
            setPendingOrders(orders);
        },
        !!ticker,
    );

    return pendingOrders ?? [];
}
