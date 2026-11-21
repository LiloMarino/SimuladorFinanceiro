import { useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { dividendsToast, splitToast } from "@/shared/lib/corporate-actions-toast";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { queryKeys } from "@/shared/lib/queryKeys";

/**
 * Dono único dos avisos de proventos e desdobramentos: avisa o jogador do que caiu no caixa e do
 * que mudou nas ações, e relê os proventos recebidos. A carteira chega por `portfolio_update` e o
 * histórico do ativo por `corporate_events_update:{ticker}`.
 */
export function CorporateActionsNotifications() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { isToastOn } = useNotificationPreferences();

  useRealtime("corporate_actions", (event) => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.portfolioDividends("personal") });

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
