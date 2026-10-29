import { useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useRenewElection } from "./useRenewElection";

/** Renova o que um acordo de apoio mexe: a base, o orçamento (a emenda é gasto) e o painel do governo. */
export function useRenewBase() {
  const queryClient = useQueryClient();
  const renew = useRenewElection();

  return () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.base() });
    void queryClient.invalidateQueries({ queryKey: queryKeys.budget() });
    renew();
  };
}
