import { useGovernment } from "@/shared/hooks/queries/useGovernment";
import { useSimulation } from "@/shared/hooks/useSimulation";
import type { GovernmentPanel } from "@/types";

/** O último dia do mandato do jogador presidente, até quando a carteira dele congela se ele desligar o automático; nulo fora da presidência. */
export const presidencyFreezeEnd = (government: GovernmentPanel | undefined) =>
  government?.is_president && government.portfolio ? government.portfolio.frozen_until : null;

/** O fim do mandato do presidente logado, vindo do painel do governo. */
export function usePresidencyFreeze() {
  const { simulation } = useSimulation();
  const { data: government } = useGovernment({ enabled: !!simulation?.simulation?.government_enabled });
  return presidencyFreezeEnd(government);
}
