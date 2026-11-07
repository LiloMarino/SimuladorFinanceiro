import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { dividendsToast, splitToast } from "@/shared/lib/corporate-actions-toast";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { queryKeys } from "@/shared/lib/queryKeys";

/**
 * Dono único dos avisos de proventos e desdobramentos: cada pregão com evento renova a
 * carteira e o histórico dos ativos, e avisa o jogador do que caiu no caixa e do que mudou nas ações.
 */
export function CorporateActionsNotifications() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { isToastOn } = useNotificationPreferences();

  useRealtime("corporate_actions", (event) => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.portfolio() });
    const tickers = [...event.dividends.map((line) => line.ticker), ...event.splits.map((split) => split.ticker)];
    for (const ticker of tickers) {
      void queryClient.invalidateQueries({ queryKey: queryKeys.corporateEvents(ticker) });
    }

    if (!isToastOn("CORPORATE_ACTIONS")) return;

    const dividends = dividendsToast(event);
    if (dividends) {
      toast.success(dividends.title, {
        description: dividends.description,
        action: { label: "Ver carteira", onClick: () => void navigate("/portfolio") },
      });
    }
    for (const split of event.splits) {
      const text = splitToast(split);
      toast.info(text.title, {
        description: text.description,
        action: { label: "Ver ativo", onClick: () => void navigate(`/variable-income/${split.ticker}`) },
      });
    }
  });

  return null;
}
