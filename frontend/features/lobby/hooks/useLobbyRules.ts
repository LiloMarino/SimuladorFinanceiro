import { useSimulationList } from "@/shared/hooks/queries/useSimulationList";
import type { SimulationSettings } from "@/types";

/** As regras que valem para a sala: as da partida salva selecionada ou, sem seleção, as da nova partida. */
export function useLobbyRules(settings: SimulationSettings) {
  const { data: savedSimulations } = useSimulationList();
  const selected = savedSimulations?.find((s) => s.id === settings.selected_simulation_id);
  const rules = selected ?? settings.simulation;
  // Cada jogador escolhe uma profissão só no viver de renda com o modo de profissões
  const professions = rules.game_type === "FINANCIAL_INDEPENDENCE" && rules.salary_mode === "PROFESSIONS";
  return { grouping: rules.player_grouping, naming: rules.team_naming, professions };
}
