import { useMyStrategy } from "@/shared/hooks/queries/useMyStrategy";
import { useGovernment } from "@/shared/hooks/queries/useGovernment";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { isSovereignAccount } from "@/shared/lib/active-account";

/**
 * Por que as boletas estão travadas: o automático opera pelo jogador, o presidente não opera
 * enquanto governa, a gestora ativa fica parada porque o gestor governa e ela não tem co-gestor, ou o
 * jogador foi eliminado (perdeu a assembleia da própria gestora) e só assiste.
 */
export type TradeLock =
  | { reason: "eliminated"; since: string }
  | { reason: "automatic" }
  | { reason: "president"; until: string }
  | { reason: "fund"; until: string; name: string }
  | { reason: "sovereign"; name: string };

/** O bloqueio das boletas do jogador, ou nulo quando ele opera à mão. */
export function useTradeLock(): TradeLock | null {
  const automatic = !!useMyStrategy().data?.active;
  const { simulation } = useSimulation();
  const { fund, accounts } = useActiveAccount();
  const { data: government } = useGovernment({ enabled: !!simulation?.simulation?.government_enabled });

  // A eliminação vale em qualquer conta: o jogador só assiste
  const eliminatedOn = accounts?.find((account) => account.fund_id === null)?.eliminated_on;
  if (eliminatedOn) return { reason: "eliminated", since: eliminatedOn };

  // Com uma gestora ativa vale o congelamento dela, não o da conta pessoal
  if (fund?.frozen_until) return { reason: "fund", until: fund.frozen_until, name: fund.name };
  if (!fund && government?.is_president && government.portfolio) {
    return { reason: "president", until: government.portfolio.frozen_until };
  }
  return automatic ? { reason: "automatic" } : null;
}

/** O bloqueio das boletas de renda fixa e Tesouro: as de sempre, mais a conta do Fundo Soberano, que só compra ações e cotas de gestora. */
export function useFixedIncomeLock(): TradeLock | null {
  const lock = useTradeLock();
  const { fund } = useActiveAccount();
  if (lock) return lock;
  return isSovereignAccount(fund) && fund ? { reason: "sovereign", name: fund.name } : null;
}
