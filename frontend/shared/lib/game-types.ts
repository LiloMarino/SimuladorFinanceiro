import { Building, Crown, Flag, Sun, Trophy, type LucideIcon } from "lucide-react";
import type { GameType, SimulationData, VictoryCriterion } from "@/types";
import type { ExpansionKey } from "./expansions";
import { VICTORY_CRITERIA } from "./victory-criteria";

type GameTypeInfo = {
  label: string;
  description: string;
  icon: LucideIcon;
  /** A expansão que o tipo exige ligada; ausente nos tipos de qualquer partida */
  expansion?: ExpansionKey;
};

/** O tipo que a expansão Governo & Política acrescenta. */
export const POLITICAL_GAME_TYPE: GameTypeInfo = {
  label: "Política",
  description: "Vence o partido com mais capital político: pontos de cadeiras, presidência e promessas cumpridas.",
  icon: Crown,
  expansion: "government",
};

/** O tipo que a expansão Gestoras acrescenta. */
export const FUND_TAKEOVER_GAME_TYPE: GameTypeInfo = {
  label: "Aquisição hostil",
  description: "Todos começam com a carteira dentro da própria gestora. Vence o último jogador de pé.",
  icon: Building,
  expansion: "funds",
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
  FUND_TAKEOVER: FUND_TAKEOVER_GAME_TYPE,
};

/** Tipo que exige uma expansão ligada: `expansion` sempre presente. */
type ExpansionGameTypeInfo = GameTypeInfo & { expansion: ExpansionKey };

const GAME_TYPE_OPTIONS = Object.entries(GAME_TYPES) as [GameType, GameTypeInfo][];

function isExpansionOption(option: [GameType, GameTypeInfo]): option is [GameType, ExpansionGameTypeInfo] {
  return option[1].expansion !== undefined;
}

/** Os tipos de qualquer partida. */
export const BASE_GAME_TYPE_OPTIONS = GAME_TYPE_OPTIONS.filter(([, type]) => !type.expansion);

/** Os tipos de expansão: aparecem sempre, e só se escolhem com a expansão ligada. */
export const EXPANSION_GAME_TYPE_OPTIONS = GAME_TYPE_OPTIONS.filter(isExpansionOption);

/** O que decide a partida em uma palavra: o critério na Clássica, o tipo fora dela. */
export function winRuleLabel(gameType: GameType, criterion: VictoryCriterion) {
  return gameType === "CLASSIC" ? VICTORY_CRITERIA[criterion].label : (GAME_TYPES[gameType]?.label ?? gameType);
}

/** O viver de renda com uma profissão por jogador: a página Profissão só existe nele. */
export function hasProfessions(match: Pick<SimulationData, "game_type" | "salary_mode">) {
  return match.game_type === "FINANCIAL_INDEPENDENCE" && match.salary_mode === "PROFESSIONS";
}

/** A partida acaba quando alguém chega a um patrimônio-alvo: a meta aparece no topo, no menu e nas estatísticas. */
export function hasGoal(gameType: GameType) {
  return gameType === "GOAL_RACE" || gameType === "FINANCIAL_INDEPENDENCE";
}
