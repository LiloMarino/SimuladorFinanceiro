import type { Order } from "@/types";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import { useRealtime } from "@/shared/hooks/useRealtime";

export function usePendingOrders(ticker: string | undefined) {
    const { data: pendingOrders, setData: setPendingOrders } = useQueryApi<Order[]>(
        `/api/variable-income/${ticker}/orders`,
    );

    useRealtime(`order_added:${ticker}`, ({ order }) => {
        setPendingOrders((prev) => {
            if (!prev) return [order];

            if (prev.some((o) => o.id === order.id)) {
                return prev;
            }

            return [...prev, order];
        });
    });

    useRealtime(`order_updated:${ticker}`, ({ order }) => {
        setPendingOrders((prev) => {
            if (!prev) return prev;
            return prev.map((o) => (o.id === order.id ? order : o));
        });
    });

    useRealtime(`order_book_snapshot:${ticker}`, ({ orders }) => {
        setPendingOrders(orders);
    });

    return pendingOrders ?? [];
}
