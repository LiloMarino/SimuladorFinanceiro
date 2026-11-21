import { useGovernmentStatus } from "@/shared/hooks/queries/useGovernmentStatus";
import { useSimulation } from "@/shared/hooks/useSimulation";
import type { GovernmentStatus } from "@/types";

/** O último dia do mandato do jogador presidente, até quando a carteira dele congela se ele desligar o automático; nulo fora da presidência. */
export const presidencyFreezeEnd = (government: GovernmentStatus | undefined) =>
  government?.is_president ? government.frozen_until : null;

/** O fim do mandato do presidente logado, vindo do resumo do governo. */
export function usePresidencyFreeze() {
  const { simulation } = useSimulation();
  const { data: government } = useGovernmentStatus({ enabled: !!simulation?.simulation?.government_enabled });
  return presidencyFreezeEnd(government);
}
