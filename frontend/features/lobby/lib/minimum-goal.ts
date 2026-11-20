import { WITHDRAWAL_RATE_RANGE } from "@/shared/lib/financial-independence";
import { PROFESSIONS } from "@/shared/lib/professions";
import { normalizeNumberString } from "@/shared/lib/utils";
import { displayMoneyWhole } from "@/shared/lib/utils/display";
import type { GameType, SalaryMode } from "@/types";
import { calculatedGoal } from "./life-rules";

/** O Herdeiro da sala, jogador ou bot, com o capital com que ele começa. */
export type RoomHeir = {
  nickname: string;
  isBot: boolean;
  capital: number;
};

type GoalValues = {
  gameType: GameType;
  goalNetWorth: string;
  monthlyExpense: string;
  withdrawalRate: string;
};

const EXPENSE_STEP = 100;
const RATE_STEP = 0.1;
// Folga que absorve o erro de ponto flutuante nas fronteiras dos arredondamentos
const EPSILON = 1e-9;

/** A meta que o tipo de partida pede, em reais; nula nos tipos sem meta e com campos inválidos. */
export function ruleGoal(values: GoalValues): number | null {
  if (values.gameType === "GOAL_RACE") {
    const goal = Number(normalizeNumberString(values.goalNetWorth));
    return goal > 0 ? goal : null;
  }
  if (values.gameType === "FINANCIAL_INDEPENDENCE") return calculatedGoal(values.monthlyExpense, values.withdrawalRate);
  return null;
}

type HeirValues = { gameType: GameType; salaryMode: SalaryMode };

/** O Herdeiro só pesa no piso quando cada jogador escolhe a profissão: no viver de renda com o modo de profissões. */
function activeHeir(heir: RoomHeir | null, values: HeirValues) {
  const usesProfessions = values.gameType === "FINANCIAL_INDEPENDENCE" && values.salaryMode === "PROFESSIONS";
  return usesProfessions ? heir : null;
}

/** O capital do Herdeiro quando a meta da regra não passa dele e ele começa acima do saldo inicial; nulo quando a meta passa ou sem Herdeiro. */
export function blockingHeirFloor(heir: RoomHeir | null, values: GoalValues & HeirValues & { startingCash: string }) {
  const richHeir = activeHeir(heir, values);
  const goal = ruleGoal(values);
  if (!richHeir || goal === null) return null;
  const cash = Number(normalizeNumberString(values.startingCash));
  return richHeir.capital > cash && goal <= richHeir.capital ? richHeir.capital : null;
}

/** O menor valor inteiro em reais que uma meta pode ter para passar do piso. */
export const minimumGoal = (floor: number) => Math.ceil(floor);

/** O aviso curto da meta abaixo do capital do Herdeiro. */
export const heirFloorMessage = (floor: number) =>
  `Meta mínima de ${displayMoneyWhole(minimumGoal(floor))} por causa do ${PROFESSIONS.HEIR.name}.`;

/** A menor despesa mensal, em múltiplos de R$ 100, cuja meta passa do piso com essa taxa (fração ao ano). */
export function minimumExpense(floor: number, rate: number) {
  const exact = (floor * rate) / 12;
  return (Math.floor(exact / EXPENSE_STEP + EPSILON) + 1) * EXPENSE_STEP;
}

/** A maior taxa de retirada, em pontos percentuais com uma casa, cuja meta passa do piso com essa despesa; nula abaixo do mínimo que o servidor aceita. */
export function maximumWithdrawalPercent(floor: number, expense: number) {
  const exact = (12 * expense * 100) / floor;
  const below = Math.round((Math.ceil(exact / RATE_STEP - EPSILON) * RATE_STEP - RATE_STEP) * 10) / 10;
  return below >= WITHDRAWAL_RATE_RANGE.min * 100 - EPSILON ? below : null;
}
