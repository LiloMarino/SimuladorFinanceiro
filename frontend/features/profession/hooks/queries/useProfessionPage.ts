import { useQuery } from "@tanstack/react-query";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { hasProfessions } from "@/shared/lib/game-types";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { ProfessionPage } from "@/types";

/**
 * A página da profissão: o cabeçalho de renda, as séries que mexem nela e o bloco da
 * mecânica. Só existe no viver de renda com uma profissão por jogador. Busca ao abrir a
 * tela; o aviso de que a hora extra pode voltar e o botão da hora extra pedem a releitura.
 */
export function useProfessionPage() {
  const { simulation } = useSimulation();
  const current = simulation?.active ? simulation.simulation : null;

  return useQuery({
    queryKey: queryKeys.profession(current?.id ?? 0),
    queryFn: ({ signal }) => apiFetch<ProfessionPage>("/api/simulation/profession", { signal }),
    enabled: current !== null && hasProfessions(current),
    staleTime: 0,
  });
}
