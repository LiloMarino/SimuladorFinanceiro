import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { eventAccountKey } from "@/shared/lib/active-account";
import { dayOrdersSummary, isCreditAction, orderToastTitle } from "@/shared/lib/strategy-orders";
import { mergeStrategyLog, type StrategyLogData } from "@/shared/lib/strategy-log-merge";
import { applyRealtime, applyRealtimeDelta } from "@/shared/lib/realtime/apply-realtime";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { queryKeys } from "@/shared/lib/queryKeys";
import { displayMoney } from "@/shared/lib/utils/display";
import type { MyStrategy, StrategyLogFilter } from "@/types";

/** Até este número de ordens no dia, cada uma tem o seu aviso; acima, um resumo só. */
const INDIVIDUAL_TOAST_LIMIT = 2;

const LOG_FILTERS: StrategyLogFilter[] = ["all", "orders", "modes"];

/**
 * Dono único dos avisos da estratégia em tempo real: o modo e o registro da conta chegam prontos e entram no
 * cache de quem os pediu, esteja a tela aberta ou não; os toasts avisam do que a estratégia fez.
 */
export function StrategyNotifications() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { isToastOn } = useNotificationPreferences();

  const seeStrategies = { label: "Ver", onClick: () => void navigate("/strategies") };

  // O modo da conta (a estratégia ligada, o erro que a devolveu ao manual e o painel)
  useRealtime("strategy_update", ({ account, my_strategy }) => {
    void applyRealtime<MyStrategy>(queryClient, queryKeys.myStrategyOf(eventAccountKey(account)), my_strategy);
  });

  // Linhas novas ou mudadas do registro da conta, com o total de cada filtro
  useRealtime("strategy_log_update", ({ account, rows, total_all, total_orders, total_modes }) => {
    const totals = { all: total_all, orders: total_orders, modes: total_modes };
    for (const filter of LOG_FILTERS) {
      void applyRealtimeDelta<StrategyLogData>(
        queryClient,
        queryKeys.strategyLog(eventAccountKey(account), filter),
        (current) => mergeStrategyLog(current, filter, rows, totals[filter]),
      );
    }
  });

  useRealtime("strategy_orders", ({ orders }) => {
    if (!isToastOn("STRATEGY_ORDERS")) return;
    if (orders.length > INDIVIDUAL_TOAST_LIMIT) {
      toast.info(`A estratégia mandou ${orders.length} ordens hoje`, {
        description: dayOrdersSummary(orders),
        action: seeStrategies,
      });
      return;
    }
    for (const order of orders) {
      const show =
        order.status === "refused"
          ? toast.warning
          : order.status === "executed" || order.status === "partial"
            ? toast.success
            : toast.info;
      show(orderToastTitle(order), {
        description: [
          order.price === null || isCreditAction(order.action) ? null : displayMoney(order.price),
          order.reason,
        ]
          .filter(Boolean)
          .join(" · "),
        action: seeStrategies,
      });
    }
  });

  return null;
}
