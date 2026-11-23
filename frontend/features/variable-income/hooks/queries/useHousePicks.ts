import { useQuery } from "@tanstack/react-query";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { hasProfessions } from "@/shared/lib/game-types";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { HousePick } from "@/types";

/** As ações do relatório vigente por código, com o lado da recomendação. */
function sidesByTicker(picks: HousePick[]): ReadonlyMap<string, HousePick["side"]> {
  return new Map(picks.map((pick) => [pick.ticker, pick.side]));
}

/**
 * As ações do relatório da casa que o selo marca na Renda variável. Só o Corretor recebe
 * a lista; para os demais ela vem vazia. Busca ao abrir a tela; o aviso do relatório novo
 * pede a releitura.
 */
export function useHousePicks() {
  const { simulation } = useSimulation();
  const current = simulation?.active ? simulation.simulation : null;

  return useQuery({
    queryKey: queryKeys.housePicks(current?.id ?? 0),
    queryFn: ({ signal }) => apiFetch<HousePick[]>("/api/simulation/house-picks", { signal }),
    select: sidesByTicker,
    enabled: current !== null && hasProfessions(current),
    staleTime: 0,
  });
}
