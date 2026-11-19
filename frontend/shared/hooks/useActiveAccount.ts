import { useQueryClient } from "@tanstack/react-query";
import { useSyncExternalStore } from "react";
import { useFundAccounts } from "@/shared/hooks/queries/useFundAccounts";
import { useSimulation } from "@/shared/hooks/useSimulation";
import {
  accountKey,
  getSelectedFundId,
  hasAccountChoice,
  resolveActiveAccount,
  selectFund,
  subscribeActiveAccount,
} from "@/shared/lib/active-account";
import { queryKeys } from "@/shared/lib/queryKeys";

// Trocar de conta renova tudo isso. A carteira, o caixa e o crédito têm uma entrada de cache
// por conta, e o tempo real mantém viva a da carteira e do caixa.
const ACCOUNT_KEYS = [queryKeys.variableIncome(), queryKeys.fixedIncome(), queryKeys.treasury(), queryKeys.credit()];

/** A conta com que o jogador opera (a pessoal ou uma gestora que ele gere) e a troca entre elas. */
export function useActiveAccount() {
  const queryClient = useQueryClient();
  const { simulation } = useSimulation();
  const match = simulation?.simulation;
  const simulationId = match?.id;
  const { data: accounts } = useFundAccounts({ enabled: hasAccountChoice(match) });

  const storedFundId = useSyncExternalStore(subscribeActiveAccount, () =>
    simulationId === undefined ? null : getSelectedFundId(simulationId),
  );
  // Sem Gestoras nem Governo ligados só existe a conta pessoal
  const selectedFundId = hasAccountChoice(match) ? storedFundId : null;

  const switchAccount = (fundId: number | null) => {
    if (simulationId === undefined) return;
    selectFund(simulationId, fundId);
    ACCOUNT_KEYS.forEach((queryKey) => void queryClient.invalidateQueries({ queryKey }));
  };

  const active = resolveActiveAccount(accounts, selectedFundId);

  return {
    accounts,
    active,
    /** A conta em uso quando não é a pessoal: uma gestora ou o Fundo Soberano; nulo na conta pessoal */
    fund: active !== undefined && active.fund_id !== null ? active : null,
    /** A chave de cache da conta em uso: a mesma que o cabeçalho X-Account manda ao servidor */
    accountKey: accountKey(selectedFundId, accounts),
    switchAccount,
  };
}
