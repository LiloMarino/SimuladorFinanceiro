import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useNotificationPreferences } from "@/shared/hooks/useNotificationPreferences";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { queryKeys } from "@/shared/lib/queryKeys";
import { displayMoney } from "@/shared/lib/utils/display";

/**
 * Dono único do aviso de resgate automático: cada título vendido para cobrir uma
 * despesa renova a carteira e a renda fixa e avisa o jogador do que saiu.
 */
export function AutoRedeemNotifications() {
  const queryClient = useQueryClient();
  const { isToastOn } = useNotificationPreferences();

  useRealtime("auto_redeem", (event) => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.portfolio() });
    void queryClient.invalidateQueries({ queryKey: queryKeys.fixedIncome() });

    if (!isToastOn("AUTO_REDEEM")) return;
    toast.info(`Resgatado ${displayMoney(event.net_amount)} de ${event.asset_name}`, {
      description: `Para cobrir ${event.reason}`,
    });
  });

  return null;
}
