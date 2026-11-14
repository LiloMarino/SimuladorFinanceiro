import { useQueryClient } from "@tanstack/react-query";
import { useSyncExternalStore } from "react";
import { useFundAccounts } from "@/shared/hooks/queries/useFundAccounts";
import { useSimulation } from "@/shared/hooks/useSimulation";
import {
  accountKey,
  getSelectedFundId,
  resolveActiveAccount,
  selectFund,
  subscribeActiveAccount,
} from "@/shared/lib/active-account";
import { queryKeys } from "@/shared/lib/queryKeys";

// O que não carrega a conta na chave: trocar de conta renova tudo isso. A carteira e o caixa
// têm uma entrada de cache por conta e o tempo real mantém cada uma viva.
const ACCOUNT_KEYS = [queryKeys.variableIncome(), queryKeys.fixedIncome(), queryKeys.treasury()];

/** A conta com que o jogador opera (a pessoal ou uma gestora que ele gere) e a troca entre elas. */
export function useActiveAccount() {
  const queryClient = useQueryClient();
  const { simulation } = useSimulation();
  const match = simulation?.simulation;
  const simulationId = match?.id;
  const { data: accounts } = useFundAccounts({ enabled: match?.funds_enabled === true });

  const storedFundId = useSyncExternalStore(subscribeActiveAccount, () =>
    simulationId === undefined ? null : getSelectedFundId(simulationId),
  );
  // Sem a expansão ligada só existe a conta pessoal
  const selectedFundId = match?.funds_enabled === true ? storedFundId : null;

  const switchAccount = (fundId: number | null) => {
    if (simulationId === undefined) return;
    selectFund(simulationId, fundId);
    ACCOUNT_KEYS.forEach((queryKey) => void queryClient.invalidateQueries({ queryKey }));
  };

  const active = resolveActiveAccount(accounts, selectedFundId);

  return {
    accounts,
    active,
    /** A gestora em uso; nulo na conta pessoal */
    fund: active !== undefined && active.fund_id !== null ? active : null,
    /** A chave de cache da conta em uso: a mesma que o cabeçalho X-Account manda ao servidor */
    accountKey: accountKey(selectedFundId, accounts),
    switchAccount,
  };
}
