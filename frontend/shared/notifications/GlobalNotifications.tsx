import { toast } from "sonner";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { useNotificationSettings } from "@/shared/hooks/useNotificationSettings";
import { displayMoney } from "../lib/utils/display";

export function GlobalNotifications() {
  const { preferences } = useNotificationSettings();

  useRealtime(
    "order_executed",
    (event) => {
      if (!preferences.orders.executed) return;

      toast.info(`${event.action === "buy" ? "Compra" : "Venda"} executada`, {
        description: `${event.quantity}x ${event.ticker} @ ${displayMoney(event.price)}`,
      });
    },
    preferences.orders.executed
  );

  useRealtime(
    "order_partial_executed",
    (event) => {
      if (!preferences.orders.partial) return;

      toast.info(`${event.action === "buy" ? "Compra" : "Venda"} parcial`, {
        description: `${event.quantity}x ${event.ticker} @ ${displayMoney(event.price)} (restam ${event.remaining})`,
      });
    },
    preferences.orders.partial
  );

  useRealtime("order_rejected", (event) => {
    toast.error(`Ordem rejeitada`, {
      description: event.reason,
    });
  });

  useRealtime("player_join", ({ nickname }) => {
    toast.info(`${nickname} entrou na partida`);
  });

  useRealtime("player_exit", ({ nickname }) => {
    toast.info(`${nickname} saiu da partida`);
  });

  return null;
}
