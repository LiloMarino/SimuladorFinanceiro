import { useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/shared/lib/queryKeys";

/** Renova o que uma operação de crédito mexe: o crédito, a carteira e o caixa. */
export function useRenewCredit() {
  const queryClient = useQueryClient();

  return () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.credit() });
    void queryClient.invalidateQueries({ queryKey: queryKeys.portfolio() });
    void queryClient.invalidateQueries({ queryKey: queryKeys.simulationState() });
  };
}
