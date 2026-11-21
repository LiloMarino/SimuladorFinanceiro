import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { dayOrdersSummary, orderToastTitle } from "@/shared/lib/strategy-orders";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { queryKeys } from "@/shared/lib/queryKeys";
import { displayMoney } from "@/shared/lib/utils/display";

/** Até este número de ordens no dia, cada uma tem o seu aviso; acima, um resumo só. */
const INDIVIDUAL_TOAST_LIMIT = 2;

/**
 * Dono único dos avisos da estratégia em tempo real: cada evento renova o modo e o registro, e avisa do que ela fez ou de por que voltou ao manual.
 */
export function StrategyNotifications() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { isToastOn } = useNotificationPreferences();

  const renewLog = () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.myStrategy() });
    void queryClient.invalidateQueries({ queryKey: queryKeys.strategyLogs() });
  };
  const renew = () => {
    renewLog();
    void queryClient.invalidateQueries({ queryKey: queryKeys.portfolio() });
  };
  const seeStrategies = { label: "Ver", onClick: () => void navigate("/strategies") };

  // A carteira muda com a ordem executada e chega pronta por `portfolio_update` ao fim do pregão
  useRealtime("strategy_orders", ({ orders }) => {
    renewLog();
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
        description: [order.price === null ? null : displayMoney(order.price), order.reason]
          .filter(Boolean)
          .join(" · "),
        action: seeStrategies,
      });
    }
  });

  // O desligamento por erro é pendência: o aviso nasce na lista de pendências; aqui só renova a tela
  useRealtime("strategy_update", renew);

  return null;
}
