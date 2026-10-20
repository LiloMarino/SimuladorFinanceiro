import { Flag, Trophy, type LucideIcon } from "lucide-react";
import type { GameType, VictoryCriterion } from "@/types";
import { VICTORY_CRITERIA } from "./victory-criteria";

type GameTypeInfo = { label: string; description: string; icon: LucideIcon };

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
};

export const GAME_TYPE_OPTIONS = Object.entries(GAME_TYPES) as [GameType, GameTypeInfo][];

/** O que decide a partida em uma palavra: o critério na Clássica, o tipo fora dela. */
export function winRuleLabel(gameType: GameType, criterion: VictoryCriterion) {
  return gameType === "CLASSIC" ? VICTORY_CRITERIA[criterion].label : (GAME_TYPES[gameType]?.label ?? gameType);
}
