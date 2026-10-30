import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { queryKeys } from "@/shared/lib/queryKeys";
import { displayMonthName, displaySignedMoney } from "@/shared/lib/utils/display";

/**
 * Dono único da vida financeira em tempo real: renova a vida financeira e o histórico
 * quando o caixa muda (cash_update) ou um imprevisto cai (life_event) e avisa de cada imprevisto.
 * A renovação acompanha os eventos que mexem no caixa, não o ritmo dos pregões.
 */
export function LifeNotifications() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { simulation } = useSimulation();
  const { isToastOn } = useNotificationPreferences();
  const current = simulation?.active ? simulation.simulation : null;
  const simulationId = current?.id ?? 0;
  const independence = current?.game_type === "FINANCIAL_INDEPENDENCE";

  const showHistory = (highlightDate: string) => ({
    label: "Ver histórico",
    onClick: () => navigate("/goal", { state: { highlightDate } }),
  });

  useRealtime(
    "life_event",
    (event) => {
      void queryClient.invalidateQueries({
        queryKey: queryKeys.lifeStatus(simulationId),
      });
      void queryClient.invalidateQueries({
        queryKey: queryKeys.lifeHistoryAll(simulationId),
      });

      if (!isToastOn("LIFE_EVENT")) return;

      // O imprevisto que corta o salário não tira dinheiro do caixa: o aviso fala do mês seguinte
      if (event.effect === "SKIP_NEXT_SALARY") {
        toast.warning(`Imprevisto: ${event.label.toLowerCase()}`, {
          description: `O salário de ${displayMonthName(event.event_date, 1)} não entra; a despesa continua`,
          action: showHistory(event.event_date),
        });
        return;
      }
      toast.warning(`Imprevisto: ${event.label.toLowerCase()}`, {
        description: `${displaySignedMoney(-Number(event.amount))} do caixa · todos receberam o mesmo`,
        action: showHistory(event.event_date),
      });
    },
    independence,
  );

  // O caixa negativo avisa pela pendência; aqui o caixa só renova a vida financeira
  useRealtime(
    "cash_update",
    () => {
      void queryClient.invalidateQueries({
        queryKey: queryKeys.lifeStatus(simulationId),
      });
    },
    independence,
  );

  return null;
}
