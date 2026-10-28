import { useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/shared/lib/queryKeys";

/** Renova o que uma ação política mexe: a eleição, a campanha, o governo, as promessas e o caixa (contribuição e doação saem dele). */
export function useRenewElection() {
  const queryClient = useQueryClient();

  return () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.election() });
    void queryClient.invalidateQueries({ queryKey: queryKeys.government() });
    void queryClient.invalidateQueries({ queryKey: queryKeys.campaign() });
    void queryClient.invalidateQueries({ queryKey: queryKeys.promises() });
    void queryClient.invalidateQueries({ queryKey: queryKeys.balances() });
    void queryClient.invalidateQueries({ queryKey: queryKeys.portfolio() });
  };
}
