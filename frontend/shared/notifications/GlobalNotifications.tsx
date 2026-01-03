import { toast } from "sonner";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { useNotificationSettings } from "@/shared/hooks/useNotificationSettings";

export function GlobalNotifications() {
  const { preferences } = useNotificationSettings();

  useRealtime("order_executed", (event) => {
    if (!preferences.orders.executed) return;

    const { ticker, action, quantity, price, status } = event;

    if (status === "PARTIAL" && !preferences.orders.partial) {
      return;
    }

    toast.success(`${action === "BUY" ? "Compra" : "Venda"} executada`, {
      description: `${quantity}x ${ticker} @ R$ ${price.toFixed(2)}${status === "PARTIAL" ? " (parcial)" : ""}`,
    });
  });

  return null;
}
