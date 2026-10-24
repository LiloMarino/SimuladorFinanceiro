import { useStatisticsReport } from "@/shared/hooks/queries/useStatisticsReport";
import { useSimulation } from "@/shared/hooks/useSimulation";
import type { GoalRise } from "@/shared/lib/goal";
import { parseLocalDate } from "@/shared/lib/utils/display";
import { hasGoal } from "@/shared/lib/game-types";

// Por quantos dias da partida o aviso de meta subindo fica na topbar
const RISE_NOTICE_DAYS = 30;

/**
 * A meta em degraus da partida em andamento (o início e cada reajuste pelo IPCA).
 * Vazia na Clássica; na corrida é um ponto só.
 */
export function useGoalSteps() {
  const { simulation } = useSimulation();
  const current = simulation?.active ? simulation.simulation : null;

  const { data } = useStatisticsReport("overview", current && hasGoal(current.game_type) ? [current.id] : []);
  return data?.goal_steps;
}

/** O último reajuste da meta pelo IPCA, enquanto o dia da partida está a até 30 dias dele. */
export function useGoalRise(currentDate: string | undefined): GoalRise | null {
  const steps = useGoalSteps();
  if (!steps || steps.length < 2 || !currentDate) return null;

  const last = steps[steps.length - 1];
  const previous = steps[steps.length - 2];
  const days = (parseLocalDate(currentDate).getTime() - parseLocalDate(last.date).getTime()) / 86_400_000;
  if (days > RISE_NOTICE_DAYS) return null;
  return {
    fraction: Number(last.value) / Number(previous.value) - 1,
    date: last.date,
  };
}
