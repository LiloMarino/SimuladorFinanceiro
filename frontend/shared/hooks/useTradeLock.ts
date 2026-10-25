import { useMyStrategy } from "@/shared/hooks/queries/useMyStrategy";
import { useGovernment } from "@/shared/hooks/queries/useGovernment";
import { useSimulation } from "@/shared/hooks/useSimulation";

/** Por que as boletas estão travadas: o automático opera pelo jogador, ou o presidente não opera enquanto governa. */
export type TradeLock = { reason: "automatic" } | { reason: "president"; until: string };

/** O bloqueio das boletas do jogador, ou nulo quando ele opera à mão. */
export function useTradeLock(): TradeLock | null {
  const automatic = !!useMyStrategy().data?.active;
  const { simulation } = useSimulation();
  const { data: government } = useGovernment({ enabled: !!simulation?.simulation?.government_enabled });

  if (government?.is_president && government.portfolio) {
    return { reason: "president", until: government.portfolio.frozen_until };
  }
  return automatic ? { reason: "automatic" } : null;
}
