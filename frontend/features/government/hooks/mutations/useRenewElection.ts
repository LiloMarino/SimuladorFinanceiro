import { useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/shared/lib/queryKeys";

/** Renova o que uma ação política mexe: a eleição e o caixa (contribuição e doação saem dele). */
export function useRenewElection() {
  const queryClient = useQueryClient();

  return () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.election() });
    void queryClient.invalidateQueries({ queryKey: queryKeys.portfolio() });
  };
}
