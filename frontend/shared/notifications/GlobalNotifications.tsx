import { useRef } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { useNotificationSettings } from "@/shared/hooks/useNotificationSettings";
import { displayMoney } from "../lib/utils/display";

const EXECUTIONS_TOAST_ID = "orders-executed";
// Execuções que chegam dentro desta janela somam no mesmo toast
const STACK_WINDOW_MS = 4000;

function joinTickers(tickers: string[]) {
  return tickers.length > 1 ? `${tickers.slice(0, -1).join(", ")} e ${tickers.at(-1)}` : tickers[0];
}

/** Avisos do que acontece longe da tela atual, com atalho para ver. */
export function GlobalNotifications() {
  const navigate = useNavigate();
  const { preferences } = useNotificationSettings();
  const stack = useRef({ tickers: [] as string[], count: 0, lastAt: 0 });

  useRealtime(
    "order_executed",
    (event) => {
      const now = Date.now();
      const stacking = now - stack.current.lastAt < STACK_WINDOW_MS;
      const tickers = stacking ? stack.current.tickers : [];
      stack.current = {
        tickers: tickers.includes(event.ticker) ? tickers : [...tickers, event.ticker],
        count: stacking ? stack.current.count + 1 : 1,
        lastAt: now,
      };

      if (stack.current.count === 1) {
        toast.success(`${event.action === "buy" ? "Compra" : "Venda"} executada`, {
          id: EXECUTIONS_TOAST_ID,
          description: `${event.quantity} ${event.ticker} a ${displayMoney(event.price)}`,
          action: { label: "Ver", onClick: () => navigate(`/variable-income/${event.ticker}`) },
        });
        return;
      }

      toast.success(`${stack.current.count} ordens executadas`, {
        id: EXECUTIONS_TOAST_ID,
        description: joinTickers(stack.current.tickers),
        action: { label: "Ver todas", onClick: () => navigate("/portfolio") },
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
      toast.info(`${nickname} entrou na sala`);
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
