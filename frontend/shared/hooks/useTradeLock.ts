import { useMyStrategy } from "@/shared/hooks/queries/useMyStrategy";
import { useGovernment } from "@/shared/hooks/queries/useGovernment";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import { useSimulation } from "@/shared/hooks/useSimulation";

/**
 * Por que as boletas estão travadas: o automático opera pelo jogador, o presidente não opera
 * enquanto governa, ou a gestora ativa fica parada porque o gestor governa e ela não tem co-gestor.
 */
export type TradeLock =
  | { reason: "automatic" }
  | { reason: "president"; until: string }
  | { reason: "fund"; until: string; name: string };

/** O bloqueio das boletas do jogador, ou nulo quando ele opera à mão. */
export function useTradeLock(): TradeLock | null {
  const automatic = !!useMyStrategy().data?.active;
  const { simulation } = useSimulation();
  const { fund } = useActiveAccount();
  const { data: government } = useGovernment({ enabled: !!simulation?.simulation?.government_enabled });

  // Com uma gestora ativa vale o congelamento dela, não o da conta pessoal
  if (fund?.frozen_until) return { reason: "fund", until: fund.frozen_until, name: fund.name };
  if (!fund && government?.is_president && government.portfolio) {
    return { reason: "president", until: government.portfolio.frozen_until };
  }
  return automatic ? { reason: "automatic" } : null;
}
