import { Crown, Flag, Sun, Trophy, type LucideIcon } from "lucide-react";
import type { GameType, VictoryCriterion } from "@/types";
import { VICTORY_CRITERIA } from "./victory-criteria";

type GameTypeInfo = { label: string; description: string; icon: LucideIcon };

/** O tipo que a expansão Governo & Política acrescenta; a tela o mostra à parte dos tipos base. */
export const POLITICAL_GAME_TYPE: GameTypeInfo = {
  label: "Política",
  description: "Vence o partido com a maior soma de patrimônio dos filiados.",
  icon: Crown,
};

/**
 * Tipos de partida que o host escolhe no lobby. A tela itera este mapa: um tipo novo
 * é uma entrada nova aqui, na ordem em que aparece.
 */
export const GAME_TYPES: Partial<Record<GameType, GameTypeInfo>> = {
  CLASSIC: {
    label: "Clássica",
    description: "Joga até a data final; o critério escolhido diz quem vence.",
    icon: Trophy,
  },
  GOAL_RACE: {
    label: "Corrida à meta",
    description: "Vence quem chegar primeiro a um patrimônio-alvo.",
    icon: Flag,
  },
  FINANCIAL_INDEPENDENCE: {
    label: "Viver de renda",
    description: "Salário, despesa e imprevistos; vence quem chegar à independência.",
    icon: Sun,
  },
  POLITICAL: POLITICAL_GAME_TYPE,
};

const GAME_TYPE_OPTIONS = Object.entries(GAME_TYPES) as [GameType, GameTypeInfo][];

/** Os tipos de qualquer partida; os de expansão aparecem à parte, quando a expansão está ligada. */
export const BASE_GAME_TYPE_OPTIONS = GAME_TYPE_OPTIONS.filter(([value]) => value !== "POLITICAL");

/** O que decide a partida em uma palavra: o critério na Clássica, o tipo fora dela. */
export function winRuleLabel(gameType: GameType, criterion: VictoryCriterion) {
  return gameType === "CLASSIC" ? VICTORY_CRITERIA[criterion].label : (GAME_TYPES[gameType]?.label ?? gameType);
}

/** A partida acaba quando alguém chega a um patrimônio-alvo: a meta aparece no topo, no menu e nas estatísticas. */
export function hasGoal(gameType: GameType) {
  return gameType === "GOAL_RACE" || gameType === "FINANCIAL_INDEPENDENCE";
}
