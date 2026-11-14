import { useQueryClient } from "@tanstack/react-query";
import { useSyncExternalStore } from "react";
import { useFundAccounts } from "@/shared/hooks/queries/useFundAccounts";
import { useSimulation } from "@/shared/hooks/useSimulation";
import {
  getSelectedFundId,
  resolveActiveAccount,
  selectFund,
  subscribeActiveAccount,
} from "@/shared/lib/active-account";
import { queryKeys } from "@/shared/lib/queryKeys";

// O que as ordens movimentam: trocar de conta renova tudo isso
const ACCOUNT_KEYS = [
  queryKeys.variableIncome(),
  queryKeys.fixedIncome(),
  queryKeys.treasury(),
  queryKeys.portfolio(),
  queryKeys.fundAccounts(),
];

/** A conta com que o jogador opera (a pessoal ou uma gestora que ele gere) e a troca entre elas. */
export function useActiveAccount() {
  const queryClient = useQueryClient();
  const { simulation } = useSimulation();
  const match = simulation?.simulation;
  const simulationId = match?.id;
  const { data: accounts } = useFundAccounts({ enabled: match?.funds_enabled === true });

  const selectedFundId = useSyncExternalStore(subscribeActiveAccount, () =>
    simulationId === undefined ? null : getSelectedFundId(simulationId),
  );

  const switchAccount = (fundId: number | null) => {
    if (simulationId === undefined) return;
    selectFund(simulationId, fundId);
    ACCOUNT_KEYS.forEach((queryKey) => void queryClient.invalidateQueries({ queryKey }));
  };

  return { accounts, active: resolveActiveAccount(accounts, selectedFundId), switchAccount };
}
