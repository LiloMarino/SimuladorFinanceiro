import { useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useLifeStatus } from "@/shared/hooks/queries/useLifeStatus";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { displayRatePercent } from "@/shared/lib/financial-independence";
import { queryKeys } from "@/shared/lib/queryKeys";
import { displayMonthName, displaySignedMoney } from "@/shared/lib/utils/display";
import type { SimulationState } from "@/types";

/**
 * Dono único da vida financeira em tempo real: renova a vida financeira e o histórico
 * quando o caixa muda (cash_update) ou um imprevisto cai (life_event) e avisa de cada um.
 * A renovação acompanha os eventos que mexem no caixa, não o ritmo dos pregões.
 */
export function LifeNotifications() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { simulation } = useSimulation();
  const { data: status } = useLifeStatus();
  const current = simulation?.active ? simulation.simulation : null;
  const simulationId = current?.id ?? 0;
  const independence = current?.game_type === "FINANCIAL_INDEPENDENCE";

  // O caixa do evento anterior; o primeiro evento parte do que a vida financeira já mostrava
  const lastCash = useRef<number | null>(null);

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

  useRealtime(
    "cash_update",
    ({ cash }) => {
      const now = Number(cash);
      const wasNegative =
        lastCash.current === null ? Number(status?.overdraft_daily_interest ?? 0) > 0 : lastCash.current < 0;
      lastCash.current = now;

      void queryClient.invalidateQueries({
        queryKey: queryKeys.lifeStatus(simulationId),
      });
      if (wasNegative || now >= 0) return;

      void queryClient.invalidateQueries({
        queryKey: queryKeys.lifeHistoryAll(simulationId),
      });
      const today = queryClient.getQueryData<SimulationState>(queryKeys.simulationState())?.current_date;
      const rate = status ? `${displayRatePercent(status.overdraft_monthly_rate)} ao mês` : "juros";
      toast.error(`Caixa negativo: ${displaySignedMoney(now)}`, {
        description: `Cheque especial cobra ${rate} até você cobrir`,
        action: today ? showHistory(today) : undefined,
      });
    },
    independence,
  );

  return null;
}
