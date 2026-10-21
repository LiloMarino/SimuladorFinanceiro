import { useNavigate } from "react-router-dom";
import { Users } from "lucide-react";
import { toast } from "sonner";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";
import { displayMoney } from "../lib/utils/display";

/** Avisos do que acontece longe da tela atual, com atalho para ver. */
export function GlobalNotifications() {
  const navigate = useNavigate();
  const { preferences } = useNotificationPreferences();

  useRealtime(
    "order_executed",
    (event) => {
      // Cada execução é um aviso; o Toaster os empilha com o mais novo na frente
      toast.success(`${event.action === "buy" ? "Compra" : "Venda"} executada`, {
        description: `${event.quantity} ${event.ticker} a ${displayMoney(event.price)}`,
        action: { label: "Ver", onClick: () => navigate(`/variable-income/${event.ticker}`) },
      });
    },
    preferences.orders.executed,
  );

  useRealtime(
    "order_partial_executed",
    (event) => {
      const missing = event.action === "sell" ? "comprador" : "vendedor";
      toast.warning(`${event.action === "buy" ? "Compra" : "Venda"} executada em parte`, {
        description: `${event.quantity} ${event.ticker} executadas, ${event.remaining} seguem abertas · faltou ${missing}`,
        action: { label: "Ver ordem", onClick: () => navigate(`/variable-income/${event.ticker}`) },
      });
    },
    preferences.orders.partial,
  );

  useRealtime(
    "player_join",
    ({ nickname }) => {
      toast.info(`${nickname} entrou na sala`, { icon: <Users className="size-4 text-toast-info" /> });
    },
    preferences.players.join_exit,
  );

  useRealtime(
    "player_exit",
    ({ nickname }) => {
      toast.info(`${nickname} saiu da sala`);
    },
    preferences.players.join_exit,
  );

  return null;
}
